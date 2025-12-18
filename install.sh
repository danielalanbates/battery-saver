#!/bin/bash
# LowPower Automator Installer
# https://github.com/danielalanbates/LowPower-Automator

set -e

REPO="danielalanbates/LowPower-Automator"
APP_NAME="LowPower Automator"

echo "🔋 Installing $APP_NAME..."
echo ""

# Get latest release download URL
DOWNLOAD_URL=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep "browser_download_url.*\.dmg" | cut -d '"' -f 4)

if [ -z "$DOWNLOAD_URL" ]; then
    echo "❌ Could not find latest release. Please download manually from:"
    echo "   https://github.com/$REPO/releases"
    exit 1
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
DMG_PATH="$TEMP_DIR/LowPowerAutomator.dmg"

echo "📥 Downloading latest release..."
curl -L -o "$DMG_PATH" "$DOWNLOAD_URL"

echo "📦 Mounting disk image..."
MOUNT_POINT=$(hdiutil attach "$DMG_PATH" -nobrowse | grep "/Volumes" | awk '{print $3}')

echo "🚀 Installing to /Applications..."
cp -R "$MOUNT_POINT"/*.app /Applications/ 2>/dev/null || {
    echo "❌ Could not copy app. You may need to run with sudo."
    hdiutil detach "$MOUNT_POINT" -quiet
    rm -rf "$TEMP_DIR"
    exit 1
}

echo "🧹 Cleaning up..."
hdiutil detach "$MOUNT_POINT" -quiet
rm -rf "$TEMP_DIR"

echo ""
echo "✅ $APP_NAME installed successfully!"
echo "📍 Location: /Applications/"
echo ""
echo "To run: Open '$APP_NAME' from your Applications folder or Spotlight."
