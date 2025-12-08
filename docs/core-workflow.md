# Core Iterative Logic Documentation

## Overview

This document describes the core iterative logic and workflow of the Evony Active Generals Tracker application. The system automates the extraction of general information from the Evony MMO game through a systematic, iterative process that combines platform interface automation, screen navigation, OCR processing, and data management.

### Coordinate System

The `locations.xml` file defines all click points and processing areas using normalized coordinates:

- **Coordinate Calculation**: 
  - `xLoc` and `xDest` are multiplied by screenshot width for actual coordinates
  - `yLoc` and `yDest` are multiplied by screenshot height for actual coordinates
- **Tap Actions**: Midpoint between `(xLoc, yLoc)` and `(xDest, yDest)` is used for device interaction
- **Image Processing**: `(xLoc, yLoc)` to `(xDest, yDest)` define rectangular extraction areas

- for debugging purposes, a navigation event which pulls coordinates from `locations.xml` should send the preset name and its associated calculated coordinates to the console





## Main Workflow Architecture

### High-Level Process Flow

```mermaid
graph TD
    A[Initialize Platform] --> B[Navigate to Generals List]
    B --> C[Set Generals List State]
    C --> D[Get Total Generals Count]
    D --> E{For Each General}
        E --> F[Open General Details]
        F --> G[Capture Screenshot]
        G --> H[Extract Main Data via OCR]
        H --> I[Navigate to Cultivation Screen]
        I --> J[Extract Cultivation Data]
        J --> K[Navigate to Specialties Screen]
        K --> L[Extract Specialty Data]
        L --> M[Navigate to Covenant Screen]
        M --> N[Extract Covenant Data]
        N --> O[Store Complete General Data]
        O --> P[Update Excel File Incrementally]
        P --> Q[Update UI Table in Real-time]
        Q --> R[Close Details Screen]
        R --> E
    E --> S[Final Excel Export (Optional)]
    S --> T[Reset Generals List State]
    T --> U[Cleanup & Disconnect]


## Detailed Workflow Steps

### 1. Platform Initialization Phase

**Purpose**: Establish connection with the target device/emulator

**Process**:
- Initialize platform interface (ADB for Android/Bluestacks for Windows)
- Create OCR engine instance with configured settings
- Initialize game navigator with coordinate presets
- Establish connection to device

**Error Handling**:
- Retry connection up to 3 attempts
- Fall back to different connection methods if available
- Log all connection attempts and failures

**Code Reference**: [`application_controller.py:80-123`](application_controller.py:80)

### 2. Navigation Phase

**Purpose**: Reach the generals list screen to begin data collection

**Navigation Path to Generals List**:
1. Navigate from current screen to access generals list by clicking "ThreeDots" button (wait 1.0s)
2. Tap "Generals" button (wait 1.0s)
3. Verify screen loaded successfully

**Error Handling**:
- Retry failed navigation actions up to 3 times
- Timeout protection for screen transitions
- Fallback navigation paths for different interface states

**Code Reference**: [`game_navigator.py:409-416`](game_navigator.py:409)

### 3. Generals List State Management Phase

**Purpose**: Ensure consistent generals list state for accurate data collection

**Process**:
- Set list filter to "All" mode for complete general coverage by clicking "All" button (wait 1.0s)
- Reset state change flags to False
- Verify and set each view mode if not already active:
  - **Mode View**: Compare current view to `GeneralsListMode.png` template
    - If mismatch detected: click "GeneralsListMode" preset and set state_change_flag = True
  - **Favorites View**: Compare current view to `GeneralsListFavorites.png` template  
    - If mismatch detected: click "GeneralsListFavorites" preset and set state_change_flag = True
  - **Idle View**: Compare current view to `GeneralsListIdle.png` template
    - If mismatch detected: click "GeneralsListIdle" preset and set state_change_flag = True

**State Tracking**:
- Maintains flags to track which view modes were modified
- Ensures consistent starting state for reliable navigation
- Template matching ensures accurate screen state detection
- After all generals information is collected, any states triggered as True will be clicked to reset state






### 3. General Counting Phase

**Purpose**: Determine total number of generals for accurate progress tracking

**Process**:
- Capture screenshot of generals list
- Extract image region using "GeneralsListCount" coordinates from `locations.xml`
- Use OCR to extract general count in format "current/total" (e.g., "45/100")
- Parse the count information for progress tracking, using the "current" value as the expected number of generals to iterate through

**Error Handling**:
- Retry extraction up to 3 times if failed
- Fallback to different extraction methods if available
- Use confidence scores to validate extraction success

**Count Information**:
- Format: "current_generals/total_available_slots"
- Used for progress calculation and completion detection
- Enables accurate time estimation for remaining collection

**Code Reference**: [`application_controller.py:214-256`](application_controller.py:214)

### 4. Core Iterative Collection Loop

**Purpose**: Collect detailed data for each individual general

**Process Flow**:

```mermaid
graph TD
    A[For First General] --> B[Open General Details]
    B --> C[Capture Screenshot]
    C --> D[Extract Main General Data]
    D --> E[Navigate to Cultivation Screen]
    E --> F[Extract Cultivation Data]
    F --> G[Navigate to Specialties Screen]
    G --> H[Extract Specialty Data]
    H --> I[Navigate to Covenant Screen]
    I --> J[Extract Covenant Data]
    J --> K[Store Complete General Data]
    K --> L[Close Details Screen]
    L --> M[Next General]
    M --> B
