#!/bin/bash
# Shared build utility functions - sourced by other build scripts

# Display app bundle output information
show_app_output() {
    echo "========================================"
    echo "Build Complete!"
    echo "========================================"
    echo ""
    echo "Output location:"
    if [ -d "src-tauri/target/release/bundle/macos" ]; then
        APP_PATH=$(find src-tauri/target/release/bundle/macos -name "*.app" | head -1)
        if [ -n "$APP_PATH" ]; then
            echo "  $APP_PATH"
            echo ""
            echo "Bundle size:"
            du -sh "$APP_PATH"
            echo ""
            echo "To test the app:"
            echo "  open \"$APP_PATH\""
        fi
    else
        echo "  src-tauri/target/release/bundle/"
    fi
    echo ""
}

# Display DMG output information
show_dmg_output() {
    echo "========================================"
    echo "DMG Build Complete!"
    echo "========================================"
    echo ""
    echo "DMG location:"
    if [ -d "src-tauri/target/release/bundle/dmg" ]; then
        DMG_PATH=$(find src-tauri/target/release/bundle/dmg -name "*.dmg" | head -1)
        if [ -n "$DMG_PATH" ]; then
            echo "  $DMG_PATH"
            echo ""
            echo "DMG size:"
            du -sh "$DMG_PATH"
        fi
    else
        echo "  src-tauri/target/release/bundle/dmg/"
    fi
    echo ""
}
