"""
Application controller for Evony Active Generals Tracker
"""

import time
import logging
from typing import List, Dict, Any, Callable, Optional, Tuple
from pathlib import Path

from models.general import General
from platform_adb.bluestacks_interface import BluestacksInterface
from ocr.ocr_engine import OCREngine
from navigation.game_navigator import GameNavigator
from export.excel_exporter import ExcelExporter
from utils.resource_manager import resource_manager

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

    def reset_collection_state(self) -> None:
        """Reset all collection state for a fresh start"""
        logger.info("Resetting collection state")
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

    def collect_all_generals(self, progress_callback: Optional[Callable] = None, export_path: Optional[str] = None) -> Tuple[List[General], Optional[str]]:
        """Collect data for all generals"""
        if not self._check_initialization():
            raise RuntimeError("Platform not properly initialized")

        # Reset collection state for fresh start
        self.reset_collection_state()

        self.start_time = time.time()
        generals = []
        excel_file_path = None

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

            # Always create timestamped Excel file in ./Spreadsheets directory
            # Create Spreadsheets directory if it doesn't exist
            spreadsheets_dir = Path("./Spreadsheets")
            spreadsheets_dir.mkdir(exist_ok=True)
            
            # Create timestamped filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"ActiveGenerals_{timestamp}.xlsx"
            excel_path = spreadsheets_dir / excel_filename
            
            # Create initial Excel file from template
            initial_generals = []  # Empty list for initial creation
            if not self.exporter.export_generals(initial_generals, str(excel_path), self.count_text, incremental=False):
                logger.warning(f"Failed to create initial Excel file: {excel_path}")
                excel_path = None
            else:
                logger.info(f"Created Excel file: {excel_path}")
                excel_file_path = str(excel_path)

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

                # Write general to Excel immediately
                if excel_path and general:
                    try:
                        row_index = i + 7  # Start from row 7 (after headers)
                        if not self.exporter.append_general(general, str(excel_path), row_index):
                            logger.warning(f"Failed to append general {i+1} to Excel file")
                    except Exception as e:
                        logger.warning(f"Failed to write general {i+1} to Excel: {e}")

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
            return generals, excel_file_path

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

            logger.info(f"Extracted main data for {general.name}: level={general.level}, power={general.power}, exp={general.exp_ratio}")

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
                    logger.info(f"Extracted specialty data for {general.name}: {general.specialty_names[:100] if general.specialty_names else 'None'}")
                else:
                    logger.warning(f"Failed to capture specialty screenshot for {general.name}")
                # Return to general details screen
                self.navigator.close_general_details()
            else:
                logger.warning(f"Failed to navigate to specialties screen for {general.name}")

            # Navigate to covenant screen and extract data
            if self.navigator.navigate_to_covenant_screen():
                covenant_screenshot = self.platform.capture_screenshot()
                if covenant_screenshot:
                    self._extract_covenant_data(general, covenant_screenshot)
                    logger.info(f"Extracted covenant data for {general.name}: {general.covenant_data[:100] if general.covenant_data else 'None'}")
                else:
                    logger.warning(f"Failed to capture covenant screenshot for {general.name}")
                # Return to general details screen
                self.navigator.close_general_details()
            else:
                logger.warning(f"Failed to navigate to covenant screen for {general.name}")

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
        # Extract name and level
        name_result = self.ocr_engine.extract_text(screenshot, "GeneralsListName")
        if name_result and name_result.text:
            full_text = name_result.text.strip()
            # Parse "Lv ## Name" format
            if full_text.startswith("Lv "):
                # Find the space after the level number
                level_end = full_text.find(" ", 3)  # Start searching after "Lv "
                if level_end != -1:
                    try:
                        level_str = full_text[3:level_end]
                        general.level = int(level_str)
                        general.name = full_text[level_end + 1:].strip()
                    except ValueError:
                        # If level parsing fails, treat whole text as name
                        general.name = full_text
                        general.level = None
                else:
                    # No space found after "Lv", treat as name only
                    general.name = full_text
                    general.level = None
            else:
                # Doesn't start with "Lv", treat whole text as name
                general.name = full_text
                general.level = None
        else:
            general.name = ""
            general.level = None
        general.confidence_scores['name'] = name_result.confidence if name_result else 0.0

        # Extract power
        # Check which power location to use
        template_path = "Resources/GeneralsListPowerLocation.png"
        use_location_1 = False
        # Massena should be lower, so location 2
        template_resource_path = resource_manager.get_resource_path(template_path)
        if template_resource_path.exists():
            use_location_1 = self.ocr_engine.check_template_match(screenshot, "GeneralsListPowerLocation", str(template_resource_path))
        
        power_region = "GeneralsListPower1" if use_location_1 else "GeneralsListPower2"
        power_result = self.ocr_engine.extract_text(screenshot, power_region)
        if power_result and power_result.text:
            # Parse number from text, handling comma-separated numbers
            import re
            matches = re.findall(r'\d+(?:,\d{3})*', power_result.text)
            if matches:
                # Take the largest value (most likely to be the power number)
                clean_number = max(matches).replace(',', '')
                try:
                    general.power = int(clean_number)
                except ValueError:
                    general.power = None
            else:
                general.power = None
        else:
            general.power = None
        general.confidence_scores['power'] = power_result.confidence if power_result else 0.0

        # Extract experience ratio
        exp_region = "GeneralsListExp1" if use_location_1 else "GeneralsListExp2"
        exp_result = self.ocr_engine.extract_text(screenshot, exp_region)
        general.exp_ratio = exp_result.text.strip() if exp_result else ""
        general.confidence_scores['exp_ratio'] = exp_result.confidence if exp_result else 0.0

        # Extract type image
        type_region = "GeneralsListType1" if use_location_1 else "GeneralsListType2"
        type_image = self.ocr_engine.extract_image(screenshot, type_region)
        general.type_image = type_image or b""
        
        # Extract stars image
        stars_image = self.ocr_engine.extract_image(screenshot, "GeneralsListStars")
        if stars_image:
            # Resize stars image to 50%
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(stars_image))
            new_size = (int(img.width * 0.5), int(img.height * 0.5))
            img_resized = img.resize(new_size, Image.LANCZOS)
            buf = io.BytesIO()
            img_resized.save(buf, format='PNG')
            stars_image = buf.getvalue()
        general.stars_image = stars_image or b""
        logger.debug(f"Extracted stars image for {general.name}: {len(general.stars_image)} bytes")

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

        # Check if this is a purple general (indicated by purple pixel on cultivation screen)
        general.is_purple_general = not self.ocr_engine.check_pixel_color(screenshot, "GeneralsListCultivatePurple", (123, 81, 8), tolerance=20)
        logger.info(f"General {general.name} is_purple_general: {general.is_purple_general}")

        # Extract each stat
        stats = ['Leadership', 'Attack', 'Defense', 'Politics']
        total_confidence = 0.0

        for stat in stats:
            preset_name = f"GeneralsListCultivate{stat}"
            result = self.ocr_engine.extract_text(screenshot, preset_name)
            if result and result.text:
                cultivation_parts.append(result.text.strip())
                total_confidence += result.confidence
            else:
                cultivation_parts.append("Unknown")
                total_confidence += 0.0

        general.cultivation_data = chr(10).join(cultivation_parts)
        general.confidence_scores['cultivation'] = total_confidence / len(stats)
        
        logger.info(f"Extracted cultivation data: {general.cultivation_data}")

    def _extract_specialty_data(self, general: General, screenshot) -> None:
        """Extract specialty data from screenshot"""
        specialty_names = []
        specialty_images = []
        total_confidence = 0.0

        # Use the purple general flag that was determined during cultivation screen processing
        if general.is_purple_general:
            logger.info("Processing purple general specialties - processing 3 specialties")
            specialty_range = range(1, 4)  # P1, P2, P3
            specialty_presets = ["GeneralsListSpecialtyP1", "GeneralsListSpecialtyP2", "GeneralsListSpecialtyP3"]
        else:
            logger.info("Processing regular general specialties - processing 5 specialties")
            specialty_range = range(1, 6)  # 1, 2, 3, 4, 5
            specialty_presets = [f"GeneralsListSpecialty{i}" for i in range(1, 6)]

        for i, specialty_click_preset in zip(specialty_range, specialty_presets):
            # Click on the specialty item to select it
            if not self.navigator.tap_preset(specialty_click_preset):
                logger.warning(f"Failed to click on specialty {i}")
                specialty_names.append("Unknown Specialty")
                total_confidence += 0.0
                continue

            # Wait for UI to update after click
            time.sleep(0.5)

            # Take a new screenshot after clicking
            new_screenshot = self.platform.capture_screenshot()
            if not new_screenshot:
                logger.warning(f"Failed to take screenshot after clicking specialty {i}")
                specialty_names.append("Unknown Specialty")
                total_confidence += 0.0
                continue

            # Extract image
            image_preset = specialty_click_preset
            image_data = self.ocr_engine.extract_image(new_screenshot, image_preset)

            # Extract name (yellow text on dark background)
            name_preset = "GeneralsListSpecialtyName"
            name_result = self.ocr_engine.extract_text(new_screenshot, name_preset)

            if image_data and name_result and name_result.text:
                specialty_names.append(name_result.text.strip())
                specialty_images.append(image_data)
                total_confidence += name_result.confidence
            else:
                specialty_names.append("Unknown Specialty")
                total_confidence += 0.0

        general.specialty_names = chr(10).join(specialty_names)
        combined_image = self.exporter.combine_images_side_by_side(specialty_images)
        if combined_image:
            # Resize combined specialty image to 50%
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(combined_image))
            new_size = (int(img.width * 0.5), int(img.height * 0.5))
            img_resized = img.resize(new_size, Image.LANCZOS)
            buf = io.BytesIO()
            img_resized.save(buf, format='PNG')
            combined_image = buf.getvalue()
        general.specialty_combined_image = combined_image
        general.confidence_scores['specialty'] = total_confidence / len(specialty_range)

    def _extract_covenant_data(self, general: General, screenshot) -> None:
        """Extract covenant data from screenshot"""
        covenant_parts = []
        covenant_names = []
        covenant_images = []
        total_confidence = 0.0

        # First, click on the covenant general button to access covenant generals
        if not self.navigator.tap_preset("GeneralsListCovenantGeneral"):
            logger.warning("Failed to click on covenant general button")
            general.covenant_data = "No Covenant Data"
            general.covenant_names = ""
            general.covenant_combined_image = b""
            general.covenant_attributes_image = self.exporter.load_covenant_attributes_image()
            general.confidence_scores['covenant'] = 0.0
            return

        # Wait for covenant general screen to load
        time.sleep(0.5)

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
                covenant_names.append("Unknown Covenant")
                total_confidence += 0.0
                continue

            # Extract data
            image_data = self.ocr_engine.extract_image(new_screenshot, "GeneralsListCovenantCoGenImage")
            name_result = self.ocr_engine.extract_text(new_screenshot, "GeneralsListCovenantCoGenName")

            if image_data and name_result.text:
                # Resize covenant image to 50%
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(image_data))
                new_size = (int(img.width * 0.5), int(img.height * 0.5))
                img_resized = img.resize(new_size, Image.LANCZOS)
                buf = io.BytesIO()
                img_resized.save(buf, format='PNG')
                image_data = buf.getvalue()
                
                covenant_names.append(name_result.text.strip())
                covenant_images.append(image_data)
                total_confidence += name_result.confidence
            else:
                covenant_names.append("Unknown Covenant")
                total_confidence += 0.0

        # Close covenant sub-screen
        self.navigator.close_covenant_subscreen()

        general.covenant_names = chr(10).join(covenant_names)
        combined_image = self.exporter.combine_images_side_by_side(covenant_images)
        if combined_image:
            # Resize combined covenant image to 50%
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(combined_image))
            new_size = (int(img.width * 0.5), int(img.height * 0.5))
            img_resized = img.resize(new_size, Image.LANCZOS)
            buf = io.BytesIO()
            img_resized.save(buf, format='PNG')
            combined_image = buf.getvalue()
        general.covenant_combined_image = combined_image
        general.covenant_attributes_image = self.exporter.load_covenant_attributes_image()
        general.confidence_scores['covenant'] = total_confidence / 3

    def export_to_excel(self, file_path: str, generals: List[General], incremental: bool = False) -> bool:
        """Export generals data to Excel"""
        if not self.exporter:
            logger.error("Excel exporter not initialized")
            return False

        try:
            return self.exporter.export_generals(generals, file_path, self.count_text, incremental)
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