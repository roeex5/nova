"""
Configuration manager for Browser Automation Desktop App.
Handles API key storage and retrieval with security best practices.

Created: 2025-12-17
Modified: 2025-12-17
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Tuple


class ConfigManager:
    """Manages application configuration and API keys"""

    # macOS standard location for app config
    CONFIG_DIR = Path.home() / "Library" / "Application Support" / "BrowserAutomation"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get configuration directory, creating if needed"""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        return cls.CONFIG_DIR

    @classmethod
    def config_exists(cls) -> bool:
        """Check if configuration file exists"""
        return cls.CONFIG_FILE.exists()

    @classmethod
    def load_config(cls) -> Dict[str, str]:
        """Load configuration from file"""
        if not cls.config_exists():
            return {}

        try:
            with open(cls.CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    @classmethod
    def save_config(cls, config: Dict[str, str]) -> bool:
        """Save configuration to file"""
        try:
            cls.get_config_dir()  # Ensure directory exists
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)

            # Set restrictive permissions (owner read/write only)
            os.chmod(cls.CONFIG_FILE, 0o600)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Get Nova Act API key from config or environment"""
        # Priority: environment variable > config file
        env_key = os.getenv('NOVA_ACT_API_KEY')
        if env_key:
            return env_key

        config = cls.load_config()
        return config.get('nova_act_api_key')

    @classmethod
    def get_agent_id(cls) -> Optional[str]:
        """Get ElevenLabs Agent ID from config or environment"""
        # Priority: environment variable > config file
        env_id = os.getenv('ELEVENLABS_AGENT_ID')
        if env_id:
            return env_id

        config = cls.load_config()
        return config.get('elevenlabs_agent_id')

    @classmethod
    def clear_config(cls) -> bool:
        """Remove configuration file"""
        try:
            if cls.config_exists():
                cls.CONFIG_FILE.unlink()
            return True
        except Exception as e:
            print(f"Error clearing config: {e}")
            return False

    @staticmethod
    def validate_api_key(api_key: str) -> Tuple[bool, str]:
        """
        Validate API key by testing it with a simple operation.

        Args:
            api_key: API key to validate

        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, error_message) if invalid
        """
        if not api_key or len(api_key) < 10:
            return False, "API key is too short or empty"

        test_agent = None
        try:
            # Quick validation: try to initialize NovaAct with the key
            from nova_act import NovaAct

            # Create a temporary headless instance for validation
            # We'll just initialize it without starting the browser
            test_agent = NovaAct(
                starting_page="https://google.com",
                headless=True,
                tty=False,
                nova_act_api_key=api_key
            )

            # If we got here, the key format is valid
            # Note: This doesn't start the browser, just validates the key format
            return True, ""

        except Exception as e:
            error_msg = str(e)
            if "api" in error_msg.lower() or "key" in error_msg.lower() or "auth" in error_msg.lower():
                return False, "Invalid API key - please check and try again"
            else:
                return False, f"Validation error: {error_msg}"
        finally:
            # Ensure proper cleanup of NovaAct instance
            if test_agent is not None:
                try:
                    # Stop the agent if it was started (defensive cleanup)
                    if hasattr(test_agent, 'stop'):
                        test_agent.stop()
                except Exception:
                    # Ignore cleanup errors - agent might not have been started
                    pass
