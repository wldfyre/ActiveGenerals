"""
Resource management for embedded files in PyInstaller bundles
"""

import sys
import os
from pathlib import Path
from typing import Union, Optional
import json
import base64
import logging

logger = logging.getLogger(__name__)

class ResourceManager:
    """Manages access to application resources, both in development and bundled environments"""

    def __init__(self):
        self._bundle_path = None
        self._is_bundled = getattr(sys, '_MEIPASS', None) is not None

        if self._is_bundled:
            self._bundle_path = Path(sys._MEIPASS)
            logger.info(f"Running in bundled mode, resources at: {self._bundle_path}")
        else:
            # Development mode - use project root
            self._bundle_path = Path(__file__).parent.parent
            logger.info(f"Running in development mode, resources at: {self._bundle_path}")

    def get_resource_path(self, relative_path: Union[str, Path]) -> Path:
        """Get the absolute path to a resource file"""
        return self._bundle_path / relative_path

    def resource_exists(self, relative_path: Union[str, Path]) -> bool:
        """Check if a resource file exists"""
        return self.get_resource_path(relative_path).exists()

    def read_resource_text(self, relative_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
        """Read a text resource file"""
        try:
            resource_path = self.get_resource_path(relative_path)
            if resource_path.exists():
                return resource_path.read_text(encoding=encoding)
            else:
                logger.warning(f"Resource not found: {relative_path}")
                return None
        except Exception as e:
            logger.error(f"Error reading resource {relative_path}: {e}")
            return None

    def read_resource_bytes(self, relative_path: Union[str, Path]) -> Optional[bytes]:
        """Read a binary resource file"""
        try:
            resource_path = self.get_resource_path(relative_path)
            if resource_path.exists():
                return resource_path.read_bytes()
            else:
                logger.warning(f"Resource not found: {relative_path}")
                return None
        except Exception as e:
            logger.error(f"Error reading resource {relative_path}: {e}")
            return None

# Global resource manager instance
resource_manager = ResourceManager()

# Embedded default configuration
DEFAULT_CONFIG_JSON = """
{
    "platform_type": "bluestacks",
    "adb_path": "",
    "device_id": "127.0.0.1:5555",
    "ocr_engine": "easyocr",
    "confidence_threshold": 0.8,
    "postprocessed_confidence_threshold": 0.4,
    "preprocessing_enabled": true,
    "character_recognition_enhancement": true,
    "ocr_languages": ["en"],
    "screen_transition_delay": 0.5,
    "navigation_retry_count": 3,
    "screenshot_scale": 1.0,
    "default_export_path": "~/Documents/Evony",
    "excel_template_path": "Resources/EvonyActiveGenerals.xltx",
    "auto_open_excel": false,
    "debug_mode": false,
    "log_level": "INFO"
}
"""

def get_default_config() -> dict:
    """Get the embedded default configuration"""
    try:
        return json.loads(DEFAULT_CONFIG_JSON)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing embedded config: {e}")
        return {}

def load_config_with_fallback() -> dict:
    """Load configuration with embedded defaults as fallback"""
    config = get_default_config()

    # Try to load from file if it exists (for development or user customization)
    config_file = Path("config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                config.update(user_config)
            logger.info("User configuration loaded and merged with defaults")
        except Exception as e:
            logger.warning(f"Could not load user config, using defaults: {e}")

    return config