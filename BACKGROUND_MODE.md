# Battery Saver - Background Mode Guide

## Running Completely in the Background

Battery Saver now has a **background daemon mode** that runs without any visible UI - no menu bar icon, no dock icon, just silent battery monitoring in the background.

---

## Two Modes Available

### Mode 1: Menu Bar App (Original)
- ✅ Visual menu bar icon
- ✅ Click to see status and controls
- ✅ Slider for threshold adjustment
- ✅ Visual feedback
- ❌ Takes up space in menu bar

**Best for:** Users who want visual feedback and quick access

### Mode 2: Background Daemon (New!)
- ✅ Completely invisible
- ✅ No menu bar icon
- ✅ No dock icon
- ✅ Runs silently in background
- ✅ Control via command line
- ✅ Logs to file

**Best for:** Users who want "set and forget" operation

---

## Installing Background Daemon

### Step 1: Stop Menu Bar Version (if running)

```bash
cd /Users/daniel/Documents/aicode/Battery_saver
pkill -f battery_saver.py
```

### Step 2: Install Daemon

```bash
./install_daemon.sh
```

**What it does:**
1. Stops any running Battery Saver instances
2. Removes old menu bar LaunchAgent (if installed)
3. Installs new background daemon LaunchAgent
4. Starts daemon automatically
5. Configures auto-start on login

**Expected output:**
```
Battery Saver - Background Daemon Installation
==============================================

This will install Battery Saver as a background daemon that:
  • Runs automatically on login
  • Has NO menu bar icon
  • Has NO dock icon
  • Runs completely in the background
  • Monitors battery and enables Low Power Mode automatically

Continue with installation? (y/n): y

Stopping any running Battery Saver instances...
Installing LaunchAgent...
Loading Battery Saver daemon...

✅ Battery Saver daemon installed successfully!

The daemon is now running in the background with:
  • No menu bar icon
  • No dock icon
  • Automatic startup on login
```

### Step 3: Verify Installation

```bash
python3 battery_control.py status
```

**Expected output:**
```
==================================================
Battery Saver - Status
==================================================
Monitoring: ✅ Enabled
Threshold: 20%
Notifications: ✅ On
Check Interval: 30s

Daemon: 🟢 Running (PID: 12345)

Recent logs:
--------------------------------------------------
[2025-10-18 18:30:00] Battery Saver Daemon starting...
[2025-10-18 18:30:00] Threshold: 20%, Enabled: True
[2025-10-18 18:30:05] Battery: 85%, On battery: False
==================================================
```

---

## Controlling the Background Daemon

Since there's no UI, you control the daemon using the command-line tool:

### Check Status

```bash
python3 battery_control.py status
```

Shows:
- Current settings
- Daemon running status
- Recent log entries

### Change Threshold

```bash
python3 battery_control.py threshold 25
```

Sets Low Power Mode to activate at 25% battery instead of 20%.

**Range:** 5% to 95%

### Enable/Disable Monitoring

```bash
# Disable monitoring
python3 battery_control.py disable

# Enable monitoring
python3 battery_control.py enable
```

When disabled, the daemon keeps running but won't activate Low Power Mode.

### Start/Stop/Restart Daemon

```bash
# Stop daemon
python3 battery_control.py stop

# Start daemon
python3 battery_control.py start

# Restart daemon
python3 battery_control.py restart
```

### View Logs

```bash
# Show all logs
python3 battery_control.py logs

# Or view log file directly
cat ~/.battery_saver_daemon.log

# Follow logs in real-time
tail -f ~/.battery_saver_daemon.log
```

---

## Complete Command Reference

```bash
python3 battery_control.py <command> [options]
```

| Command | Description | Example |
|---------|-------------|---------|
| `status` | Show current status | `python3 battery_control.py status` |
| `threshold <percent>` | Set threshold (5-95) | `python3 battery_control.py threshold 25` |
| `enable` | Enable monitoring | `python3 battery_control.py enable` |
| `disable` | Disable monitoring | `python3 battery_control.py disable` |
| `start` | Start daemon | `python3 battery_control.py start` |
| `stop` | Stop daemon | `python3 battery_control.py stop` |
| `restart` | Restart daemon | `python3 battery_control.py restart` |
| `logs` | View all logs | `python3 battery_control.py logs` |
| `help` | Show help | `python3 battery_control.py help` |

---

## How It Works

### Daemon Operation

1. **Starts automatically** on login (via LaunchAgent)
2. **Checks battery** every 30 seconds (configurable)
3. **Reloads config** on each check (changes apply immediately)
4. **Activates Low Power Mode** when:
   - Battery ≤ threshold
   - On battery power (not plugged in)
   - Monitoring is enabled
5. **Sends notification** when activating (if enabled)
6. **Logs everything** to `~/.battery_saver_daemon.log`

### Configuration File

Settings are stored in: `~/.battery_saver_config.json`

```json
{
  "threshold": 20,
  "enabled": true,
  "notifications": true,
  "check_interval": 30
}
```

**You can edit this file directly**, and the daemon will pick up changes on the next check (within 30 seconds).

### Log File

Logs are saved to: `~/.battery_saver_daemon.log`

