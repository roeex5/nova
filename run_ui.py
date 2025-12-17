#!/usr/bin/env python3
"""
Launch script for the browser automation web UI.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auto_browser.web_ui import run_ui

if __name__ == '__main__':
    # You can set the agent ID via environment variable
    # export ELEVENLABS_AGENT_ID=your_agent_id
    run_ui()
