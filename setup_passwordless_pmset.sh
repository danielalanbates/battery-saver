#!/bin/bash
# Setup passwordless pmset for LowPower Automator
# Copyright (c) 2025 Daniel
# Licensed under the MIT License

# This script is run with administrator privileges via AppleScript
# No sudo needed - we already have root privileges

# Get the real username (not 'root')
# When run via AppleScript with admin privileges, USER and SUDO_USER are empty
# So we get the console user (the person logged in)
USERNAME=$(stat -f '%Su' /dev/console)

# Create sudoers rule
SUDOERS_RULE="$USERNAME ALL=(ALL) NOPASSWD: /usr/bin/pmset -b lowpowermode *"
SUDOERS_FILE="/private/etc/sudoers.d/lowpowerautomator"

# Create the directory if it doesn't exist
mkdir -p /private/etc/sudoers.d

# Create the sudoers entry with proper permissions
echo "$SUDOERS_RULE" > "$SUDOERS_FILE"

if [ $? -eq 0 ]; then
    # Set proper permissions (sudoers files must be 0440)
    chmod 0440 "$SUDOERS_FILE"

    # Validate the sudoers file
    visudo -c -f "$SUDOERS_FILE" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        exit 0
    else
        rm "$SUDOERS_FILE"
        exit 1
    fi
else
    exit 1
fi
