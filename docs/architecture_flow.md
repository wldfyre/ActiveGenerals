# Evony Active Generals Tracker - Module Interaction Flow

```mermaid
graph TB
    %% Entry Point
    A[main.py] --> B[MainWindow<br/>UI Layer]

    %% Configuration Layer
    B --> C[ConfigManager]
    C --> D[config.json]

    %% UI Layer
    B --> E[ApplicationController<br/>Business Logic]

    %% Controller Dependencies
    E --> F[BluestacksInterface<br/>Platform Layer]
    E --> G[OCREngine<br/>OCR Layer]
    E --> H[GameNavigator<br/>Navigation Layer]
    E --> I[ExcelExporter<br/>Export Layer]

    %% Platform Layer Details
    F --> J[ADB Shell Commands]
    F --> K[Screenshot Capture]

    %% OCR Layer Details
    G --> L[EasyOCR/Tesseract]
    G --> M[Text Extraction<br/>Presets]

    %% Navigation Layer Details
    H --> N[Coordinate-based<br/>UI Automation]
    H --> O[Screen Transitions]

    %% Data Flow
    E --> P[General Model<br/>Data Objects]
    P --> Q[Confidence Scoring]
    P --> R[Uncertainty Flags]

    %% Export Layer Details
    I --> S[OpenPyXL<br/>Excel Generation]
    I --> T[Template Processing]

    %% UI Feedback Loop
    E --> U[Progress Callbacks]
    U --> B
    E --> V[Collection Results]
    V --> B

    %% Threading
    B --> W[CollectionWorker<br/>Background Thread]
    W --> E

    %% Styling
    B --> X[Dark Mode Theme<br/>Custom Styling]

    %% Logging
    Y[Logging System] --> A
    Y --> B
    Y --> E
    Y --> F
    Y --> G
    Y --> H
    Y --> I

    %% External Dependencies
    Z[PyQt5] --> B
    AA[OpenCV] --> G
    BB[ADB] --> F
    CC[OpenPyXL] --> I

    %% Data Persistence
    P --> DD[JSON Serialization]
    DD --> EE[Temp Directory]

    %% Configuration Flow
    C -.->|Load| B
    B -.->|Save| C

    %% Main Collection Flow
    subgraph "Main Collection Process"
        FF[Navigate to Generals List] --> GG[Count Generals]
        GG --> HH[Process Each General]
        HH --> II[Extract Main Data]
        II --> JJ[Extract Cultivation Data]
        JJ --> KK[Extract Specialty Data]
        KK --> LL[Extract Covenant Data]
        LL --> MM[Calculate Confidence]
        MM --> NN[Mark Uncertain if Low Confidence]
    end

    E --> FF

    %% Styling
    classDef entryPoint fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef uiLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef controllerLayer fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef dataLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef external fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef process fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px

    class A entryPoint
    class B,C uiLayer
    class E,F,G,H,I controllerLayer
    class P,Q,R dataLayer
    class Z,AA,BB,CC,Y external
    class FF,GG,HH,II,JJ,KK,LL,MM,NN process
```

## Module Interaction Overview

### **Entry Point Layer**
- **`main.py`**: Application bootstrap, logging setup, Qt application initialization

### **UI Layer**
- **`MainWindow`**: PyQt5-based GUI with dark mode theming
- **`ConfigManager`**: JSON-based configuration management with defaults
- **Threading**: `CollectionWorker` handles background data collection

### **Controller Layer**
- **`ApplicationController`**: Main orchestration logic, coordinates all components
- **Initialization**: Sets up platform, OCR, navigation, and export components
- **Progress Tracking**: Manages callbacks and status updates

### **Platform Layer**
- **`BluestacksInterface`**: ADB-based device communication
- **Screenshot Capture**: Device screen capture for OCR processing
- **Connection Management**: Device connectivity and session handling

### **OCR Layer**
- **`OCREngine`**: Text extraction from game screenshots
- **Preset-based Extraction**: Uses coordinate presets for different data types
- **Confidence Scoring**: Quality assessment for extracted data

### **Navigation Layer**
- **`GameNavigator`**: UI automation within the Evony game
- **Coordinate Navigation**: Tap coordinates for menu navigation
- **Screen Transitions**: Handles delays and state changes

### **Data Layer**
- **`General Model`**: Dataclass representing general information
- **Confidence Tracking**: Per-field confidence scores
- **Uncertainty Flags**: Marks low-confidence extractions

### **Export Layer**
- **`ExcelExporter`**: Spreadsheet generation using OpenPyXL
- **Template Processing**: Uses Excel template for formatting
- **Data Formatting**: Converts model data to spreadsheet format

### **Key Data Flows**

1. **Configuration Flow**: `main.py` → `ConfigManager` → `MainWindow` → `ApplicationController`
2. **Collection Flow**: `MainWindow` → `CollectionWorker` → `ApplicationController` → Platform/OCR/Navigation
3. **Data Flow**: OCR/Navigation → `General` models → `ExcelExporter`
4. **Feedback Flow**: `ApplicationController` → Progress Callbacks → `MainWindow` UI updates

### **External Dependencies**
- **PyQt5**: GUI framework
- **OpenCV**: Image processing for OCR
- **ADB**: Android device communication
- **OpenPyXL**: Excel file manipulation
- **EasyOCR/Tesseract**: OCR engines

### **Process Flow Details**

The main collection process follows this sequence:
1. Navigate to generals list screen
2. Count total available generals
3. For each general:
   - Open general details
   - Capture and extract main data (name, level, type, power, exp)
   - Navigate to cultivation screen and extract stats
   - Navigate to specialties screen and extract abilities
   - Navigate to covenant screen and extract linked generals
   - Calculate overall confidence score
   - Mark as uncertain if confidence below threshold
4. Export collected data to Excel format

### **Error Handling & Recovery**
- Platform connection failures → User notification
- OCR extraction failures → Uncertainty flags
- Navigation timeouts → Retry logic with configurable attempts
- Thread interruption → Graceful collection stopping

### **Configuration Management**
- JSON-based configuration with sensible defaults
- Runtime configuration updates saved automatically
- Debug mode for enhanced logging
- Platform-specific settings (ADB paths, device IDs)