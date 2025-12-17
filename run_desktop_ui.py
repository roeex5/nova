#!/usr/bin/env python3
"""
Launch script for the browser automation desktop UI.
Embeds Flask server in PyQt6 window with ElevenLabs voice interface.

Phase 0: Tests ElevenLabs integration without Nova Act backend.
"""

import sys
import os
import argparse


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Browser Automation Desktop UI with Voice Interface (Phase 0)"
    )
    parser.add_argument(
        '--agent-id',
        help='ElevenLabs Agent ID (or set ELEVENLABS_AGENT_ID env var)'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Flask server host (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Flask server port (default: 5000)'
    )
    parser.add_argument(
        '--disable-web-security',
        action='store_true',
        help='Disable web security (for debugging WebSocket issues)'
    )

    args = parser.parse_args()

    # Set Chromium flags to allow microphone access from localhost
    # IMPORTANT: Must be set BEFORE importing Qt
    chromium_flags = [
        '--unsafely-treat-insecure-origin-as-secure=http://127.0.0.1:5000',
        '--use-fake-ui-for-media-stream',  # Auto-grant media permissions
        '--allow-running-insecure-content'
    ]

    if args.disable_web_security:
        print("\n⚠️  WARNING: Web security disabled (development mode only)")
        chromium_flags.append('--disable-web-security')

    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = ' '.join(chromium_flags)
    print(f"\n[Chromium Flags] {os.environ['QTWEBENGINE_CHROMIUM_FLAGS']}\n")

    # Set ElevenLabs agent ID if provided
    if args.agent_id:
        os.environ['ELEVENLABS_AGENT_ID'] = args.agent_id

    # NOW import Qt (after setting environment variables)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from auto_browser.desktop_app import run_desktop_app

    # Check if agent ID is set
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')
    if agent_id:
        print(f"\nUsing ElevenLabs Agent ID: {agent_id}")
    else:
        print("\nNote: Using default ElevenLabs Agent ID from web_ui.py")
        print("Set ELEVENLABS_AGENT_ID environment variable or use --agent-id to override\n")

    # Launch desktop app
    run_desktop_app(
        host=args.host,
        port=args.port
    )


if __name__ == '__main__':
    main()
