# Changelog

All notable changes to this project will be documented in this file.

## [1.4.0] - 2025-06-21

### Enhanced Multi-Interface Bandwidth Monitoring
- **Improved Network Interface Detection**: Enhanced filtering logic to skip virtual/container interfaces (lo, docker*, br-*, veth*, virbr*, tun*, tap*)
- **Multi-Interface Support**: Monitor ALL physical network interfaces simultaneously for accurate bandwidth calculation
- **Enhanced Display**: Show active/total interface count with visual status indicators (🟢 active, ⚫ inactive)
- **Smart Interface Sorting**: Sort interfaces by traffic volume (highest traffic first)
- **Better Error Handling**: Improved handling of malformed network data
- **Interface Classification**: Automatic detection of interface types (Ethernet, WiFi, etc.)
- **Advanced Traffic Warnings**: Smart alerts for high bandwidth usage on total and per-interface basis

### New Tools & Scripts
- **test_multi_interface.py**: Comprehensive interface detection and testing script
- **demo_multi_interface.py**: Demo script showcasing multi-interface monitoring improvements

### Technical Improvements
- Enhanced `get_network_stats()` function with robust error handling
- Improved `get_bandwidth_usage()` to track all interfaces and provide detailed statistics
- Better monitoring display format with interface counts and status
- Optimized data structures for multi-interface monitoring

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
