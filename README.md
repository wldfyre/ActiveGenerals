# Evony Active Generals Tracker

A Python application that automates the extraction of general information from the Evony MMO game and exports it to Excel.

## Features

- **Automated Data Collection**: Automatically navigates through Evony's interface to collect general data
- **OCR Integration**: Uses advanced OCR to extract text from game screenshots
- **Cross-Platform Support**: Works with Bluestacks emulator and Android devices
- **Excel Export**: Generates formatted Excel spreadsheets with images and data
- **Progress Tracking**: Real-time progress updates and detailed statistics
- **Configurable Settings**: Adjustable OCR confidence thresholds, delays, and export options

## Requirements

- Python 3.8+
- PyQt5
- ADB (Android Debug Bridge)
- Bluestacks or Android device with Evony installed

## Installation

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install ADB if not already installed
4. Ensure Evony is running on Bluestacks or Android device

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Configure connection settings:
   - Select platform (bluestacks/android)
   - Set device ID (default: 127.0.0.1:5555 for Bluestacks)
   - Browse to ADB executable location

3. Click "Connect" to establish connection

4. Adjust settings as needed:
   - OCR Engine (easyocr/tesseract)
   - Confidence threshold
   - Transition delays

5. Click "Start Collection" to begin data extraction

6. Monitor progress in the Progress tab

7. Export results to Excel when collection is complete

## Configuration

The application uses `config.json` for settings:

```json
{
  "platform_type": "bluestacks",
  "adb_path": "",
  "device_id": "127.0.0.1:5555",
  "ocr_engine": "easyocr",
  "confidence_threshold": 0.8,
  "screen_transition_delay": 1.5,
  "navigation_retry_count": 3,
  "debug_mode": false
}
```

## Data Collected

For each general, the application extracts:

- **Basic Info**: Name, Level, Type, Power, Experience Ratio
- **Stars**: Star rating image
- **Cultivation**: Leadership, Attack, Defense, Politics stats
- **Specialties**: Up to 5 specialty icons with names
- **Covenant**: Covenant information and related generals

## Architecture

The application follows a modular architecture:

- **UI Layer**: PyQt5-based user interface
- **Controller**: Orchestrates data collection workflow
- **Platform Interface**: Handles ADB communication
- **OCR Engine**: Text extraction from screenshots
- **Game Navigator**: Automated interface navigation
- **Data Models**: Structured data storage
- **Excel Exporter**: Spreadsheet generation

## Troubleshooting

### Connection Issues
- Ensure ADB is installed and in PATH
- Check device ID is correct
- Verify Evony is running on target device

### OCR Accuracy
- Adjust confidence threshold
- Enable debug mode for preprocessing images
- Ensure good screenshot quality

### Navigation Failures
- Increase transition delays
- Check coordinate presets are up to date
- Verify Evony interface hasn't changed

## Development

The application is structured as follows:

```
ActiveGenerals/
├── main.py                 # Application entry point
├── main_window.ui         # Qt Designer UI file
├── main_window_ui.py      # Generated UI code
├── config.json           # Configuration file
├── requirements.txt      # Python dependencies
├── docs/                 # Documentation
├── ui/                   # UI components
├── controllers/          # Application logic
├── models/              # Data models
├── platform_adb/        # Platform interfaces
├── ocr/                 # OCR functionality
├── navigation/          # Game navigation
├── export/              # Excel export
└── Resources/           # Templates and coordinates
```

## License

This project is for educational and personal use only. Please respect Evony's terms of service.