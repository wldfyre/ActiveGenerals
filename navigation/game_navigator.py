"""
Game Navigator for automating Evony interface navigation

Uses locations.xml from the global EvonyTools directory for coordinate presets.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
from xml.etree import ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class GameNavigator:
    """Handles navigation through Evony's game interface"""

    def __init__(self, platform, ocr_engine, config: Dict[str, Any]):
        self.platform = platform
        self.ocr_engine = ocr_engine
        self.config = config

        # Load coordinate presets
        self.coordinates = self._load_coordinates()

        # Get screen size for coordinate scaling
        detected_size = self.platform.get_screen_size()
        if detected_size:
            logger.info(f"Detected screen size: {detected_size[0]}x{detected_size[1]}")
            self.screen_size = detected_size
        else:
            logger.warning("Failed to detect screen size, using 540x960")
            self.screen_size = (540, 960)

        # Navigation settings
        self.transition_delay = config.get('screen_transition_delay', 1.5)
        self.retry_count = config.get('navigation_retry_count', 3)

        # State tracking
        self.state_change_flags = {
            'mode': False,
            'favorites': False,
            'idle': False
        }

    def _load_coordinates(self) -> Dict[str, Dict[str, float]]:
        """Load coordinate presets from XML file"""
        coordinates = {}

        try:
            # Use the global locations.xml file from parent directory
            location_file = Path(__file__).parent.parent.parent / "locations.xml"

            if not location_file.exists():
                logger.error(f"Location XML file not found: {location_file}")
                return coordinates

            # Parse the XML file
            tree = ET.parse(location_file)
            root = tree.getroot()

            # Parse preset elements
            for preset in root.findall('.//preset'):
                try:
                    preset_name = preset.get('name')
                    if not preset_name:
                        continue

                    preset_data = {'name': preset_name}

                    # Extract coordinate attributes
                    for attr in ['xLoc', 'yLoc', 'xDest', 'yDest']:
                        value = preset.get(attr)
                        if value is not None:
                            preset_data[attr] = float(value)

                    # Extract other attributes
                    for attr in ['ClickAndDrag']:
                        value = preset.get(attr)
                        if value is not None:
                            preset_data[attr] = value.lower() == 'true'

                    coordinates[preset_name] = preset_data

                except Exception as e:
                    logger.warning(f"Failed to parse preset {preset.get('name', 'unknown')}: {e}")

            logger.info(f"Loaded {len(coordinates)} coordinate presets from {location_file}")
            return coordinates

        except Exception as e:
            logger.error(f"Failed to load coordinates from XML: {e}")
            return coordinates

    def _get_coordinates(self, preset_name: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a preset"""
        return self.coordinates.get(preset_name)

    def _calculate_tap_point(self, preset_name: str, screenshot_size: Optional[Tuple[int, int]] = None) -> Optional[Tuple[int, int]]:
        """Calculate actual tap coordinates from normalized preset"""
        preset = self._get_coordinates(preset_name)
        if not preset:
            logger.error(f"Preset not found: {preset_name}")
            return None

        # Calculate tap point based on available coordinates
        if 'xDest' in preset and 'yDest' in preset:
            # Rectangular region - use center point
            x_center = (preset['xLoc'] + preset['xDest']) / 2
            y_center = (preset['yLoc'] + preset['yDest']) / 2
        else:
            # Single point coordinate
            x_center = preset['xLoc']
            y_center = preset['yLoc']

        # Use provided screenshot size, or detected screen size
        if screenshot_size:
            width, height = screenshot_size
        else:
            width, height = self.screen_size

        x_pixel = int(x_center * width)
        y_pixel = int(y_center * height)

        # For debugging - show preset and calculated coordinates before tap
        if self.config.get('debug_mode', False):
            logger.debug(f"Using preset {preset_name}: {preset} -> tapping at ({x_pixel}, {y_pixel}) on {width}x{height} screen")

        return (x_pixel, y_pixel)

    def _tap_preset(self, preset_name: str, delay: Optional[float] = None) -> bool:
        """Tap on a coordinate preset"""
        if delay is None:
            delay = self.transition_delay

        coords = self._calculate_tap_point(preset_name)
        if not coords:
            return False

        x, y = coords

        success = self.platform.send_tap(x, y)
        if success:
            # Always add 0.5 second delay for screen update
            time.sleep(0.5)
            # Additional transition delay if specified
            if delay is not None:
                time.sleep(delay)
        return success

    def tap_preset(self, preset_name: str, delay: Optional[float] = None) -> bool:
        """Public method to tap on a coordinate preset"""
        return self._tap_preset(preset_name, delay)

    def navigate_to_generals_list(self) -> bool:
        """Navigate to the generals list screen"""
        try:
            logger.info("Navigating to generals list")

            # Click ThreeDots button
            if not self._tap_preset("ThreeDots"):
                return False

            # Click Generals button
            if not self._tap_preset("Generals"):
                return False

            # Wait for screen to load
            time.sleep(self.transition_delay)
            return True

        except Exception as e:
            logger.error(f"Navigation to generals list failed: {e}")
            return False

    def _compare_with_reference_image(self, preset_name: str, screenshot_bytes: bytes) -> bool:
        """Compare a screenshot region with reference image to check if filter is active"""
        try:
            # Convert bytes to PIL Image
            from io import BytesIO
            screenshot_image = Image.open(BytesIO(screenshot_bytes))

            # Get coordinates for the preset
            coords = self._get_coordinates(preset_name)
            if not coords:
                logger.warning(f"No coordinates found for {preset_name}")
                return False

            # Calculate pixel coordinates
            x1 = int(coords['xLoc'] * self.screen_size[0])
            y1 = int(coords['yLoc'] * self.screen_size[1])
            x2 = int(coords['xDest'] * self.screen_size[0])
            y2 = int(coords['yDest'] * self.screen_size[1])

            # Crop the screenshot to the region
            region = screenshot_image.crop((x1, y1, x2, y2))

            # Load reference image
            reference_path = Path(__file__).parent.parent / "Resources" / f"{preset_name}.png"
            if not reference_path.exists():
                logger.warning(f"Reference image not found: {reference_path}")
                return False

            reference = Image.open(reference_path)
            logger.info(f"DEBUG: Loaded reference image: {reference_path} (size: {reference.size}, mode: {reference.mode})")

            # Convert both to RGB if needed
            if region.mode != 'RGB':
                region = region.convert('RGB')
                logger.info(f"DEBUG: Converted image region to RGB")
            if reference.mode != 'RGB':
                reference = reference.convert('RGB')
                logger.info(f"DEBUG: Converted reference to RGB")

            # Resize region to match reference if needed
            if region.size != reference.size:
                original_size = region.size
                region = region.resize(reference.size, Image.Resampling.LANCZOS)
                logger.info(f"DEBUG: Resized region from {original_size} to {reference.size}")

            logger.info(f"DEBUG: Final image sizes - Region: {region.size}, Reference: {reference.size}")

            # DEBUG: Save images for visual inspection
            debug_dir = Path(__file__).parent.parent / "debug_images"
            debug_dir.mkdir(exist_ok=True)

            region_path = debug_dir / f"{preset_name}_region.png"
            reference_debug_path = debug_dir / f"{preset_name}_reference.png"

            region.save(region_path)
            reference.save(reference_debug_path)

            logger.info(f"DEBUG: Saved comparison images to {debug_dir}")
            logger.info(f"DEBUG: Region image: {region_path} (size: {region.size})")
            logger.info(f"DEBUG: Reference image: {reference_debug_path} (size: {reference.size})")

            # Convert to numpy arrays for comparison
            region_array = np.array(region, dtype=np.float32)
            reference_array = np.array(reference, dtype=np.float32)

            # Calculate mean squared error
            mse = np.mean((region_array - reference_array) ** 2)

            # Also calculate other metrics for debugging
            max_diff = np.max(np.abs(region_array - reference_array))
            mean_diff = np.mean(np.abs(region_array - reference_array))

            logger.info(f"DEBUG: {preset_name} - MSE: {mse:.2f}, Max diff: {max_diff}, Mean diff: {mean_diff:.2f}")
            logger.info(f"DEBUG: Region shape: {region_array.shape}, Reference shape: {reference_array.shape}")

            # Check if images are identical (for debugging)
            are_identical = np.array_equal(region_array, reference_array)
            logger.info(f"DEBUG: Images are identical: {are_identical}")

            # Consider them matching if MSE is below threshold (strict threshold for accuracy)
            threshold = 10.0  # Very strict threshold to prevent false matches
            is_match = bool(mse < threshold)

            logger.info(f"DEBUG: {preset_name} comparison result: {is_match} (MSE {mse:.2f} < {threshold})")
            logger.info(f"DEBUG: Threshold analysis - Current MSE: {mse:.2f}, Threshold: {threshold}, Ratio: {mse/threshold:.2f}")

            # Additional debug: show if this would match with different thresholds
            test_thresholds = [1.0, 5.0, 10.0, 25.0, 50.0, 100.0]
            logger.info(f"DEBUG: Would match with thresholds: {', '.join([f'{t}: {mse < t}' for t in test_thresholds])}")

            return is_match

        except Exception as e:
            logger.error(f"Failed to compare image for {preset_name}: {e}")
            return False

    def set_generals_list_state(self) -> bool:
        """Set the generals list to the desired state by checking current filter states"""
        try:
            logger.info("Setting generals list state")

            # Reset state change flags
            self.state_change_flags = {'mode': False, 'favorites': False, 'idle': False}

            # Set to "All" filter first
            if not self._tap_preset("All"):
                return False

            # Capture screenshot to check current filter states
            screenshot_bytes = self.platform.capture_screenshot()
            if not screenshot_bytes:
                logger.error("Failed to capture screenshot for filter state check")
                return False

            # Check and set Mode filter
            val = self._compare_with_reference_image("GeneralsListMode", screenshot_bytes)
            if val:  # Images match - filter is NOT active, need to activate it
                logger.info("List Mode filter not active, activating it")
                if not self._tap_preset("GeneralsListMode"):
                    return False
                self.state_change_flags['mode'] = True
            else:  # Images don't match - filter is already active
                logger.info("List Mode filter already active")

            # Check and set Favorites filter
            val = self._compare_with_reference_image("GeneralsListFavorites", screenshot_bytes)
            if not val:  # Images match - filter is active, need to deactivate it
                logger.info("Favorites filter active, deactivating it")
                if not self._tap_preset("GeneralsListFavorites"):
                    return False
                self.state_change_flags['favorites'] = True
            else:  # Images don't match - filter is already inactive
                logger.info("Favorites filter already inactive")

            # Check and set Idle filter
            val = self._compare_with_reference_image("GeneralsListIdle", screenshot_bytes)
            if not val:  # Images match - filter is active, need to deactivate it
                logger.info("Idle filter active, deactivating it")
                if not self._tap_preset("GeneralsListIdle"):
                    return False
                self.state_change_flags['idle'] = True
            else:  # Images don't match - filter is already inactive
                logger.info("Idle filter already inactive")

            logger.info(f"Filter states set: mode={self.state_change_flags['mode']}, favorites={self.state_change_flags['favorites']}, idle={self.state_change_flags['idle']}")
            return True

        except Exception as e:
            logger.error(f"Setting generals list state failed: {e}")
            return False

    def reset_generals_list_state(self) -> bool:
        """Reset generals list state to original settings"""
        try:
            logger.info("Resetting generals list state")

            # Reset each state that was changed
            if self.state_change_flags.get('mode'):
                self._tap_preset("GeneralsListMode")

            if self.state_change_flags.get('favorites'):
                self._tap_preset("GeneralsListFavorites")

            if self.state_change_flags.get('idle'):
                self._tap_preset("GeneralsListIdle")

            return True

        except Exception as e:
            logger.error(f"Resetting generals list state failed: {e}")
            return False

    def get_total_generals_count(self) -> tuple[int, str]:
        """Get the total number of generals and the count text"""
        try:
            # Capture screenshot
            screenshot = self.platform.capture_screenshot()
            if not screenshot:
                return 0, ""

            # Extract count region
            count_result = self.ocr_engine.extract_text(screenshot, "GeneralsListCount")
            if not count_result:
                return 0, ""

            # Parse "current/total" format
            count_text = count_result.text.strip()
            if '/' in count_text:
                try:
                    current, total = count_text.split('/')
                    return int(current.strip()), count_text
                except ValueError:
                    logger.warning(f"Failed to parse count: {count_text}")

            return 0, count_text

        except Exception as e:
            logger.error(f"Failed to get generals count: {e}")
            return 0, ""

    def open_general_details(self, general_index: int) -> bool:
        """Open details for a specific general"""
        try:
            if general_index == 1:
                # First general
                return self._tap_preset("GeneralsFirstGeneral")
            else:
                # Subsequent generals - would need scrolling logic
                # For now, just tap next
                return self._tap_preset("GeneralsListMoveRight")

        except Exception as e:
            logger.error(f"Failed to open general {general_index} details: {e}")
            return False

    def close_general_details(self) -> bool:
        """Close general details screen"""
        try:
            return self._tap_preset("Back")
        except Exception as e:
            logger.error(f"Failed to close general details: {e}")
            return False

    def navigate_to_cultivation_screen(self) -> bool:
        """Navigate to cultivation screen"""
        try:
            return self._tap_preset("GeneralsListCultivate")
        except Exception as e:
            logger.error(f"Failed to navigate to cultivation screen: {e}")
            return False

    def navigate_to_specialties_screen(self) -> bool:
        """Navigate to specialties screen"""
        try:
            return self._tap_preset("GeneralsListSpecialty")
        except Exception as e:
            logger.error(f"Failed to navigate to specialties screen: {e}")
            return False

    def navigate_to_covenant_screen(self) -> bool:
        """Navigate to covenant screen"""
        try:
            # Capture screenshot to check if covenant button is active
            screenshot = self.platform.capture_screenshot()
            if not screenshot:
                logger.warning("Failed to capture screenshot for covenant button check")
                return False

            # Check if the covenant button matches the inactive (grayed out) reference image
            # If it matches, the button is inactive and we should skip covenant routines
            if self._compare_with_reference_image("GeneralsListCovenant", screenshot):
                logger.info("Covenant button is inactive (grayed out), skipping covenant routines")
                return False

            # Button is active, proceed with navigation
            logger.info("Covenant button is active, navigating to covenant screen")
            return self._tap_preset("GeneralsListCovenant")
        except Exception as e:
            logger.error(f"Failed to navigate to covenant screen: {e}")
            return False

    def navigate_to_next_covenant_general(self) -> bool:
        """Navigate to next covenant general"""
        try:
            return self._tap_preset("GeneralsListCovenantRight")
        except Exception as e:
            logger.error(f"Failed to navigate to next covenant general: {e}")
            return False

    def close_covenant_subscreen(self) -> bool:
        """Close covenant subscreen"""
        try:
            return self._tap_preset("GeneralsListCovenantXOut")
        except Exception as e:
            logger.error(f"Failed to close covenant subscreen: {e}")
            return False