#!/usr/bin/env python3
"""
Evony Active Generals Tracker - Main Application

A Python application that automates the extraction of general information
from the Evony MMO game and exports it to Excel.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
import logging

def setup_logging(config):
    """Setup application logging"""
    log_level = getattr(logging, config.get('log_level', 'INFO').upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('evony_tracker.log', mode='w')
        ]
    )

def main():
    """Main application entry point"""
    # Load configuration
    from config.config_manager import ConfigManager
    config_manager = ConfigManager()
    config = config_manager.load_config()

    # Setup logging
    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info("Starting Evony Active Generals Tracker")

    # Create Qt application
    app = QApplication(sys.argv)
    try:
        aa_hdpi = getattr(Qt, 'AA_EnableHighDpiScaling', None)
        aa_pixmaps = getattr(Qt, 'AA_UseHighDpiPixmaps', None)
        if aa_hdpi is not None:
            app.setAttribute(aa_hdpi, True)
        if aa_pixmaps is not None:
            app.setAttribute(aa_pixmaps, True)
    except AttributeError:
        # Qt version doesn't support these attributes
        pass

    # Create and show main window
    window = MainWindow(config_manager)
    window.show()

    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()