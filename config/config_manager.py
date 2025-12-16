"""
Configuration management for Evony Active Generals Tracker
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

from utils.resource_manager import get_default_config

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(__file__).parent.parent / config_file
        # Use embedded defaults instead of hardcoded dict
        self._config = get_default_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._config.update(loaded_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info("Configuration file not found, using embedded defaults")
                # Don't create config file automatically in bundled mode
                if not getattr(__import__('sys'), '_MEIPASS', None):
                    self.save_config()  # Create default config file only in development
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Reset to embedded defaults on error
            self._config = get_default_config()

        return self._config.copy()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._config.update(loaded_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.warning(f"Configuration file {self.config_file} not found, using defaults")
                self.save_config()  # Create default config file
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._config = self.DEFAULT_CONFIG.copy()

        return self._config.copy()

    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def get(self, key: str, default=None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self._config.update(updates)