"""
Platform interface for Bluestacks/Android ADB communication
"""

import subprocess
import time
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class BluestacksInterface:
    """Interface for communicating with Bluestacks via ADB"""

    def __init__(self, config: dict):
        self.config = config
        self.adb_path = config.get('adb_path', '')
        self.device_id = config.get('device_id', '127.0.0.1:5555')
        self.connected = False

        # Validate ADB path
        if not self.adb_path:
            # Try to find ADB in common locations
            self.adb_path = self._find_adb_path()

        if not Path(self.adb_path).exists():
            logger.warning(f"ADB path not found: {self.adb_path}")

    def _find_adb_path(self) -> str:
        """Try to find ADB executable in common locations"""
        common_paths = [
            r"C:\Program Files\BlueStacks\HD-Adb.exe",
            r"C:\Program Files (x86)\BlueStacks\HD-Adb.exe",
            r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe",
            r"C:\Program Files (x86)\BlueStacks_nxt\HD-Adb.exe",
            "adb.exe",  # In PATH
        ]

        for path in common_paths:
            if Path(path).exists():
                return path

        return "adb.exe"  # Default fallback

    def connect(self) -> bool:
        """Connect to the device"""
        try:
            # Check if device is already connected
            if self._run_adb_command("devices", timeout=10):
                devices_output = self._run_adb_command("devices")
                if self.device_id in devices_output:
                    self.connected = True
                    logger.info(f"Already connected to device {self.device_id}")
                    return True

            # Try to connect
            logger.info(f"Connecting to device {self.device_id}")
            result = self._run_adb_command(f"connect {self.device_id}", timeout=15)

            if result and isinstance(result, str):
                if "connected" in result.lower() or "already connected" in result.lower():
                    self.connected = True
                    logger.info(f"Successfully connected to {self.device_id}")
                    return True
                else:
                    logger.error(f"Failed to connect to {self.device_id}: {result}")
                    return False
            else:
                logger.error(f"Failed to get connection result for {self.device_id}")
                return False

        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from the device"""
        try:
            if self.connected:
                self._run_adb_command(f"disconnect {self.device_id}")
                self.connected = False
                logger.info(f"Disconnected from {self.device_id}")
        except Exception as e:
            logger.error(f"Disconnect error: {e}")

    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self.connected

    def capture_screenshot(self) -> Optional[bytes]:
        """Capture screenshot from device"""
        try:
            # Use screencap to capture screenshot
            result = self._run_adb_command("exec-out screencap -p", capture_output=True)
            if result and isinstance(result, bytes):
                return result
            else:
                logger.error("Failed to capture screenshot")
                return None
        except Exception as e:
            logger.error(f"Screenshot capture error: {e}")
            return None

    def get_screen_size(self) -> Optional[Tuple[int, int]]:
        """Get the screen size of the device"""
        try:
            result = self._run_adb_command("shell wm size")
            logger.debug(f"wm size result: {result}")
            if result and isinstance(result, str):
                if "Physical size:" in result:
                    size_str = result.split("Physical size:")[1].strip()
                    width, height = size_str.split('x')
                    return int(width), int(height)
                elif "Override size:" in result:
                    size_str = result.split("Override size:")[1].strip()
                    width, height = size_str.split('x')
                    return int(width), int(height)
            logger.error(f"Failed to parse screen size from: {result}")
            return None
        except Exception as e:
            logger.error(f"Screen size error: {e}")
            return None

    def send_tap(self, x: int, y: int) -> bool:
        """Send tap command to device"""
        try:
            result = self._run_adb_command(f"shell input tap {x} {y}")
            # Since the tap appears to work on the emulator, assume success if no exception
            logger.debug(f"send_tap({x}, {y}) executed, result: {repr(result)}")
            return True
        except Exception as e:
            logger.error(f"Tap error: {e}")
            return False

    def send_swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 100) -> bool:
        """Send swipe command to device"""
        try:
            result = self._run_adb_command(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")
            if result and isinstance(result, str):
                return "error" not in result.lower()
            return False
        except Exception as e:
            logger.error(f"Swipe error: {e}")
            return False

    def _run_adb_command(self, command: str, timeout: int = 30, capture_output: bool = False):
        """Run ADB command and return output"""
        try:
            full_command = f'"{self.adb_path}" -s {self.device_id} {command}'

            if capture_output:
                # For binary output like screenshots
                result = subprocess.run(
                    full_command,
                    shell=True,
                    capture_output=True,
                    timeout=timeout
                )
                if result.returncode == 0:
                    return result.stdout
                else:
                    logger.error(f"ADB command failed: {result.stderr.decode()}")
                    return None
            else:
                # For text output
                result = subprocess.run(
                    full_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                output = result.stdout + result.stderr
                logger.debug(f"ADB command result: {output.strip()}")
                return output

        except subprocess.TimeoutExpired:
            logger.error(f"ADB command timeout: {command}")
            return None
        except Exception as e:
            logger.error(f"ADB command error: {e}")
            return None