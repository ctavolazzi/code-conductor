#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Work Node Creator

This script creates "work node" documents that serve as connection points between
multiple related work efforts, forming a knowledge graph within your markdown files.

Workflow Description:
---------------------
This script implements the following workflow:

1. Knowledge Discovery Phase:
   - Scanning existing work efforts to identify potential relationships
   - Analyzing document content to detect thematic connections
   - Creating connection suggestions based on content similarity

2. Node Creation Phase:
   - Generating specialized "work node" documents to serve as connection points
   - Adding metadata about connected documents and their relationships
   - Establishing a structured knowledge graph in your documentation

3. Link Integration Phase:
   - Creating bidirectional links between work nodes and connected documents
   - Updating frontmatter of all related documents to reflect connections
   - Preserving existing links while adding new relationship information

4. Visualization Phase (Optional):
   - Generating metadata for knowledge graph visualization
   - Creating connection maps to illustrate document relationships
   - Preparing data for visual exploration of your work network

Usage:
    python create_work_node.py --title "Node Title" --documents doc1.md doc2.md [--category Category]
    python create_work_node.py --auto-discover [--min-similarity 0.6] [--max-nodes 5]
    python create_work_node.py --visualize [--output graph.json]

Options:
    --title TITLE         Title for the work node (required unless using --auto-discover)
    --documents DOCS      List of documents to connect (required unless using --auto-discover)
    --category CAT        Category for the work node (default: "connection")
    --description DESC    Description of the relationship between documents
    --auto-discover       Automatically discover related documents and create nodes
    --min-similarity VAL  Minimum similarity score for auto-discovery (default: 0.5)
    --max-nodes NUM       Maximum number of nodes to create in auto-discover mode (default: 10)
    --visualize           Generate a visualization of the knowledge graph
    --output FILE         Output file for visualization data (default: "knowledge_graph.json")
    --work-dir DIR        Work efforts directory (default: _AI-Setup/work_effort)
    --dry-run             Don't actually create or modify files, just show what would be done
    --verbose             Enable verbose logging
"""

import os
import sys
import re
import argparse
import logging
import datetime
import json
import yaml
import fnmatch
from pathlib import Path
import shutil
from collections import defaultdict
import difflib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('work_nodes.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
ROOT_DIR = os.getcwd()
WORK_DIR = os.path.join(ROOT_DIR, '_AI-Setup', 'work_effort')
NODE_DIR = os.path.join(WORK_DIR, 'node')
MARKDOWN_EXTENSIONS = ['.md', '.markdown']
YAML_FRONTMATTER_PATTERN = re.compile(r'^---\s*$(.*?)^---\s*$', re.MULTILINE | re.DOTALL)
WIKI_LINK_PATTERN = re.compile(r'\[\[(.*?)\]\]')
NODE_TEMPLATE = """---
title: "{title}"
created: "{date}"
category: "{category}"
connected_document:
{connected_docs}
description: "{description}"
---

# {title}

## Connected Document

{doc_list}

## Description

{description}

## Connection Map

{connections_map}
"""

class WorkNode:
    """
    Represents a connection point between multiple work effort documents.

    A WorkNode is a specialized document that serves as a hub connecting multiple
    related work efforts. It contains metadata about the connections and provides
    bidirectional links between all connected documents.
    """

    def __init__(self, title, category="connection", description="", documents=None):
        """
        Initialize a work node with the given title, category, and connected documents.

        Args:
            title (str): Title of the work node
            category (str): Category of the node (e.g., "connection", "theme", "project")
            description (str): Description of the relationship between documents
            documents (list): List of documents to connect via this node
        """
        self.title = title
        self.category = category
        self.description = description
        self.documents = documents or []
        self.created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.filename = self._generate_filename()

    def _generate_filename(self):
        """Generate a filename for the work node based on its title."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        title_slug = self.title.lower().replace(" ", "_")
        return f"{timestamp}_node_{title_slug}.md"

    def to_markdown(self):
        """Convert the work node to markdown format."""
        connected_docs = "\n".join([f"  - \"[[{doc}]]\"" for doc in self.documents])
        doc_list = "\n".join([f"- [[{doc}]]" for doc in self.documents])

        # Create a simple ASCII connections map
        connections_map = "```\n"
        connections_map += f"    {self.title}\n"
        connections_map += "       |\n"
        for i, doc in enumerate(self.documents):
            prefix = "       ├──" if i < len(self.documents) - 1 else "       └──"
            connections_map += f"{prefix} {doc}\n"
        connections_map += "```"

        return NODE_TEMPLATE.format(
            title=self.title,
            date=self.created,
            category=self.category,
            connected_docs=connected_docs,
            description=self.description,
            doc_list=doc_list,
            connections_map=connections_map
        )

    def to_dict(self):
        """Convert the work node to a dictionary for visualization."""
        return {
            "id": self.filename,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "created": self.created,
            "connected_document": self.documents
        }


