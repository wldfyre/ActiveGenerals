# Evony Active Generals Tracker - Architecture Overview

## High-Level Architecture

```mermaid
graph TD
    A[User Interface<br/>PyQt5 + Dark Mode] --> B[Application Controller<br/>Orchestration Logic]
    B --> C[Platform Interface<br/>ADB Communication]
    B --> D[OCR Engine<br/>Text Extraction]
    B --> E[Game Navigator<br/>UI Automation]
    B --> F[Excel Exporter<br/>Data Export]

    C --> G[Device Connection<br/>Screenshot Capture]
    D --> H[Text Recognition<br/>Confidence Scoring]
    E --> I[Coordinate Navigation<br/>Screen Transitions]
    F --> J[Spreadsheet Generation<br/>Template Processing]

    B --> K[General Data Models<br/>Confidence Tracking]
    K --> L[JSON Serialization<br/>Uncertainty Flags]

    M[Configuration Manager<br/>JSON Settings] --> A
    M --> B

    N[Background Worker<br/>Threading] --> B

    O[Logging System] --> P[File + Console Output]
```

## Component Responsibilities

### 🎯 **Main Entry Point** (`main.py`)
- Application bootstrap and Qt initialization
- Logging configuration setup
- High-DPI scaling support

### 🖥️ **User Interface** (`ui/main_window.py`)
- PyQt5-based GUI with custom dark theming
- Configuration management interface
- Progress tracking and status display
- Background thread coordination

### ⚙️ **Application Controller** (`controllers/application_controller.py`)
- **Central orchestration hub** coordinating all components
- Platform initialization and lifecycle management
- Data collection workflow management
- Progress callback handling and error recovery

### 🔧 **Platform Interface** (`platform_adb/bluestacks_interface.py`)
- ADB shell command execution
- Device connectivity management
- Screenshot capture from game device
- Connection state monitoring

### 👁️ **OCR Engine** (`ocr/ocr_engine.py`)
- Text extraction from game screenshots
- Multiple OCR engine support (EasyOCR/Tesseract)
- Coordinate-based text region detection
- Confidence scoring for data quality

### 🧭 **Game Navigator** (`navigation/game_navigator.py`)
- In-game UI automation using coordinates
- Screen transition management with delays
- Navigation state validation
- Retry logic for failed operations

### 📊 **Data Models** (`models/general.py`)
- General information data structures
- Confidence score tracking per field
- Uncertainty flag management
- JSON serialization support

### 📈 **Excel Exporter** (`export/excel_exporter.py`)
- Spreadsheet generation using OpenPyXL
- Template-based formatting
- Image embedding for specialties/covenants
- Auto-open functionality

### 🔧 **Configuration Manager** (`config/config_manager.py`)
- JSON-based settings management
- Default configuration handling
- Runtime configuration updates
- Settings persistence

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant UI as MainWindow
    participant AC as ApplicationController
    participant PI as PlatformInterface
    participant GN as GameNavigator
    participant OE as OCREngine
    participant DM as DataModels
    participant EE as ExcelExporter

    U->>UI: Click "Connect"
    UI->>AC: initialize_platform()
    AC->>PI: connect()
    PI-->>AC: connection_status
    AC-->>UI: connection_result

    U->>UI: Click "Start Collection"
    UI->>AC: collect_all_generals()
    AC->>GN: navigate_to_generals_list()
    GN->>PI: execute_adb_commands()
    PI-->>GN: navigation_result

    AC->>GN: get_total_generals_count()
    GN->>PI: capture_screenshot()
    PI-->>GN: screenshot_data
    GN->>OE: extract_number()
    OE-->>GN: count_result
    GN-->>AC: total_count

    loop For each general
        AC->>GN: open_general_details(index)
        GN->>PI: tap_coordinates()
        PI-->>GN: tap_result

        AC->>PI: capture_screenshot()
        PI-->>AC: screenshot
        AC->>OE: extract_main_data()
        OE-->>AC: general_data
        AC->>DM: create_general()

        AC->>GN: navigate_to_cultivation()
        GN->>PI: capture_screenshot()
        PI-->>GN: cult_screenshot
        GN->>OE: extract_cultivation_data()
        OE-->>GN: cultivation_data
        GN-->>AC: cultivation_result

        AC->>DM: update_general(cultivation)
    end

    AC->>EE: export_to_excel()
    EE-->>AC: export_result
    AC-->>UI: collection_complete
    UI-->>U: Show results
```

## Key Interaction Patterns

### **Initialization Pattern**
```
ConfigManager → MainWindow → ApplicationController → [Platform, OCR, Navigator, Exporter]
```

### **Collection Pattern**
```
MainWindow → CollectionWorker → ApplicationController → GameNavigator → PlatformInterface
                                                            ↓
                                                     OCREngine → DataModels
```

### **Export Pattern**
```
MainWindow → ApplicationController → ExcelExporter → OpenPyXL → Excel File
```

### **Feedback Pattern**
```
ApplicationController → Progress Callbacks → MainWindow → UI Updates
```

## Error Handling Strategy

- **Platform Errors**: Connection failures → User notification with retry options
- **OCR Errors**: Low confidence → Uncertainty flags on data
- **Navigation Errors**: Timeout/retry logic with configurable attempts
- **Threading Errors**: Graceful interruption and cleanup
- **Export Errors**: Fallback to basic export without advanced formatting

## Configuration Flow

```mermaid
graph LR
    A[Default Config] --> B[Load from JSON]
    B --> C[Runtime Updates]
    C --> D[Save to JSON]
    D --> E[Persist Settings]

    F[UI Controls] --> C
    C --> G[Component Updates]
    G --> H[Apply Settings]
```

This architecture provides a clean separation of concerns with the ApplicationController serving as the central coordination point, ensuring maintainable and testable code structure.