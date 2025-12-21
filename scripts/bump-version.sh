#!/bin/bash
# Bump version across the entire codebase
# Usage: ./scripts/bump-version.sh <new-version>
# Example: ./scripts/bump-version.sh 0.1.4

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <new-version>"
    echo "Example: $0 0.1.4"
    echo ""
    echo "Current version detection:"
    CURRENT=$(grep '"version":' package.json | head -1 | sed 's/.*"version": "\(.*\)".*/\1/')
    echo "  Current version: $CURRENT"
    exit 1
fi

NEW_VERSION=$1

# Detect current version
CURRENT=$(grep '"version":' package.json | head -1 | sed 's/.*"version": "\(.*\)".*/\1/')

echo "========================================"
echo "Version Bump"
echo "========================================"
echo "Current: $CURRENT"
echo "New:     $NEW_VERSION"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Updating files..."

# 1. package.json
echo "  - package.json"
sed -i '' "s/\"version\": \"$CURRENT\"/\"version\": \"$NEW_VERSION\"/" package.json

# 2. src-tauri/tauri.conf.json
echo "  - src-tauri/tauri.conf.json"
sed -i '' "s/\"version\": \"$CURRENT\"/\"version\": \"$NEW_VERSION\"/" src-tauri/tauri.conf.json

# 3. src-tauri/Cargo.toml
echo "  - src-tauri/Cargo.toml"
sed -i '' "s/^version = \"$CURRENT\"/version = \"$NEW_VERSION\"/" src-tauri/Cargo.toml

# 4. src/auto_browser/__init__.py
echo "  - src/auto_browser/__init__.py"
sed -i '' "s/__version__ = \"$CURRENT\"/__version__ = \"$NEW_VERSION\"/" src/auto_browser/__init__.py

# 5. Update Cargo.lock
echo "  - src-tauri/Cargo.lock (via cargo update)"
cd src-tauri && cargo update -p app --quiet
cd ..

echo ""
echo "========================================"
echo "✅ Version bumped to $NEW_VERSION"
echo "========================================"
echo ""
echo "Files updated:"
echo "  - package.json"
echo "  - src-tauri/tauri.conf.json"
echo "  - src-tauri/Cargo.toml"
echo "  - src-tauri/Cargo.lock"
echo "  - src/auto_browser/__init__.py"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Build: ./scripts/build-app-only.sh"
echo "  3. Commit: git add -A && git commit -m 'Bump version to $NEW_VERSION'"
echo ""
