"""
Application controller for Evony Active Generals Tracker
"""

import time
import logging
from typing import List, Dict, Any, Callable, Optional
from pathlib import Path

from models.general import General
from platform_adb.bluestacks_interface import BluestacksInterface
from ocr.ocr_engine import OCREngine
from navigation.game_navigator import GameNavigator
from export.excel_exporter import ExcelExporter

logger = logging.getLogger(__name__)

class ApplicationController:
    """Main application controller that orchestrates data collection and export"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.platform = None
        self.ocr_engine = None
        self.navigator = None
        self.exporter = None

        # Progress tracking
        self.start_time = None
        self.total_generals = 0
        self.count_text = ""
        self.processed_generals = 0

    def initialize_platform(self) -> bool:
        """Initialize platform interface"""
        try:
            platform_type = self.config.get('platform_type', 'bluestacks')

            if platform_type == 'bluestacks':
                self.platform = BluestacksInterface(self.config)
            else:
                # Future: Add AndroidInterface, IOSInterface
                logger.error(f"Unsupported platform type: {platform_type}")
                return False

            if not self.platform.connect():
                logger.error("Failed to connect to platform")
                return False

            # Initialize OCR engine
            self.ocr_engine = OCREngine(self.config)

            # Initialize game navigator
            self.navigator = GameNavigator(self.platform, self.ocr_engine, self.config)

            # Initialize Excel exporter
            self.exporter = ExcelExporter(self.config)

            logger.info("Platform initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Platform initialization error: {e}")
            return False

    def collect_all_generals(self, progress_callback: Optional[Callable] = None) -> List[General]:
        """Collect data for all generals"""
        if not self._check_initialization():
            raise RuntimeError("Platform not properly initialized")

        self.start_time = time.time()
        generals = []

        try:
            # Navigate to generals list
            self._update_progress(progress_callback, {
                'status': 'Navigating to generals list',
                'current_step': 'Navigation',
                'percentage': 5
            })

            if not self.navigator.navigate_to_generals_list():
                raise RuntimeError("Failed to navigate to generals list")

            # Set generals list state
            self._update_progress(progress_callback, {
                'status': 'Setting generals list filters',
                'current_step': 'Configuration',
                'percentage': 10
            })

            if not self.navigator.set_generals_list_state():
                raise RuntimeError("Failed to set generals list state")

            # Get total generals count
            self._update_progress(progress_callback, {
                'status': 'Extracting generals count',
                'current_step': 'Analysis',
                'percentage': 15
            })

            self.total_generals, self.count_text = self.navigator.get_total_generals_count()
            if self.total_generals <= 0:
                raise RuntimeError("No generals found")

            logger.info(f"Found {self.total_generals} generals to process (count text: {self.count_text})")

            # Process each general
            for i in range(self.total_generals):
                if progress_callback:
                    # Check for stop signal
                    try:
                        progress_callback({})
                    except KeyboardInterrupt:
                        raise

                general = self._collect_single_general(i + 1, progress_callback)
                generals.append(general)
                self.processed_generals = i + 1

                # Update progress
                percentage = 15 + (i + 1) / self.total_generals * 80  # 15-95%
                elapsed = time.time() - self.start_time
                avg_confidence = sum(g.get_average_confidence() for g in generals) / len(generals)

                self._update_progress(progress_callback, {
                    'current_general': i + 1,
                    'total_generals': self.total_generals,
                    'percentage': percentage,
                    'elapsed_time': elapsed,
                    'estimated_remaining': self._estimate_remaining_time(),
                    'average_confidence': avg_confidence * 100,
                    'status': f'Processing general {i + 1}/{self.total_generals}',
                    'current_step': f'General {general.name or "Unknown"}',
                    'generals_data': generals.copy()  # Include current generals data for table update
                })

            # Reset generals list state
            self._update_progress(progress_callback, {
                'status': 'Cleaning up',
                'current_step': 'Cleanup',
                'percentage': 98
            })

            self.navigator.reset_generals_list_state()

            # Final progress update
            self._update_progress(progress_callback, {
                'percentage': 100,
                'status': 'Collection complete',
                'current_step': 'Complete'
            })

            logger.info(f"Successfully collected data for {len(generals)} generals")
            return generals

        except Exception as e:
            logger.error(f"Collection failed: {e}")
            raise

        finally:
            # Cleanup
            if self.platform:
                self.platform.disconnect()

    def _collect_single_general(self, general_index: int, progress_callback: Optional[Callable] = None) -> General:
        """Collect data for a single general"""
        general = General()

        try:
            # Open general details
            if not self.navigator.open_general_details(general_index):
                logger.warning(f"Failed to open details for general {general_index}")
                general.is_uncertain = True
                return general

            # Capture main details screenshot
            screenshot = self.platform.capture_screenshot()
            if screenshot is None:
                logger.warning(f"Failed to capture screenshot for general {general_index}")
                general.is_uncertain = True
                return general

            # Extract main general data
            self._extract_main_general_data(general, screenshot)

            # Navigate to cultivation screen and extract data

            if self.navigator.navigate_to_cultivation_screen():
                cult_screenshot = self.platform.capture_screenshot()
                if cult_screenshot:
                    self._extract_cultivation_data(general, cult_screenshot)
                # Return to general details screen
                self.navigator.close_general_details()

            # Navigate to specialties screen and extract data
            if self.navigator.navigate_to_specialties_screen():
                spec_screenshot = self.platform.capture_screenshot()
                if spec_screenshot:
                    self._extract_specialty_data(general, spec_screenshot)
                # Return to general details screen
                self.navigator.close_general_details()

            # Navigate to covenant screen and extract data
            if self.navigator.navigate_to_covenant_screen():
                covenant_screenshot = self.platform.capture_screenshot()
                if covenant_screenshot:
                    self._extract_covenant_data(general, covenant_screenshot)
                # Return to general details screen
                self.navigator.close_general_details()

            # Determine if general is uncertain
            confidence_threshold = self.config.get('confidence_threshold', 0.8)
            avg_confidence = general.get_average_confidence()
            general.is_uncertain = avg_confidence < confidence_threshold

            logger.info(f"Collected data for general: {general.name} (confidence: {avg_confidence:.2f})")

        except Exception as e:
            logger.error(f"Error collecting data for general {general_index}: {e}")
            general.is_uncertain = True

        return general

    def _extract_main_general_data(self, general: General, screenshot) -> None:
        """Extract main general information from screenshot"""
        # Extract name
        name_result = self.ocr_engine.extract_text(screenshot, "GeneralsListName")
        general.name = name_result.text if name_result else ""
        general.confidence_scores['name'] = name_result.confidence if name_result else 0.0

        # Extract level
        level_result = self.ocr_engine.extract_number(screenshot, "GeneralsListLevel")
        general.level = level_result.value if level_result else None
        general.confidence_scores['level'] = level_result.confidence if level_result else 0.0

        # Extract type image
        type_image = self.ocr_engine.extract_image(screenshot, "GeneralsListType")
        general.type_image = type_image or b""

        # Extract power
        power_result = self.ocr_engine.extract_number(screenshot, "GeneralsListPower")
        general.power = power_result.value if power_result else None
        general.confidence_scores['power'] = power_result.confidence if power_result else 0.0

        # Extract experience ratio
        exp_result = self.ocr_engine.extract_text(screenshot, "GeneralsListExp")
        general.exp_ratio = exp_result.text if exp_result else ""
        general.confidence_scores['exp_ratio'] = exp_result.confidence if exp_result else 0.0

        # Extract stars image
        stars_image = self.ocr_engine.extract_image(screenshot, "GeneralsListStars")
        general.stars_image = stars_image or b""

    def _parse_general_name(self, raw_name: str) -> str:
        """Parse general name to remove level prefix"""
        import re

        # Remove level prefix patterns like "Lv 25 ", "Lv25 ", "Level 25 ", etc.
        # Pattern matches: "Lv" or "Level" followed by optional space, digits, and space
        cleaned_name = re.sub(r'(?i)^(lv|level)\s*\d+\s+', '', raw_name.strip())

        logger.debug(f"Parsed general name: '{raw_name}' -> '{cleaned_name}'")
        return cleaned_name

    def _extract_cultivation_data(self, general: General, screenshot) -> None:
        """Extract cultivation data from screenshot"""
        cultivation_parts = []

        # Extract each stat
        stats = ['Leadership', 'Attack', 'Defense', 'Politics']
        total_confidence = 0.0

        for stat in stats:
            preset_name = f"GeneralsListCultivate{stat}"
            result = self.ocr_engine.extract_text(screenshot, preset_name)
            if result and result.text:
                cultivation_parts.append(f"{stat}: {result.text}")
                total_confidence += result.confidence
            else:
                cultivation_parts.append(f"{stat}: Unknown")
                total_confidence += 0.0

        general.cultivation_data = "\n".join(cultivation_parts)
        general.confidence_scores['cultivation'] = total_confidence / len(stats)

    def _extract_specialty_data(self, general: General, screenshot) -> None:
        """Extract specialty data from screenshot"""
        specialty_parts = []
        total_confidence = 0.0

        for i in range(1, 6):  # 5 specialties
            # Click on the specialty item to select it
            specialty_click_preset = f"GeneralsListSpecialty{i}"
            if not self.navigator.tap_preset(specialty_click_preset):
                logger.warning(f"Failed to click on specialty {i}")
                specialty_parts.append("Unknown Specialty")
                total_confidence += 0.0
                continue

            # Wait for UI to update after click
            time.sleep(0.5)

            # Take a new screenshot after clicking
            new_screenshot = self.platform.capture_screenshot()
            if not new_screenshot:
                logger.warning(f"Failed to take screenshot after clicking specialty {i}")
                specialty_parts.append("Unknown Specialty")
                total_confidence += 0.0
                continue

            # Extract image
            image_preset = f"GeneralsListSpecialtyImage{i}"
            image_data = self.ocr_engine.extract_image(new_screenshot, image_preset)

            # Extract name (yellow text on dark background)
            name_preset = "GeneralsListSpecialtyName"
            name_result = self.ocr_engine.extract_text(new_screenshot, name_preset)

            if image_data and name_result and name_result.text:
                specialty_parts.append(f"{image_data.decode('latin-1')} {name_result.text}")
                total_confidence += name_result.confidence
            else:
                specialty_parts.append("Unknown Specialty")
                total_confidence += 0.0

        general.specialty_data = "\n".join(specialty_parts)
        general.confidence_scores['specialty'] = total_confidence / 5

    def _extract_covenant_data(self, general: General, screenshot) -> None:
        """Extract covenant data from screenshot"""
        covenant_parts = []
        total_confidence = 0.0

        # First, click on the covenant general button to access covenant generals
        if not self.navigator.tap_preset("GeneralsListCovenantGeneral"):
            logger.warning("Failed to click on covenant general button")
            general.covenant_data = "No Covenant Data"
            general.confidence_scores['covenant'] = 0.0
            return

        # Wait for covenant general screen to load
        time.sleep(1.0)

        # Navigate through covenant sub-screens
        for i in range(4):  # main general +3 covenant generals
            # Navigate to next covenant general (skip for first one)
            if i > 0:
                self.navigator.navigate_to_next_covenant_general()

            # Take a new screenshot after navigation
            new_screenshot = self.platform.capture_screenshot()
            if not new_screenshot:
                logger.warning(f"Failed to capture screenshot for covenant general {i+1}")
                covenant_parts.append("Unknown Covenant")
                total_confidence += 0.0
                continue

            # Extract data
            image_data = self.ocr_engine.extract_image(new_screenshot, "GeneralsListCovenantCoGenImage")
            name_result = self.ocr_engine.extract_text(new_screenshot, "GeneralsListCovenantCoGenName")

            if image_data and name_result and name_result.text:
                covenant_parts.append(f"{image_data.decode('latin-1')} {name_result.text}")
                total_confidence += name_result.confidence
            else:
                covenant_parts.append("Unknown Covenant")
                total_confidence += 0.0

        # Close covenant sub-screen
        self.navigator.close_covenant_subscreen()

        general.covenant_data = "\n".join(covenant_parts)
        general.confidence_scores['covenant'] = total_confidence / 3

    def export_to_excel(self, file_path: str, generals: List[General]) -> bool:
        """Export generals data to Excel"""
        if not self.exporter:
            logger.error("Excel exporter not initialized")
            return False

        try:
            return self.exporter.export_generals(generals, file_path, self.count_text)
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False

    def _check_initialization(self) -> bool:
        """Check if all components are properly initialized"""
        return all([
            self.platform is not None,
            self.ocr_engine is not None,
            self.navigator is not None,
            self.exporter is not None
        ])

    def _update_progress(self, callback: Optional[Callable], progress_info: Dict[str, Any]) -> None:
        """Update progress through callback"""
        if callback:
            try:
                callback(progress_info)
            except KeyboardInterrupt:
                raise

    def _estimate_remaining_time(self) -> Optional[float]:
        """Estimate remaining time based on current progress"""
        if self.processed_generals == 0 or self.total_generals == 0:
            return None

        elapsed = time.time() - self.start_time
        avg_time_per_general = elapsed / self.processed_generals
        remaining_generals = self.total_generals - self.processed_generals

        return avg_time_per_general * remaining_generals