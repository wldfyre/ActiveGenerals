#!/usr/bin/env python3
"""
Process Flow Diagrams for Evony Active Generals Tracker

This script generates detailed process flow diagrams showing various workflows.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Arrow
import numpy as np

def create_startup_process_diagram():
    """Create a detailed startup process flow diagram"""

    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Process steps
    processes = [
        {'name': 'main.py\nexecuted', 'x': 7, 'y': 9.5, 'w': 2, 'h': 0.6, 'color': '#e1f5fe'},
        {'name': 'Load Configuration\nfrom config.json', 'x': 7, 'y': 8.5, 'w': 3, 'h': 0.8, 'color': '#f3e5f5'},
        {'name': 'Setup Logging\nSystem', 'x': 7, 'y': 7.5, 'w': 2.5, 'h': 0.6, 'color': '#e8f5e8'},
        {'name': 'Create QApplication\nInstance', 'x': 7, 'y': 6.5, 'w': 3, 'h': 0.6, 'color': '#fff3e0'},
        {'name': 'Initialize MainWindow\nwith ConfigManager', 'x': 7, 'y': 5.5, 'w': 4, 'h': 0.8, 'color': '#fce4ec'},
        {'name': 'Setup UI Components\nand Signal Connections', 'x': 7, 'y': 4.5, 'w': 4, 'h': 0.8, 'color': '#e3f2fd'},
        {'name': 'Load UI Settings\ninto Controls', 'x': 7, 'y': 3.5, 'w': 3, 'h': 0.6, 'color': '#f1f8e9'},
        {'name': 'Apply Custom\nDark Mode Styling', 'x': 7, 'y': 2.5, 'w': 3, 'h': 0.6, 'color': '#fff8e1'},
        {'name': 'Show Main Window\nand Start Event Loop', 'x': 7, 'y': 1.5, 'w': 4, 'h': 0.8, 'color': '#ffebee'},
    ]

    # Decision points
    decisions = [
        {'name': 'Config file\nexists?', 'x': 7, 'y': 8.0, 'w': 2, 'h': 0.5},
        {'name': 'High DPI\nscaling needed?', 'x': 7, 'y': 6.0, 'w': 2.5, 'h': 0.5},
    ]

    # Draw process boxes
    for process in processes:
        rect = FancyBboxPatch((process['x']-process['w']/2, process['y']-process['h']/2),
                             process['w'], process['h'],
                             boxstyle="round,pad=0.05",
                             facecolor=process['color'],
                             edgecolor='#333333',
                             linewidth=1.5)
        ax.add_patch(rect)

        ax.text(process['x'], process['y'], process['name'],
               ha='center', va='center', fontsize=8, fontweight='bold',
               wrap=True)

    # Draw decision diamonds
    for decision in decisions:
        diamond = patches.Polygon([
            (decision['x'], decision['y'] + decision['h']/2),
            (decision['x'] + decision['w']/2, decision['y']),
            (decision['x'], decision['y'] - decision['h']/2),
            (decision['x'] - decision['w']/2, decision['y'])
        ], facecolor='#fff3e0', edgecolor='#f57c00', linewidth=2)
        ax.add_patch(diamond)

        ax.text(decision['x'], decision['y'], decision['name'],
               ha='center', va='center', fontsize=8, fontweight='bold',
               wrap=True)

    # Draw flow arrows
    flow_arrows = [
        (7, 9.2, 7, 8.8),    # main.py -> Load Config
        (7, 8.1, 7, 7.9),    # Config decision -> Setup Logging
        (7, 7.2, 7, 6.8),    # Logging -> Create QApplication
        (7, 6.2, 7, 5.8),    # QApplication decision -> Initialize MainWindow
        (7, 5.2, 7, 4.8),    # MainWindow -> Setup UI
        (7, 4.2, 7, 3.8),    # Setup UI -> Load Settings
        (7, 3.2, 7, 2.8),    # Load Settings -> Apply Styling
        (7, 2.2, 7, 1.8),    # Apply Styling -> Show Window
    ]

    for x1, y1, x2, y2 in flow_arrows:
        ax.arrow(x1, y1, x2-x1, y2-y1,
                head_width=0.08, head_length=0.1,
                fc='#666666', ec='#666666',
                length_includes_head=True, alpha=0.8)

    # Decision branches
    ax.arrow(7, 8.25, -1.5, 0, head_width=0.06, head_length=0.08,
            fc='#4caf50', ec='#4caf50', alpha=0.8)
    ax.text(5.5, 8.3, 'Yes', fontsize=8, fontweight='bold', color='#4caf50')

    ax.arrow(7, 8.25, 1.5, 0, head_width=0.06, head_length=0.08,
            fc='#f44336', ec='#f44336', alpha=0.8)
    ax.text(8.5, 8.3, 'No\nUse Defaults', fontsize=8, fontweight='bold', color='#f44336')

    ax.arrow(7, 6.25, -1.5, 0, head_width=0.06, head_length=0.08,
            fc='#4caf50', ec='#4caf50', alpha=0.8)
    ax.text(5.5, 6.3, 'Yes', fontsize=8, fontweight='bold', color='#4caf50')

    ax.arrow(7, 6.25, 1.5, 0, head_width=0.06, head_length=0.08,
            fc='#4caf50', ec='#4caf50', alpha=0.8)
    ax.text(8.5, 6.3, 'No', fontsize=8, fontweight='bold', color='#4caf50')

    # Add title
    ax.text(7, 10.2, 'Application Startup Process Flow',
           ha='center', va='center', fontsize=16, fontweight='bold')

    plt.tight_layout()
    plt.savefig('docs/startup_process_flow.png', dpi=300, bbox_inches='tight')
    plt.savefig('docs/startup_process_flow.pdf', bbox_inches='tight')
    plt.close()

def create_collection_process_diagram():
    """Create a detailed data collection process flow diagram"""

    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Main process steps
    processes = [
        {'name': 'User Clicks\n"Start Collection"', 'x': 2, 'y': 11, 'w': 2.5, 'h': 0.8, 'color': '#e1f5fe'},
        {'name': 'Validate Controller\nand Platform Connection', 'x': 2, 'y': 9.5, 'w': 3, 'h': 0.8, 'color': '#f3e5f5'},
        {'name': 'Initialize ApplicationController\nwith Configuration', 'x': 2, 'y': 8, 'w': 3.5, 'h': 0.8, 'color': '#e8f5e8'},
        {'name': 'Navigate to\nGenerals List Screen', 'x': 6, 'y': 11, 'w': 3, 'h': 0.8, 'color': '#fff3e0'},
        {'name': 'Set Generals List\nFilters and State', 'x': 6, 'y': 9.5, 'w': 3, 'h': 0.8, 'color': '#fce4ec'},
        {'name': 'Count Total\nAvailable Generals', 'x': 6, 'y': 8, 'w': 2.5, 'h': 0.8, 'color': '#e3f2fd'},
        {'name': 'Start Background\nCollection Thread', 'x': 10, 'y': 11, 'w': 3, 'h': 0.8, 'color': '#f1f8e9'},
        {'name': 'Process Each General\n(Loop)', 'x': 10, 'y': 9.5, 'w': 3, 'h': 0.8, 'color': '#fff8e1'},
        {'name': 'Open General\nDetails Screen', 'x': 14, 'y': 11, 'w': 2.5, 'h': 0.8, 'color': '#ffebee'},
        {'name': 'Capture Main\nScreenshot', 'x': 14, 'y': 9.5, 'w': 2.5, 'h': 0.8, 'color': '#e1f5fe'},
        {'name': 'Extract Basic Data\n(Name, Level, Power, etc.)', 'x': 10, 'y': 7, 'w': 3.5, 'h': 0.8, 'color': '#f3e5f5'},
        {'name': 'Navigate to\nCultivation Screen', 'x': 6, 'y': 7, 'w': 3, 'h': 0.8, 'color': '#e8f5e8'},
        {'name': 'Capture Cultivation\nScreenshot', 'x': 2, 'y': 7, 'w': 3, 'h': 0.8, 'color': '#fff3e0'},
        {'name': 'Extract Cultivation\nStats (Leadership, etc.)', 'x': 2, 'y': 5.5, 'w': 3.5, 'h': 0.8, 'color': '#fce4ec'},
        {'name': 'Navigate to\nSpecialties Screen', 'x': 6, 'y': 5.5, 'w': 3, 'h': 0.8, 'color': '#e3f2fd'},
        {'name': 'Capture Specialties\nScreenshot', 'x': 10, 'y': 5.5, 'w': 3, 'h': 0.8, 'color': '#f1f8e9'},
        {'name': 'Extract Specialty\nData and Images', 'x': 14, 'y': 5.5, 'w': 3, 'h': 0.8, 'color': '#fff8e1'},
        {'name': 'Navigate to\nCovenant Screen', 'x': 6, 'y': 4, 'w': 3, 'h': 0.8, 'color': '#ffebee'},
        {'name': 'Capture Covenant\nScreenshot', 'x': 10, 'y': 4, 'w': 3, 'h': 0.8, 'color': '#e1f5fe'},
        {'name': 'Extract Covenant\nGeneral Data', 'x': 14, 'y': 4, 'w': 3, 'h': 0.8, 'color': '#f3e5f5'},
        {'name': 'Calculate Overall\nConfidence Score', 'x': 8, 'y': 2.5, 'w': 3, 'h': 0.8, 'color': '#e8f5e8'},
        {'name': 'Mark General as\nUncertain if Low Confidence', 'x': 8, 'y': 1.5, 'w': 4, 'h': 0.8, 'color': '#fff3e0'},
        {'name': 'Close General\nDetails Screen', 'x': 14, 'y': 2.5, 'w': 2.5, 'h': 0.8, 'color': '#fce4ec'},
        {'name': 'Update Progress\nand Continue Loop', 'x': 10, 'y': 1.5, 'w': 3, 'h': 0.8, 'color': '#e3f2fd'},
        {'name': 'Reset Generals List\nState', 'x': 6, 'y': 1.5, 'w': 3, 'h': 0.8, 'color': '#f1f8e9'},
        {'name': 'Collection Complete\n- Update UI', 'x': 2, 'y': 1.5, 'w': 3, 'h': 0.8, 'color': '#fff8e1'},
    ]

    # Decision points
    decisions = [
        {'name': 'Controller\nConnected?', 'x': 2, 'y': 10.25, 'w': 2, 'h': 0.4},
        {'name': 'Navigation\nSuccessful?', 'x': 6, 'y': 10.25, 'w': 2, 'h': 0.4},
        {'name': 'More\nGenerals?', 'x': 10, 'y': 8.25, 'w': 1.5, 'h': 0.4},
        {'name': 'Confidence\n≥ Threshold?', 'x': 8, 'y': 2.0, 'w': 2, 'h': 0.4},
    ]

    # Draw process boxes
    for process in processes:
        rect = FancyBboxPatch((process['x']-process['w']/2, process['y']-process['h']/2),
                             process['w'], process['h'],
                             boxstyle="round,pad=0.02",
                             facecolor=process['color'],
                             edgecolor='#333333',
                             linewidth=1)
        ax.add_patch(rect)

        ax.text(process['x'], process['y'], process['name'],
               ha='center', va='center', fontsize=7, fontweight='bold',
               wrap=True)

    # Draw decision diamonds
    for decision in decisions:
        diamond = patches.Polygon([
            (decision['x'], decision['y'] + decision['h']/2),
            (decision['x'] + decision['w']/2, decision['y']),
            (decision['x'], decision['y'] - decision['h']/2),
            (decision['x'] - decision['w']/2, decision['y'])
        ], facecolor='#fff3e0', edgecolor='#f57c00', linewidth=2)
        ax.add_patch(diamond)

        ax.text(decision['x'], decision['y'], decision['name'],
               ha='center', va='center', fontsize=7, fontweight='bold',
               wrap=True)

    # Draw flow arrows (simplified - main flow)
    main_flow = [
        (2, 10.6, 2, 9.9),    # Start -> Validate
        (2, 9.1, 2, 8.4),     # Validate -> Init Controller
        (2, 7.6, 4.25, 11.4), # Init -> Navigate (parallel)
        (6, 10.6, 6, 9.9),    # Navigate -> Set Filters
        (6, 9.1, 6, 8.4),     # Set Filters -> Count
        (6, 7.6, 8.25, 11.4), # Count -> Start Thread
        (10, 10.6, 10, 9.9),  # Start Thread -> Process Loop
        (10, 9.1, 12.25, 11.4), # Process -> Open Details
        (14, 10.6, 14, 9.9),  # Open -> Capture Main
        (14, 9.1, 12.25, 7.4), # Capture -> Extract Basic
        (10, 6.6, 7.75, 7.4), # Extract Basic -> Navigate Cultivation
        (6, 6.6, 3.75, 7.4),  # Navigate -> Capture Cultivation
        (2, 6.6, 2, 5.9),     # Capture -> Extract Cultivation
        (2, 5.1, 4.25, 5.9),  # Extract -> Navigate Specialties
        (6, 5.1, 8.25, 5.9),  # Navigate -> Capture Specialties
        (10, 5.1, 12.25, 5.9), # Capture -> Extract Specialties
        (14, 5.1, 7.75, 4.4), # Extract -> Navigate Covenant
        (6, 3.6, 8.25, 4.4),  # Navigate -> Capture Covenant
        (10, 3.6, 12.25, 4.4), # Capture -> Extract Covenant
        (14, 3.6, 10.75, 2.9), # Extract -> Calculate Confidence
        (14, 2.1, 12.25, 1.9), # Close Details -> Update Progress
        (10, 1.1, 7.75, 1.9), # Update -> Reset List
        (6, 1.1, 3.75, 1.9),  # Reset -> Complete
    ]

    for x1, y1, x2, y2 in main_flow:
        ax.arrow(x1, y1, x2-x1, y2-y1,
                head_width=0.06, head_length=0.08,
                fc='#666666', ec='#666666',
                length_includes_head=True, alpha=0.7)

    # Decision branches
    # Controller connected
    ax.arrow(2, 10.5, 0, -0.3, head_width=0.04, head_length=0.06,
            fc='#4caf50', ec='#4caf50', alpha=0.8)
    ax.arrow(2, 10.5, -1, 0, head_width=0.04, head_length=0.06,
            fc='#f44336', ec='#f44336', alpha=0.8)
    ax.text(1, 10.6, 'Yes', fontsize=6, fontweight='bold', color='#4caf50')
    ax.text(1.2, 10.2, 'No\nShow Error', fontsize=6, fontweight='bold', color='#f44336')

    # Navigation successful
    ax.arrow(6, 10.5, 0, -0.3, head_width=0.04, head_length=0.06,
            fc='#4caf50', ec='#4caf50', alpha=0.8)
    ax.arrow(6, 10.5, 1, 0, head_width=0.04, head_length=0.06,
            fc='#f44336', ec='#f44336', alpha=0.8)

    # More generals
    ax.arrow(10, 8.5, 0, -0.3, head_width=0.04, head_length=0.06,
            fc='#4caf50', ec='#4caf50', alpha=0.8)
    ax.arrow(10, 8.5, 2, 0, head_width=0.04, head_length=0.06,
            fc='#f44336', ec='#f44336', alpha=0.8)
    ax.text(11.2, 8.6, 'Yes\nContinue', fontsize=6, fontweight='bold', color='#4caf50')
    ax.text(12.2, 8.2, 'No\nComplete', fontsize=6, fontweight='bold', color='#f44336')

    # Confidence check
    ax.arrow(8, 2.25, -1, 0, head_width=0.04, head_length=0.06,
            fc='#4caf50', ec='#4caf50', alpha=0.8)
    ax.arrow(8, 2.25, 1, 0, head_width=0.04, head_length=0.06,
            fc='#f44336', ec='#f44336', alpha=0.8)
    ax.text(7, 2.35, 'Yes', fontsize=6, fontweight='bold', color='#4caf50')
    ax.text(9, 2.35, 'No\nMark Uncertain', fontsize=6, fontweight='bold', color='#f44336')

    # Add title
    ax.text(8, 12.2, 'Data Collection Process Flow Diagram',
           ha='center', va='center', fontsize=16, fontweight='bold')

    plt.tight_layout()
    plt.savefig('docs/collection_process_flow.png', dpi=300, bbox_inches='tight')
    plt.savefig('docs/collection_process_flow.pdf', bbox_inches='tight')
    plt.close()

def create_error_handling_diagram():
    """Create an error handling and recovery flow diagram"""

    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Error types and handling
    error_processes = [
        {'name': 'Platform Connection\nError', 'x': 2, 'y': 9, 'w': 2.5, 'h': 0.8, 'color': '#ffebee'},
        {'name': 'Navigation Timeout\nError', 'x': 6, 'y': 9, 'w': 2.5, 'h': 0.8, 'color': '#ffebee'},
        {'name': 'OCR Extraction\nError', 'x': 10, 'y': 9, 'w': 2.5, 'h': 0.8, 'color': '#ffebee'},
        {'name': 'Screenshot Capture\nError', 'x': 2, 'y': 7, 'w': 2.5, 'h': 0.8, 'color': '#ffebee'},
        {'name': 'Excel Export\nError', 'x': 6, 'y': 7, 'w': 2.5, 'h': 0.8, 'color': '#ffebee'},
        {'name': 'Log Error Details\nwith Context', 'x': 7, 'y': 5, 'w': 3, 'h': 0.8, 'color': '#fff3e0'},
        {'name': 'Attempt Retry\n(up to 3 times)', 'x': 7, 'y': 3.5, 'w': 3, 'h': 0.8, 'color': '#e8f5e8'},
        {'name': 'Apply Graceful\nDegradation', 'x': 3, 'y': 2, 'w': 3, 'h': 0.8, 'color': '#f3e5f5'},
        {'name': 'Mark Data as\nUncertain', 'x': 7, 'y': 2, 'w': 2.5, 'h': 0.8, 'color': '#fce4ec'},
        {'name': 'Continue with\nPartial Data', 'x': 11, 'y': 2, 'w': 2.5, 'h': 0.8, 'color': '#e3f2fd'},
        {'name': 'Show User-Friendly\nError Message', 'x': 7, 'y': 0.5, 'w': 4, 'h': 0.8, 'color': '#f1f8e9'},
    ]

    # Recovery strategies
    recovery_actions = [
        {'name': 'Check ADB Connection\nand Device Status', 'x': 2, 'y': 8, 'w': 2.5, 'h': 0.6, 'color': '#e1f5fe'},
        {'name': 'Wait and Retry\nNavigation', 'x': 6, 'y': 8, 'w': 2.5, 'h': 0.6, 'color': '#e1f5fe'},
        {'name': 'Use Alternative\nOCR Engine', 'x': 10, 'y': 8, 'w': 2.5, 'h': 0.6, 'color': '#e1f5fe'},
        {'name': 'Retry Screenshot\nCapture', 'x': 2, 'y': 6, 'w': 2.5, 'h': 0.6, 'color': '#e1f5fe'},
        {'name': 'Fallback to Basic\nExport Format', 'x': 6, 'y': 6, 'w': 2.5, 'h': 0.6, 'color': '#e1f5fe'},
    ]

    # Decisions
    decisions = [
        {'name': 'Retry\nCount < 3?', 'x': 7, 'y': 4.25, 'w': 1.5, 'h': 0.4},
        {'name': 'Can\nContinue?', 'x': 7, 'y': 2.75, 'w': 1.5, 'h': 0.4},
    ]

    # Draw error process boxes
    for process in error_processes:
        rect = FancyBboxPatch((process['x']-process['w']/2, process['y']-process['h']/2),
                             process['w'], process['h'],
                             boxstyle="round,pad=0.02",
                             facecolor=process['color'],
                             edgecolor='#d32f2f',
                             linewidth=1.5)
        ax.add_patch(rect)

        ax.text(process['x'], process['y'], process['name'],
               ha='center', va='center', fontsize=8, fontweight='bold',
               wrap=True)

    # Draw recovery action boxes
    for action in recovery_actions:
        rect = FancyBboxPatch((action['x']-action['w']/2, action['y']-action['h']/2),
                             action['w'], action['h'],
                             boxstyle="round,pad=0.02",
                             facecolor=action['color'],
                             edgecolor='#1976d2',
                             linewidth=1.5)
        ax.add_patch(rect)

        ax.text(action['x'], action['y'], action['name'],
               ha='center', va='center', fontsize=7, wrap=True)

    # Draw decision diamonds
    for decision in decisions:
        diamond = patches.Polygon([
            (decision['x'], decision['y'] + decision['h']/2),
            (decision['x'] + decision['w']/2, decision['y']),
            (decision['x'], decision['y'] - decision['h']/2),
            (decision['x'] - decision['w']/2, decision['y'])
        ], facecolor='#fff3e0', edgecolor='#f57c00', linewidth=2)
        ax.add_patch(diamond)

        ax.text(decision['x'], decision['y'], decision['name'],
               ha='center', va='center', fontsize=7, fontweight='bold',
               wrap=True)

    # Draw flow arrows
    error_flows = [
        (2, 8.6, 2, 7.4),    # Connection error -> Recovery
        (6, 8.6, 6, 7.4),    # Navigation error -> Recovery
        (10, 8.6, 10, 7.4),  # OCR error -> Recovery
        (2, 6.6, 2, 5.4),    # Screenshot error -> Recovery
        (6, 6.6, 6, 5.4),    # Export error -> Recovery

        # All errors -> Log
        (2, 5.4, 5.25, 5.4), (6, 5.4, 5.25, 5.4), (10, 5.4, 5.25, 5.4),
        (2, 5.4, 7, 5.4), (6, 5.4, 7, 5.4), (10, 5.4, 7, 5.4),
        (2, 5.4, 8.75, 5.4), (6, 5.4, 8.75, 5.4), (10, 5.4, 8.75, 5.4),

        # Log -> Retry decision
        (7, 4.6, 7, 3.9),

        # Retry decision branches
        (7, 4.5, 5, 3.9),     # Yes -> Retry
        (7, 4.5, 9, 3.9),     # No -> Degradation

        # Retry -> Continue check
        (7, 3.1, 7, 2.9),

        # Continue decision branches
        (7, 3.0, 4.5, 2.4),   # Yes -> Mark uncertain
        (7, 3.0, 9.5, 2.4),   # No -> Continue partial

        # Final -> User message
        (3, 1.6, 5.25, 0.9), (7, 1.6, 5.25, 0.9), (11, 1.6, 5.25, 0.9),
        (3, 1.6, 7, 0.9), (7, 1.6, 7, 0.9), (11, 1.6, 7, 0.9),
        (3, 1.6, 8.75, 0.9), (7, 1.6, 8.75, 0.9), (11, 1.6, 8.75, 0.9),
    ]

    for x1, y1, x2, y2 in error_flows:
        ax.arrow(x1, y1, x2-x1, y2-y1,
                head_width=0.05, head_length=0.07,
                fc='#666666', ec='#666666',
                length_includes_head=True, alpha=0.6)

    # Decision labels
    ax.text(6, 4.6, 'Yes', fontsize=7, fontweight='bold', color='#4caf50')
    ax.text(8, 4.6, 'No', fontsize=7, fontweight='bold', color='#f44336')

    ax.text(6.2, 3.1, 'Yes', fontsize=7, fontweight='bold', color='#4caf50')
    ax.text(7.8, 3.1, 'No', fontsize=7, fontweight='bold', color='#f44336')

    # Add title
    ax.text(7, 10.2, 'Error Handling and Recovery Process Flow',
           ha='center', va='center', fontsize=16, fontweight='bold')

    # Add legend
    legend_elements = [
        ('Error Types', '#ffebee', '#d32f2f'),
        ('Recovery Actions', '#e1f5fe', '#1976d2'),
        ('Decisions', '#fff3e0', '#f57c00'),
        ('Process Steps', '#f3e5f5', '#333333')
    ]

    legend_x, legend_y = 0.02, 0.02
    for i, (label, color, edge_color) in enumerate(legend_elements):
        rect = FancyBboxPatch((legend_x, legend_y + i*0.06), 0.04, 0.04,
                             boxstyle="round,pad=0",
                             facecolor=color, edgecolor=edge_color)
        ax.add_patch(rect)
        ax.text(legend_x + 0.05, legend_y + i*0.06 + 0.02, label,
               fontsize=8, va='center')

    plt.tight_layout()
    plt.savefig('docs/error_handling_flow.png', dpi=300, bbox_inches='tight')
    plt.savefig('docs/error_handling_flow.pdf', bbox_inches='tight')
    plt.close()

def create_export_process_diagram():
    """Create a detailed Excel export process flow diagram"""

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Export process steps
    processes = [
        {'name': 'User Selects\nExport Location', 'x': 2, 'y': 7, 'w': 2.5, 'h': 0.8, 'color': '#e1f5fe'},
        {'name': 'Validate Export\nPath and Permissions', 'x': 6, 'y': 7, 'w': 3, 'h': 0.8, 'color': '#f3e5f5'},
        {'name': 'Load Excel\nTemplate File', 'x': 10, 'y': 7, 'w': 2.5, 'h': 0.8, 'color': '#e8f5e8'},
        {'name': 'Clear Existing\nData Rows', 'x': 2, 'y': 5.5, 'w': 2.5, 'h': 0.8, 'color': '#fff3e0'},
        {'name': 'Sort Generals by\nName/Level/Power', 'x': 6, 'y': 5.5, 'w': 3, 'h': 0.8, 'color': '#fce4ec'},
        {'name': 'For Each General\n(Loop)', 'x': 10, 'y': 5.5, 'w': 2.5, 'h': 0.8, 'color': '#e3f2fd'},
        {'name': 'Write Basic Data\n(Name, Level, Type, Power)', 'x': 3, 'y': 4, 'w': 3.5, 'h': 0.8, 'color': '#f1f8e9'},
        {'name': 'Write Experience\nRatio Data', 'x': 7, 'y': 4, 'w': 2.5, 'h': 0.8, 'color': '#fff8e1'},
        {'name': 'Insert Stars\nImage', 'x': 11, 'y': 4, 'w': 2, 'h': 0.8, 'color': '#ffebee'},
        {'name': 'Write Cultivation\nStats (Leadership, etc.)', 'x': 2, 'y': 2.5, 'w': 3.5, 'h': 0.8, 'color': '#e1f5fe'},
        {'name': 'Insert Specialty\nImages and Names', 'x': 6, 'y': 2.5, 'w': 3, 'h': 0.8, 'color': '#f3e5f5'},
        {'name': 'Insert Covenant\nGeneral Images', 'x': 10, 'y': 2.5, 'w': 3, 'h': 0.8, 'color': '#e8f5e8'},
        {'name': 'Apply Cell\nFormatting and Styles', 'x': 4, 'y': 1, 'w': 3, 'h': 0.8, 'color': '#fff3e0'},
        {'name': 'Add Confidence\nScore Column', 'x': 8, 'y': 1, 'w': 2.5, 'h': 0.8, 'color': '#fce4ec'},
        {'name': 'Save Excel\nWorkbook', 'x': 6, 'y': 0.5, 'w': 2.5, 'h': 0.8, 'color': '#e3f2fd'},
    ]

    # Decisions
    decisions = [
        {'name': 'Path\nValid?', 'x': 6, 'y': 6.25, 'w': 1.5, 'h': 0.4},
        {'name': 'Template\nExists?', 'x': 10, 'y': 6.25, 'w': 1.5, 'h': 0.4},
        {'name': 'More\nGenerals?', 'x': 10, 'y': 4.75, 'w': 1.5, 'h': 0.4},
    ]

    # Draw process boxes
    for process in processes:
        rect = FancyBboxPatch((process['x']-process['w']/2, process['y']-process['h']/2),
                             process['w'], process['h'],
                             boxstyle="round,pad=0.02",
                             facecolor=process['color'],
                             edgecolor='#333333',
                             linewidth=1)
        ax.add_patch(rect)

        ax.text(process['x'], process['y'], process['name'],
               ha='center', va='center', fontsize=7, fontweight='bold',
               wrap=True)

    # Draw decision diamonds
    for decision in decisions:
        diamond = patches.Polygon([
            (decision['x'], decision['y'] + decision['h']/2),
            (decision['x'] + decision['w']/2, decision['y']),
            (decision['x'], decision['y'] - decision['h']/2),
            (decision['x'] - decision['w']/2, decision['y'])
        ], facecolor='#fff3e0', edgecolor='#f57c00', linewidth=2)
        ax.add_patch(diamond)

        ax.text(decision['x'], decision['y'], decision['name'],
               ha='center', va='center', fontsize=7, fontweight='bold',
               wrap=True)

    # Draw flow arrows
    export_flows = [
        (2, 6.6, 2, 5.9),    # Select path -> Validate
        (2, 5.1, 4.25, 7.4), # Validate -> Load template (parallel)
        (6, 6.6, 6, 5.9),    # Validate decision -> Sort
        (10, 6.6, 10, 5.9),  # Template decision -> Loop
        (6, 5.1, 8.25, 5.9), # Sort -> Loop
        (10, 5.1, 10, 4.4),  # Loop -> Write basic
        (10, 4.4, 3, 4.4),   # -> Write basic
        (3, 3.6, 5.25, 4.4), # Write basic -> Write exp
        (7, 3.6, 9.25, 4.4), # Write exp -> Insert stars
        (11, 3.6, 11, 2.9),  # Insert stars -> Write cultivation
        (11, 2.9, 3.75, 2.9), # -> Write cultivation
        (2, 2.1, 4.25, 2.9), # Write cultivation -> Insert specialties
        (6, 2.1, 8.25, 2.9), # Insert specialties -> Insert covenant
        (10, 2.1, 10, 1.4),  # Insert covenant -> Apply formatting
        (10, 1.4, 5.75, 1.4), # -> Apply formatting
        (4, 0.6, 6.25, 0.9), # Apply formatting -> Add confidence
        (8, 0.6, 6.25, 0.9), # Add confidence -> Save
    ]

    for x1, y1, x2, y2 in export_flows:
        ax.arrow(x1, y1, x2-x1, y2-y1,
                head_width=0.05, head_length=0.07,
                fc='#666666', ec='#666666',
                length_includes_head=True, alpha=0.6)

    # Decision branches
    ax.arrow(6, 6.5, 0, -0.3, head_width=0.04, head_length=0.06,
            fc='#4caf50', ec='#4caf50', alpha=0.8)
    ax.arrow(6, 6.5, 1, 0, head_width=0.04, head_length=0.06,
            fc='#f44336', ec='#f44336', alpha=0.8)
    ax.text(5.2, 6.6, 'Yes', fontsize=6, fontweight='bold', color='#4caf50')
    ax.text(7.2, 6.2, 'No\nShow Error', fontsize=6, fontweight='bold', color='#f44336')

    ax.arrow(10, 6.5, 0, -0.3, head_width=0.04, head_length=0.06,
            fc='#4caf50', ec='#4caf50', alpha=0.8)
    ax.arrow(10, 6.5, 1, 0, head_width=0.04, head_length=0.06,
            fc='#f44336', ec='#f44336', alpha=0.8)

    ax.arrow(10, 5.0, 0, -0.3, head_width=0.04, head_length=0.06,
            fc='#4caf50', ec='#4caf50', alpha=0.8)
    ax.arrow(10, 5.0, 2, 0, head_width=0.04, head_length=0.06,
            fc='#f44336', ec='#f44336', alpha=0.8)
    ax.text(11.2, 5.1, 'Yes\nContinue', fontsize=6, fontweight='bold', color='#4caf50')
    ax.text(12.2, 4.7, 'No\nComplete', fontsize=6, fontweight='bold', color='#f44336')

    # Add title
    ax.text(6, 8.2, 'Excel Export Process Flow Diagram',
           ha='center', va='center', fontsize=16, fontweight='bold')

    plt.tight_layout()
    plt.savefig('docs/export_process_flow.png', dpi=300, bbox_inches='tight')
    plt.savefig('docs/export_process_flow.pdf', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Generating detailed process flow diagrams...")

    try:
        print("1. Creating application startup process flow...")
        create_startup_process_diagram()
        print("   ✓ Saved as docs/startup_process_flow.png and .pdf")

        print("2. Creating data collection process flow...")
        create_collection_process_diagram()
        print("   ✓ Saved as docs/collection_process_flow.png and .pdf")

        print("3. Creating error handling process flow...")
        create_error_handling_diagram()
        print("   ✓ Saved as docs/error_handling_flow.png and .pdf")

        print("4. Creating Excel export process flow...")
        create_export_process_diagram()
        print("   ✓ Saved as docs/export_process_flow.png and .pdf")

        print("\nAll process flow diagrams generated successfully!")
        print("Open the PNG files in docs/ to view the detailed process flows.")

    except ImportError as e:
        print(f"Error: Missing required library. {e}")
        print("Install with: pip install matplotlib")
    except Exception as e:
        print(f"Error generating diagrams: {e}")