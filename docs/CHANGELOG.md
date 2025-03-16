# Changelog

All notable changes to the Code Conductor project will be documented in this file.

## [Unreleased]

### Added
- Changed directory naming from ".AI-Setup" to "_AI-Setup" for better visibility in file systems
- Created migration script to help users transition from .AI-Setup to _AI-Setup
- Updated all code references and documentation to use the new naming convention
- Created retrieve_work_effort.py script for gathering comprehensive context about work efforts
- Implemented AI-focused workflow for work effort exploration and context gathering
- Updated AI instructions to prioritize using existing scripts for work effort management
- Enhanced workflow_runner.py with template integration from .AI-Setup/work_efforts/templates
- Added work effort status management (active, completed, archived) with automatic file movement
- Implemented directory structure integration for scripts and work efforts
- Added support for additional metadata fields (assignee, due date, last updated)
- Created test_status_change.py for validating status management functionality
- Added comprehensive documentation for the workflow runner in docs/workflow_runner.md
- Created workflow_runner.py script to automate the entire Code Conductor workflow process
- Added interactive and non-interactive modes for guided workflow execution
- Implemented automated documentation updating and verification as part of the workflow
- Added script generation templates with proper structure and testing framework integration
- Implemented Work Node system for creating knowledge graph connections between documents
- Added automatic document relationship discovery based on content similarity
- Created visualization capabilities for exploring document relationships
- Added command-line interface for work node management
- Reimagined Code Conductor as a lightweight system for creating powerful AI work circuits
- Enhanced documentation emphasizing scalable, hardware-agnostic knowledge management
- Implemented Obsidian-style wiki links between work efforts using double bracket syntax `[[link]]`
- Added `related_efforts` field in work effort frontmatter for structured document linking
- Created examples of different work effort naming conventions (timestamp-based, sequential, UUID, semantic)
- Added comprehensive documentation on work effort naming strategies
- Restructured project with proper `src` directory package layout
- Enhanced work effort listing to detect and display work efforts in subdirectories
- Added verbose mode with `-q/--quiet` flag to control output detail
- Improved directory search messaging for better transparency
- Added support for listing archived work efforts
- Created a more robust import system with fallbacks for better reliability
- Enhanced current working directory (PWD) detection and usage

### Changed
- Updated AI instructions to prioritize using scripts over manual work effort creation
- Added detailed documentation on context gathering for AI assistants
- Updated workflow_runner.py to use official template file instead of hardcoded template
- Modified script path generation to use .AI-Setup/work_efforts/scripts directory
- Improved the feature name handling in non-interactive mode
- Enhanced feedback with detailed file paths and status information
- Added cleanup of files in test scripts for better maintainability
- Adopted consistent singular naming for all file and directory references
- Refined project description to highlight text-based, contextual workflow capabilities
- Consolidated all work efforts into a single location at `.AI-Setup/work_efforts`
- Improved organization and structure of work effort directories
- Enhanced linking between related work efforts for better navigation
- Fixed package structure to eliminate need for manually setting PYTHONPATH
- Made CLI commands use the current directory by default for better usability
- Improved user messaging when no work effort folder is found
- Updated setup.py to correctly reference the new directory structure
- Modified command output to show exact paths for clarity
- Enhanced search logic to be more transparent about paths being checked

### Fixed
- Fixed import path issues that required manual PYTHONPATH setting
- Corrected work effort listing to properly show work efforts in subdirectories
- Resolved create_work_effort function reference issues
- Fixed directory structure handling for nested work effort folders
- Fixed entry point name to use `cc-work-e` consistently
- Updated documentation to reflect the correct command name
- Addressed an issue where work efforts were sometimes created in unexpected locations
- Modified `cc-work-e` command to use a smarter default behavior that creates work efforts in the current directory when run with defaults
- Fixed entry points to use the new command names (`code-conductor` and `cc-worke`)
- Updated package structure for better consistency with the new name

## [0.4.5] - 2025-03-09

