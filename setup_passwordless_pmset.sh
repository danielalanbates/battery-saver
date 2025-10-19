#!/bin/bash
# Setup passwordless pmset for Battery Saver
# Copyright (c) 2025 Daniel
# Licensed under the MIT License

echo "Battery Saver - Passwordless Setup"
echo "===================================="
echo ""
echo "This script will configure your Mac to allow Battery Saver to"
echo "enable/disable Low Power Mode WITHOUT asking for your password."
echo ""
echo "This is done by adding a sudoers rule that allows ONLY the"
echo "pmset lowpowermode command to run without a password."
echo ""
echo "⚠️  This requires admin privileges (you'll need to enter your password once now)."
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 1
fi

# Get current username
USERNAME=$(whoami)

# Create sudoers rule
SUDOERS_RULE="$USERNAME ALL=(ALL) NOPASSWD: /usr/bin/pmset -b lowpowermode *"
SUDOERS_FILE="/private/etc/sudoers.d/batterysaver"

echo ""
echo "Creating sudoers rule..."
echo "Rule: $SUDOERS_RULE"
echo "File: $SUDOERS_FILE"
echo ""

# Create the sudoers entry with proper permissions
# This requires entering password once
echo "$SUDOERS_RULE" | sudo tee "$SUDOERS_FILE" > /dev/null

if [ $? -eq 0 ]; then
    # Set proper permissions (sudoers files must be 0440)
    sudo chmod 0440 "$SUDOERS_FILE"

    # Validate the sudoers file
    sudo visudo -c -f "$SUDOERS_FILE"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Success! Passwordless pmset is now configured."
        echo ""
        echo "Battery Saver can now enable/disable Low Power Mode"
        echo "automatically without asking for your password."
        echo ""
        echo "To test, try:"
        echo "  sudo pmset -b lowpowermode 1"
        echo "  (should work without password)"
        echo ""
        echo "To remove this later, run:"
        echo "  sudo rm /private/etc/sudoers.d/batterysaver"
        echo ""
    else
        echo ""
        echo "❌ Error: Sudoers file validation failed."
        echo "Removing invalid file..."
        sudo rm "$SUDOERS_FILE"
        exit 1
    fi
else
    echo ""
    echo "❌ Error: Failed to create sudoers file."
    echo "You may need admin privileges."
    exit 1
fi
