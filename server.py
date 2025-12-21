#!/usr/bin/env python3
"""
Standalone Flask server for Browser Automation.
This script is spawned by the Tauri app.
"""

import sys
import os
import signal
import subprocess
import argparse
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auto_browser.web_ui import app, automation_server
from auto_browser.config_manager import ConfigManager


def cleanup_port(port=5555):
    """Kill any processes using the specified port (only if it's a Python/Flask process)"""
    try:
        # Use lsof to find process details using the port
        result = subprocess.run(
            ['lsof', '-i', f':{port}', '-sTCP:LISTEN'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    command = parts[0]
                    pid = parts[1]

                    # Only kill if it's a Python process (likely our server)
                    if command.lower().startswith('python'):
                        try:
                            pid = int(pid)
                            print(f"[CLEANUP] Found hanging Python process on port {port} (PID: {pid}), killing it...")
                            os.kill(pid, signal.SIGTERM)
                            print(f"[CLEANUP] Successfully killed process {pid}")
                        except (ValueError, ProcessLookupError) as e:
                            print(f"[CLEANUP] Could not kill process {pid}: {e}")
                    else:
                        print(f"[CLEANUP] WARNING: Port {port} is in use by '{command}' (PID: {pid})")
                        print(f"[CLEANUP] This doesn't appear to be our server. Skipping cleanup.")
                        print(f"[CLEANUP] You may need to:")
                        print(f"           - Stop that process manually")
                        print(f"           - Use a different port")
                        print(f"           - Disable AirPlay Receiver in System Settings if it's the culprit")
    except FileNotFoundError:
        # lsof not available (unlikely on macOS, but handle gracefully)
        pass
    except Exception as e:
        print(f"[CLEANUP] Error during port cleanup: {e}")


def main():
    """Start Flask server"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Browser Automation Flask Server')
    parser.add_argument('--port', '-p', type=int, default=5555,
                       help='Port to run the server on (default: 5555)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging for debugging Nova Act connection')
    parser.add_argument('--debug', action='store_true',
                       help='Enable Flask debug mode')
    args = parser.parse_args()

    # Setup logging based on verbose flag
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(levelname)s] %(name)s: %(message)s'
        )
        # Enable Nova Act SDK logging if it has a logger
        logging.getLogger('nova_act').setLevel(logging.DEBUG)
        logging.getLogger('selenium').setLevel(logging.DEBUG)
        print("\n" + "="*80)
        print("VERBOSE MODE ENABLED - Detailed Nova Act debugging")
        print("="*80 + "\n")

    print("\n[DEBUG] Starting server initialization...")
    print(f"[DEBUG] Config file exists: {ConfigManager.config_exists()}")
    print(f"[DEBUG] Config file path: {ConfigManager.CONFIG_FILE}")

    # Get API key from config or environment
    api_key = os.getenv('NOVA_ACT_API_KEY')  # Internal env var name
    print(f"[DEBUG] API key from environment: {('***' + api_key[-4:]) if api_key else 'None'}")

    if not api_key:
        api_key = ConfigManager.get_api_key()
        print(f"[DEBUG] API key from config: {('***' + api_key[-4:]) if api_key else 'None'}")

    if args.verbose and api_key:
        # Only show last 4 chars for security (don't expose first 8 chars)
        print(f"[VERBOSE] API key present: ***{api_key[-4:]}")
        print(f"[VERBOSE] API key length: {len(api_key)} characters")

    # Get agent ID
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')
    if not agent_id:
        agent_id = ConfigManager.get_agent_id()
        if agent_id:
            os.environ['ELEVENLABS_AGENT_ID'] = agent_id

    print(f"[DEBUG] automation_server.is_configured BEFORE configure: {automation_server.is_configured}")

    # Clean up any hanging processes on the port we're going to use
    cleanup_port(args.port)

    # Set verbose mode in environment for web_ui to pick up
    if args.verbose:
        os.environ['VERBOSE'] = 'true'

    # Validate and configure automation
    if api_key:
        print("[DEBUG] Validating API key...")
        if args.verbose:
            print("[VERBOSE] Attempting to import nova_act module...")
            try:
                import nova_act
                print(f"[VERBOSE] nova_act module imported successfully")
                print(f"[VERBOSE] nova_act version: {getattr(nova_act, '__version__', 'unknown')}")
                print(f"[VERBOSE] nova_act location: {nova_act.__file__}")
            except ImportError as e:
                print(f"[VERBOSE] ERROR: Failed to import nova_act: {e}")

        is_valid, error_msg = ConfigManager.validate_api_key(api_key)

        if is_valid:
            if args.verbose:
                print("[VERBOSE] API key validation successful")
                print("[VERBOSE] Configuring automation server...")

            automation_server.configure(
                api_key=api_key,
                starting_page="https://google.com",
                headless=False
            )
            print(f"[DEBUG] automation_server.is_configured AFTER configure: {automation_server.is_configured}")
            print("✓ Automation enabled")

            if args.verbose:
                print("[VERBOSE] Automation server configured successfully")
                print("[VERBOSE] Browser will initialize on first automation command (lazy init)")
        else:
            print(f"[DEBUG] API key validation failed: {error_msg}")
            print(f"⚠️  Invalid API key: {error_msg}")
            print("   Please update your configuration with a valid API key")
            if args.verbose:
                print(f"[VERBOSE] Full validation error: {error_msg}")
            # Leave automation_server.is_configured as False
    else:
        print(f"[DEBUG] No API key found, automation_server.is_configured: {automation_server.is_configured}")
        print("⚠️  No API key found - automation disabled")
        print("   Configure via setup or set API key in configuration")

    # Start Flask server
    print(f"\nStarting Flask server on http://127.0.0.1:{args.port}")
    if args.verbose:
        print("[VERBOSE] Flask debug mode:", "ENABLED" if args.debug else "DISABLED")
        print("[VERBOSE] Flask threading mode: DISABLED (single-threaded for Selenium compatibility)")
    print("="*80 + "\n")

    app.run(
        host='127.0.0.1',
        port=args.port,
        debug=args.debug,
        threaded=False,  # CRITICAL: Selenium WebDriver is NOT thread-safe - must use single thread
        use_reloader=False  # Important: disable reloader for subprocess
    )


if __name__ == '__main__':
    main()