```

#### 4.1 General Navigation and Selection

**Process**:
- Calculate click coordinates, or image box from locations.xml
- Use coordinate presets to tap on a specific location, or clip a rectangular area

**Coordinate Calculation**:
- First general: click on centerpoint defined by "GeneralsFirstGeneral" calculated coordinates
- Subsequent generals: Click on centerpoint defined by "GeneralsNextGeneral" calculated coordinates
- Cultivate screen:  Click on centerpoint defined by "GeneralsListCultivate" calculated coordinates
- Specialty screen:  Click on centerpoint defined by "GeneralsListSpecialty" calculated coordinates
- Covenant screen:  Click on centerpoint defined by "GeneralsListCovenant" calculated coordinates
- Covenant sub screen:  Click on centerpoint defined by "GeneralsListCovenantGeneral" calculated coordinates
- Exit Covenant sub screen: Click on centerpoint defined by "GeneralsListCovenantXOut" calculated coordinates
- Exit each screen:  Click on centerpoint defined by "Back" calculated coordinates






**Error Handling**:
- **Retry Logic**: Failed navigation actions are automatically retried up to 3 times with progressive delays
- **Missing Presets**: If coordinate presets are not found in `locations.xml`, the system logs the specific preset item error, and exits gracefully
- **Logging**: All navigation failures are logged with coordinates, preset names, and error details for debugging
- **Graceful Degradation**: Navigation errors don't halt the entire collection process - the system continues with available data
- **Fallback Strategies**: Alternative navigation paths are attempted if primary navigation fails
- **Timeout Protection**: All navigation actions have timeout limits to prevent infinite waiting

**Code Reference**: [`game_navigator.py:418-447`](game_navigator.py:418)

#### 4.2 Screenshot Capture

**Process**:
- Capture high-resolution screenshot of general details
- Store screenshot for debugging if debug mode enabled
- Verify screenshot quality before proceeding

**Technical Details**:
- Screenshot format: PIL Image object
- Resolution: Device native resolution
- Timing: Immediately after screen transition

#### 4.3 Data Extraction via OCR Pipeline

**Purpose**: Extract structured data from general details screenshots across multiple screens

**Extraction Strategy**: The system navigates through five distinct screens per general to collect comprehensive data:
1. **Main Details Screen**: Basic general information
2. **Cultivation Screen**: Leadership, Attack, Defense, Politics stats
3. **Specialties Screen**: Specialty icons and names
4. **Covenant Screen**: Covenant attributes
5. **Covenant Sub Screen**: Covenant sub attributes



**Main General Details Screen**

| Field | location.xml name | Data Type | OCR Method | Excel Column |
|-------|------------------|-----------|------------|--------------|
| Name | GeneralsListName | Text | Text Extraction | A |
| Level | GeneralsListLevel | Text | Text Extraction | B |
| Type | GeneralsListType | Text | Text Extraction | C |
| Power | GeneralsListPower | Numeric | Numeric Extraction | D |
| Stars | GeneralsListStars | Image | Image Extraction | E |
| Experience | GeneralsListExp | Text | Text Extraction | F |

**Cultivation Screen**

| Field | location.xml name | Data Type | OCR Method | Excel Column |
|-------|------------------|-----------|------------|--------------|
| Leadership | GeneralsListCultivateLeadership | Text | Text Extraction | G |
| Attack | GeneralsListCultivateAttack | Text | Text Extraction | G (append as new line) |
| Defense | GeneralsListCultivateDefense | Text | Text Extraction | G (append as new line) |
| Politics | GeneralsListCultivatePolitics | Text | Text Extraction | G (append as new line) |

*Note: All cultivation data is concatenated into column G with newlines between each stat*


**Specialties Screen**

| Field | location.xml name | Data Type | OCR Method | Excel Column |
|-------|------------------|-----------|------------|--------------|
| Specialty Image 1 | GeneralsListSpecialtyImage1 | Image | Image Extraction | H |
| Specialty Name 1 | GeneralsListSpecialtyName | Text | Text Extraction | H (append with a preceding space, followed by a newline) |
| Specialty Image 2 | GeneralsListSpecialtyImage2 | Image | Image Extraction | H (append) |
| Specialty Name 2 | GeneralsListSpecialtyName | Text | Text Extraction | H (append with a preceding space, followed by a newline) |
| Specialty Image 3 | GeneralsListSpecialtyImage3 | Image | Image Extraction | H (append) |
| Specialty Name 3 | GeneralsListSpecialtyName | Text | Text Extraction | H (append with a preceding space, followed by a newline) |
| Specialty Image 4 | GeneralsListSpecialtyImage4 | Image | Image Extraction | H (append) |
| Specialty Name 4 | GeneralsListSpecialtyName | Text | Text Extraction | H (append with a preceding space, followed by a newline) |
| Specialty Image 5 | GeneralsListSpecialtyImage5 | Image | Image Extraction | H (append) |
| Specialty Name 5 | GeneralsListSpecialtyName | Text | Text Extraction | H (append with a preceding space, followed by a newline) |

*Note: All specialty data is concatenated into column H with each line containing an images and text, followed by a newline*

**Covenant Screen**
| Field | location.xml name | Data Type | OCR Method | Excel Column |
|-------|------------------|-----------|------------|--------------|
| Covenant Image| GeneralsListCovenantImage | Image | Image Extraction | I |


**Covenant Sub Screen**

| Field | location.xml name | Data Type | OCR Method | Excel Column |
|-------|------------------|-----------|------------|--------------|
| Covenant SubImage 1 | GeneralsListCovenantCoGenImage | Image | Image Extraction | I |
| Covenant SubName 1 | GeneralsListCovenantCoGenName | Text | Text Extraction | I (append with a preceding space, followed by a newline) |
| Covenant SubImage 2 | GeneralsListCovenantCoGenImage | Image | Image Extraction | I (append) |
| Covenant SubName 2 | GeneralsListCovenantCoGenName | Text | Text Extraction | I (append with a preceding space, followed by a newline) |
| Covenant SubImage 3 | GeneralsListCovenantCoGenImage | Image | Image Extraction | I (append) |
| Covenant SubName 3 | GeneralsListCovenantCoGenName | Text | Text Extraction | I (append with a preceding space, followed by a newline) |

*Note: All covenant data is concatenated into column I with each line containing an image, a space, and text, followed by a newline*
- Collecting data requires navigation on the sub screen as follows:
   A. Tap "GeneralsListCovenantGeneral" button (wait 1.0s)
   B. Iterate 3 times:
      1. Tap "GeneralsListCovenantRight" button (wait 1.0s)
      2. Collect GeneralsListCovenantCoGenName and GeneralsListCovenantCoGenImage
   C. Tap "GeneralsListCovenantXOut" button (wait 1.0s)
   




**OCR Processing Methods**:

- **Text Extraction**: Standard OCR for general text fields (names, types, experience ratios)
- **Numeric Extraction**: Specialized OCR for numbers (power)  
- **Image Extraction**: Direct image cropping and conversion to PNG bytes for Excel embedding


**OCR Processing Pipeline**:
1. **Region Extraction**: Crop screenshot to defined regions
2. **Image Preprocessing** (if enabled):
   - Convert to grayscale
   - Apply adaptive thresholding
   - Denoise with bilateral filter
   - Enhance contrast
3. **Text Extraction**:
   - Try primary OCR engine (EasyOCR or Tesseract)
   - Fallback to secondary engine if confidence < threshold
   - Apply confidence scoring
4. **Data Validation**:
   - Filter results with confidence < 50%
   - Convert numeric fields to appropriate types
   - Handle extraction failures gracefully

**Confidence Handling**:
- Accept results with confidence > 50%
- Flag general as "uncertain" if any field < 80% confidence
- Store confidence scores per field for quality assessment

**Code Reference**: [`ocr_engine.py:438-520`](ocr_engine.py:438)

#### 4.4 Image Extraction

**Process**:
- Extract image from screenshot using predefined regions
- Convert to PNG bytes for Excel embedding
- Handle extraction failures with empty bytes

**Technical Details**:
- Format: PNG image bytes
- Storage:  `general.type_image`
            `general.stars_image`
            `general.specialty_image1` 
            `general.specialty_image2` 
            `general.specialty_image3` 
            `general.specialty_image4` 
            `general.specialty_image5` 
            `general.covenant_image1` 
            `general.covenant_image2` 
            `general.covenant_image3` 
            

- Fallback: Empty bytes array if extraction fails

#### 4.5 Data Storage and Model Management

**Process**:
- Create `General` data object with extracted information
- Store confidence scores for quality tracking
- Add to generals collection in application controller
- **Update Excel file incrementally** after each general is processed
- **Update UI table in real-time** to show progress during collection
- Update progress information

**Incremental Export Benefits**:
- Data is saved immediately, preventing loss if collection is interrupted
- Users can review partial results during long collection processes
- Excel file remains available even if "Stop" button is clicked

**Real-time UI Updates**:
- Table refreshes after each general is processed
- Shows live progress instead of waiting for completion
- Provides immediate feedback on collection status

**Data Model Structure**:
```python
@dataclass
class General:
    # Core fields from main details screen
    name: str
    level: str
    type: str
    power: int
    exp_ratio: str
    stars_image: bytes
    
    # Concatenated data from subscreens (stored as CRLF-separated strings)
    cultivation_data: str  # "Leadership: 85+15\nAttack: 92+1\nDefense: 78+7\nPolitics: 81-3"
    specialty_data: str    # "'Specialty1 Icon'+' '+'Specialty1 Name'\n'Specialty2 Icon'+' '+'Specialty2 Name'\n'Specialty3 Icon'+' '+'Specialty3 Name'\n'Specialty4 Icon'+' '+'Specialty4 Name'\n'Specialty5 Icon'+' '+'Specialty5 Name'"
    covenant_data: str     # "'Covenant1 Icon'+' '+'Covenant1 Name'\n'Covenant2 Icon'+' '+'Covenant2 Name'\n'Covenant3 Icon'+ ' '+'Covenant3 Name'"
    
    # Metadata
    confidence_scores: Dict[str, float]
    is_uncertain: bool
    timestamp: datetime
