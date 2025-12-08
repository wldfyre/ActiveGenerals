# Requirements Document

# Evony Active Generals Tracker

## Version 1.0

## Overall Programming Goal

The source generated in this project is intended for a hobbist tool, not intended for general production release, and easy to understand and maintain with ample in code documentation.
It will utilize externally develooped libraries as much as possible, to include:
- Python 
- PyQT5 
- EasyOCR
- an xml management library for reading from locations.xml
- an excel management library for writing to the output file and viewing the results
- opencv for image processing
- an ADB library for connecting to the emulator 

## Introduction

This document outlines the requirements for the Evony Active Generals Tracker, a tool designed to help Evony MMO players manage and analyze their active generals. The system will extract general information from the game and compile it into an organized Excel spreadsheet for easy reference and analysis.

## Glossary

- **Evony ActiveGenerals Tracker**: The application system that collects and exports general data
- **General**: A character unit in Evony that players can recruit and use in battles
- **Player**: The user of the Evony Active Generals Tracker application
- **General Data**: Information about a general including stats, skills, level, and equipment
- **Excel Export**: The generated spreadsheet file containing compiled general information
- **OCR Engine**: Optical Character Recognition component that extracts text from game screenshots
- **ADB**: Android Debug Bridge, a command-line tool for communicating with Android devices and emulators
- **Bluestacks Emulator**: An Android emulator running on Windows that hosts the Evony game
- **Platform Interface**: The component that handles platform-specific interactions (Windows/Android/iOS)
- **Game Screen**: The visual interface of Evony displayed on the target platform

## Requirements

### Requirement 1

**User Story:** As a player, I want to connect to Evony running on the Bluestacks Emulator, or Android devices connected via USB or Bluetooth, so that I can access my generals information from the application.

#### Acceptance Criteria

1. THE Evony Active Generals Tracker SHALL detect and connect to Bluestacks Emulator on Windows using ADB
2. THE Evony Active Generals Tracker SHALL connect to Evony running on Android devices
3. WHEN the player selects a platform, THE Evony Active Generals Tracker SHALL establish connection within 5 seconds
4. IF connection fails, THEN THE Evony Active Generals Tracker SHALL display an error message with troubleshooting guidance

### Requirement 2

**User Story:** As a player, I want to view all my active generals in one place, so that I can quickly assess my roster without navigating through the game interface.

#### Acceptance Criteria

1. THE Evony Active Generals Tracker SHALL navigate from the Evony home screen to the generals list screen, and select settings appropriate for navigating all generals
2. THE Evony Active Generals Tracker SHALL capture screenshots of the generals list from the Game Screen
3. THE Evony Active Generals Tracker SHALL use the OCR Engine to extract general names and relevant information from captured images and add to an excel spreadsheet
4. THE Evony Active Generals Tracker SHALL display a list of all retrieved generals with their names in the application interface list
5. WHEN the player runs the application, THE Evony Active Generals Tracker SHALL compile a complete list of active generals, ranging from one general to several hundred generals
6. IF the retrieval fails, THEN THE Evony Active Generals Tracker SHALL display an error message indicating the failure reason and exit gracefully

### Requirement 3

**User Story:** As a player, I want the app to automatically navigate through the game interface, so that I don't have to manually open each general's details.

#### Acceptance Criteria

1. THE Evony Active Generals Tracker SHALL send touch commands through the Platform Interface to navigate game menus
2. WHEN navigating to a general's detail screen, THE Evony Active Generals Tracker SHALL wait for screen transitions to complete
3. THE Evony Active Generals Tracker SHALL detect when a target screen has loaded by analyzing screenshot content
4. THE Evony Active Generals Tracker SHALL return to the generals list after collecting data from each general in order to navigate to the next general

### Requirement 4

**User Story:** As a player, I want the app to accurately read text from game screenshots, so that my general data is correct even with different backgrounds and visual effects.

#### Acceptance Criteria

