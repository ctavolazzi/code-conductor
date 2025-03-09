# Changelog

All notable changes to the Code Conductor project will be documented in this file.

## [0.4.1] - 2025-03-09

### Fixed
- Fixed entry points to use the new command names (`code-conductor` and `code-work-effort`)
- Updated package structure for better consistency with the new name

## [0.4.0] - 2025-03-09

### Added
- Initial public release as Code Conductor
- Renamed commands to `code-conductor` and `code-work-effort`
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