### Added
- Implemented comprehensive testing framework with automated test discovery
- Added test categorization by type (simple, unit, integration, CLI, performance)
- Created modular test runner with timeout protection and detailed reporting
- Enhanced CLI with non-interactive mode for work effort creation using `-y` flag
- Added support for CI/CD integration with non-interactive work effort creation
- Created sample simple tests for basic functionality validation
- Added automated Markdown report generation for test results
- Implemented script for creating work efforts in non-interactive mode (`create_test_work_effort.sh`)
- Added comprehensive documentation of the testing framework

### Changed
- Refactored CLI code to support non-interactive execution
- Improved validation for command-line arguments
- Enhanced work_effort creation process to support CI/CD environments

## [0.4.4] - 2025-03-09

### Added
- Implemented multi-work-manager system for managing work efforts in different directories
- Added config.json to track and manage multiple work effort managers
- Created commands for adding, listing, and setting default work effort managers
- Enhanced CLI to support command-line arguments for creating work efforts

### Fixed
- Fixed issue with work efforts being created in incorrect directories
- Improved manager selection logic based on current directory context

## [0.4.2] - 2025-03-09

### Added
- Implemented new WorkEffortManager class to centralize work effort operations
- Added event loop system for monitoring work effort changes
- Created validation to ensure work efforts are only created in properly configured projects
- Added comprehensive JSON handling for configuration and work effort creation
- Implemented advanced filtering and sorting capabilities for work efforts
- Added convenient methods for retrieving active, recent, and overdue work efforts
- Enhanced CLI with improved display and filtering options
- Added ability to create work efforts from JSON input (both files and strings)
- Improved `cc-work-e` command to create work efforts in the current directory by default when no parameters are provided

### Fixed
- Fixed entry point name to use `cc-work-e` consistently
- Updated documentation to reflect the correct command name
- Addressed an issue where work efforts were sometimes created in unexpected locations
- Modified `cc-work-e` command to use a smarter default behavior that creates work efforts in the current directory when run with defaults

## [0.4.1] - 2025-03-09

### Added
- Added ability to create default work efforts in the current directory when running `cc-worke` without flags
- Improved usability with simpler command name `cc-worke`

### Fixed
- Fixed entry points to use the new command names (`code-conductor` and `cc-worke`)
- Updated package structure for better consistency with the new name

## [0.4.0] - 2025-03-09

### Added
- Initial public release as Code Conductor
- Renamed commands to `code-conductor` and `cc-work-e`
- Fully functional work effort management system
- Comprehensive CLI tools
- Project template creation and management
- Support for AI-generated work effort content
- Improved documentation and examples
- Enhanced testing to verify proper installation in various locations
- Updated setup_ai_in_current_dir function for more reliable initialization
- Added verification steps to create missing template files if needed
- Added `--version` and `-v` flags to display the current version of the package

### Changed
- Improved code cleanup by removing debug prints
- Enhanced error handling for more robust installation
- Updated installation and uninstallation functionality
- Better handling of edge cases in template creation
- Simplified version display in CLI

## [0.3.0] - 2025-03-08

### Added
- Added work_efforts folder inside the .AI-Setup directory
- Included work effort scripts in the .AI-Setup/work_efforts/scripts folder
- Added parameter to setup_work_efforts_structure function to support the new location
- Updated documentation to reflect the new structure

### Changed
- Updated version number to 0.3.0 for consistency across all files
- Improved AI-Setup folder structure with more comprehensive documentation
- Enhanced organization of work effort scripts and templates

## [0.2.1] - 2024-03-07

### Changed
- Updated version number for consistency
- Reinstalled and verified work efforts structure functionality
- Confirmed AI usage is properly disabled by default

## [0.2.0] - 2024-03-07

### Added
- Added explicit messaging that AI content generation is OFF by default in the new_work_effort.py script
- Updated the command-line help text to clearly indicate AI content generation default state

### Changed
- Improved user interface in the interactive mode of the new_work_effort.py script
- Cleaned up project structure by removing duplicate .AI-Setup folders in subdirectories

### Fixed
- Made default behavior for AI content generation more explicit to prevent unintended usage

## [0.1.0] - Initial Release

### Added
- Initial project structure for AI-assisted development
- Work efforts management system
- AI setup folder structure for better AI assistant context
- CLI for managing AI setup across projects