"""
Excel Exporter for generating formatted Excel spreadsheets
"""

import logging
from typing import List, Optional, Any
from pathlib import Path
import openpyxl
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO

from models.general import General

logger = logging.getLogger(__name__)

class ExcelExporter:
    """Handles Excel export functionality"""

    def __init__(self, config: dict):
        self.config = config
        self.template_path = config.get('excel_template_path', 'Resources/EvonyActiveGenerals.xltx')

    def export_generals(self, generals: List[General], file_path: str, count_text: str = "") -> bool:
        """Export generals data to Excel file"""
        try:
            logger.info(f"Exporting {len(generals)} generals to {file_path}")

            # Create or load workbook
            workbook = self.create_workbook(self.template_path)
            if not workbook:
                logger.error("Failed to create workbook")
                return False

            worksheet = workbook.active
            if not worksheet:
                worksheet = workbook.create_sheet("Generals")

            # Write count text to B3 if provided
            if count_text:
                worksheet.cell(row=3, column=2, value=count_text)
                logger.info(f"Wrote count text to B3: {count_text}")

            # Clear existing data rows (keep headers)
            self.clear_data_rows(worksheet)

            # Populate with general data
            self.populate_data(worksheet, generals)

            # Apply formatting
            self.format_cells(worksheet, len(generals))

            # Insert images
            self.insert_images(worksheet, generals)

            # Save file
            workbook.save(file_path)
            logger.info(f"Excel export completed: {file_path}")

            return True

        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            return False

    def create_workbook(self, template_path: Optional[str] = None) -> Optional[Any]:
        """Create or load Excel workbook"""
        try:
            if template_path and Path(template_path).exists():
                logger.info(f"Loading template: {template_path}")
                return openpyxl.load_workbook(template_path)
            else:
                logger.info("Creating new workbook")
                workbook = openpyxl.Workbook()
                # Create headers
                worksheet = workbook.active
                headers = [
                    "Name", "Level", "Type", "Power", "Experience Ratio",
                    "Stars", "Cultivation", "Specialty", "Covenant", "Uncertain"
                ]
                for col, header in enumerate(headers, 1):
                    worksheet.cell(row=1, column=col, value=header)
                return workbook
        except Exception as e:
            logger.error(f"Failed to create workbook: {e}")
            return None

    def clear_data_rows(self, worksheet: Any) -> None:
        """Clear existing data rows in workbook"""
        try:
            # Clear from row 6 onwards (keep headers and any template content above)
            for row in range(6, worksheet.max_row + 1):
                for col in range(1, worksheet.max_column + 1):
                    worksheet.cell(row=row, column=col).value = None
            logger.info("Cleared existing data rows")
        except Exception as e:
            logger.error(f"Failed to clear data rows: {e}")

    def populate_data(self, worksheet: Any, generals: List[General]) -> None:
        """Populate worksheet with general data"""
        try:
            for row, general in enumerate(generals, 6):  # Start from row 6
                worksheet.cell(row=row, column=1, value=general.name or "")
                worksheet.cell(row=row, column=2, value=general.level)
                worksheet.cell(row=row, column=3, value=general.type or "")
                worksheet.cell(row=row, column=4, value=general.power)
                worksheet.cell(row=row, column=5, value=general.exp_ratio or "")
                # Stars column (6) will have image
                worksheet.cell(row=row, column=7, value=general.cultivation_data or "")
                worksheet.cell(row=row, column=8, value=general.specialty_data or "")
                worksheet.cell(row=row, column=9, value=general.covenant_data or "")
                worksheet.cell(row=row, column=10, value="Yes" if general.is_uncertain else "No")

            logger.info(f"Populated data for {len(generals)} generals")
        except Exception as e:
            logger.error(f"Failed to populate data: {e}")

    def format_cells(self, worksheet: Any, num_generals: int) -> None:
        """Apply formatting to worksheet cells"""
        try:
            # Define styles
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")

            data_alignment = Alignment(horizontal="left", vertical="top")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

            # Format headers
            for col in range(1, 11):
                cell = worksheet.cell(row=1, column=col)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border

            # Format data cells
            for row in range(6, num_generals + 6):
                for col in range(1, 11):
                    cell = worksheet.cell(row=row, column=col)
                    cell.alignment = data_alignment
                    cell.border = border

            # Apply number formatting to power column (column 4)
            from openpyxl.styles import NamedStyle
            number_style = NamedStyle(name='number_with_commas', number_format='#,##0')
            for row in range(6, num_generals + 6):
                cell = worksheet.cell(row=row, column=4)
                cell.style = number_style

            # Auto-adjust column widths
            for col in range(1, 11):
                column_letter = get_column_letter(col)
                max_length = 0
                for row in range(1, num_generals + 6):
                    cell_value = worksheet.cell(row=row, column=col).value
                    if cell_value:
                        max_length = max(max_length, len(str(cell_value)))
                adjusted_width = min(max_length + 2, 50)  # Cap at 50
                worksheet.column_dimensions[column_letter].width = adjusted_width

            # Auto-adjust row heights based on content
            for row in range(1, num_generals + 6):
                max_height = 15  # Default height
                for col in range(1, 11):
                    cell_value = worksheet.cell(row=row, column=col).value
                    if cell_value:
                        # Estimate height based on text length (rough approximation)
                        text_length = len(str(cell_value))
                        # For multi-line content (like specialty data), estimate lines
                        if '\n' in str(cell_value):
                            lines = str(cell_value).count('\n') + 1
                            estimated_height = lines * 15  # 15 points per line
                        else:
                            # Single line, but wrap if very long
                            estimated_height = min(text_length // 50 + 1, 5) * 15
                        max_height = max(max_height, estimated_height)
                worksheet.row_dimensions[row].height = max_height

            # Special width for stars column (images)
            worksheet.column_dimensions['F'].width = 15

            logger.info("Applied cell formatting")
        except Exception as e:
            logger.error(f"Failed to format cells: {e}")

    def insert_images(self, worksheet: Any, generals: List[General]) -> None:
        """Insert images into worksheet"""
        try:
            for row, general in enumerate(generals, 6):  # Start from row 6
                if general.stars_image and len(general.stars_image) > 0:
                    try:
                        # Create image from bytes
                        image_stream = BytesIO(general.stars_image)
                        img = XLImage(image_stream)

                        # Resize image to fit cell
                        img.width = 60
                        img.height = 20

                        # Add image to worksheet
                        worksheet.add_image(img, f'F{row}')

                    except Exception as img_error:
                        logger.warning(f"Failed to insert image for general {general.name}: {img_error}")

                # Add type image if available
                if general.type_image and len(general.type_image) > 0:
                    try:
                        # Create image from bytes
                        image_stream = BytesIO(general.type_image)
                        img = XLImage(image_stream)

                        # Resize image to fit cell
                        img.width = 40
                        img.height = 20

                        # Add image to worksheet
                        worksheet.add_image(img, f'C{row}')

                    except Exception as img_error:
                        logger.warning(f"Failed to insert type image for general {general.name}: {img_error}")

            logger.info(f"Inserted images for {len(generals)} generals")
        except Exception as e:
            logger.error(f"Failed to insert images: {e}")