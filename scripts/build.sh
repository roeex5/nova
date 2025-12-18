#!/bin/bash
# Build production Tauri app with bundled Python dependencies

set -e  # Exit on error

echo "========================================"
echo "Building Browser Automation Desktop App"
echo "========================================"
echo ""

# Step 1: Prepare Python bundle
echo "Step 1: Preparing Python bundle..."
echo "------------------------------------"
./scripts/prepare-bundle.sh

echo ""
echo "Step 2: Building Tauri application..."
echo "------------------------------------"
npm run build

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Output location:"
if [ -d "src-tauri/target/release/bundle/macos" ]; then
    APP_PATH=$(find src-tauri/target/release/bundle/macos -name "*.app" | head -1)
    echo "  $APP_PATH"
    echo ""
    echo "Bundle size:"
    du -sh "$APP_PATH"
    echo ""
    echo "To test the app:"
    echo "  open \"$APP_PATH\""
else
    echo "  src-tauri/target/release/bundle/"
fi
echo ""
