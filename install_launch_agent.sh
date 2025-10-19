#!/bin/bash
# Install LaunchAgent for Battery Saver
# Copyright (c) 2025 Daniel
# Licensed under the MIT License

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_FILE="$SCRIPT_DIR/com.daniel.batterysaver.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
INSTALLED_PLIST="$LAUNCH_AGENTS_DIR/com.daniel.batterysaver.plist"

echo "Battery Saver - LaunchAgent Installation"
echo "========================================"
echo ""

# Create LaunchAgents directory if it doesn't exist
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo "Creating LaunchAgents directory..."
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

# Unload existing agent if running
if launchctl list | grep -q "com.daniel.batterysaver"; then
    echo "Unloading existing Battery Saver agent..."
    launchctl unload "$INSTALLED_PLIST" 2>/dev/null
fi

# Copy plist file
echo "Installing LaunchAgent..."
cp "$PLIST_FILE" "$INSTALLED_PLIST"

# Load the agent
echo "Loading Battery Saver agent..."
launchctl load "$INSTALLED_PLIST"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Battery Saver has been installed successfully!"
    echo ""
    echo "The app will now:"
    echo "  • Start automatically when you log in"
    echo "  • Appear in your menu bar"
    echo "  • Monitor your battery level every 30 seconds"
    echo "  • Enable Low Power Mode when battery reaches your threshold"
    echo ""
    echo "To uninstall, run: ./uninstall_launch_agent.sh"
else
    echo ""
    echo "❌ Failed to load Battery Saver agent."
    echo "You can still run it manually with: ./start_battery_saver.sh"
fi
