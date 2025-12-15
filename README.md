# Browser Automation UI

A simple, interactive UI for browser automation. Control web browsers through natural language commands using text or voice input.

## Features

- **Text Input**: Type commands in natural language to automate browser tasks
- **Voice Input**: Hands-free operation with speech recognition
- **Interactive Sessions**: Continuous command loop - give multiple commands in one session
- **Simple & Focused**: Clean CLI interface without unnecessary complexity

## Setup

### Prerequisites

**macOS users**: Install PortAudio and FLAC (required for voice input)
```bash
brew install portaudio flac
```

### Using Conda (recommended)

```bash
conda create -n nova python=3.10
conda activate nova
pip install -r requirements.txt
```

### Using venv

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Get your API key from https://nova.amazon.com/act

Set your API key using one of these methods:
1. Environment variable: `export NOVA_ACT_API_KEY=your_key_here`
2. Command line argument: `--api-key your_key_here`
3. Direct parameter when using the API programmatically

## Usage

### Running the Interactive UI

```bash
# Basic usage
python -m src.auto_browser.main

# With options
python -m src.auto_browser.main --api-key YOUR_KEY
python -m src.auto_browser.main --starting-page https://amazon.com
python -m src.auto_browser.main --headless  # Run browser in background
```

### Example Commands

Once the interactive session starts, you can give natural language commands:
- "Search for Sony M4 headphones and show me the results"
- "Add the second item to my cart"
- "Fill in the shipping address form"
- Type `voice` to switch to voice input mode
- Type `quit` to exit

### Voice-Controlled Mode (Hands-Free)

For completely hands-free operation with wake word detection:

```bash
# Basic usage
python test_voice_browser.py

# With specific microphone (useful when laptop lid is closed)
python test_voice_browser.py --device 3

# With custom starting page
python test_voice_browser.py --starting-page https://amazon.com
```

Once started, simply say "Hey Browser" followed by your command:
- "Hey Browser, search for Python tutorials"
- "Hey Browser, go to wikipedia.org"
- "Hey Browser, click on the first link"

The system will continuously listen for the wake word, execute commands, and return to listening mode automatically.

### Example Scripts

See the `examples/` folder for automated script examples:
- `compare_headphones.py` - Product search and shopping cart automation

## Project Structure

```
nova/
├── examples/          # Example automation scripts
├── src/auto_browser/  # Main application source code
├── tests/             # Unit tests
├── requirements.txt   # Python dependencies
├── CLAUDE.md          # Development guidelines
└── README.md          # This file
```

## How It Works

This UI provides a simple interface for browser automation. Under the hood, it uses the Amazon Nova Act SDK for the actual automation capabilities, but you don't need to worry about the implementation details - just give it commands and it handles the rest.

## License

TBD
