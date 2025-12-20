# Battery Saver for macOS

**Automatic Low Power Mode Manager** - A lightweight macOS menu bar application that automatically enables Low Power Mode when your battery reaches a customizable threshold.

![macOS](https://img.shields.io/badge/macOS-10.14%2B-blue)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🔋 **Dual Operating Modes**:
  - **Automatic Mode** - Automatically enables Low Power Mode at your threshold (requires one-time setup)
  - **Prompt Mode** - Asks you to enable Low Power Mode manually (works immediately, Mac App Store compatible)
- 🎚️ **Threshold Slider** - Easily adjust activation threshold from 5% to 95% via dropdown menu
- 💤 **Visual Indicators** - Clear menu bar icons show battery and Low Power Mode status
- ⚡ **Manual Controls** - Enable or disable Low Power Mode with one click
- 🔔 **Smart Notifications** - Get notified when Low Power Mode is activated
- 💾 **Persistent Settings** - Your preferences are saved and restored automatically
- 🚀 **Auto-Launch** - Optional automatic startup on login via LaunchAgent
- 🔓 **Passwordless Operation** - Optional setup for password-free Low Power Mode switching

## 📸 Screenshots

**Menu Bar Interface:**
```
┌──────────────────────────────────┐
│ Threshold: 20%               ▶   │ ← Slider submenu (5-95%)
├──────────────────────────────────┤
│ ✓ Enabled                        │ ← Enable Low Power Mode
│   Disabled                       │ ← Disable Low Power Mode
├──────────────────────────────────┤
│ Mode: Automatic                  │ ← Toggle between Auto/Prompt
├──────────────────────────────────┤
│ Current Battery                  │
│ Current Power Mode               │
├──────────────────────────────────┤
│ About                            │
├──────────────────────────────────┤
│ Quit                             │
└──────────────────────────────────┘
```

**Menu Bar Icons:**
- 💤 Low Power Mode is ON
- 🔌 Charging (AC Power)
- 🔋 On Battery (normal)
- 🪫 Low Battery (≤ 20%)
- ⚡ At Threshold

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/daniel/battery-saver.git
   cd battery-saver
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   ./start_battery_saver.sh
   ```

The app will appear in your menu bar!

### Auto-Launch on Login (Optional)

```bash
./install_launch_agent.sh
```

Battery Saver will now start automatically every time you log in.

### Operating Modes

Battery Saver has two modes:

**1. Prompt Mode (Default)**
- Works immediately, no setup required
- Opens System Settings when battery hits threshold
- You manually enable Low Power Mode
- **Mac App Store compatible**

**2. Automatic Mode (Recommended)**
- Enables Low Power Mode automatically
- Requires one-time passwordless setup:
  ```bash
  ./setup_passwordless_pmset.sh
  ```
- Creates a secure sudoers rule for `pmset lowpowermode` only

**Switch modes:** Click "Mode: ..." in the menu to toggle between Auto and Prompt modes.

## 📋 Requirements

- macOS 10.14 (Mojave) or later
- Python 3.7 or later
- `rumps` library (installed via requirements.txt)

## 🎮 Usage

### Setting Your Threshold

1. Click the Battery Saver icon in your menu bar
2. Hover over **"Threshold: XX%"**
3. Select your desired percentage (5-95%)
4. Done! Low Power Mode will now activate at that battery level

### Manual Control

- Click **"Enabled"** to immediately enable Low Power Mode
- Click **"Disabled"** to immediately disable Low Power Mode
- Checkmark shows which mode is currently active

### Checking Status

- **Current Battery** - View battery level and power source
- **Current Power Mode** - Check if Low Power Mode is active

## 🔧 Advanced Features

### Background Daemon Mode

Run Battery Saver completely invisibly with no menu bar icon:

```bash
./install_daemon.sh
```

Control via command line:
```bash
python3 battery_control.py status
python3 battery_control.py threshold 25
python3 battery_control.py enable
python3 battery_control.py disable
```

See [BACKGROUND_MODE.md](BACKGROUND_MODE.md) for full documentation.

### Minimal Version

For a version designed to sit next to the system battery icon:

```bash
python3 battery_saver_minimal.py
```

See [ICON_STYLES.md](ICON_STYLES.md) for details on different icon styles.

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 2 minutes
- **[PASSWORDLESS_SETUP.md](PASSWORDLESS_SETUP.md)** - Setup password-free operation
- **[BACKGROUND_MODE.md](BACKGROUND_MODE.md)** - Run without menu bar icon
- **[ICON_STYLES.md](ICON_STYLES.md)** - Different icon style options
- **[POSITIONING_GUIDE.md](POSITIONING_GUIDE.md)** - Position icon next to system battery
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

## 🔒 Security & Privacy

Battery Saver:
- ✅ Stores settings locally in `~/.battery_saver_config.json`
- ✅ Does not collect or transmit any data
- ✅ Does not access the internet
- ✅ Is fully open source
- ✅ Passwordless setup only affects `pmset lowpowermode` command

## 🛠️ How It Works

1. **Monitors** your battery level every 30 seconds
2. **Detects** when you're on battery power (not plugged in)
3. **Activates** Low Power Mode when battery ≤ your threshold
4. **Uses** macOS `pmset` command to control Low Power Mode
5. **Logs** everything for troubleshooting

## 🗂️ Project Structure

```
Battery_saver/
├── battery_saver.py              # Main menu bar application
├── battery_saver_daemon.py       # Background daemon (no UI)
├── battery_saver_minimal.py      # Minimal version
├── battery_control.py            # CLI control tool
├── start_battery_saver.sh        # Quick launch script
├── install_launch_agent.sh       # Auto-start installer
├── install_daemon.sh             # Background daemon installer
├── setup_passwordless_pmset.sh   # Passwordless setup
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── LICENSE                       # MIT License
```

## 🧪 Testing

Run the test suite:

```bash
python3 test_battery_functions.py
```

Expected output:
```
✅ Battery level detection working
✅ Power mode detection working
✅ Config file exists
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Daniel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- Built with [rumps](https://github.com/jaredks/rumps) - Ridiculously Uncomplicated macOS Python Statusbar apps
- Uses macOS `pmset` for power management

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/daniel/battery-saver/issues)
- **Discussions:** [GitHub Discussions](https://github.com/daniel/battery-saver/discussions)

## 🔄 Changelog

### [1.1.0] - 2025-10-24

**Added:**
- **Dual mode support**: Automatic Mode and Prompt Mode
- Automatic mode detection (checks if passwordless sudo is configured)
- User-switchable modes via menu
- Prompt Mode opens System Settings with helpful notifications
- Updated About dialog with mode information
- Mac App Store compatibility via Prompt Mode

**Changed:**
- Default mode is now Prompt Mode (no setup required)
- Enhanced user experience with mode indicators
- Version bumped to 1.1.0

### [1.0.0] - 2025-10-18

**Added:**
- Initial release
- Automatic Low Power Mode activation at customizable battery threshold
- Menu bar application with visual battery indicator
- Threshold slider submenu (5-95%)
- Manual Low Power Mode enable/disable controls
- Smart notifications
- Persistent configuration
- LaunchAgent support for auto-launch
- Background daemon mode (no UI)
- CLI control tool
- Passwordless sudo setup
- Comprehensive documentation

## 🚦 Status

**Version:** 1.1.0
**Status:** Stable
**Last Updated:** October 24, 2025
**Compatibility:** macOS 10.14+ (Mojave and later)

---

**Made with ❤️ for macOS users who want smarter battery management**


---

## License

Copyright (c) 2025 Daniel Bates / BatesAI

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Copyright Notice

While this code is open source under the MIT License, the BatesAI brand name and associated trademarks are proprietary. Please do not use the BatesAI name or logo without permission.

For commercial support or custom development, contact: daniel@batesai.org

## License & Commercial Use

- **Personal projects:** Free to download, study, and modify for your own hobby, research, or learning needs.
- **Attribution required:** Include “Built with BatesAI software by Daniel Bates (https://batesai.org)” anywhere you showcase or distribute this work.
- **Organizations & monetization:** Any company, client, school, nonprofit, or government project must either buy a commercial license (daniel@batesai.org) or share 10% of gross revenue from every sale that includes this software.
- **Compliance:** Missing attribution, skipping payments, or sublicensing under new terms immediately sunsets your access until the issue is fixed.

Read the full “BatesAI Personal & Revenue Share License v1.0” in LICENSE.

