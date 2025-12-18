# Building Production App

## Prerequisites

- macOS 10.15+
- Node.js and npm (for Tauri)
- Python 3.8+ (for creating the venv)
- Rust (Tauri will install if needed)

## Build Process

The build process creates a production .app bundle with:
- Tauri window (Rust + WebKit)
- Python Flask server (bundled in venv)
- All required dependencies (minimal set)

### Quick Build

```bash
./scripts/build.sh
```

This script will:
1. Create a clean virtual environment (`bundle-venv/`)
2. Install minimal production dependencies
3. Build the Tauri application
4. Bundle everything into a .app

### Manual Build Steps

If you prefer to run steps manually:

```bash
# 1. Prepare Python bundle
./scripts/prepare-bundle.sh

# 2. Build Tauri app
npm run build
```

## Output

The built application will be at:
```
src-tauri/target/release/bundle/macos/BrowserAutomation.app
```

## Testing the Build

```bash
# Open the built app
open src-tauri/target/release/bundle/macos/BrowserAutomation.app
```

## Bundle Size

Expected sizes:
- Flask + dependencies: ~20-30 MB
- Nova Act SDK: ~50-100 MB
- Python runtime (in venv): ~30-40 MB
- Tauri + WebKit: ~10-20 MB

**Total: ~150-250 MB** (much smaller than PyQt6 version)

## Distribution

To distribute the app:

1. **Simple distribution**: Zip the .app and share
   ```bash
   cd src-tauri/target/release/bundle/macos
   zip -r BrowserAutomation.zip BrowserAutomation.app
   ```

2. **DMG creation** (optional):
   - Use `hdiutil` or Disk Utility to create a DMG
   - Add Applications folder symlink for drag-and-drop install

3. **Code signing** (for wider distribution):
   - Requires Apple Developer account
   - Use `codesign` and notarization

## Configuration

The app expects:
- API key via environment variable: `NOVA_ACT_API_KEY`
- Or config file: `~/Library/Application Support/BrowserAutomation/config.json`

First-run setup dialog will guide users through API key configuration.

## Troubleshooting

**Build fails with "python3 not found":**
- Ensure Python 3.8+ is installed and in PATH

**Build succeeds but app won't open:**
- Check Console.app for error messages
- Verify bundle-venv was created correctly
- Test Flask server manually: `bundle-venv/bin/python3 server.py`

**App opens but automation doesn't work:**
- Verify API key is configured
- Check that Nova Act SDK installed correctly in bundle-venv
