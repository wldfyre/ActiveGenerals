"""
OCR Engine for text extraction from game screenshots
"""

import logging
import io
import os
from datetime import datetime
from typing import Optional, Any, Tuple, Dict
from dataclasses import dataclass
from PIL import Image
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """Result of OCR text extraction"""
    text: str
    confidence: float

@dataclass
class NumberResult:
    """Result of OCR number extraction"""
    value: Optional[int]
    confidence: float

class OCREngine:
    """OCR Engine for extracting text from screenshots"""

    def __init__(self, config: dict):
        self.config = config
        self.engine_type = config.get('ocr_engine', 'easyocr')
        self.confidence_threshold = config.get('confidence_threshold', 0.8)
        self.preprocessing_enabled = config.get('preprocessing_enabled', True)
        self.languages = config.get('ocr_languages', ['en'])

        # Region definitions (pixel coordinates for cropping)
        # These should match the presets in locations.xml
        self.regions: Dict[str, Tuple[int, int, int, int]] = {}
        
        # Load OCR regions from locations.xml
        self._load_ocr_regions()

        # Initialize OCR engine
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize the OCR engine"""
        try:
            if self.engine_type == 'easyocr':
                import easyocr
                self.reader = easyocr.Reader(self.languages, gpu=False)  # Set gpu=True if GPU available
                logger.info("EasyOCR engine initialized")
            elif self.engine_type == 'tesseract':
                import pytesseract
                # pytesseract is configured via path if needed
                self.pytesseract = pytesseract
                logger.info("Tesseract engine initialized")
            else:
                logger.warning(f"Unknown OCR engine: {self.engine_type}, falling back to EasyOCR")
                import easyocr
                self.reader = easyocr.Reader(self.languages, gpu=False)
                self.engine_type = 'easyocr'
        except ImportError as e:
            logger.error(f"Failed to import OCR library: {e}. Please install required packages.")
            self.reader = None
        except Exception as e:
            logger.error(f"Failed to initialize OCR engine: {e}")
            self.reader = None

    def _load_ocr_regions(self) -> None:
        """Load OCR region coordinates from locations.xml"""
        try:
            # Use the global locations.xml file from parent directory
            location_file = Path(__file__).parent.parent.parent / "locations.xml"

            if not location_file.exists():
                logger.error(f"Location XML file not found: {location_file}")
                return

            # Parse the XML file
            tree = ET.parse(location_file)
            root = tree.getroot()

            # Default screen size (same as GameNavigator)
            screen_width, screen_height = 540, 960

            # Parse preset elements
            for preset in root.findall('.//preset'):
                try:
                    preset_name = preset.get('name')
                    if not preset_name:
                        continue

                    # Extract coordinate attributes
                    x_loc = preset.get('xLoc')
                    y_loc = preset.get('yLoc')
                    x_dest = preset.get('xDest')
                    y_dest = preset.get('yDest')

                    if x_loc and y_loc and x_dest and y_dest:
                        # Convert to float and calculate pixel coordinates
                        x1 = int(float(x_loc) * screen_width)
                        y1 = int(float(y_loc) * screen_height)
                        x2 = int(float(x_dest) * screen_width)
                        y2 = int(float(y_dest) * screen_height)

                        self.regions[preset_name] = (x1, y1, x2, y2)

                except Exception as e:
                    logger.warning(f"Failed to parse preset {preset.get('name', 'unknown')}: {e}")

            logger.info(f"Loaded {len(self.regions)} OCR regions from {location_file}")

        except Exception as e:
            logger.error(f"Failed to load OCR regions from XML: {e}")

    def _bytes_to_image(self, image_bytes: bytes) -> Optional[Image.Image]:
        """Convert bytes to PIL Image"""
        try:
            return Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"Failed to convert bytes to image: {e}")
            return None

    def _crop_image(self, image: Image.Image, region: Tuple[int, int, int, int]) -> Image.Image:
        """Crop image to region"""
        x1, y1, x2, y2 = region
        return image.crop((x1, y1, x2, y2))

    def _save_debug_image(self, image: Image.Image, region: str) -> None:
        """Save image to debug directory for review"""
        try:
            # Create debug directory if it doesn't exist
            debug_dir = "debug_images"
            os.makedirs(debug_dir, exist_ok=True)
            
            # Create filename with region only (no timestamp)
            filename = f"{debug_dir}/ocr_{region}.png"
            
            # Save the image
            image.save(filename, "PNG")
            logger.debug(f"Saved debug image: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save debug image: {e}")

    def extract_text(self, image_bytes: bytes, region: Optional[str] = None) -> Optional[OCRResult]:
        """Extract text from image region"""
        try:
            if not self.reader and self.engine_type != 'tesseract':
                logger.error("OCR engine not initialized")
                return None

            # Convert bytes to image
            image = self._bytes_to_image(image_bytes)
            if not image:
                return None

            # Crop to region if specified
            if region and region in self.regions:
                image = self._crop_image(image, self.regions[region])
                logger.debug(f"Cropped image to region: {region}")
                
                # Save cropped image for debugging
                if self.config.get('debug_mode', False):
                    self._save_debug_image(image, region)
                    
            elif region:
                logger.warning(f"Unknown region: {region}, processing full image")

            # Preprocess if enabled
            if self.preprocessing_enabled:
                # Apply region-specific preprocessing
                if region == "GeneralsListExp":
                    # Special preprocessing for experience text (light yellow on dark background)
                    image = self._enhance_light_text(image)
                    image = self._remove_green_elements(image)
                    # Convert to grayscale and enhance
                    image = image.convert('L')
                    from PIL import ImageEnhance
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(2.5)  # Higher contrast for light text
                    enhancer = ImageEnhance.Sharpness(image)
                    image = enhancer.enhance(2.0)  # More sharpening for light text
                else:
                    # Standard preprocessing for other regions
                    image = self.preprocess_image(image)
                
                # Save postprocessed image for debugging
                if self.config.get('debug_mode', False):
                    self._save_debug_image(image, f"{region}_postprocessed" if region else "postprocessed")

            # Convert to numpy array for EasyOCR
            if self.engine_type == 'easyocr':
                image_np = np.array(image)
                
                # Run OCR
                results = self.reader.readtext(image_np)
                
                if not results:
                    return None
                
                # Combine all detected text
                text_parts = []
                total_confidence = 0.0
                
                for (bbox, text, confidence) in results:
                    if confidence >= self.confidence_threshold:
                        text_parts.append(text)
                        total_confidence += confidence
                
                if not text_parts:
                    return None
                
                combined_text = ' '.join(text_parts)
                avg_confidence = total_confidence / len(text_parts)
                
                return OCRResult(text=combined_text, confidence=avg_confidence)
                
            elif self.engine_type == 'tesseract':
                # For Tesseract
                text = self.pytesseract.image_to_string(image)
                confidence = 0.9  # Tesseract doesn't provide per-character confidence easily
                
                if text.strip() and confidence >= self.confidence_threshold:
                    return OCRResult(text=text.strip(), confidence=confidence)
                else:
                    return None

        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return None

    def extract_number(self, image_bytes: bytes, region: Optional[str] = None) -> Optional[NumberResult]:
        """Extract number from image region"""
        try:
            text_result = self.extract_text(image_bytes, region)
            if not text_result:
                return None
            
            # Try to extract number from text, handling both comma-separated and plain numbers
            import re
            # Match numbers that may contain commas (e.g., "143,657") or plain numbers (e.g., "1234567")
            matches = re.findall(r'\d+(?:,\d{3})*', text_result.text)
            
            if matches:
                # Clean each match and convert to int
                values = []
                for match in matches:
                    clean_number = match.replace(',', '')
                    try:
                        values.append(int(clean_number))
                    except ValueError:
                        continue
                
                if values:
                    # Take the largest value (most likely to be the power number)
                    value = max(values)
                    # Reduce confidence slightly for number extraction
                    confidence = text_result.confidence * 0.95
                    return NumberResult(value=value, confidence=confidence)
            
            return None

        except Exception as e:
            logger.error(f"Number extraction error: {e}")
            return None

    def extract_image(self, image_bytes: bytes, region: Optional[str] = None) -> Optional[bytes]:
        """Extract image region as bytes"""
        try:
            image = self._bytes_to_image(image_bytes)
            if not image:
                return None

            # Crop to region if specified
            if region and region in self.regions:
                image = self._crop_image(image, self.regions[region])
                
                # Save debug image for image extraction
                if self.config.get('debug_mode', False):
                    self._save_debug_image(image, region)
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()

        except Exception as e:
            logger.error(f"Image extraction error: {e}")
            return None

    def _remove_green_elements(self, image: Image.Image) -> Image.Image:
        """Remove green UI elements (like progress bars) that interfere with OCR"""
        try:
            import cv2
            import numpy as np

            # Convert PIL to numpy array
            image_np = np.array(image)

            # Convert RGB to HSV for better color detection
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)

            # Define a more restrictive green color range for progress bars
            # Focus on bright, saturated green (typical progress bar colors)
            lower_green = np.array([33, 53, 0])  # More restrictive
            upper_green = np.array([181, 255, 123])

            # Create mask for green pixels
            green_mask = cv2.inRange(hsv, lower_green, upper_green)

            # Apply morphological opening to remove noise and small elements
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)

            # Find contours and filter by size and aspect ratio (progress bars are usually thin rectangles)
            contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Create a new mask for elements to remove
            removal_mask = np.zeros_like(green_mask)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 20 and area < 2000:  # Size range for progress bars
                    # Check aspect ratio (progress bars are usually wide and thin)
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0

                    # Progress bars are typically much wider than tall
                    if aspect_ratio > 2.0:
                        cv2.drawContours(removal_mask, [contour], -1, 255, -1)

            # Apply the removal mask to the original image
            # Only replace pixels that are both green AND in our removal mask
            final_mask = cv2.bitwise_and(green_mask, removal_mask)

            # Create result image
            result = image_np.copy()

            # Replace masked areas with the dominant background color
            # Instead of white, use a color that blends better
            background_color = self._estimate_background_color(image_np, final_mask)
            result[final_mask > 0] = background_color

            # Convert back to PIL Image
            result_image = Image.fromarray(result)

            logger.debug(f"Removed {np.sum(final_mask > 0)} green pixels from progress bars")
            return result_image

        except ImportError:
            logger.warning("OpenCV not available, skipping green element removal")
            return image
        except Exception as e:
            logger.error(f"Failed to remove green elements: {e}")
            return image

    def _estimate_background_color(self, image_np, mask):
        """Estimate the background color from non-masked areas"""
        # Sample pixels from areas not in the mask
        background_pixels = image_np[mask == 0]

        if len(background_pixels) > 0:
            # Return the most common color (simplified as mean)
            return np.mean(background_pixels, axis=0).astype(np.uint8)
        else:
            # Fallback to a neutral gray
            return np.array([128, 128, 128])

    def _enhance_light_text(self, image: Image.Image) -> Image.Image:
        """Enhance light colored text (like yellow) on dark backgrounds"""
        try:
            import cv2
            import numpy as np
            
            # Convert PIL to numpy array
            image_np = np.array(image)
            
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
            
            # Create masks for light colors (yellow/white text)
            # Light yellow: Hue 20-40, Saturation 30-255, Value 140-255 (expanded ranges)
            lower_light_yellow = np.array([20, 30, 140])
            upper_light_yellow = np.array([40, 255, 255])
            
            # Also catch very bright white/light colors
            lower_bright = np.array([0, 0, 160])  # Very bright pixels
            upper_bright = np.array([180, 40, 255])  # Low saturation, high value
            
            light_mask1 = cv2.inRange(hsv, lower_light_yellow, upper_light_yellow)
            light_mask2 = cv2.inRange(hsv, lower_bright, upper_bright)
            light_mask = cv2.bitwise_or(light_mask1, light_mask2)
            
            # Apply morphological operations to clean up the text mask
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            light_mask = cv2.morphologyEx(light_mask, cv2.MORPH_CLOSE, kernel)
            
            # Create enhanced image
            enhanced = image_np.copy().astype(np.float32)
            
            # More aggressive enhancement for light text
            if np.sum(light_mask > 0) > 0:
                # Boost brightness significantly for detected light areas
                enhanced[light_mask > 0] = np.clip(enhanced[light_mask > 0] * 1.8 + 50, 0, 255)
            
            # Darken background areas, but not as aggressively
            dark_mask = cv2.bitwise_not(light_mask)
            if np.sum(dark_mask > 0) > 0:
                enhanced[dark_mask > 0] = enhanced[dark_mask > 0] * 0.6
            
            # Additional pass: enhance any remaining light pixels that might be text
            final_hsv = cv2.cvtColor(enhanced.astype(np.uint8), cv2.COLOR_RGB2HSV)
            additional_light = cv2.inRange(final_hsv, np.array([0, 0, 200]), np.array([180, 50, 255]))
            
            # Boost any additional bright areas
            enhanced[additional_light > 0] = np.clip(enhanced[additional_light > 0] * 1.2 + 20, 0, 255)
            
            # Convert back to uint8
            enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
            
            # Convert back to PIL Image
            result_image = Image.fromarray(enhanced)
            
            logger.debug(f"Enhanced {np.sum(light_mask > 0)} light text pixels")
            return result_image
            
        except ImportError:
            logger.warning("OpenCV not available, skipping light text enhancement")
            return image
        except Exception as e:
            logger.error(f"Failed to enhance light text: {e}")
            return image

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy"""
        if not self.preprocessing_enabled:
            return image

        try:
            # Check if this is an experience region (light yellow text on dark background)
            # For now, apply general preprocessing, but we could enhance this based on region
            image = self._enhance_light_text(image)
            
            # Remove green progress bars that interfere with text
            image = self._remove_green_elements(image)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Apply slight sharpening
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)
            
            logger.debug("Image preprocessing applied")
            return image
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return image