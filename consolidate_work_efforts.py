#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Work Effort Consolidator

This script automates the consolidation of work effort files from various directories across a project
into a single centralized location (.AI-Setup/work_efforts). It also provides options
for adding Obsidian-style links between related documents.

Workflow Description:
---------------------
This script captures and replicates the following manual workflow:

1. Discovery Phase:
   - Finding all directories that contain work efforts across a project
   - Identifying markdown files that represent work efforts
   - Categorizing work efforts based on their status (active, completed, archived)

2. Consolidation Phase:
   - Creating a centralized directory structure for work efforts
   - Preserving the hierarchical organization with subdirectories
   - Resolving file naming conflicts during consolidation
   - Handling file copying with appropriate error management

3. Knowledge Linking Phase (Optional):
   - Analyzing content relationships between work efforts
   - Implementing Obsidian-style wiki links ([[document]]) between related documents
   - Updating frontmatter metadata to track relationships
   - Building a network of connected documents for easier navigation

4. Cleanup Phase:
   - Safely removing original scattered directories after confirmation
   - Preserving the original structure in the centralized location

5. Documentation Update Phase:
   - Updating project documentation (changelog, devlog)
   - Recording the consolidation process for traceability

The script mimics how a developer would manually:
- Search for work effort files across a project
- Decide how to organize them in a central location
- Establish connections between related documents
- Clean up duplicate or scattered files after migration
- Update project documentation to reflect changes

Usage:
    python consolidate_work_efforts.py [--dry-run] [--no-delete] [--force] [--add-links]
    python consolidate_work_efforts.py --root-dir /path/to/project --dest-dir /path/to/destination

Options:
    --root-dir PATH     Root directory to search for work efforts (default: current directory)
    --dest-dir PATH     Destination directory for consolidated work efforts (default: .AI-Setup/work_efforts)
    --dry-run           Don't actually copy or delete files, just show what would be done
    --no-delete         Copy files but don't delete the original directories
    --force             Don't ask for confirmation before deleting original directories
    --add-links         Scan for related documents and add Obsidian-style links
    --verbose           Enable verbose logging
