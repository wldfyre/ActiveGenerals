"""
Configuration management for Evony Active Generals Tracker
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration"""

    DEFAULT_CONFIG = {
        "platform_type": "bluestacks",
        "adb_path": "",
        "device_id": "127.0.0.1:5555",
        "ocr_engine": "easyocr",
        "confidence_threshold": 0.8,
        "preprocessing_enabled": True,
        "ocr_languages": ["en"],
        "screen_transition_delay": 0.5,
        "navigation_retry_count": 3,
        "screenshot_scale": 1.0,
        "default_export_path": "~/Documents/Evony",
        "excel_template_path": "Resources/EvonyActiveGenerals.xltx",
        "auto_open_excel": False,
        "debug_mode": False,
        "log_level": "INFO"
    }

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(__file__).parent.parent / config_file
        self._config = self.DEFAULT_CONFIG.copy()

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