Example log entries:
```
[2025-10-18 18:30:00] Battery Saver Daemon starting...
[2025-10-18 18:30:00] Threshold: 20%, Enabled: True, Check interval: 30s
[2025-10-18 18:30:30] Battery: 100%, On battery: False, Power mode: 0, Threshold: 20%
[2025-10-18 18:31:00] Battery: 100%, On battery: False, Power mode: 0, Threshold: 20%
[2025-10-18 19:00:00] Battery: 18%, On battery: True, Power mode: 0, Threshold: 20%
[2025-10-18 19:00:00] Battery at 18%, enabling Low Power Mode...
[2025-10-18 19:00:01] Low Power Mode enabled successfully
```

---

## Passwordless Operation

For automatic Low Power Mode activation **without password prompts**, run the passwordless setup:

```bash
./setup_passwordless_pmset.sh
```

**This is REQUIRED for background daemon** - otherwise it cannot enable Low Power Mode automatically.

See [PASSWORDLESS_SETUP.md](PASSWORDLESS_SETUP.md) for details.

---

## Notifications

When Low Power Mode activates, you'll see a macOS notification:

```
Battery Saver
Battery at 18% - Low Power Mode enabled
```

**To disable notifications:**
```bash
# Edit config file
nano ~/.battery_saver_config.json

# Change "notifications": true to "notifications": false
```

---

## Uninstalling

To remove the background daemon:

```bash
./uninstall_daemon.sh
```

This will:
- Stop the daemon
- Remove LaunchAgent
- NOT delete your settings or logs (in case you want to reinstall)

---

## Switching Between Modes

### From Menu Bar to Background Daemon

```bash
# Uninstall menu bar version
./uninstall_launch_agent.sh

# Install background daemon
./install_daemon.sh
```

### From Background Daemon to Menu Bar

```bash
# Uninstall daemon
./uninstall_daemon.sh

# Install menu bar version
./install_launch_agent.sh
```

---

## Troubleshooting

### Daemon won't start

**Check if it's running:**
```bash
ps aux | grep battery_saver_daemon
```

**View error logs:**
```bash
cat /tmp/battery_saver_daemon_stderr.log
```

**Manually start to see errors:**
```bash
python3 battery_saver_daemon.py
```

### Low Power Mode doesn't activate

**Check logs:**
```bash
python3 battery_control.py logs
```

**Verify passwordless sudo:**
```bash
sudo -n pmset -b lowpowermode 1
```

If this asks for password, run:
```bash
./setup_passwordless_pmset.sh
```

### Can't control daemon

**Make sure it's running:**
```bash
python3 battery_control.py status
```

**Restart daemon:**
```bash
python3 battery_control.py restart
```

### Settings don't apply

**Check config file:**
```bash
cat ~/.battery_saver_config.json
```

**Restart daemon:**
```bash
python3 battery_control.py restart
```

---

## Advanced Usage

### Change Check Interval

Edit `~/.battery_saver_config.json`:

```json
{
  "threshold": 20,
  "enabled": true,
  "notifications": true,
  "check_interval": 60
}
```

**Values:**
- `30` = Check every 30 seconds (default)
- `60` = Check every minute
- `300` = Check every 5 minutes

### Run Daemon Manually (for testing)

```bash
python3 battery_saver_daemon.py
```

Runs in foreground with output to terminal. Press Ctrl+C to stop.

### Monitor Logs in Real-Time

```bash
tail -f ~/.battery_saver_daemon.log
```

### Create Aliases (optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias battery='python3 /Users/daniel/Documents/aicode/Battery_saver/battery_control.py'
```

Then use:
```bash
battery status
battery threshold 25
battery enable
```

---

## Comparison: Menu Bar vs Background Daemon

| Feature | Menu Bar App | Background Daemon |
|---------|--------------|-------------------|
| **Visibility** | Menu bar icon | Invisible |
| **UI** | Click for menu | Command-line only |
| **Threshold adjustment** | Visual slider | Command or edit config |
| **Status check** | Click icon | Run `status` command |
| **Enable/Disable** | Click buttons | Run commands |
| **Logs** | None | File logging |
| **System resources** | ~50MB RAM | ~30MB RAM |
| **Auto-start** | LaunchAgent | LaunchAgent |
| **Passwordless setup** | Optional | Required |

---

## Files Created

- `battery_saver_daemon.py` - Background daemon script
- `battery_control.py` - CLI control tool
- `install_daemon.sh` - Installation script
- `uninstall_daemon.sh` - Uninstallation script
- `com.daniel.batterysaver.daemon.plist` - LaunchAgent config
- `~/.battery_saver_daemon.log` - Log file (created on first run)
- `~/.battery_saver_config.json` - Settings (shared with menu bar app)

---

## Recommendation

**For most users:** Background daemon mode

**Why:**
- ✅ Set and forget - no visual clutter
- ✅ Runs silently in background
- ✅ Easy to control when needed
- ✅ Full logging for troubleshooting
- ✅ Lower resource usage

**Use menu bar app if:**
- You want quick visual access
- You frequently change threshold
- You prefer GUI over command-line

**Both work perfectly!** Choose what fits your workflow.

---

**Last Updated:** October 18, 2025
**Applies to:** Battery Saver v1.0.0
