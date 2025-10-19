# Battery Saver - Quick Start Guide

**Get up and running in 2 minutes!**

## Installation

### Option 1: Quick Launch (No Installation)

```bash
cd /Users/daniel/Documents/aicode/Battery_saver
./start_battery_saver.sh
```

The app will appear in your menu bar as ⚡️ or 🔋

### Option 2: Auto-Launch on Login (Recommended)

```bash
cd /Users/daniel/Documents/aicode/Battery_saver
./install_launch_agent.sh
```

Battery Saver will now start automatically every time you log in!

## First-Time Setup

1. **Find the app** - Look for the battery icon in your menu bar (top-right)
2. **Click the icon** - Opens the menu
3. **Set threshold** - Click "Threshold: 20%" and enter your preferred percentage
4. **Done!** - The app will now monitor your battery automatically

## How It Works

- **Monitors** your battery level every 30 seconds
- **Activates** Low Power Mode when battery ≤ your threshold
- **Only works** when on battery power (not plugged in)
- **Requires** admin password when changing power mode (macOS security)

## Common Tasks

### Change Battery Threshold
Menu bar → Click "Threshold: XX%" → Enter new percentage → Click "Set"

### Disable Monitoring Temporarily
Menu bar → Click "Enabled" → Changes to "Disabled"

### Manually Enable Low Power Mode
Menu bar → Click "Enable Low Power Mode Now"

### Check Battery Status
Menu bar → Click "Current Battery"

### Uninstall Auto-Launch
```bash
./uninstall_launch_agent.sh
```

## Troubleshooting

**App doesn't appear in menu bar?**
- Make sure Python 3 is installed: `python3 --version`
- Install rumps: `pip3 install rumps`
- Run manually: `python3 battery_saver.py`

**Low Power Mode doesn't activate?**
- Check that you're on **battery power** (not plugged in)
- Verify battery is **at or below** threshold
- Make sure monitoring is **Enabled** (not Disabled)

**Password prompt appears?**
- This is normal! macOS requires admin access to change power settings
- Enter your password and click "OK"
- You may need to do this once per session

## What's Next?

- Customize your threshold based on your usage
- Enable auto-launch so you never forget
- Check the full [README.md](README.md) for advanced features

---

**Questions?** Read the full [README.md](README.md) or check [CHANGELOG.md](CHANGELOG.md) for version history.
