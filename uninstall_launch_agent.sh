#!/bin/bash
# Uninstall LaunchAgent for Battery Saver
# Copyright (c) 2025 Daniel
# Licensed under the MIT License

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
INSTALLED_PLIST="$LAUNCH_AGENTS_DIR/com.daniel.batterysaver.plist"

echo "Battery Saver - LaunchAgent Uninstallation"
echo "==========================================="
echo ""

# Check if agent is installed
if [ ! -f "$INSTALLED_PLIST" ]; then
    echo "❌ Battery Saver LaunchAgent is not installed."
    exit 1
fi

# Unload the agent
echo "Unloading Battery Saver agent..."
launchctl unload "$INSTALLED_PLIST" 2>/dev/null

# Remove plist file
echo "Removing LaunchAgent file..."
rm "$INSTALLED_PLIST"

# Kill any running instances
echo "Stopping Battery Saver..."
pkill -f "battery_saver.py"

echo ""
echo "✅ Battery Saver has been uninstalled successfully!"
echo ""
echo "To reinstall, run: ./install_launch_agent.sh"
