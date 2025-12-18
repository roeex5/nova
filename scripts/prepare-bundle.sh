#!/bin/bash
# Prepare Python environment for Tauri bundle
# This script creates a minimal venv with only production dependencies

set -e  # Exit on error

echo "=================================="
echo "Preparing Python Bundle for Tauri"
echo "=================================="

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Using Python $PYTHON_VERSION"

# Verify Python 3.10+
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "ERROR: Python 3.10+ required (found $PYTHON_VERSION)"
    echo "Please activate a Python 3.10+ environment or use a compatible interpreter"
    exit 1
fi

# Clean previous bundle
echo "Cleaning previous bundle..."
rm -rf bundle-venv

# Create fresh venv
echo "Creating virtual environment..."
python -m venv bundle-venv

# Activate venv
source bundle-venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install production dependencies
echo "Installing production dependencies..."
pip install -r requirements-bundle.txt

# Verify installation
echo ""
echo "Installed packages:"
pip list

echo ""
echo "=================================="
echo "Bundle preparation complete!"
echo "=================================="
echo "Virtual environment: bundle-venv/"
echo "Size: $(du -sh bundle-venv | cut -f1)"
echo ""
