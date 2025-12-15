#!/usr/bin/env python3
"""
Voice-Controlled Browser Automation

A hands-free browser automation tool that listens for wake word commands
and executes them using the browser automation service.

Usage:
    python test_voice_browser.py [--api-key KEY] [--device INDEX]

The script will:
1. Start a browser automation session
2. Continuously listen for the wake word "Hey Browser"
3. When detected, capture your command via speech-to-text
4. Execute the command in the browser
5. Return to listening for the next wake word

Commands:
- Say "Hey Browser" followed by your command (e.g., "Hey Browser, search for Python tutorials")
- Or say "Hey Browser" and wait for the prompt, then say your command
- Press Ctrl+C to exit
"""

import sys
import os
import argparse
import queue
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auto_browser.main import BrowserUI
from auto_browser.wake_word_lite import LightweightWakeWordListener, SpeechToText


def main():
    """Main entry point for voice-controlled browser automation"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Voice-controlled browser automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--api-key',
        help='API key for automation service (or set NOVA_ACT_API_KEY env var)'
    )
    parser.add_argument(
        '--device',
        type=int,
        default=None,
        help='Microphone device index (run test_microphone.py to see available devices)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--starting-page',
        default='https://google.com',
        help='Starting page URL (default: https://google.com)'
    )

    args = parser.parse_args()

    # Initialize browser automation
    print("\n" + "="*60)
    print("Voice-Controlled Browser Automation")
    print("="*60)

    # Check API key
    api_key = args.api_key or os.getenv('NOVA_ACT_API_KEY')
    if not api_key:
        print("\nError: No API key provided!")
        print("Set NOVA_ACT_API_KEY environment variable or use --api-key")
        sys.exit(1)

    # Show microphone info with diagnostics
    print("\n" + "-"*60)
    print("Microphone Configuration:")
    print("-"*60)

    if args.device is not None:
        print(f"Using specified device: {args.device}")

        # Show device details
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            device_info = p.get_device_info_by_index(args.device)
            print(f"  Device name: {device_info['name']}")
            print(f"  Sample rate: {device_info['defaultSampleRate']}")
            print(f"  Channels: {device_info['maxInputChannels']}")
            p.terminate()
        except Exception as e:
            print(f"  Warning: Could not get device details: {e}")
    else:
        print("Using default microphone device")
        print("(Use --device <index> to select a different microphone)")

        # Show default device
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            default_info = p.get_default_input_device_info()
            print(f"  Default device: [{default_info['index']}] {default_info['name']}")
            p.terminate()
        except Exception as e:
            print(f"  Warning: Could not get default device info: {e}")

    print("-"*60)

    print("\nStarting browser session...")

    # Initialize browser UI
    browser = BrowserUI(api_key=api_key, headless=args.headless)

    try:
        # Start browser session
        browser.start(starting_page=args.starting_page)

        print("\n" + "-"*60)
        print("Voice Assistant Ready!")
        print("-"*60)
        print("\nSay 'Hey Browser' followed by your command")
        print("Examples:")
        print("  - 'Hey Browser, search for Python tutorials'")
        print("  - 'Hey Browser, go to wikipedia.org'")
        print("  - 'Hey Browser, click on the first link'")
        print("\nPress Ctrl+C to exit")
        print("-"*60 + "\n")

        # Command queue for thread-safe communication
        command_queue = queue.Queue()

        # Voice command handler (runs in background thread)
        def on_wake_word():
            """Handle wake word detection - runs in background thread"""
            print("\n🎤 Wake word detected! Listening for command...")

            # Capture command using speech-to-text
            stt = SpeechToText(service='google', device_index=args.device)
            command = stt.recognize(timeout=10, phrase_time_limit=15)

            if command:
                print(f"\n✓ Command: '{command}'")
                # Put command in queue for main thread to execute
                command_queue.put(command)
            else:
                print("\n✗ No command recognized")
                print("Listening for next command...\n")

        # Start wake word listener
        listener = LightweightWakeWordListener(
            wake_phrase="hey browser",
            callback=on_wake_word,
            device_index=args.device
        )

        listener.start()

        # Main loop - execute commands from queue in main thread
        try:
            while True:
                try:
                    # Check for commands from wake word listener (non-blocking)
                    command = command_queue.get(timeout=0.1)

                    print("Executing...\n")
                    try:
                        # Execute command with Nova Act (must run in main thread)
                        browser.agent.act(command)
                        print("\n✓ Done! Listening for next command...\n")
                    except Exception as e:
                        print(f"\n✗ Error executing command: {e}\n")
                        print("Listening for next command...\n")

                except queue.Empty:
                    # No command available, continue waiting
                    pass

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\nStopping...")
        finally:
            listener.stop()

    finally:
        # Clean up
        print("Closing browser session...")
        browser.stop()
        print("\nGoodbye!")


if __name__ == '__main__':
    main()
