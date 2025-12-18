#!/bin/bash
# Clean build script for Browser Automation
# Removes all build artifacts except bundle-venv (which is needed for production builds)

set -e

# Parse command line arguments
CLEAN_USER_DATA=false
if [ "$1" = "--all" ] || [ "$1" = "--user-data" ]; then
    CLEAN_USER_DATA=true
fi

echo "🧹 Cleaning Browser Automation build artifacts..."
echo ""

# Python cache
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# macOS metadata
echo "Removing macOS .DS_Store files..."
find . -name ".DS_Store" -delete 2>/dev/null || true

# Node modules (optional - uncomment if you want to clean npm packages)
# echo "Removing node_modules..."
# rm -rf node_modules

# Tauri build artifacts
echo "Removing Tauri build artifacts..."
if [ -d "src-tauri/target" ]; then
    echo "  - Removing src-tauri/target/release/bundle..."
    rm -rf src-tauri/target/release/bundle 2>/dev/null || true

    echo "  - Removing src-tauri/target/release/deps..."
    rm -rf src-tauri/target/release/deps 2>/dev/null || true

    echo "  - Removing src-tauri/target/release/build..."
    rm -rf src-tauri/target/release/build 2>/dev/null || true

    # Optional: clean entire target directory (takes longer to rebuild)
    # Uncomment if you want a completely clean build
    # echo "  - Removing entire src-tauri/target..."
    # rm -rf src-tauri/target
fi

# Distribution artifacts
echo "Removing distribution files..."
rm -rf dist/*.dmg 2>/dev/null || true
rm -rf dist/*.app 2>/dev/null || true

# Temporary files
echo "Removing temporary files..."
rm -rf /tmp/BrowserAutomation* 2>/dev/null || true

# Flask cache
echo "Removing Flask cache..."
rm -rf .flask_session 2>/dev/null || true

# User data (optional - only if --all or --user-data flag is set)
if [ "$CLEAN_USER_DATA" = true ]; then
    echo "Removing user data (config, API keys, browser history)..."
    rm -rf ~/Library/Application\ Support/BrowserAutomation/ 2>/dev/null || true
    echo "  ⚠️  User data removed (you'll need to reconfigure API key on next run)"
fi

echo ""
echo "✅ Clean complete!"
echo ""
echo "📝 Notes:"
echo "   - bundle-venv was NOT removed (needed for production builds)"
echo "     To clean bundle-venv: rm -rf bundle-venv"
if [ "$CLEAN_USER_DATA" = false ]; then
    echo "   - User data was NOT removed (API keys and config preserved)"
    echo "     To clean user data: ./clean.sh --all"
fi
echo ""
echo "Next steps:"
echo "  1. Test dev mode: npm run server (terminal 1) && npm run dev (terminal 2)"
echo "  2. Build production: npm run build"
echo ""
