#!/bin/bash
# Build production Tauri app with bundled Python dependencies and DMG

set -e  # Exit on error

echo "========================================"
echo "Building Browser Automation Desktop App"
echo "========================================"
echo ""

# Step 1: Build app bundle
./scripts/build-app-only.sh

# Step 2: Build DMG from the app
echo ""
echo "Step 3: Building DMG installer..."
echo "------------------------------------"
./scripts/build-dmg.sh

echo ""
echo "========================================"
echo "Full Build Complete!"
echo "========================================"
echo ""
