#!/bin/bash
# Build script for Browser Automation Desktop App
# Creates macOS .app bundle using PyInstaller
#
# Created: 2025-12-17

set -e  # Exit on error

echo "========================================"
echo "Building Browser Automation Desktop App"
echo "========================================"

# Check if we're in conda environment
if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo "WARNING: Not in a conda environment"
    echo "Please activate the 'nova' environment first:"
    echo "  conda activate nova"
    exit 1
fi

echo "Environment: $CONDA_DEFAULT_ENV"
echo "Python: $(which python)"
echo "Python version: $(python --version)"
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ 2>/dev/null || true
echo "Done"
echo ""

# Check PyInstaller is installed
echo "Checking PyInstaller..."
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi
echo "PyInstaller version: $(pyinstaller --version)"
echo ""

# Run PyInstaller with spec file
echo "Running PyInstaller..."
pyinstaller BrowserAutomation.spec

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Application bundle: dist/BrowserAutomation.app"
echo "Size: $(du -sh dist/BrowserAutomation.app | cut -f1)"
echo ""
echo "To test the app:"
echo "  open dist/BrowserAutomation.app"
echo ""
echo "To create a DMG for distribution:"
echo "  ./create_dmg.sh"
echo ""
