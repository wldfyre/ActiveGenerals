# Evony Active Generals Tracker - Executable Version

This is a standalone executable version of the Evony Active Generals Tracker application, packaged for easy distribution and deployment.

## System Requirements

- Windows 10 or later (64-bit)
- No Python installation required
- Approximately 500MB free disk space for the executable and temporary files

## Installation

1. Download the `EvonyActiveGenerals.exe` file
2. Place it in a folder where you have write permissions
3. Ensure the following files are in the same directory as the executable:
   - `config.json` (configuration file)
   - `Resources/` folder (contains template images and resources)

## Usage

1. Double-click `EvonyActiveGenerals.exe` to start the application
2. The application will open a GUI window
3. Configure your settings as needed
4. Use the application to capture and analyze Evony game data

## Features

- Automated screenshot capture from Evony mobile game
- OCR (Optical Character Recognition) for text extraction
- Excel export with formatted spreadsheets
- Image processing and enhancement
- Progress tracking and logging

## Troubleshooting

- If the application fails to start, ensure all required files are present
- Check the log file `evony_tracker.log` for error messages
- Make sure you have sufficient RAM (at least 4GB recommended)
- The application may take some time to start on first run due to initialization

## File Structure

```
YourFolder/
├── EvonyActiveGenerals.exe    # Main executable
├── config.json               # Configuration file
├── Resources/                # Resource files (images, templates)
│   ├── EvonyActiveGenerals.xltx
│   └── EvonyGeneralsCoords.txt
└── evony_tracker.log         # Log file (created automatically)
```

## Technical Details

- Built with PyInstaller
- Includes PyQt5 GUI framework
- Uses EasyOCR for text recognition
- Supports OpenCV for image processing
- Exports to Excel format with OpenPyXL

## Support

For issues or questions, please refer to the main project repository or documentation.