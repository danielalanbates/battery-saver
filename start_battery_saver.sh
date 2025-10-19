#!/bin/bash
# Battery Saver - Startup Script
# Copyright (c) 2025 Daniel
# Licensed under the MIT License

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/battery_saver.py"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "Python 3 is required but not found. Please install Python 3 to use Battery Saver." buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Check if rumps is installed
if ! python3 -c "import rumps" 2>/dev/null; then
    echo "Installing rumps..."
    pip3 install rumps --user

    if [ $? -ne 0 ]; then
        osascript -e 'display dialog "Failed to install rumps. Please run: pip3 install rumps" buttons {"OK"} default button "OK" with icon stop'
        exit 1
    fi
fi

# Kill any existing instances
pkill -f "battery_saver.py"

# Wait a moment for the process to terminate
sleep 1

# Launch the app
python3 "$PYTHON_SCRIPT" &

echo "Battery Saver started successfully!"
