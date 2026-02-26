#!/bin/bash
# Launcher for LowPower Automator

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"

# Use the GUI Python framework which is required for rumps menu bar apps
if [ -f "/Library/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python" ]; then
    PYTHON="/Library/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python"
elif [ -f "/System/Library/Frameworks/Python.framework/Versions/Current/Resources/Python.app/Contents/MacOS/Python" ]; then
    PYTHON="/System/Library/Frameworks/Python.framework/Versions/Current/Resources/Python.app/Contents/MacOS/Python"
else
    # Fallback to regular python3
    PYTHON="/usr/bin/python3"
fi

# Run the Python script
cd "$RESOURCES_DIR"
"$PYTHON" lowpower_automator.py
