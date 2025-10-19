# Changelog

All notable changes to Battery Saver will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-18

### Added
- Initial release of Battery Saver
- Automatic Low Power Mode activation at customizable battery threshold
- Menu bar application with visual battery indicator
- Real-time battery monitoring (30-second intervals)
- Customizable battery percentage threshold (5-95%)
- Manual Low Power Mode override controls
- Smart notifications when Low Power Mode is activated
- Persistent configuration storage in JSON format
- LaunchAgent support for auto-launch on login
- Installation and uninstallation scripts
- Current battery and power mode status display
- Enable/disable toggle for monitoring
- Only activates on battery power (not when plugged in)
- Admin privilege handling via AppleScript
- Error handling and user-friendly dialogs
- Comprehensive README documentation
- MIT License

### Features
- Menu bar icon changes based on battery level:
  - 🔋 (80-100%)
  - 🔋 (50-79%)
  - 🪫 (20-49%)
  - ⚠️ (below 20%)
- Configuration persists across restarts
- Compatible with macOS built-in power management
- Lightweight and minimal resource usage

### Technical Details
- Built with Python 3.7+ and rumps 0.3.0
- Uses macOS pmset for power mode control
- AppleScript integration for admin privileges
- JSON-based configuration storage
- LaunchAgent for background execution

---

## Future Releases

### Planned for [1.1.0]
- Multiple threshold profiles
- Time-based automation rules
- Battery health monitoring
- Charging optimization features
- Enhanced notification options

### Planned for [2.0.0]
- iOS companion app
- Cross-platform support (Windows, Ubuntu)
- Battery usage statistics
- Power consumption analytics
- Scheduled power mode switching
