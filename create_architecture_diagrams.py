#!/usr/bin/env python3
"""
Architecture Visualization Script for Evony Active Generals Tracker

This script generates clean, professional architecture diagrams using Python libraries.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_layered_architecture_diagram():
    """Create a layered architecture diagram using matplotlib"""

    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Define colors for different layers
    colors = {
        'entry': '#e1f5fe',      # Light blue
        'ui': '#f3e5f5',         # Light purple
        'controller': '#e8f5e8', # Light green
        'platform': '#fff3e0',   # Light orange
        'ocr': '#fce4ec',        # Light pink
        'navigator': '#e3f2fd',  # Light blue
        'data': '#f1f8e9',       # Light green
        'export': '#fff8e1',     # Light yellow
        'config': '#f5f5f5',     # Light gray
        'external': '#ffebee'    # Light red
    }

    # Layer definitions with positions
    layers = [
        {'name': 'main.py\nEntry Point', 'x': 8, 'y': 9, 'w': 2, 'h': 0.8, 'color': colors['entry']},
        {'name': 'MainWindow\nUI Layer\n(PyQt5 + Dark Mode)', 'x': 8, 'y': 7.5, 'w': 3, 'h': 1.2, 'color': colors['ui']},
        {'name': 'ApplicationController\nBusiness Logic\nOrchestration', 'x': 8, 'y': 5.5, 'w': 4, 'h': 1.4, 'color': colors['controller']},
        {'name': 'BluestacksInterface\nPlatform Layer\nADB Communication', 'x': 3, 'y': 3.5, 'w': 3, 'h': 1.2, 'color': colors['platform']},
        {'name': 'OCREngine\nOCR Layer\nText Extraction', 'x': 8, 'y': 3.5, 'w': 3, 'h': 1.2, 'color': colors['ocr']},
        {'name': 'GameNavigator\nNavigation Layer\nUI Automation', 'x': 13, 'y': 3.5, 'w': 3, 'h': 1.2, 'color': colors['navigator']},
        {'name': 'General Model\nData Layer\nConfidence Tracking', 'x': 8, 'y': 1.5, 'w': 3, 'h': 1.2, 'color': colors['data']},
        {'name': 'ExcelExporter\nExport Layer\nSpreadsheet Generation', 'x': 13, 'y': 1.5, 'w': 3, 'h': 1.2, 'color': colors['export']},
        {'name': 'ConfigManager\nConfiguration\nJSON Settings', 'x': 3, 'y': 7.5, 'w': 2.5, 'h': 1, 'color': colors['config']},
    ]

    # External dependencies
    externals = [
        {'name': 'PyQt5\nGUI', 'x': 1, 'y': 8.5, 'w': 1.5, 'h': 0.6, 'color': colors['external']},
        {'name': 'OpenCV\nImaging', 'x': 1, 'y': 7.5, 'w': 1.5, 'h': 0.6, 'color': colors['external']},
        {'name': 'ADB\nDevice', 'x': 1, 'y': 6.5, 'w': 1.5, 'h': 0.6, 'color': colors['external']},
        {'name': 'OpenPyXL\nExcel', 'x': 1, 'y': 5.5, 'w': 1.5, 'h': 0.6, 'color': colors['external']},
        {'name': 'EasyOCR\nText Recog', 'x': 1, 'y': 4.5, 'w': 1.5, 'h': 0.6, 'color': colors['external']},
        {'name': 'Background\nWorker', 'x': 14.5, 'y': 8.5, 'w': 1.5, 'h': 0.6, 'color': colors['external']},
        {'name': 'Logging\nSystem', 'x': 14.5, 'y': 7.5, 'w': 1.5, 'h': 0.6, 'color': colors['external']},
    ]

    # Draw layers
    for layer in layers:
        rect = FancyBboxPatch((layer['x']-layer['w']/2, layer['y']-layer['h']/2),
                             layer['w'], layer['h'],
                             boxstyle="round,pad=0.05",
                             facecolor=layer['color'],
                             edgecolor='#333333',
                             linewidth=1.5)
        ax.add_patch(rect)

        # Add text
        ax.text(layer['x'], layer['y'], layer['name'],
               ha='center', va='center', fontsize=9, fontweight='bold',
               wrap=True)

    # Draw external dependencies
    for ext in externals:
        rect = FancyBboxPatch((ext['x']-ext['w']/2, ext['y']-ext['h']/2),
                             ext['w'], ext['h'],
                             boxstyle="round,pad=0.02",
                             facecolor=ext['color'],
                             edgecolor='#666666',
                             linewidth=1)
        ax.add_patch(rect)

        ax.text(ext['x'], ext['y'], ext['name'],
               ha='center', va='center', fontsize=7, wrap=True)

    # Draw connection arrows
    connections = [
        # Main flow
        (8, 8.6, 8, 8.3),    # main.py -> MainWindow
        (8, 7.1, 8, 6.7),    # MainWindow -> Controller
        (8, 6.1, 8, 4.7),    # Controller -> OCR
        (8, 6.1, 3, 4.7),    # Controller -> Platform
        (8, 6.1, 13, 4.7),   # Controller -> Navigator
        (8, 4.1, 8, 2.7),    # OCR -> Data Model
        (13, 4.1, 13, 2.7),  # Navigator -> Excel Exporter
        (8, 2.1, 13, 2.7),   # Data Model -> Excel Exporter

        # Configuration
        (4.25, 7.5, 6.5, 7.5),  # Config -> MainWindow
        (4.25, 7.5, 6.5, 6.1),  # Config -> Controller

        # External connections
        (2.25, 8.5, 6.5, 8.3),  # PyQt5 -> MainWindow
        (2.25, 7.5, 4.7, 4.7),  # OpenCV -> Platform
        (2.25, 6.5, 4.7, 4.7),  # ADB -> Platform
        (2.25, 5.5, 11.3, 2.7), # OpenPyXL -> Excel Exporter
        (2.25, 4.5, 9.3, 4.7),  # EasyOCR -> OCR
        (13.25, 8.5, 11.3, 6.7), # Worker -> Controller
        (13.25, 7.5, 8, 6.7),   # Logging -> All
    ]

    for x1, y1, x2, y2 in connections:
        ax.arrow(x1, y1, x2-x1, y2-y1,
                head_width=0.08, head_length=0.1,
                fc='#666666', ec='#666666',
                length_includes_head=True, alpha=0.7)

    # Add title
    ax.text(8, 9.7, 'Evony Active Generals Tracker - Architecture Overview',
           ha='center', va='center', fontsize=16, fontweight='bold')

    # Add legend
    legend_elements = [
        ('Entry Point', colors['entry']),
        ('UI Layer', colors['ui']),
        ('Controller Layer', colors['controller']),
        ('Platform/OCR/Navigation', colors['platform']),
        ('Data/Export Layer', colors['data']),
        ('Configuration', colors['config']),
        ('External Dependencies', colors['external'])
    ]

    legend_x, legend_y = 0.02, 0.02
    for i, (label, color) in enumerate(legend_elements):
        rect = FancyBboxPatch((legend_x, legend_y + i*0.05), 0.03, 0.03,
                             boxstyle="round,pad=0",
                             facecolor=color, edgecolor='#333333')
        ax.add_patch(rect)
        ax.text(legend_x + 0.04, legend_y + i*0.05 + 0.015, label,
               fontsize=8, va='center')

    plt.tight_layout()
    plt.savefig('docs/architecture_diagram.png', dpi=300, bbox_inches='tight')
    plt.savefig('docs/architecture_diagram.pdf', bbox_inches='tight')
    plt.show()

def create_network_graph_diagram():
    """Create a network graph showing component relationships"""

    # Create directed graph
    G = nx.DiGraph()

    # Add nodes with categories
    nodes = {
        'main.py': {'layer': 'entry', 'size': 800},
        'MainWindow': {'layer': 'ui', 'size': 1000},
        'ConfigManager': {'layer': 'config', 'size': 600},
        'ApplicationController': {'layer': 'controller', 'size': 1200},
        'BluestacksInterface': {'layer': 'platform', 'size': 800},
        'OCREngine': {'layer': 'ocr', 'size': 800},
        'GameNavigator': {'layer': 'navigator', 'size': 800},
        'General': {'layer': 'data', 'size': 700},
        'ExcelExporter': {'layer': 'export', 'size': 700},
        'CollectionWorker': {'layer': 'threading', 'size': 500},
        'Logging': {'layer': 'external', 'size': 400},
    }

    for node, attrs in nodes.items():
        G.add_node(node, **attrs)

    # Add edges (relationships)
    edges = [
        ('main.py', 'MainWindow'),
        ('main.py', 'ConfigManager'),
        ('MainWindow', 'ConfigManager'),
        ('MainWindow', 'ApplicationController'),
        ('MainWindow', 'CollectionWorker'),
        ('ConfigManager', 'ApplicationController'),
        ('ApplicationController', 'BluestacksInterface'),
        ('ApplicationController', 'OCREngine'),
        ('ApplicationController', 'GameNavigator'),
        ('ApplicationController', 'General'),
        ('ApplicationController', 'ExcelExporter'),
        ('GameNavigator', 'BluestacksInterface'),
        ('GameNavigator', 'OCREngine'),
        ('OCREngine', 'General'),
        ('General', 'ExcelExporter'),
        ('CollectionWorker', 'ApplicationController'),
        ('Logging', 'MainWindow'),
        ('Logging', 'ApplicationController'),
        ('Logging', 'BluestacksInterface'),
        ('Logging', 'OCREngine'),
        ('Logging', 'GameNavigator'),
        ('Logging', 'ExcelExporter'),
    ]

    G.add_edges_from(edges)

    # Define colors for layers
    layer_colors = {
        'entry': '#e1f5fe',
        'ui': '#f3e5f5',
        'config': '#f5f5f5',
        'controller': '#e8f5e8',
        'platform': '#fff3e0',
        'ocr': '#fce4ec',
        'navigator': '#e3f2fd',
        'data': '#f1f8e9',
        'export': '#fff8e1',
        'threading': '#f5f5f5',
        'external': '#ffebee'
    }

    # Create layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    plt.figure(figsize=(14, 10))

    # Draw nodes
    node_colors = [layer_colors[G.nodes[node]['layer']] for node in G.nodes()]
    node_sizes = [G.nodes[node]['size'] for node in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                          node_size=node_sizes, alpha=0.8,
                          edgecolors='#333333', linewidths=1.5)

    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='#666666',
                          arrows=True, arrowsize=20,
                          arrowstyle='->', alpha=0.6,
                          connectionstyle='arc3,rad=0.1')

    # Draw labels
    labels = {node: node.replace('ApplicationController', 'AppController')
                     .replace('BluestacksInterface', 'PlatformInterface')
                     .replace('CollectionWorker', 'WorkerThread')
              for node in G.nodes()}

    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')

    plt.title('Evony Active Generals Tracker - Component Relationship Graph',
             fontsize=16, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()

    plt.savefig('docs/architecture_network.png', dpi=300, bbox_inches='tight')
    plt.savefig('docs/architecture_network.pdf', bbox_inches='tight')
    plt.show()

def create_data_flow_diagram():
    """Create a data flow diagram showing the collection process"""

    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Define process steps
    processes = [
        {'name': 'User Clicks\n"Start Collection"', 'x': 1, 'y': 6, 'w': 2, 'h': 1},
        {'name': 'Navigate to\nGenerals List', 'x': 4, 'y': 6, 'w': 2, 'h': 1},
        {'name': 'Count Total\nGenerals', 'x': 7, 'y': 6, 'w': 2, 'h': 1},
        {'name': 'For Each General:\nOpen Details', 'x': 10, 'y': 6, 'w': 2, 'h': 1},
        {'name': 'Capture\nScreenshot', 'x': 13, 'y': 6, 'w': 2, 'h': 1},
        {'name': 'Extract Data\nvia OCR', 'x': 7, 'y': 4, 'w': 2, 'h': 1},
        {'name': 'Create General\nModel', 'x': 10, 'y': 4, 'w': 2, 'h': 1},
        {'name': 'Navigate to\nSubscreens', 'x': 13, 'y': 4, 'w': 2, 'h': 1},
        {'name': 'Extract Additional\nData', 'x': 7, 'y': 2, 'w': 2, 'h': 1},
        {'name': 'Calculate\nConfidence', 'x': 10, 'y': 2, 'w': 2, 'h': 1},
        {'name': 'Export to\nExcel', 'x': 13, 'y': 2, 'w': 2, 'h': 1},
    ]

    # Draw process boxes
    for process in processes:
        rect = FancyBboxPatch((process['x']-process['w']/2, process['y']-process['h']/2),
                             process['w'], process['h'],
                             boxstyle="round,pad=0.05",
                             facecolor='#e3f2fd',
                             edgecolor='#1976d2',
                             linewidth=2)
        ax.add_patch(rect)

        ax.text(process['x'], process['y'], process['name'],
               ha='center', va='center', fontsize=9, fontweight='bold',
               wrap=True)

    # Draw flow arrows
    flow_connections = [
        (1, 6, 4, 6),   # Start -> Navigate
        (4, 6, 7, 6),   # Navigate -> Count
        (7, 6, 10, 6),  # Count -> Open Details
        (10, 6, 13, 6), # Open Details -> Capture
        (13, 6, 13, 5), # Capture -> Extract Data
        (13, 5, 10, 4), # -> Create Model
        (10, 4, 13, 4), # Create Model -> Navigate Subscreens
        (13, 4, 13, 3), # Navigate -> Extract Additional
        (13, 3, 10, 2), # -> Calculate Confidence
        (10, 2, 13, 2), # Calculate -> Export
    ]

    for x1, y1, x2, y2 in flow_connections:
        ax.arrow(x1, y1, x2-x1, y2-y1,
                head_width=0.1, head_length=0.15,
                fc='#1976d2', ec='#1976d2',
                length_includes_head=True, alpha=0.8)

    # Add loop indicator
    ax.text(7, 7.2, 'Loop through all generals', fontsize=10, fontweight='bold',
           ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor='#fff3e0'))

    # Add data stores
    data_stores = [
        {'name': 'Screenshot\nBuffer', 'x': 13, 'y': 5, 'w': 1.5, 'h': 0.6},
        {'name': 'General\nModels', 'x': 10, 'y': 3, 'w': 1.5, 'h': 0.6},
        {'name': 'Excel\nTemplate', 'x': 13, 'y': 1, 'w': 1.5, 'h': 0.6},
    ]

    for store in data_stores:
        rect = FancyBboxPatch((store['x']-store['w']/2, store['y']-store['h']/2),
                             store['w'], store['h'],
                             boxstyle="round,pad=0.02",
                             facecolor='#f1f8e9',
                             edgecolor='#388e3c',
                             linewidth=1.5)
        ax.add_patch(rect)

        ax.text(store['x'], store['y'], store['name'],
               ha='center', va='center', fontsize=8, wrap=True)

    # Add title
    ax.text(8, 7.5, 'Data Collection Process Flow',
           ha='center', va='center', fontsize=16, fontweight='bold')

    plt.tight_layout()
    plt.savefig('docs/data_flow_diagram.png', dpi=300, bbox_inches='tight')
    plt.savefig('docs/data_flow_diagram.pdf', bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("Generating architecture diagrams...")

    try:
        print("1. Creating layered architecture diagram...")
        create_layered_architecture_diagram()
        print("   ✓ Saved as docs/architecture_diagram.png and .pdf")

        print("2. Creating network relationship graph...")
        create_network_graph_diagram()
        print("   ✓ Saved as docs/architecture_network.png and .pdf")

        print("3. Creating data flow diagram...")
        create_data_flow_diagram()
        print("   ✓ Saved as docs/data_flow_diagram.png and .pdf")

        print("\nAll diagrams generated successfully!")
        print("Open the PNG files to view the visualizations.")

    except ImportError as e:
        print(f"Error: Missing required library. {e}")
        print("Install with: pip install matplotlib networkx")
    except Exception as e:
        print(f"Error generating diagrams: {e}")