```

**Code Reference**: [`application_controller.py:258-295`](application_controller.py:258)

#### 4.6 Screen Navigation and Cleanup

**Process**:
- Tap "Back" button to return to generals list
- Wait for screen transition
- Verify return to generals list
- Tap "GeneralsListMoveRight"
- Prepare for next iteration
- When done:
     close generals details screen
     reset Generals state for GeneralsListMode, GeneralsListFavorites, and GeneralsListIdle


**Navigation Path**:
1. Tap "Back" button (wait 1.0s)
2. Wait for generals list screen load (timeout: 10s)
3. Tap "GeneralsListMoveRight" button (wait 1.0s)


**Code Reference**: [`game_navigator.py:449-464`](game_navigator.py:449)

### 5. Progress Tracking and Reporting

**Purpose**: Provide real-time feedback and statistics

**Progress Information Tracked**:
- Current general index and total count
- Current workflow step
- Elapsed time and estimated remaining time
- Success/failure counts
- Average confidence scores

**Update Mechanism**:
- Progress callbacks notify UI components
- Status callbacks provide detailed step information
- Thread-safe updates for concurrent operation

**Progress Calculation**:
```python
percentage = (current_general / total_generals) * 100
estimated_remaining = (elapsed_time / current_general) * (total_generals - current_general)
```

**Code Reference**: [`application_controller.py:56-78`](application_controller.py:56)

### 6. Export Phase

**Purpose**: Convert collected data to Excel format

**Process**:
- Validate collected data completeness
- Create or load Excel workbook template
- Insert general data with proper formatting
- Embed images after resizing them by 50% (stars, cultivate, specialty and Covenant icons)
- Some cells will include image + text, and include multiple lines within the cell.  
- Apply cell formatting and styling

**Excel Export Features**:
- Template-based formatting support
- Image anchoring to prevent shifting
- Confidence-based cell highlighting
- Automatic file naming with timestamp

**Code Reference**: [`excel_exporter.py:1-100`](excel_exporter.py:1)

### 7. Cleanup and Disconnection

**Purpose**: Clean resources and disconnect from platform

**Process**:
- Disconnect from device/emulator
- Save configuration changes
- Clear temporary data
- Log final statistics

**Resource Management**:
- Platform connection cleanup
- OCR engine shutdown
- Temporary file cleanup
- Memory cleanup for large image data

## Error Handling and Recovery

### Error Categories

1. **Connection Errors**
   - Platform not detected
   - ADB connection failed
   - Device disconnected during operation

2. **Navigation Errors**
   - Screen not found
   - Navigation timeout
   - Unexpected screen state

3. **OCR Errors**
   - Low confidence extraction
   - Unrecognized text format
   - Image capture failed

4. **Export Errors**
   - File write permission denied
   - Invalid template format
   - Image insertion failed

### Recovery Strategies

**Retry Logic**:
- Automatic retry for transient errors (max 3 attempts)
- Progressive backoff between retries
- Different strategies for different error types

**Graceful Degradation**:
- Continue with partial data if some fields fail
- Mark uncertain data rather than failing completely
- Preserve already collected data

**User Notification**:
- Clear error messages with troubleshooting steps
- Progress updates even during error recovery
- Log all errors for debugging

**State Preservation**:
- Save progress before critical operations
- Allow pause/resume functionality
- Maintain collected data during interruptions

## Performance Characteristics

### Expected Timing
- **Platform initialization**: 5-10 seconds
- **Per-general processing**: 5-10 seconds
- **OCR processing per field**: 0.5-2 seconds
- **Excel export (100 generals)**: 10-20 seconds
- **Total time (100 generals)**: 10-15 minutes

### Optimization Strategies

1. **Parallel Processing**
   - Process multiple screenshot regions simultaneously
   - Use thread pool for OCR operations
   - Batch image processing where possible

2. **Caching**
   - Cache coordinate presets
   - Reuse preprocessed images
   - Cache platform connections

3. **Resource Management**
   - Limit screenshot resolution if needed
   - Clean up temporary images
   - Release resources when idle

## Threading Model

### Background Processing

The application uses a threading model to keep the UI responsive during long operations:

**Main Thread**:
- UI rendering and user interaction
- Progress display and status updates
- Configuration management

**Worker Thread**:
- Platform communication
- Screen navigation
- OCR processing
- Data collection
- Excel export

**Thread-Safe Communication**:
- Signal/slot mechanism for progress updates
- Lock-free progress information sharing
- Safe UI updates from worker thread

**Code Reference**: [`application_controller.py:533-572`](application_controller.py:533)

## Configuration Impact on Workflow

### Key Configuration Parameters

| Parameter | Impact on Workflow | Default |
|-----------|-------------------|---------|
| `ocr_engine` | Affects text extraction method | "easyocr" |
| `confidence_threshold` | Data quality filtering | 0.8 |
| `screen_transition_delay` | Navigation timing | 1.5s |
| `navigation_retry_count` | Error recovery attempts | 3 |
| `preprocessing_enabled` | OCR accuracy vs speed | true |

### Configuration File Structure

```json
{
  "platform": {
    "type": "bluestacks",
    "adb_path": "C:\\Program Files\\BlueStacks\\HD-Adb.exe",
    "device_id": "127.0.0.1:5555"
  },
  "ocr": {
    "engine": "easyocr",
    "confidence_threshold": 0.8,
    "languages": ["en"]
  },
  "navigation": {
    "transition_delay": 1.5,
    "retry_count": 3,
    "screenshot_scale": 1.0
  },
  "export": {
    "default_path": "~/Documents/Evony",
    "template_path": "./templates/generals_template.xlsx",
    "auto_open": true
  }
}
```

## Testing and Debugging

### Debug Mode Features

When `debug_mode` is enabled:
- Save preprocessed images to `temp/` directory
- Detailed logging of all operations
- OCR confidence scores for all fields
- Navigation action traces
- Screenshot caching for analysis

### Debug Output Files

- `temp/preprocessed_*.png`: OCR preprocessing results
- `temp/text_extraction_*.png`: Text extraction regions
- `temp/number_extraction_*.png`: Number extraction regions
- Application log: Complete operation trace


### User Experience Enhancements

1. **Real-time Preview**: Show extracted data as it's collected
2. **Interactive Correction**: Allow manual corrections
3. **Smart Recommendations**: Suggest optimal settings
4. **Progress Prediction**: Better time estimation

## Conclusion

The core iterative logic of the Evony Active Generals Tracker represents a sophisticated automation system that combines multiple technologies (OCR, screen automation, data processing) into a cohesive workflow. The system's strength lies in its modular design, comprehensive error handling, and user-focused progress tracking. Understanding this workflow is essential for maintaining, debugging, and enhancing the application.