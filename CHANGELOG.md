# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-06-21

### Added
- Initial release of VPS Backup Tool
- Parallel backup with rsync support
- Real-time bandwidth monitoring during backup
- Interactive shell script with menu options
- Quick bandwidth check utility
- Standalone bandwidth monitoring tool
- Configurable monitoring intervals
- Automatic retry mechanism for failed chunks
- Comprehensive logging system
- Security-focused configuration management
- Auto setup script for easy installation
- Multiple configuration templates
- Support for custom rsync options
- Background monitoring with threading
- Bandwidth usage warnings and alerts

### Features
- **main.py**: Core backup script with integrated monitoring
- **monitor_bandwidth.py**: Standalone bandwidth monitoring tool
- **quick_bandwidth.py**: Quick bandwidth check utility
- **backup_with_monitoring.sh**: Interactive script with user menu
- **setup.sh**: Automated setup and configuration
- **config templates**: Secure configuration management
- **Multi-threading**: Parallel chunk processing
- **Real-time monitoring**: Live bandwidth usage display
- **Error handling**: Automatic retry for failed operations
- **Cross-platform**: Works on macOS, Linux, and other Unix systems

### Security
- SSH key protection in .gitignore
- Configuration template system
- Sensitive data exclusion from repository
- Secure SSH connection handling
