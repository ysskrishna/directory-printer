# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.0.0] - 2025-02-16
### Added
- Internationalization Support
  - Added multi-language support using python-i18n package
  - Implemented translations for English, Spanish, and Chinese languages
  - Added language selection feature in the `File` menu
  - Stored language preference in application settings

- Enhanced File Menu Features
  - Added `Open Recent` section to track and access last 5 recently opened files
  - Added `Clear Open Recent` option to reset the recent files list
  - Improved file handling with persistent storage of file history

- New Configuration Management System
  - Implemented robust configuration storage for application settings
  - Added persistent storage for language preferences, recent files, and user settings
  - Created a centralized configuration interface for better maintainability

- Expanded Help Menu
  - Added `Check for Updates` feature to verify and notify about new versions
  - Implemented `FAQ` section with comprehensive user guidance
  - Added `About` section with detailed application information

### Changed
- Architectural Improvements
  - Refactored `get_resource_path` into core module for better code organization
  - Enhanced resource management for better cross-module accessibility

### Documentation
- Added detailed instructions in DEVELOPMENT.md for adding new packages using poetry


## [0.5.0] - 2025-02-15
### Added
- Introduced a new `IgnorePattern` class that supports more complex ignore patterns

### Fixed
- Resolved issues with handling negation patterns and directory-only patterns in the `.gitignore` file parsing logic


## [0.4.0] - 2025-02-15
### Added
- Added a window close handler to confirm if the user wants to quit the application
- Added stop button feature to stop the directory scanning process

### Changed
- Updated github actions to include version number in the release files
- Cleaned up README file and seperated the Development Guide into a separate file


## [0.3.0] - 2025-02-11
### Added
- Added progress bar and status indicator for directory scanning
- Added support for .gitignore file integration
- Added "Reset All" button to clear all inputs and results
- Added clear buttons for directory and gitignore file inputs

### Changed
- Enhanced UI layout with better spacing and organization
- Updated directory scanning to respect gitignore patterns
- Improved progress tracking with detailed status updates


## [0.2.0] - 2025-02-11
### Added
- Added CHANGELOG.md file
- Added "Copy to Clipboard" feature 
- Added "Download as text file" feature for saving folder trees locally

### Changed
- Updated README file with Product Hunt link and header image

## [0.1.0] - 2025-01-19
### Added
- Initial release with core features:
  - Interactive GUI for directory selection
  - Tree-like visualization of directory structures
  - Cross-platform compatibility (Windows, Linux, macOS)
  - Permission error handling
  - Directory structure export functionality


[1.0.0]: https://github.com/ysskrishna/directory-printer/compare/v0.5.0...v1.0.0
[0.5.0]: https://github.com/ysskrishna/directory-printer/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/ysskrishna/directory-printer/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ysskrishna/directory-printer/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ysskrishna/directory-printer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ysskrishna/directory-printer/releases/tag/v0.1.0 