class WorkNodeManager:
    """
    Manages the creation and linking of work nodes across work effort documents.

    This class provides methods for creating work nodes, discovering related documents,
    updating connected documents with links, and generating visualization data.
    """

    def __init__(self, work_dir=WORK_DIR, dry_run=False, verbose=False):
        """
        Initialize the work node manager.

        Args:
            work_dir (str): Directory containing work effort documents
            dry_run (bool): If True, don't actually create or modify files
            verbose (bool): If True, enable verbose logging
        """
        self.work_dir = os.path.abspath(work_dir)
        self.node_dir = os.path.join(self.work_dir, 'node')
        self.dry_run = dry_run
        self.verbose = verbose

        if verbose:
            logger.setLevel(logging.DEBUG)

        logger.info(f"Initializing Work Node Manager")
        logger.info(f"Work directory: {self.work_dir}")
        logger.info(f"Node directory: {self.node_dir}")
        logger.info(f"Dry run: {self.dry_run}")

    def ensure_node_dir_exists(self):
        """Ensure the node directory exists."""
        if not os.path.exists(self.node_dir):
            if not self.dry_run:
                os.makedirs(self.node_dir, exist_ok=True)
                logger.info(f"Created node directory: {self.node_dir}")
            else:
                logger.info(f"Would create node directory: {self.node_dir}")

    def find_all_documents(self):
        """Find all markdown documents in the work directory."""
        documents = []

        for root, _, files in os.walk(self.work_dir):
            for file in files:
                if any(file.endswith(ext) for ext in MARKDOWN_EXTENSIONS):
                    if os.path.basename(root) != 'node':  # Exclude node documents themselves
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, self.work_dir)
                        documents.append(rel_path)

        logger.info(f"Found {len(documents)} documents in {self.work_dir}")
        return documents

    def read_document(self, doc_path):
        """Read the content of a document."""
        full_path = os.path.join(self.work_dir, doc_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {full_path}: {e}")
            return ""

    def extract_document_info(self, doc_path):
        """Extract title and content from a document."""
        content = self.read_document(doc_path)
        title = os.path.splitext(os.path.basename(doc_path))[0]

        # Try to extract title from frontmatter
        match = YAML_FRONTMATTER_PATTERN.search(content)
        if match:
            frontmatter_text = match.group(1)
            title_match = re.search(r'title:\s*"?(.*?)"?$', frontmatter_text, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()

        return {
            "path": doc_path,
            "title": title,
            "content": content
        }

    def discover_related_documents(self, min_similarity=0.5):
        """Discover related documents based on content similarity."""
        documents = self.find_all_documents()
        document_info = [self.extract_document_info(doc) for doc in documents]

        # Build a matrix of similarity scores
        relationships = defaultdict(list)

        for i, doc1 in enumerate(document_info):
            for j, doc2 in enumerate(document_info):
                if i >= j:  # Only calculate upper triangle to avoid duplicates
                    continue

                # Calculate similarity score using SequenceMatcher
                similarity = difflib.SequenceMatcher(
                    None, doc1["content"], doc2["content"]
                ).ratio()

                if similarity >= min_similarity:
                    logger.debug(f"Similarity between {doc1['path']} and {doc2['path']}: {similarity:.2f}")
                    relationships[doc1["path"]].append((doc2["path"], similarity))
                    relationships[doc2["path"]].append((doc1["path"], similarity))

        # Group related documents
        clusters = []
        processed = set()

        for doc_path, relations in relationships.items():
            if doc_path in processed:
                continue

            cluster = {doc_path}
            for related_path, _ in relations:
                cluster.add(related_path)
                processed.add(related_path)

            if len(cluster) > 1:  # Only consider clusters with at least 2 documents
                clusters.append(list(cluster))
                processed.add(doc_path)

        logger.info(f"Discovered {len(clusters)} potential document clusters")
        return clusters

    def create_work_node(self, title, category, description, documents):
        """Create a work node document."""
        node = WorkNode(
            title=title,
            category=category,
            description=description,
            documents=documents
        )

        # Ensure node directory exists
        self.ensure_node_dir_exists()

        # Write the node document
        node_path = os.path.join(self.node_dir, node.filename)
        if not self.dry_run:
            with open(node_path, 'w', encoding='utf-8') as f:
                f.write(node.to_markdown())
            logger.info(f"Created work node: {node_path}")
        else:
            logger.info(f"Would create work node: {node_path}")

        # Update connected documents
        for doc in documents:
            self.add_node_link_to_document(doc, node)

        return node

    def add_node_link_to_document(self, doc_path, node):
        """Add a link to the work node in the specified document."""
        full_path = os.path.join(self.work_dir, doc_path)
        content = self.read_document(doc_path)

        # Process frontmatter
        match = YAML_FRONTMATTER_PATTERN.search(content)
        if match:
            frontmatter_text = match.group(1)
            updated_frontmatter = frontmatter_text

            # Check if connected_node field exists
            if 'connected_node:' in frontmatter_text:
                # Update existing field
                if f"[[{node.filename}]]" not in frontmatter_text:
                    # Find the end of the connected_node list
                    nodes_pattern = re.compile(r'connected_node:\s*\n((?:  - .*\n)*)', re.MULTILINE)
                    nodes_match = nodes_pattern.search(frontmatter_text)
                    if nodes_match:
                        nodes_list = nodes_match.group(1)
                        updated_frontmatter = frontmatter_text.replace(
                            nodes_list,
                            nodes_list + f"  - [[{node.filename}]]\n"
                        )
            else:
                # Add new connected_node field
                updated_frontmatter = frontmatter_text.rstrip() + "\nconnected_node:\n  - [[" + node.filename + "]]\n"

            # Replace frontmatter
            updated_content = content.replace(match.group(0), f"---\n{updated_frontmatter}---\n")

            # Write updated content
            if not self.dry_run:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                logger.info(f"Updated document with node link: {full_path}")
            else:
                logger.info(f"Would update document with node link: {full_path}")
        else:
            # No frontmatter, create a new one
            frontmatter = f"---\ntitle: \"{os.path.splitext(os.path.basename(doc_path))[0]}\"\nconnected_node:\n  - [[{node.filename}]]\n---\n\n"
            updated_content = frontmatter + content

            # Write updated content
            if not self.dry_run:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                logger.info(f"Added frontmatter with node link: {full_path}")
            else:
                logger.info(f"Would add frontmatter with node link: {full_path}")

    def create_auto_nodes(self, min_similarity=0.5, max_nodes=10):
        """Automatically discover related documents and create work nodes."""
        clusters = self.discover_related_documents(min_similarity)

        # Limit to max_nodes
        clusters = clusters[:max_nodes]

        created_nodes = []
        for i, cluster in enumerate(clusters):
            # Generate a title based on common words or simply "Document Cluster {i+1}"
            title = f"Document Cluster {i+1}"

            # Generate a description based on the documents in the cluster
            description = f"Automatically generated connection between {len(cluster)} related documents."

            # Create the work node
            node = self.create_work_node(
                title=title,
                category="auto-discovered",
                description=description,
                documents=cluster
            )
            created_nodes.append(node)

        logger.info(f"Created {len(created_nodes)} work nodes")
        return created_nodes

    def generate_visualization(self, output_file="knowledge_graph.json"):
        """Generate a visualization of the knowledge graph."""
        # Collect all documents and nodes
        documents = self.find_all_documents()
        nodes = [os.path.join("node", f) for f in os.listdir(self.node_dir)
                if any(f.endswith(ext) for ext in MARKDOWN_EXTENSIONS)]

        # Extract information for each document and node
        nodes_info = []
        for node_file in nodes:
            content = self.read_document(node_file)
            match = YAML_FRONTMATTER_PATTERN.search(content)
            if match:
                try:
                    frontmatter = yaml.safe_load(match.group(1))
                    node_info = {
                        "id": node_file,
                        "title": frontmatter.get("title", os.path.basename(node_file)),
                        "type": "node",
                        "category": frontmatter.get("category", "connection"),
                        "connected_document": frontmatter.get("connected_document", [])
                    }
                    nodes_info.append(node_info)
                except yaml.YAMLError:
                    logger.error(f"Error parsing frontmatter in {node_file}")

        # Extract information for each document
        docs_info = []
        for doc_file in documents:
            content = self.read_document(doc_file)
            match = YAML_FRONTMATTER_PATTERN.search(content)
            if match:
                try:
                    frontmatter = yaml.safe_load(match.group(1))
                    doc_info = {
                        "id": doc_file,
                        "title": frontmatter.get("title", os.path.basename(doc_file)),
                        "type": "document",
                        "connected_node": frontmatter.get("connected_node", [])
                    }
                    docs_info.append(doc_info)
                except yaml.YAMLError:
                    logger.error(f"Error parsing frontmatter in {doc_file}")

        # Build edges between nodes and documents
        edges = []
        for node in nodes_info:
            for doc_ref in node["connected_document"]:
                # Extract document filename from wiki link
                doc_match = WIKI_LINK_PATTERN.search(doc_ref)
                if doc_match:
                    doc_file = doc_match.group(1)
                    edges.append({
                        "source": node["id"],
                        "target": doc_file,
                        "type": "node_to_document"
                    })

        # Create the final graph data
        graph_data = {
            "nodes": nodes_info + docs_info,
            "edges": edges
        }

        # Write to output file
        if not self.dry_run:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2)
            logger.info(f"Generated visualization data: {output_file}")
        else:
            logger.info(f"Would generate visualization data: {output_file}")

        return graph_data


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Create work nodes to connect related documents.')
    parser.add_argument('--title', dest='title',
                        help='Title for the work node')
    parser.add_argument('--documents', dest='documents', nargs='+',
                        help='List of documents to connect')
    parser.add_argument('--category', dest='category', default='connection',
                        help='Category for the work node')
    parser.add_argument('--description', dest='description', default='',
                        help='Description of the relationship between documents')
    parser.add_argument('--auto-discover', dest='auto_discover', action='store_true',
                        help='Automatically discover related documents and create nodes')
    parser.add_argument('--min-similarity', dest='min_similarity', type=float, default=0.5,
                        help='Minimum similarity score for auto-discovery')
    parser.add_argument('--max-nodes', dest='max_nodes', type=int, default=10,
                        help='Maximum number of nodes to create in auto-discover mode')
    parser.add_argument('--visualize', dest='visualize', action='store_true',
                        help='Generate a visualization of the knowledge graph')
    parser.add_argument('--output', dest='output', default='knowledge_graph.json',
                        help='Output file for visualization data')
    parser.add_argument('--work-dir', dest='work_dir', default=WORK_DIR,
                        help=f'Work efforts directory')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        help="Don't actually create or modify files, just show what would be done")
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help="Enable verbose logging")
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_args()

    # Validate arguments
    if not args.auto_discover and not args.visualize:
        if not args.title:
            print("Error: --title is required unless using --auto-discover or --visualize")
            return 1
        if not args.documents:
            print("Error: --documents is required unless using --auto-discover or --visualize")
            return 1

    # Initialize the work node manager
    manager = WorkNodeManager(
        work_dir=args.work_dir,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    try:
        if args.auto_discover:
            # Automatically discover related documents and create nodes
            created_nodes = manager.create_auto_nodes(
                min_similarity=args.min_similarity,
                max_nodes=args.max_nodes
            )
            print(f"\nCreated {len(created_nodes)} work nodes:")
            for node in created_nodes:
                print(f"- {node.title}: {len(node.documents)} connected documents")

        elif args.visualize:
            # Generate a visualization of the knowledge graph
            graph_data = manager.generate_visualization(output_file=args.output)
            print(f"\nGenerated visualization data:")
            print(f"- Nodes: {len(graph_data['nodes'])}")
            print(f"- Edges: {len(graph_data['edges'])}")
            print(f"- Output file: {args.output}")

        else:
            # Create a single work node
            node = manager.create_work_node(
                title=args.title,
                category=args.category,
                description=args.description,
                documents=args.documents
            )
            print(f"\nCreated work node:")
            print(f"- Title: {node.title}")
            print(f"- Category: {node.category}")
            print(f"- Connected documents: {len(node.documents)}")
            print(f"- File: {os.path.join(manager.node_dir, node.filename)}")

        if args.dry_run:
            print("\nThis was a dry run. No files were actually modified.")

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