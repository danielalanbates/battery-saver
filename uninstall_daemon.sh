#!/bin/bash
# Uninstall Battery Saver Background Daemon
# Copyright (c) 2025 Daniel
# Licensed under the MIT License

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
INSTALLED_PLIST="$LAUNCH_AGENTS_DIR/com.daniel.batterysaver.daemon.plist"

echo "Battery Saver - Background Daemon Uninstallation"
echo "================================================="
echo ""

# Check if daemon is installed
if [ ! -f "$INSTALLED_PLIST" ]; then
    echo "❌ Battery Saver daemon is not installed."
    exit 1
fi

# Unload the daemon
echo "Unloading Battery Saver daemon..."
launchctl unload "$INSTALLED_PLIST" 2>/dev/null

# Remove plist file
echo "Removing LaunchAgent file..."
rm "$INSTALLED_PLIST"

# Kill any running instances
echo "Stopping daemon..."
pkill -f "battery_saver_daemon.py"

echo ""
echo "✅ Battery Saver daemon has been uninstalled successfully!"
echo ""
echo "To reinstall, run: ./install_daemon.sh"
