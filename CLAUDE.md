# Project: Browser Automation UI

## Overview
This project provides a simple UI for browser automation powered by Amazon Nova Act SDK (backend only - not exposed to users).

## Key Principles

### Branding
- **IMPORTANT**: The UI must be completely generic and NOT mention "Nova" anywhere in user-facing text
- Users should not be aware that we're using Nova Act as the backend
- Internal code comments and variable names can reference Nova Act for clarity
- User sees: "Browser Automation UI" or similar generic terms

### Architecture
- **Backend**: Amazon Nova Act SDK (nova-act package)
- **Frontend**: Simple CLI-based interactive UI
- **Input Methods**: Text and voice (using SpeechRecognition)
- **Session Management**: Continuous prompt loop allowing multiple commands per session

### Dependencies
- Primary environment: Conda environment named "nova"
- Alternative: venv or other Python package managers
- All dependencies in `requirements.txt`

## Project Structure

```
nova/
├── src/auto_browser/    # Main application (generic name, no "nova" in public code)
│   ├── main.py          # Interactive UI and session management
│   └── voice.py         # Voice input handler
├── examples/            # Example scripts showing capabilities
├── tests/               # Unit tests
└── requirements.txt     # Python dependencies
```

## Development Guidelines

1. **User-Facing Text**: Never mention Nova, use generic terms like "browser automation", "agent", "session"
2. **API Key Management**: Support multiple methods (env var, direct parameter, config file)
3. **Error Handling**: Provide helpful, generic error messages
4. **Voice Input**: Keep implementation simple, optional, and easy to enable/disable
5. **Browser Debugging**: Enabled by default on port 9222 for development

## Common Tasks

### Adding New Features
- Keep UI simple and focused on prompt input/output loop
- Any new user-facing messages must use generic terminology
- Test with both text and voice input if applicable

### Testing
- Place example scripts in `examples/` folder
- Unit tests go in `tests/` folder
- Each example should be self-contained and documented

### Documentation
- README.md: Generic, user-facing documentation
- This file (CLAUDE.md): Internal development guidelines
- Code comments: Can reference Nova Act for clarity

## API Key Setup
Users can provide API key via:
1. Environment variable: `NOVA_ACT_API_KEY`
2. Command line argument: `--api-key`
3. Direct parameter in code

## Notes
- Browser debugging port: 9222 (for development/troubleshooting)
- Default starting page: https://google.com
- Voice recognition: Google Speech Recognition (free tier)
