#!/bin/bash
# Build production Tauri app (app bundle only, no DMG)

set -e  # Exit on error

echo "========================================"
echo "Building Browser Automation Desktop App"
echo "========================================"
echo ""

# Step 1: Prepare Python bundle with PyInstaller
echo "Step 1: Preparing Python bundle with PyInstaller..."
echo "------------------------------------"
./scripts/prepare-bundle-pyinstaller.sh

echo ""
echo "Step 2: Building Tauri application (app only, no DMG)..."
echo "------------------------------------"
npm run tauri build -- --bundles app

echo ""
# Call helper function to show output info
source "$(dirname "$0")/build-utils.sh"
show_app_output

echo "NOTE: To build DMG separately, run: ./scripts/build-dmg.sh"
echo ""