"""

import os
import sys
import shutil
import re
import argparse
import logging
import datetime
import yaml
import fnmatch
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('consolidate_work_efforts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
ROOT_DIR = os.getcwd()
DEST_DIR = os.path.join(ROOT_DIR, '.AI-Setup', 'work_efforts')
WORK_EFFORT_DIR_PATTERNS = [
    '*work_effort*',
    '*work-effort*',
    'work_efforts',
    'work-efforts',
    'work_effort',
    'work-effort',
]
EXCLUDED_DIRS = ['.git', 'node_modules', 'venv', '.env', '__pycache__']
SUBDIRS_TO_CREATE = ['active', 'completed', 'archived', 'templates']
MARKDOWN_EXTENSIONS = ['.md', '.markdown']
YAML_FRONTMATTER_PATTERN = re.compile(r'^---\s*$(.*?)^---\s*$', re.MULTILINE | re.DOTALL)
WIKI_LINK_PATTERN = re.compile(r'\[\[(.*?)\]\]')
CHANGELOG_PATH = 'CHANGELOG.md'
DEVLOG_PATH = os.path.join('.AI-Setup', 'work_efforts', 'devlog.md')

class WorkEffortConsolidator:
    """
    Class to consolidate work efforts from across a project into a central location.

    This class encapsulates the entire workflow for work effort consolidation:
    1. Finding work effort directories
    2. Copying work effort files to a central location
    3. Categorizing files into appropriate subdirectories
    4. Adding Obsidian-style links between related documents
    5. Cleaning up original directories
    6. Updating project documentation

    The process follows the principle of safe operations:
    - Dry run mode to preview changes without applying them
    - Confirmation before deleting original directories
    - Handling of file collisions to prevent data loss
    - Comprehensive logging of all operations
    """

    def __init__(self, root_dir=ROOT_DIR, dest_dir=DEST_DIR, dry_run=False,
                 no_delete=False, force=False, add_links=False, verbose=False):
        """
        Initialize the consolidator with given parameters.

        This sets up the consolidation process with the specified options and
        prepares the environment for work effort consolidation.

        Args:
            root_dir (str): Root directory to search for work efforts
            dest_dir (str): Destination directory for consolidated work efforts
            dry_run (bool): If True, don't actually make any changes, just log what would be done
            no_delete (bool): If True, don't delete original directories after copying
            force (bool): If True, don't ask for confirmation before deleting original directories
            add_links (bool): If True, scan for related documents and add Obsidian-style links
            verbose (bool): If True, enable verbose logging
        """
        self.root_dir = os.path.abspath(root_dir)
        self.dest_dir = os.path.abspath(dest_dir)
        self.dry_run = dry_run
        self.no_delete = no_delete
        self.force = force
        self.add_links = add_links
        self.verbose = verbose

        if verbose:
            logger.setLevel(logging.DEBUG)

        # Stats
        self.found_dirs = []
        self.copied_files = []
        self.deleted_dirs = []
        self.linked_docs = []

        logger.info(f"Initializing Work Effort Consolidator")
        logger.info(f"Root directory: {self.root_dir}")
        logger.info(f"Destination directory: {self.dest_dir}")
        logger.info(f"Dry run: {self.dry_run}")
        logger.info(f"No delete: {self.no_delete}")
        logger.info(f"Force: {self.force}")
        logger.info(f"Add links: {self.add_links}")

    def ensure_dest_dir_exists(self):
        """
        Ensure the destination directory exists with all required subdirectories.

        This mimics the manual process of:
        1. Creating a main work efforts directory if it doesn't exist
        2. Creating standard subdirectories for organizing work efforts by status:
           - active: For work efforts currently in progress
           - completed: For finished work efforts
           - archived: For old or deprecated work efforts
           - templates: For template files used to create new work efforts

        In dry run mode, this only logs the directories that would be created.
        """
        logger.info(f"Ensuring destination directory exists: {self.dest_dir}")

        if not os.path.exists(self.dest_dir):
            if not self.dry_run:
                os.makedirs(self.dest_dir, exist_ok=True)
                logger.info(f"Created destination directory: {self.dest_dir}")
            else:
                logger.info(f"Would create destination directory: {self.dest_dir}")

        # Create subdirectories
        for subdir in SUBDIRS_TO_CREATE:
            subdir_path = os.path.join(self.dest_dir, subdir)
            if not os.path.exists(subdir_path):
                if not self.dry_run:
                    os.makedirs(subdir_path, exist_ok=True)
                    logger.info(f"Created subdirectory: {subdir_path}")
                else:
                    logger.info(f"Would create subdirectory: {subdir_path}")

    def find_work_effort_dirs(self):
        """
        Find all work effort directories in the project.

        This replicates the manual discovery process where a developer would:
        1. Search through a project's directory structure
        2. Identify directories that contain work efforts based on naming patterns
        3. Skip certain directories that should be excluded from the search

        The search is heuristic-based, looking for directory names that match common
        patterns for work effort directories. It also applies exclusions for standard
        directories that should never be included (like .git, node_modules, etc.).

        Returns:
            list: List of directory paths containing work efforts
        """
        logger.info(f"Searching for work effort directories in {self.root_dir}")

        work_effort_dirs = []

        for root, dirs, _ in os.walk(self.root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith('.')]

            # Skip the destination directory itself
            if os.path.normpath(root) == os.path.normpath(self.dest_dir):
                continue

            # Check if current directory matches pattern
            dir_name = os.path.basename(root)
            if any(fnmatch.fnmatch(dir_name.lower(), pattern) for pattern in WORK_EFFORT_DIR_PATTERNS):
                work_effort_dirs.append(root)
                if self.verbose:
                    logger.debug(f"Found work effort directory: {root}")

        logger.info(f"Found {len(work_effort_dirs)} work effort directories")
        self.found_dirs = work_effort_dirs
        return work_effort_dirs

    def copy_files(self, dirs):
        """
        Copy all markdown files from work effort directories to destination.

        This replicates the manual process of:
        1. Going through each work effort directory
        2. Identifying markdown files that represent work efforts
        3. Determining which category each work effort belongs to (active, completed, etc.)
        4. Creating the appropriate directory structure in the destination
        5. Copying the files with conflict resolution

        The function specifically only copies markdown files, as these are the primary
        content files for work efforts. Other files (like images, code, etc.) are not copied
        to maintain focused organization.

        Args:
            dirs (list): List of directories containing work efforts

        Returns:
            list: List of tuples (source_path, dest_path) of copied files
        """
        logger.info(f"Copying files to {self.dest_dir}")

        copied_files = []

        for work_dir in dirs:
            relative_path = os.path.relpath(work_dir, self.root_dir)

            # Skip directories that are already in the destination path
            if relative_path.startswith('.AI-Setup/work_efforts'):
                logger.info(f"Skipping directory already in destination: {work_dir}")
                continue

            for root, _, files in os.walk(work_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file)

                    # Only copy markdown files
                    if ext.lower() not in MARKDOWN_EXTENSIONS:
                        continue

                    # Determine appropriate subdirectory
                    file_content = self._read_file(file_path)
                    subdirectory = self._determine_subdirectory(file_content, file)

                    # Create destination path
                    dest_path = os.path.join(self.dest_dir, subdirectory, file)

                    # Handle file name collisions
                    dest_path = self._handle_name_collision(dest_path)

                    # Copy file
                    if not self.dry_run:
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(file_path, dest_path)
                        logger.info(f"Copied {file_path} to {dest_path}")
                    else:
                        logger.info(f"Would copy {file_path} to {dest_path}")

                    copied_files.append((file_path, dest_path))

        logger.info(f"Copied {len(copied_files)} files")
        self.copied_files = copied_files
        return copied_files

    def _read_file(self, file_path):
        """
        Read the content of a file.

        This is a utility function that safely reads a file's content,
        handling potential errors like encoding issues or file access problems.

        Args:
            file_path (str): Path to the file to read

        Returns:
            str: Content of the file, or empty string if reading fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

    def _determine_subdirectory(self, content, filename):
        """
        Determine which subdirectory a file should go into based on its content.

        This replicates the manual process of examining a work effort document and
        deciding where it should be placed based on its status or content:

        1. Templates go into the 'templates' directory
        2. Completed work efforts go into the 'completed' directory
        3. Archived work efforts go into the 'archived' directory
        4. All other work efforts are considered active

        The function examines:
        - The filename for template patterns
        - The frontmatter metadata for status fields
        - Keywords in the content that indicate the status

        Args:
            content (str): Content of the file
            filename (str): Name of the file

        Returns:
            str: Name of the subdirectory where the file should be placed
        """
        content_lower = content.lower()

        # Check for templates
        if 'template' in filename.lower():
            return 'templates'

        # Check for status in frontmatter
        match = YAML_FRONTMATTER_PATTERN.search(content)
        if match:
            frontmatter_text = match.group(1)
            if 'status:' in frontmatter_text:
                status_line = re.search(r'status:\s*"?(.*?)"?$', frontmatter_text, re.MULTILINE)
                if status_line:
                    status = status_line.group(1).lower().strip()
                    if 'complete' in status or 'done' in status or 'finished' in status:
                        return 'completed'
                    if 'archive' in status or 'archived' in status:
                        return 'archived'

        # Default to active
        return 'active'

    def _handle_name_collision(self, dest_path):
        """
        Handle file name collisions by adding a suffix if necessary.

        This replicates the manual process of finding a unique filename when
        a file with the same name already exists in the destination:

        1. Check if the destination file exists
        2. If it does, add a numeric suffix to the filename
        3. Increment the suffix until a unique filename is found

        This approach preserves both files while avoiding overwriting.

        Args:
            dest_path (str): Destination path that might have a collision

        Returns:
            str: Modified destination path with suffix if needed
        """
        if not os.path.exists(dest_path) or self.dry_run:
            return dest_path

        base, ext = os.path.splitext(dest_path)
        counter = 1

        while True:
            new_path = f"{base}_{counter}{ext}"
            if not os.path.exists(new_path):
                logger.warning(f"File collision detected, renamed to {new_path}")
                return new_path
            counter += 1

    def delete_original_dirs(self, dirs):
        """
        Delete the original work effort directories after copying.

        This replicates the manual process of cleaning up after consolidation:

        1. Confirming with the user before deleting directories (unless forced)
        2. Skipping directories that are already in the destination
        3. Safely deleting each directory and handling errors

        The function respects the no_delete and dry_run flags to provide different
        levels of caution when removing directories.

        Args:
            dirs (list): List of directories to delete

        Returns:
            list: List of directories that were successfully deleted
        """
        if self.no_delete or self.dry_run:
            if self.no_delete:
                logger.info("Skipping deletion of original directories (--no-delete)")
            return []

        deleted_dirs = []

        # Ask for confirmation if not in force mode
        if not self.force:
            response = input(f"Are you sure you want to delete {len(dirs)} original work effort directories? [y/N] ")
            if response.lower() not in ['y', 'yes']:
                logger.info("Deletion cancelled by user")
                return []

        for directory in dirs:
            # Skip directories that are already in the destination path
            relative_path = os.path.relpath(directory, self.root_dir)
            if relative_path.startswith('.AI-Setup/work_efforts'):
                continue

            try:
                shutil.rmtree(directory)
                logger.info(f"Deleted directory: {directory}")
                deleted_dirs.append(directory)
            except Exception as e:
                logger.error(f"Error deleting directory {directory}: {e}")

        logger.info(f"Deleted {len(deleted_dirs)} directories")
        self.deleted_dirs = deleted_dirs
        return deleted_dirs

    def add_obsidian_links(self):
        """
        Add Obsidian-style links between related documents.

        This replicates the manual process of knowledge linking:

        1. Scanning all work effort documents for content relationships
        2. Identifying documents that mention other documents
        3. Adding Obsidian-style wiki links ([[document]]) in frontmatter
        4. Creating a knowledge graph of connected documents

        The process enhances navigation between related work efforts and
        builds a more connected knowledge base.

        Returns:
            list: List of documents that had links added to them
        """
        if not self.add_links:
            logger.info("Skipping addition of Obsidian-style links (--add-links not specified)")
            return

        logger.info("Adding Obsidian-style links between related documents")

        # Gather all documents and their titles
        documents = {}
        for subdir in SUBDIRS_TO_CREATE:
            subdir_path = os.path.join(self.dest_dir, subdir)
            if not os.path.exists(subdir_path):
                continue

            for file in os.listdir(subdir_path):
                if not any(file.endswith(ext) for ext in MARKDOWN_EXTENSIONS):
                    continue

                file_path = os.path.join(subdir_path, file)
                content = self._read_file(file_path)

                # Extract title from frontmatter or filename
                title = self._extract_title(content, file)
                documents[file_path] = {
                    'title': title,
                    'filename': file,
                    'content': content,
                    'related': []
                }

        # Find relationships between documents
        for path, doc_info in documents.items():
            for other_path, other_info in documents.items():
                if path == other_path:
                    continue

                # Check if document mentions other document's title
                if other_info['title'].lower() in doc_info['content'].lower():
                    doc_info['related'].append((other_path, other_info['filename']))

        # Update documents with links
        linked_docs = []
        for path, doc_info in documents.items():
            if not doc_info['related']:
                continue

            updated_content = self._add_links_to_document(doc_info)

            if not self.dry_run:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                    logger.info(f"Added links to {path}")
            else:
                logger.info(f"Would add links to {path}")

            linked_docs.append(path)

        logger.info(f"Added links to {len(linked_docs)} documents")
        self.linked_docs = linked_docs
        return linked_docs

    def _extract_title(self, content, filename):
        """
        Extract the title from frontmatter or fallback to filename.

        This replicates the manual process of identifying a document's title:

        1. Looking for a title field in the frontmatter metadata
        2. Falling back to using the filename (without extension) if no title is found

        The title is used to establish relationships between documents and
        for creating readable links.

        Args:
            content (str): Content of the document
            filename (str): Name of the file

        Returns:
            str: Title of the document
        """
        match = YAML_FRONTMATTER_PATTERN.search(content)
        if match:
            frontmatter_text = match.group(1)
            title_match = re.search(r'title:\s*"?(.*?)"?$', frontmatter_text, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip()

        # Fallback to filename without extension
        return os.path.splitext(filename)[0]

    def _add_links_to_document(self, doc_info):
        """
        Add links to a document's frontmatter and content.

        This replicates the manual process of updating a document with links:

        1. Processing the document's frontmatter if it exists
        2. Adding or updating a related_efforts field in the frontmatter
        3. Adding Obsidian-style wiki links to related documents
        4. Creating new frontmatter if none exists

        The function preserves existing content while adding the relationship metadata.

        Args:
            doc_info (dict): Information about the document and its related documents

        Returns:
            str: Updated content with added links
        """
        content = doc_info['content']

        # Process frontmatter if it exists
        match = YAML_FRONTMATTER_PATTERN.search(content)
        if match:
            frontmatter_text = match.group(1)

            # Check if related_efforts field exists
            if 'related_efforts:' in frontmatter_text:
                # Update existing related_efforts field
                updated_frontmatter = frontmatter_text
            else:
                # Add related_efforts field
                updated_frontmatter = frontmatter_text.rstrip() + "\nrelated_efforts:\n"

            # Add related documents to frontmatter
            for _, filename in doc_info['related']:
                if f"[[{filename}]]" not in updated_frontmatter:
                    updated_frontmatter += f"  - [[{filename}]]\n"

            # Replace frontmatter in content
            content = content.replace(match.group(0), f"---\n{updated_frontmatter}---\n")
        else:
            # Create new frontmatter if none exists
            related_links = "\n".join([f"  - [[{filename}]]" for _, filename in doc_info['related']])
            new_frontmatter = f"---\ntitle: \"{doc_info['title']}\"\nrelated_efforts:\n{related_links}\n---\n\n"
            content = new_frontmatter + content

        return content

    def update_documentation(self):
        """
        Update project documentation (changelog, devlog) with consolidation information.

        This replicates the manual process of documenting changes to a project:

        1. Updating the changelog with details about the consolidation
        2. Updating the devlog with a detailed entry about the work completed

        This ensures that the consolidation process is properly documented for
        future reference and project history.
        """
        logger.info("Updating project documentation")

        # Update changelog
        self._update_changelog()

        # Update devlog
        self._update_devlog()

    def _update_changelog(self):
        """
        Update the project changelog with consolidation information.

        This replicates the manual process of updating a changelog:

        1. Finding the Unreleased section in the changelog
        2. Adding entries about the consolidation process
        3. Categorizing changes into Added and Changed sections

        The function respects the dry_run flag and handles file access issues.

        The changelog update follows standard changelog formatting conventions.
        """
        changelog_path = os.path.join(self.root_dir, CHANGELOG_PATH)
        if not os.path.exists(changelog_path):
            logger.warning(f"Changelog not found at {changelog_path}, skipping update")
            return

        if self.dry_run:
            logger.info(f"Would update changelog at {changelog_path}")
            return

        try:
            with open(changelog_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Find the Unreleased section
            unreleased_match = re.search(r'## \[Unreleased\]\s*\n', content)
            if unreleased_match:
                insert_pos = unreleased_match.end()

                # Create update text
                update_text = (
                    "\n### Added\n"
                    "- Consolidated work efforts into a centralized location\n"
                    "- Added Obsidian-style document linking between related work efforts\n"
                    "- Created work effort naming conventions documentation\n"
                    "\n### Changed\n"
                    "- Reorganized work effort directories for better structure\n"
                    "- Enhanced linking between related work efforts\n"
                    "\n"
                )

                # Insert update text
                updated_content = content[:insert_pos] + update_text + content[insert_pos:]

                with open(changelog_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                logger.info(f"Updated changelog at {changelog_path}")
            else:
                logger.warning(f"Could not find Unreleased section in changelog, skipping update")
        except Exception as e:
            logger.error(f"Error updating changelog: {e}")

    def _update_devlog(self):
        """
        Update the project devlog with consolidation information.

        This replicates the manual process of recording detailed project activities:

        1. Creating a new entry in the devlog with the current date
        2. Documenting the goal, completed tasks, and benefits of the consolidation
        3. Linking to related work efforts for context

        The devlog entry provides a comprehensive record of the consolidation process,
        including quantitative information about files processed.
        """
        devlog_path = os.path.join(self.root_dir, DEVLOG_PATH)
        if not os.path.exists(devlog_path):
            logger.warning(f"Devlog not found at {devlog_path}, skipping update")
            return

        if self.dry_run:
            logger.info(f"Would update devlog at {devlog_path}")
            return

        try:
            with open(devlog_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Create update text
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            update_text = (
                f"\n## Work Effort Consolidation - {today}\n\n"
                f"### Goal\n\n"
                f"Consolidate all work efforts into a single location for better organization and linking.\n\n"
                f"### Completed Tasks\n\n"
                f"- Moved {len(self.copied_files)} work effort files to {self.dest_dir}\n"
                f"- Cleaned up {len(self.deleted_dirs)} duplicated directories\n"
                f"- {'Added Obsidian-style links between ' + str(len(self.linked_docs)) + ' documents' if self.add_links else 'Preserved existing document structure'}\n"
                f"- Established a standard location for all work efforts\n\n"
                f"### Benefits\n\n"
                f"- Simplified maintenance and discovery of work efforts\n"
                f"- Reduced duplication and fragmentation\n"
                f"- Improved findability and organization\n"
                f"- Enhanced integration with Obsidian-style linking\n\n"
                f"### Related Work\n\n"
                f"- [[work_effort_naming_conventions]]\n"
                f"- [[obsidian_style_document_linking]]\n\n"
            )

            # Append update text
            updated_content = content + update_text

            with open(devlog_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            logger.info(f"Updated devlog at {devlog_path}")
        except Exception as e:
            logger.error(f"Error updating devlog: {e}")

    def run(self):
        """
        Run the consolidation process.

        This is the main orchestration method that executes the entire workflow:

        1. Ensuring the destination directory structure exists
        2. Finding all work effort directories
        3. Copying relevant files to the destination
        4. Optionally adding Obsidian-style links between documents
        5. Optionally deleting original directories
        6. Updating project documentation

        The method follows a sequential process with appropriate checks and validation
        at each step to ensure safe execution. It also collects and returns statistics
        about the operations performed.

        Returns:
            dict: Statistics about the consolidation process, or None if it fails
        """
        logger.info("Starting work effort consolidation process")

        # Ensure destination directory exists
        self.ensure_dest_dir_exists()

        # Find work effort directories
        work_effort_dirs = self.find_work_effort_dirs()

        if not work_effort_dirs:
            logger.warning("No work effort directories found")
            return

        # Copy files
        copied_files = self.copy_files(work_effort_dirs)

        if not copied_files:
            logger.warning("No files were copied")
            return

        # Add Obsidian-style links
        if self.add_links:
            self.add_obsidian_links()

        # Delete original directories if requested
        if not self.no_delete and not self.dry_run:
            self.delete_original_dirs(work_effort_dirs)

        # Update documentation
        if not self.dry_run:
            self.update_documentation()

        logger.info("Work effort consolidation completed successfully")
        logger.info(f"Found {len(self.found_dirs)} directories")
        logger.info(f"Copied {len(self.copied_files)} files")
        logger.info(f"Deleted {len(self.deleted_dirs)} directories")
        if self.add_links:
            logger.info(f"Added links to {len(self.linked_docs)} documents")

        return {
            'found_dirs': len(self.found_dirs),
            'copied_files': len(self.copied_files),
            'deleted_dirs': len(self.deleted_dirs),
            'linked_docs': len(self.linked_docs) if self.add_links else 0
        }

def parse_args():
    """
    Parse command line arguments.

    This function sets up the command-line interface for the script,
    defining the available options and their default values.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Consolidate work effort files from various directories.')
    parser.add_argument('--root-dir', dest='root_dir', default=ROOT_DIR,
                        help=f'Root directory to search for work efforts (default: {ROOT_DIR})')
    parser.add_argument('--dest-dir', dest='dest_dir', default=DEST_DIR,
                        help=f'Destination directory for consolidated work efforts (default: {DEST_DIR})')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        help="Don't actually copy or delete files, just show what would be done")
    parser.add_argument('--no-delete', dest='no_delete', action='store_true',
                        help="Copy files but don't delete the original directories")
    parser.add_argument('--force', dest='force', action='store_true',
                        help="Don't ask for confirmation before deleting original directories")
    parser.add_argument('--add-links', dest='add_links', action='store_true',
                        help="Scan for related documents and add Obsidian-style links")
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help="Enable verbose logging")
    return parser.parse_args()

def main():
    """
    Main function that serves as the entry point for the script.

    This function:
    1. Parses command line arguments
    2. Creates a WorkEffortConsolidator instance with the specified options
    3. Runs the consolidation process
    4. Handles any exceptions that occur
    5. Prints a summary of the results

    The function follows a standard pattern for command-line scripts:
    - Parse arguments
    - Execute main functionality
    - Handle errors and interruptions
    - Return appropriate exit code

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    args = parse_args()

    consolidator = WorkEffortConsolidator(
        root_dir=args.root_dir,
        dest_dir=args.dest_dir,
        dry_run=args.dry_run,
        no_delete=args.no_delete,
        force=args.force,
        add_links=args.add_links,
        verbose=args.verbose
    )

    try:
        results = consolidator.run()
        if results:
            print("\nWork effort consolidation completed successfully!")
            print(f"Found {results['found_dirs']} directories")
            print(f"Copied {results['copied_files']} files")
            print(f"Deleted {results['deleted_dirs']} directories")
            if args.add_links:
                print(f"Added links to {results['linked_docs']} documents")

            if args.dry_run:
                print("\nThis was a dry run. No files were actually modified.")
                print("Run without --dry-run to perform the actual consolidation.")
        else:
            print("\nWork effort consolidation failed. See log for details.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        logger.warning("Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        logger.error(f"An error occurred: {e}", exc_info=True)
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())