# Browser Automation Examples

This folder contains example scripts demonstrating various browser automation capabilities.

## Available Examples

### compare_headphones.py

Demonstrates browser automation for e-commerce tasks:
- Searching for products (Sony M4 headphones)
- Finding specific items (second cheapest)
- Adding items to cart
- Filling out billing information

**Usage:**
```bash
# Make sure to set your API key in the file first
python examples/compare_headphones.py
```

**Note:** Remember to replace `"fill this in"` with your actual API key from https://nova.amazon.com/act

## Running Examples

All examples can be run directly with Python:

```bash
python examples/<example_name>.py
```

Make sure you have:
1. Installed all dependencies: `pip install -r requirements.txt`
2. Set your API key (either in the script or via `NOVA_ACT_API_KEY` environment variable)
