#!/bin/bash
# Build standalone Python binary using PyInstaller for Tauri bundle
# This creates a single binary that includes Python interpreter and all dependencies

set -e  # Exit on error

echo "==========================================="
echo "Building Standalone Python Binary Bundle"
echo "==========================================="

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Using Python $PYTHON_VERSION"

# Verify Python 3.10+
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "ERROR: Python 3.10+ required (found $PYTHON_VERSION)"
    exit 1
fi

# Install PyInstaller if not already installed
echo "Checking for PyInstaller..."
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found, installing..."
    pip install pyinstaller
else
    echo "PyInstaller already installed"
fi

# Clean previous build
echo "Cleaning previous build..."
rm -rf build dist bundle-bin

# Create bundle-bin directory for output
mkdir -p bundle-bin

# Build standalone binary with PyInstaller
echo ""
echo "Building standalone binary with PyInstaller..."
echo "This may take a few minutes..."
echo ""

# PyInstaller options:
# --onedir: Create a directory with all dependencies (easier to debug than --onefile)
# --name: Name of the output binary
# --hidden-import: Force include modules that PyInstaller might miss
# --collect-all: Include all files from specific packages
# --noconfirm: Overwrite without asking
# --clean: Clean PyInstaller cache before building

pyinstaller \
    --onedir \
    --name server \
    --noconfirm \
    --clean \
    --hidden-import=flask_cors \
    --hidden-import=werkzeug \
    --hidden-import=auto_browser \
    --hidden-import=auto_browser.web_ui \
    --hidden-import=auto_browser.config_manager \
    --hidden-import=auto_browser.automation_server \
    --collect-all nova_act \
    --collect-all playwright \
    --collect-all flask \
    --collect-all flask_cors \
    --add-data "src:src" \
    server.py

# Move the dist/server directory to bundle-bin
echo ""
echo "Moving build output to bundle-bin/..."
mv dist/server/* bundle-bin/
rmdir dist/server

# Install Playwright browsers into the bundle
echo ""
echo "Installing Playwright browsers into bundle..."
echo "This may take a while as it downloads Chromium..."

# Set the Playwright browsers path to install into the bundle
export PLAYWRIGHT_BROWSERS_PATH="$(pwd)/bundle-bin/_internal/playwright/driver/package/.local-browsers"
mkdir -p "$PLAYWRIGHT_BROWSERS_PATH"

# Install chromium headless shell (used by Nova Act)
playwright install chromium-headless-shell

# Verify browsers were installed
if [ -d "$PLAYWRIGHT_BROWSERS_PATH" ] && [ "$(ls -A $PLAYWRIGHT_BROWSERS_PATH 2>/dev/null)" ]; then
    echo "✓ Playwright browsers installed successfully"
    echo "  Browser location: $PLAYWRIGHT_BROWSERS_PATH"
    ls -la "$PLAYWRIGHT_BROWSERS_PATH/" | head -20
else
    echo "ERROR: Playwright browsers failed to install!"
    echo "  Expected location: $PLAYWRIGHT_BROWSERS_PATH"
    echo ""
    echo "The bundle cannot be used without Playwright browsers."
    echo "Browser automation will fail at runtime."
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check internet connection (browsers are downloaded)"
    echo "  2. Verify Playwright is installed: pip show playwright"
    echo "  3. Try manual install: playwright install chromium-headless-shell"
    exit 1
fi

# Clean up build artifacts
echo ""
echo "Cleaning up build artifacts..."
rm -rf build dist *.spec

echo ""
echo "==========================================="
echo "Build Complete!"
echo "==========================================="
echo "Standalone binary: bundle-bin/server"
echo "Bundle size: $(du -sh bundle-bin | cut -f1)"
echo ""
echo "To test the binary:"
echo "  ./bundle-bin/server"
echo ""