1. THE Evony Active Generals Tracker SHALL use the OCR Engine to extract text from screenshots with varied backgrounds
2. THE Evony Active Generals Tracker SHALL preprocess images to improve OCR accuracy before text extraction
3. WHEN text extraction confidence is below 80 percent, THE Evony Active Generals Tracker SHALL flag the data as uncertain and prompt the user for the correct text
4. THE Evony Active Generals Tracker SHALL handle multiple font styles and sizes present in the Game Screen

### Requirement 5

**User Story:** As a player, I want to export general information to Excel incrementally during collection, so that I don't lose data if the process is interrupted.

#### Acceptance Criteria

1. THE Evony Active Generals Tracker SHALL generate an Excel spreadsheet containing all general data using an xlsx template to initiate a new excel file each time
2. THE Evony Active Generals Tracker SHALL update the Excel file after each general is processed during collection
3. THE Evony Active Generals Tracker SHALL include both text and image data, exporting items to excel columns as defined in the documentation 
4. WHEN the player initiates collection, THE Evony Active Generals Tracker SHALL create an incremental export file that is updated in real-time
5. IF collection is stopped or interrupted, THE Evony Active Generals Tracker SHALL preserve all processed data in the Excel file
6. WHEN collection completes, THE Evony Active Generals Tracker SHALL offer to save the incremental file to a user-selected permanent location
7. THE Evony Active Generals Tracker SHALL utilize the .xlsx header format to identify columns of data. The data insertions will begin after the first blank row after the header information (row 6)

### Requirement 6

**User Story:** As a player, I want to see general statistics and attributes, so that I can make informed decisions about which generals to use in different scenarios.

#### Acceptance Criteria

1. THE Evony Active Generals Tracker SHALL extract the following information for each general using the OCR Engine and image snippets
    a. Name	
    b. Level	    (text)
    c. Type	        (image)
    d. Power	    (text)
    e. Stars	    (image)
    f. Exp Ratio	(text)
    g. Specialty	(images and text)
    h. Covenant List (image)	
    i. Covenant Generals (images and text)
    


### Requirement 7

**User Story:** As a player, I want the data to be organized and sortable, so that I can quickly find specific generals or compare them by different attributes.

#### Acceptance Criteria


1. THE Evony Active Generals Tracker SHALL enable sorting by any column in the Excel export
2. The Evony Active Generals Tracker SHALL enable cells containing images and text, such that the image will fit and be anchored within the cell.  All other column heights will be adjusted to match this height
3. THE Evony Active Generals Tracker SHALL apply consistent formatting across all data rows, left adjusting  non-numeric text, right adjusting numbers with a formatting using commas,  and centering vertically.


### Requirement 8

**User Story:** As a player, I want the data to be properly formatted in Excel with multi-line text support, so that I can easily read cultivation, specialty, and covenant information.

#### Acceptance Criteria

1. THE Evony Active Generals Tracker SHALL enable text wrapping in Excel cells for multi-line data
2. THE Evony Active Generals Tracker SHALL place stars images in column E and experience ratio in column F
3. THE Evony Active Generals Tracker SHALL format cultivation data with line breaks between Leadership, Attack, Defense, and Politics stats
4. THE Evony Active Generals Tracker SHALL format specialty and covenant data with proper line breaks and image positioning
5. THE Evony Active Generals Tracker SHALL adjust row heights to accommodate multi-line text and images

### Requirement 10

**User Story:** As a player, I want to see real-time progress updates during collection, so that I can monitor the process and stop it if needed.

#### Acceptance Criteria

1. THE Evony Active Generals Tracker SHALL update the generals table in real-time as each general is processed
2. THE Evony Active Generals Tracker SHALL show live progress indicators including current general count and estimated completion time
3. THE Evony Active Generals Tracker SHALL display confidence scores and processing status during collection
4. WHEN the player clicks the "Stop" button, THE Evony Active Generals Tracker SHALL immediately halt collection and preserve all processed data
5. THE Evony Active Generals Tracker SHALL provide immediate feedback on collection status and data availability
