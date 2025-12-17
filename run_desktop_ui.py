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
        description="Browser Automation Desktop UI with Voice Interface and Nova Act Integration"
    )
    parser.add_argument(
        '--api-key',
        help='Nova Act API key (or set NOVA_ACT_API_KEY env var) - REQUIRED for automation'
    )
    parser.add_argument(
        '--agent-id',
        help='ElevenLabs Agent ID (or set ELEVENLABS_AGENT_ID env var)'
    )
    parser.add_argument(
        '--starting-page',
        default='https://google.com',
        help='Initial browser page (default: https://google.com)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
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
        f'--unsafely-treat-insecure-origin-as-secure=http://{args.host}:{args.port}',
        '--use-fake-ui-for-media-stream',  # Auto-grant media permissions
        '--allow-running-insecure-content'
    ]

    if args.disable_web_security:
        print("\n⚠️  WARNING: Web security disabled (development mode only)")
        chromium_flags.append('--disable-web-security')

    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = ' '.join(chromium_flags)
    print(f"\n[Chromium Flags] {os.environ['QTWEBENGINE_CHROMIUM_FLAGS']}\n")

    # Get API key
    api_key = args.api_key or os.getenv('NOVA_ACT_API_KEY')

    # Set ElevenLabs agent ID if provided
    if args.agent_id:
        os.environ['ELEVENLABS_AGENT_ID'] = args.agent_id

    # NOW import Qt (after setting environment variables)
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from auto_browser.desktop_app import run_desktop_app

    # Show configuration
    print("\n" + "="*80)
    print("Configuration")
    print("="*80)

    if api_key:
        print(f"✓ Nova Act API Key: Provided")
    else:
        print(f"✗ Nova Act API Key: NOT provided")
        print(f"  Automation will be disabled!")

    agent_id = os.getenv('ELEVENLABS_AGENT_ID')
    if agent_id:
        print(f"✓ ElevenLabs Agent ID: {agent_id}")
    else:
        print(f"ℹ ElevenLabs Agent ID: Using default")

    print(f"  Starting page: {args.starting_page}")
    print(f"  Headless mode: {args.headless}")
    print(f"  Server: {args.host}:{args.port}")
    print("="*80 + "\n")

    # Launch desktop app
    run_desktop_app(
        api_key=api_key,
        starting_page=args.starting_page,
        headless=args.headless,
        host=args.host,
        port=args.port
    )


if __name__ == '__main__':
    main()
