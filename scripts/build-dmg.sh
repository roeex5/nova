#!/bin/bash
# Build DMG from existing app bundle

set -e  # Exit on error

echo "========================================"
echo "Building DMG Installer"
echo "========================================"
echo ""

# Check if app bundle exists
if [ ! -d "src-tauri/target/release/bundle/macos" ]; then
    echo "ERROR: App bundle not found!"
    echo "Please run ./scripts/build-app-only.sh first"
    exit 1
fi

APP_PATH=$(find src-tauri/target/release/bundle/macos -name "*.app" | head -1)
if [ -z "$APP_PATH" ]; then
    echo "ERROR: No .app bundle found in src-tauri/target/release/bundle/macos"
    exit 1
fi

echo "Found app bundle: $APP_PATH"
echo ""
echo "Building DMG installer..."
echo "------------------------------------"
npm run tauri build -- --bundles dmg

echo ""
# Call helper function to show output info
source "$(dirname "$0")/build-utils.sh"
show_dmg_output
