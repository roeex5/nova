# Browser Automation UI

A desktop application for browser automation. Control web browsers through natural language commands using a voice interface.

## Features

- **🎙️ Voice Interface**: Hands-free browser control with conversational AI
- **🖥️ Desktop App**: Native macOS application built with Tauri
- **🌐 Web UI**: Browser-based interface for remote access
- **⚡ Natural Language**: Give commands in plain English - no coding required
- **🔄 Session Management**: Continuous automation with persistent browser state

## Setup

### Prerequisites

**Node.js and npm** (required for desktop app):
- Node.js 18+ and npm
- Installation: Download from [nodejs.org](https://nodejs.org/) or use `brew install node` on macOS

**Rust** (required for Tauri desktop app):
- Rust 1.77.2+
- Installation: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Or on macOS: `brew install rust`
- Note: Tauri will prompt to install Rust if it's missing

**Python** (required for backend):
- Python 3.10+

**macOS users**: Additional dependencies for voice input (optional)
```bash
brew install portaudio flac
```

### Python Environment Setup

#### Using Conda (recommended)

```bash
conda create -n nova python=3.10
conda activate nova
pip install -r requirements.txt
```

#### Using venv

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Installing Node Dependencies

After setting up Python, install the Node.js dependencies (including Tauri CLI):

```bash
npm install
```

**Troubleshooting**:

- **"tauri command not found"**: The Tauri CLI should install automatically via `npm install`. If it doesn't work, install globally: `npm install -g @tauri-apps/cli`

- **"Failed to run cargo metadata"**: This means Rust/Cargo isn't properly installed or in your PATH. Fix with:
  ```bash
  # Install Rust (if not already installed)
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

  # Add Cargo to your current shell session
  source $HOME/.cargo/env

  # Verify installation
  cargo --version
  ```
  Then restart your terminal or run `source ~/.zshrc` (or `~/.bashrc` on Linux)

## Configuration

Obtain your API key from your service provider.

Set your API key using one of these methods:
1. Environment variable: Set via your system's environment configuration
2. Command line argument: `--api-key your_key_here`
3. Configuration file: Use the setup dialog in the desktop app
4. Direct parameter when using the API programmatically

## Usage

### Running the Desktop App (Recommended)

The easiest way to use Browser Automation is through the desktop application:

```bash
# Development mode (starts both server and Tauri app)
npm run dev
```

**Note**: The server must be running on port 5000 for the desktop app to work. If you need to run them separately:

```bash
npm run server  # Terminal 1: Start Flask backend
npm run dev     # Terminal 2: Start Tauri desktop app
```

On first launch, you'll be prompted to enter your API key and optional voice agent ID through a setup dialog.

### Running the Web UI

For a browser-based interface:

```bash
# Start the Flask server
npm run server

# Or with verbose logging (for debugging connection issues)
npm run server:verbose

# Or with full debug mode
npm run server:debug

# Then open http://localhost:5000 in your browser
```

**Troubleshooting Connection Issues:**
If the ElevenLabs widget loads but browser automation doesn't work, run with verbose logging:
```bash
python server.py --verbose
```
This will show detailed information about:
- Nova Act module import and version
- API key validation process
- Automation server configuration
- Browser initialization

### Running the CLI (Advanced)

For command-line usage:

```bash
# Basic usage
python -m src.auto_browser.main

# With options
python -m src.auto_browser.main --api-key YOUR_KEY
python -m src.auto_browser.main --starting-page https://amazon.com
python -m src.auto_browser.main --headless  # Run browser in background
```

### Example Commands

Using the desktop app's voice interface, you can give natural language commands such as:
- "Search for Sony M4 headphones and show me the results"
- "Add the second item to my cart"
- "Fill in the shipping address form"
- "Go to amazon.com"
- "Click on the first search result"

For CLI usage, type your commands or use `quit` to exit.

### Example Scripts

See the `examples/` folder for automated script examples:
- `compare_headphones.py` - Product search and shopping cart automation

## Project Structure

```
nova/
├── src-tauri/           # Tauri desktop app (Rust)
│   ├── src/            # Rust source code
│   ├── Cargo.toml      # Rust dependencies
│   └── tauri.conf.json # Tauri configuration
├── src/auto_browser/    # Python backend
│   ├── main.py         # CLI interface
│   ├── web_ui.py       # Flask web server
│   └── config_manager.py # Configuration handling
├── server.py            # Flask server entry point
├── examples/            # Example automation scripts
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
├── BUILD.md            # Build instructions
└── README.md           # This file
```

## How It Works

This UI provides a simple interface for browser automation. Under the hood, it uses a browser automation backend for the actual automation capabilities, but you don't need to worry about the implementation details - just give it commands and it handles the rest.

## License

TBD
