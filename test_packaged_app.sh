#!/bin/bash
# Test script for packaged application
# Verifies the .app bundle works correctly
#
# Created: 2025-12-17

set -e

APP_PATH="dist/BrowserAutomation.app"

echo "========================================"
echo "Testing Packaged Application"
echo "========================================"
echo ""

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "ERROR: $APP_PATH not found"
    echo "Run ./build_app.sh first"
    exit 1
fi

echo "Testing application bundle..."
echo ""

# Check app structure
echo "✓ Checking bundle structure..."
[ -f "$APP_PATH/Contents/MacOS/BrowserAutomation" ] || { echo "ERROR: Missing executable"; exit 1; }
[ -f "$APP_PATH/Contents/Info.plist" ] || { echo "ERROR: Missing Info.plist"; exit 1; }
echo "  Bundle structure: OK"

# Check bundle identifier
echo "✓ Checking bundle identifier..."
BUNDLE_ID=$(defaults read "$APP_PATH/Contents/Info.plist" CFBundleIdentifier)
echo "  Bundle ID: $BUNDLE_ID"

# Check version
echo "✓ Checking version..."
VERSION=$(defaults read "$APP_PATH/Contents/Info.plist" CFBundleShortVersionString)
echo "  Version: $VERSION"

# Check permissions
echo "✓ Checking permissions..."
PLIST_KEYS=$(defaults read "$APP_PATH/Contents/Info.plist")
if echo "$PLIST_KEYS" | grep -q "NSMicrophoneUsageDescription"; then
    echo "  Microphone permission: OK"
else
    echo "  WARNING: Microphone permission not set"
fi

# Test launch (will open the app - manual verification needed)
echo ""
echo "========================================"
echo "Manual Testing Required"
echo "========================================"
echo ""
echo "The app will now launch for manual testing."
echo ""
echo "Please verify:"
echo "  1. First-run setup dialog appears (if no config)"
echo "  2. API key can be entered and saved"
echo "  3. Main window opens with ElevenLabs widget"
echo "  4. Voice interface loads successfully"
echo "  5. Browser automation works (if API key provided)"
echo ""
read -p "Press Enter to launch the app..."

open "$APP_PATH"

echo ""
echo "App launched. Please perform manual testing."
echo ""
