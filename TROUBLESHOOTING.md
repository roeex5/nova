# Troubleshooting Guide

## ElevenLabs Widget Loads But Automation Doesn't Work

If you can see and interact with the voice widget, but browser automation commands don't execute, follow these steps:

### 1. Run Server in Verbose Mode

**Option A: Running server directly (without Tauri app):**
```bash
python server.py --verbose
```

Or using npm:
```bash
npm run server:verbose
```

**Option B: Running Tauri app in verbose mode:**
```bash
# Set environment variable before starting
export VERBOSE=true
npm run dev

# Or in one line:
VERBOSE=true npm run dev
```

**Option C: Production app (built .app bundle):**
```bash
# macOS Terminal - launch with verbose mode
VERBOSE=true open -a BrowserAutomation.app
```

### 2. What Verbose Mode Shows

The verbose output will reveal details at every stage:

#### 🔧 **Tauri/Rust Layer** (Production builds only):
```
VERBOSE mode enabled - passing --verbose to Python server
Starting Python Flask server...
Flask server starting...
```

#### 🐍 **Python Server Layer:**
```
[VERBOSE] Attempting to import nova_act module...
[VERBOSE] nova_act module imported successfully
[VERBOSE] nova_act version: X.X.X
[VERBOSE] nova_act location: /path/to/nova_act
[VERBOSE] API key validation successful
[VERBOSE] Automation server configured successfully
```

#### 🌐 **API Request Layer:**
```
[VERBOSE] /api/execute_automation called
[VERBOSE] Request data: {'prompt': 'go to google.com'}
[VERBOSE] Prompt length: 18 characters
[VERBOSE] Automation server configured: True
[VERBOSE] Browser ready: False
```

#### 🌍 **Browser Initialization Layer:**
```
[VERBOSE] Browser not ready, initializing...
[VERBOSE] Importing BrowserUI from main module...
[VERBOSE] Creating BrowserUI instance...
[VERBOSE] Starting browser with page: https://google.com
[VERBOSE] Browser session ID: 140234567890
[VERBOSE] Browser ready state: True
```

#### ⚡ **Execution Layer:**
```
[VERBOSE] Lock acquired for prompt execution
[VERBOSE] Calling browser.agent.act() with prompt length: 18
[VERBOSE] browser.agent.act() completed successfully
```

#### ✅ **What to look for when it's working:**
```
[VERBOSE] nova_act module imported successfully
[VERBOSE] nova_act version: X.X.X
[VERBOSE] API key validation successful
[VERBOSE] Automation server configured successfully
✓ Automation enabled
[VERBOSE] browser.agent.act() completed successfully
```

#### ❌ **Common Issues and Solutions:**

**Issue 1: Nova Act Module Not Found**
```
[VERBOSE] ERROR: Failed to import nova_act: No module named 'nova_act'
```
**Solution:** Install nova-act package:
```bash
pip install nova-act
# or if using conda:
conda activate nova
pip install nova-act
```

**Issue 2: API Key Validation Failed**
```
⚠️  Invalid API key: [error message]
[VERBOSE] Full validation error: [detailed error]
```
**Solution:**
- Check your API key is correct
- Verify API key has proper permissions
- Check network connectivity to Nova Act service
- Delete config and re-enter: `rm ~/Library/Application\ Support/BrowserAutomation/config.json`

**Issue 3: API Key Not Found**
```
[DEBUG] API key from environment: None
[DEBUG] API key from config: None
⚠️  No API key found - automation disabled
```
**Solution:** Configure API key using one of these methods:
1. Run setup: Delete config file and restart app
2. Set environment variable: `export NOVA_ACT_API_KEY=your_key_here`
3. Manually edit: `~/Library/Application Support/BrowserAutomation/config.json`

**Issue 4: Wrong Python Environment**
```
[VERBOSE] nova_act location: /different/path/than/expected
```
**Solution:** Make sure you're running in the correct Python environment:
```bash
which python
# Should show your conda/venv path

# If wrong, activate environment:
conda activate nova
# or
source venv/bin/activate
```

### 3. Full Debug Mode

For even more detailed logging (including Flask internals):
```bash
python server.py --verbose --debug
```

Or:
```bash
npm run server:debug
```

### 4. Check Browser Console

1. Open the desktop app
2. Press `Cmd+Option+I` (macOS) to open dev tools
3. Check Console tab for JavaScript errors
4. Check Network tab to see if API calls to `/api/execute_automation` are failing

### 5. Common Environment Issues

**macOS Specific:**
- Make sure you're running server with the same Python that has nova-act installed
- Check Python version: `python --version` (should be 3.10+)
- Verify package location: `pip show nova-act`

**Multiple Python Installations:**
```bash
# List all Python installations
which -a python python3

# Check each one for nova-act
python -c "import nova_act; print(nova_act.__file__)"
python3 -c "import nova_act; print(nova_act.__file__)"
```

### 6. Quick Diagnostic Script

Save this as `diagnose.py` and run it:

```python
#!/usr/bin/env python3
import sys
import os

print("Python version:", sys.version)
print("Python executable:", sys.executable)
print()

try:
    import nova_act
    print("✓ nova_act installed")
    print("  Version:", getattr(nova_act, '__version__', 'unknown'))
    print("  Location:", nova_act.__file__)
except ImportError as e:
    print("✗ nova_act NOT installed")
    print("  Error:", e)
print()

try:
    import flask
    print("✓ flask installed")
except ImportError:
    print("✗ flask NOT installed")

try:
    import flask_cors
    print("✓ flask_cors installed")
except ImportError:
    print("✗ flask_cors NOT installed")
print()

config_path = os.path.expanduser("~/Library/Application Support/BrowserAutomation/config.json")
print("Config file path:", config_path)
print("Config exists:", os.path.exists(config_path))
```

Run with:
```bash
python diagnose.py
```

## Still Having Issues?

1. Share the verbose output: `python server.py --verbose 2>&1 | tee server-debug.log`
2. Share diagnostic output: `python diagnose.py > diagnostic.txt`
3. Check if browser automation works with CLI: `python -m src.auto_browser.main`

## Date
Created: 2025-12-18
