#!/usr/bin/env python3
"""
Standalone Flask server for Browser Automation.
This script is spawned by the Tauri app.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auto_browser.web_ui import app, automation_server
from auto_browser.config_manager import ConfigManager


def main():
    """Start Flask server"""
    # Get API key from config or environment
    api_key = os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        api_key = ConfigManager.get_api_key()

    # Get agent ID
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')
    if not agent_id:
        agent_id = ConfigManager.get_agent_id()
        if agent_id:
            os.environ['ELEVENLABS_AGENT_ID'] = agent_id

    # Configure automation
    if api_key:
        automation_server.configure(
            api_key=api_key,
            starting_page="https://google.com",
            headless=False
        )
        print("✓ Automation enabled")
    else:
        print("⚠️  No API key found - automation disabled")
        print("   Configure via setup or set NOVA_ACT_API_KEY environment variable")

    # Start Flask server
    print(f"\nStarting Flask server on http://127.0.0.1:5000")
    print("="*80 + "\n")

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False  # Important: disable reloader for subprocess
    )


if __name__ == '__main__':
    main()
