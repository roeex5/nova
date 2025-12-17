#!/bin/bash
# Create DMG for distribution
# Packages the .app bundle into a drag-and-drop DMG installer
#
# Created: 2025-12-17

set -e

APP_NAME="BrowserAutomation"
VERSION="0.1.0"
DMG_NAME="${APP_NAME}-${VERSION}.dmg"
VOLUME_NAME="Browser Automation ${VERSION}"

echo "========================================"
echo "Creating DMG for distribution"
echo "========================================"

# Check if app exists
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "ERROR: dist/${APP_NAME}.app not found"
    echo "Run ./build_app.sh first"
    exit 1
fi

# Create temporary DMG directory
TMP_DMG_DIR=$(mktemp -d)
echo "Temporary directory: $TMP_DMG_DIR"

# Copy app to temp directory
echo "Copying app bundle..."
cp -R "dist/${APP_NAME}.app" "$TMP_DMG_DIR/"

# Create Applications symlink for drag-and-drop install
echo "Creating Applications symlink..."
ln -s /Applications "$TMP_DMG_DIR/Applications"

# Create DMG
echo "Creating DMG..."
hdiutil create -volname "$VOLUME_NAME" \
    -srcfolder "$TMP_DMG_DIR" \
    -ov -format UDZO \
    "dist/$DMG_NAME"

# Clean up
rm -rf "$TMP_DMG_DIR"

echo ""
echo "========================================"
echo "DMG Created Successfully!"
echo "========================================"
echo ""
echo "DMG file: dist/$DMG_NAME"
echo "Size: $(du -sh dist/$DMG_NAME | cut -f1)"
echo ""
echo "Distribution checklist:"
echo "  [ ] Test DMG on clean macOS system"
echo "  [ ] Verify first-run setup dialog appears"
echo "  [ ] Test voice interface functionality"
echo "  [ ] Test browser automation with real API key"
echo ""
