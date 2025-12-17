"""Main entry point for Browser Automation UI"""

import os
from pathlib import Path
from nova_act import NovaAct


class BrowserUI:
    """Simple UI for browser automation"""

    def __init__(self, api_key=None, headless=False):
        """
        Initialize Browser UI

        Args:
            api_key: API key for the automation service (if not provided, uses NOVA_ACT_API_KEY env var)
            headless: Whether to run browser in headless mode
        """
        self.api_key = api_key or os.getenv("NOVA_ACT_API_KEY")
        self.headless = headless
        self.agent = None  # Internal: uses Nova Act

    def start(self, starting_page="https://google.com"):
        """Start browser automation session"""
        if not self.api_key:
            raise ValueError(
                "API key not provided. Set NOVA_ACT_API_KEY environment variable "
                "or pass api_key to constructor"
            )

        # Enable browser debugging (for development)
        os.environ["NOVA_ACT_BROWSER_ARGS"] = "--remote-debugging-port=9222"

        # Set up persistent user data directory for stateful browser sessions
        user_data_dir = Path.home() / "Library" / "Application Support" / "BrowserAutomation" / "user_data_dir"
        user_data_dir.mkdir(parents=True, exist_ok=True)

        # Internal: Initialize Nova Act agent with statefulness
        self.agent = NovaAct(
            starting_page=starting_page,
            headless=self.headless,
            tty=True,
            nova_act_api_key=self.api_key,
            user_data_dir=str(user_data_dir),
            clone_user_data_dir=False  # Use persistent directory for cookies/auth
        )
        self.agent.start()
        print(f"Browser session started at {starting_page}")

    def run_interactive(self):
        """Run interactive prompt loop"""
        if not self.agent:
            self.start()

        print("\n=== Browser Automation Interactive Mode ===")
        print("Enter your commands (or 'quit' to exit, 'voice' for voice input)\n")

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Stopping browser session...")
                    break

                if user_input.lower() == 'voice':
                    from .voice import get_voice_input
                    print("\n[Voice mode - speak your command]")
                    voice_text = get_voice_input()
                    if voice_text:
                        print(f"Heard: {voice_text}")
                        user_input = voice_text
                    else:
                        print("No voice input detected. Try again.")
                        continue

                if not user_input:
                    continue

                print(f"\nExecuting: {user_input}")
                self.agent.act(user_input)
                print("Done!")

            except KeyboardInterrupt:
                print("\nInterrupted. Stopping...")
                break
            except Exception as e:
                print(f"Error: {e}")

        self.stop()

    def stop(self):
        """Stop browser automation session"""
        if self.agent:
            self.agent.stop()
            print("Browser session stopped.")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Browser Automation UI")
    parser.add_argument(
        "--api-key",
        help="API key for automation service (or set NOVA_ACT_API_KEY env var)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--starting-page",
        default="https://google.com",
        help="Starting page URL (default: https://google.com)"
    )

    args = parser.parse_args()

    ui = BrowserUI(api_key=args.api_key, headless=args.headless)
    ui.start(starting_page=args.starting_page)
    ui.run_interactive()


if __name__ == "__main__":
    main()
