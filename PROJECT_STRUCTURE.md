# Battery Saver - Project Structure

## Overview

Battery Saver is a macOS menu bar application that automatically enables Low Power Mode when battery reaches a user-defined threshold.

**Version:** 1.0.0  
**License:** MIT  
**Platform:** macOS 10.14+  
**Language:** Python 3.7+

## File Structure

```
Battery_saver/
├── battery_saver.py              # Main application (rumps menu bar app)
├── start_battery_saver.sh        # Startup script with dependency checks
├── install_launch_agent.sh       # Install auto-launch on login
├── uninstall_launch_agent.sh     # Remove auto-launch
├── com.daniel.batterysaver.plist # LaunchAgent configuration file
├── test_battery_functions.py     # Test script for battery monitoring
├── requirements.txt              # Python dependencies (rumps)
├── README.md                     # Complete documentation
├── QUICK_START.md               # Quick setup guide
├── CHANGELOG.md                 # Version history
├── PROJECT_STRUCTURE.md         # This file
├── LICENSE                      # MIT License
└── .gitignore                   # Git ignore rules
```

## Core Components

### 1. Main Application (`battery_saver.py`)

**Purpose:** Menu bar app with automatic battery monitoring

**Key Features:**
- `BatterySaver` class (extends `rumps.App`)
- Battery level monitoring (every 30 seconds)
- Power mode detection and control
- Configuration persistence (JSON)
- User interface (menu bar + dialogs)

**Main Methods:**
- `get_battery_level()` - Returns current battery percentage
- `is_on_battery()` - Checks if running on battery power
- `get_power_mode()` - Gets current macOS power mode (0/1/2)
- `set_power_mode(mode)` - Sets power mode using pmset + AppleScript
- `check_battery(timer)` - Timer callback for monitoring
- Menu callbacks for UI interactions

**Configuration File:** `~/.battery_saver_config.json`
```json
{
  "threshold": 20,
  "enabled": true,
  "notifications": true
}
```

### 2. Startup Scripts

**`start_battery_saver.sh`**
- Checks Python 3 installation
- Installs rumps if missing
- Kills existing instances
- Launches the app

**`install_launch_agent.sh`**
- Creates LaunchAgent in `~/Library/LaunchAgents/`
- Configures auto-start on login
- Loads the agent with launchctl

**`uninstall_launch_agent.sh`**
- Unloads LaunchAgent
- Removes plist file
- Stops running instances

### 3. LaunchAgent Configuration

**`com.daniel.batterysaver.plist`**
- Defines launch parameters
- Sets environment variables
- Configures auto-restart
- Specifies log locations

**Log Files:**
- `/tmp/battery_saver.log` - Standard output
- `/tmp/battery_saver_error.log` - Error output

### 4. Testing

**`test_battery_functions.py`**
- Tests battery level detection
- Tests power source detection
- Tests power mode retrieval
- Simulates threshold checks

## Dependencies

### Python Packages
- **rumps 0.3.0** - Menu bar app framework
  - Requires: pyobjc-framework-Cocoa
  - Requires: pyobjc-core

### macOS Tools
- **pmset** - Power Management Settings (built-in)
- **launchctl** - Launch daemon controller (built-in)
- **osascript** - AppleScript executor (built-in)

## Installation Methods

### Method 1: Manual Run
```bash
./start_battery_saver.sh
```
- Runs in current session
- Stops when you log out
- Good for testing

### Method 2: LaunchAgent (Recommended)
```bash
./install_launch_agent.sh
```
- Auto-starts on login
- Runs in background
- Survives logout/login
- Production use

## Architecture

### Power Mode Control Flow

```
User sets threshold (e.g., 20%)
         ↓
Timer checks battery every 30s
         ↓
Get battery level via pmset
         ↓
Check if on battery power
         ↓
If battery ≤ threshold AND on battery
         ↓
Get current power mode
         ↓
If not already in Low Power Mode
         ↓
Request admin privileges (AppleScript)
         ↓
Execute: pmset -b powermode 1
         ↓
Show notification
```

### macOS Power Modes

- **Mode 0** - Automatic (default)
- **Mode 1** - Low Power Mode (battery saving)
- **Mode 2** - High Power Mode (max performance)

Battery Saver sets to Mode 1 when threshold reached.

## Security & Permissions

### Required Permissions
1. **Admin privileges** - To run `pmset` command
2. **Notification access** - To show alerts (optional)

### Privacy Considerations
- ✅ All data stored locally
- ✅ No network access
- ✅ No data collection
- ✅ Open source code
- ✅ Configuration in plain JSON

### Admin Password Prompt
macOS will request your password when:
- First time enabling Low Power Mode
- After system restart
- After extended idle period

This is normal macOS security behavior.

## Integration with macOS

### Compatible With
- System Preferences → Battery → Low Power Mode
- Other battery management tools
- Time Machine and system backups
- macOS built-in power management

### Does Not Conflict With
- AlDente (charge limiting)
- Other menu bar apps
- macOS System Settings
- Third-party battery monitors

## Development

### Running in Development Mode
```bash
python3 battery_saver.py
```

### Debugging
```bash
# View LaunchAgent logs
tail -f /tmp/battery_saver.log
tail -f /tmp/battery_saver_error.log

# Check if agent is loaded
launchctl list | grep batterysaver

# Test battery functions
python3 test_battery_functions.py
```

### Modifying Check Interval
Edit `battery_saver.py` line 51:
```python
self.timer = rumps.Timer(self.check_battery, 30)  # Change 30 to desired seconds
```

## Future Enhancements

### Planned Features
- Multiple threshold profiles
- Time-based rules
- Battery health monitoring
- Charging optimization
- iOS companion app
- Cross-platform support

### Contribution Areas
- Testing on different macOS versions
- Performance optimization
- UI/UX improvements
- Documentation enhancements
- Localization/internationalization

## Troubleshooting

### Common Issues

**Issue:** Menu bar icon doesn't appear
- **Cause:** Python or rumps not installed
- **Fix:** Install Python 3 and run `pip3 install rumps`

**Issue:** Low Power Mode doesn't activate
- **Cause:** Not on battery power
- **Fix:** Unplug power adapter to test

**Issue:** Password prompt every time
- **Cause:** macOS security policy
- **Fix:** Normal behavior, required for pmset

**Issue:** LaunchAgent doesn't start
- **Cause:** Incorrect plist permissions
- **Fix:** Reinstall with `./install_launch_agent.sh`

## Performance

### Resource Usage
- **Memory:** ~30-50 MB
- **CPU:** Minimal (<1% average)
- **Battery Impact:** Negligible
- **Check Frequency:** Every 30 seconds

### Optimization
- Efficient battery polling
- No continuous loops
- Timer-based checks only
- Minimal UI overhead

## License

MIT License - See [LICENSE](LICENSE) file

## Credits

- **Author:** Daniel
- **Framework:** [rumps](https://github.com/jaredks/rumps) by Jared Suttles
- **Inspired by:** macOS power management needs

---

**Last Updated:** October 18, 2025  
**Documentation Version:** 1.0.0
