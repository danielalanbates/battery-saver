#!/bin/bash
# Install Battery Saver Background Daemon
# Copyright (c) 2025 Daniel
# Licensed under the MIT License

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_FILE="$SCRIPT_DIR/com.daniel.batterysaver.daemon.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
INSTALLED_PLIST="$LAUNCH_AGENTS_DIR/com.daniel.batterysaver.daemon.plist"

echo "Battery Saver - Background Daemon Installation"
echo "=============================================="
echo ""
echo "This will install Battery Saver as a background daemon that:"
echo "  • Runs automatically on login"
echo "  • Has NO menu bar icon"
echo "  • Has NO dock icon"
echo "  • Runs completely in the background"
echo "  • Monitors battery and enables Low Power Mode automatically"
echo ""
echo "You can control it using: python3 battery_control.py <command>"
echo ""
read -p "Continue with installation? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Stop any running menu bar version
echo ""
echo "Stopping any running Battery Saver instances..."
pkill -f battery_saver.py 2>/dev/null
pkill -f battery_saver_daemon.py 2>/dev/null

# Unload old LaunchAgent if exists
if [ -f "$HOME/Library/LaunchAgents/com.daniel.batterysaver.plist" ]; then
    echo "Unloading old menu bar version..."
    launchctl unload "$HOME/Library/LaunchAgents/com.daniel.batterysaver.plist" 2>/dev/null
    rm "$HOME/Library/LaunchAgents/com.daniel.batterysaver.plist"
fi

# Create LaunchAgents directory if it doesn't exist
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo "Creating LaunchAgents directory..."
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

# Unload existing daemon if running
if launchctl list | grep -q "com.daniel.batterysaver.daemon"; then
    echo "Unloading existing daemon..."
    launchctl unload "$INSTALLED_PLIST" 2>/dev/null
fi

# Copy plist file
echo "Installing LaunchAgent..."
cp "$PLIST_FILE" "$INSTALLED_PLIST"

# Load the agent
echo "Loading Battery Saver daemon..."
launchctl load "$INSTALLED_PLIST"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Battery Saver daemon installed successfully!"
    echo ""
    echo "The daemon is now running in the background with:"
    echo "  • No menu bar icon"
    echo "  • No dock icon"
    echo "  • Automatic startup on login"
    echo ""
    echo "Control the daemon with these commands:"
    echo "  python3 battery_control.py status      - Show status"
    echo "  python3 battery_control.py threshold 25 - Set threshold"
    echo "  python3 battery_control.py enable      - Enable monitoring"
    echo "  python3 battery_control.py disable     - Disable monitoring"
    echo "  python3 battery_control.py logs        - View logs"
    echo ""
    echo "Logs are saved to: ~/.battery_saver_daemon.log"
    echo ""
    echo "To uninstall, run: ./uninstall_daemon.sh"
else
    echo ""
    echo "❌ Failed to load daemon."
    exit 1
fi
