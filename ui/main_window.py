"""
Main window implementation for Evony Active Generals Tracker
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QProgressBar,
    QTableWidgetItem, QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

from main_window_ui import Ui_MainWindow
from controllers.application_controller import ApplicationController
from models.general import General
from config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.config_manager = config_manager
        self.controller = None
        self.collection_thread = None
        self.generals_data: List[General] = []

        self._setup_ui()
        self._connect_signals()
        self._load_config()

        logger.info("Main window initialized")

    def _setup_ui(self):
        """Setup additional UI elements"""
        # Set window icon if available
        icon_path = Path(__file__).parent.parent / "Resources" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Clean up debug images from previous sessions
        self._cleanup_debug_images()

        # Configure generals table
        self.ui.generals_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.generals_table.setAlternatingRowColors(True)
        self.ui.generals_table.horizontalHeader().setStretchLastSection(True)
        self.ui.generals_table.setSortingEnabled(True)

        # Set monospace font for log display
        log_font = QFont("Consolas", 9)
        self.ui.log_display.setFont(log_font)

        # Set default values
        self.ui.confidence_spin.setValue(0.8)
        self.ui.delay_spin.setValue(1.5)

        # Apply additional custom styling
        self._apply_custom_styling()

    def _apply_custom_styling(self):
        """Apply additional custom styling for enhanced visual appeal"""
        # Custom styling for specific buttons with accent colors
        start_button_style = """
        QPushButton {
            background-color: #a6e3a1;
            color: #1e1e2e;
            border: 2px solid #a6e3a1;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 11pt;
        }
        QPushButton:hover {
            background-color: #94e2cd;
            border-color: #94e2cd;
        }
        QPushButton:pressed {
            background-color: #89dceb;
        }
        QPushButton:disabled {
            background-color: #313244;
            color: #6c7086;
            border-color: #313244;
        }
        """
        self.ui.start_collect_btn.setStyleSheet(start_button_style)

        stop_button_style = """
        QPushButton {
            background-color: #f38ba8;
            color: #1e1e2e;
            border: 2px solid #f38ba8;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 11pt;
        }
        QPushButton:hover {
            background-color: #eba0ac;
            border-color: #eba0ac;
        }
        QPushButton:pressed {
            background-color: #f5c2e7;
        }
        QPushButton:disabled {
            background-color: #313244;
            color: #6c7086;
            border-color: #313244;
        }
        """
        self.ui.stop_collect_btn.setStyleSheet(stop_button_style)

        connect_button_style = """
        QPushButton {
            background-color: #89b4fa;
            color: #1e1e2e;
            border: 2px solid #89b4fa;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #74c7ec;
            border-color: #74c7ec;
        }
        QPushButton:pressed {
            background-color: #89dceb;
        }
        """
        self.ui.connect_btn.setStyleSheet(connect_button_style)

        export_button_style = """
        QPushButton {
            background-color: #f9e2af;
            color: #1e1e2e;
            border: 2px solid #f9e2af;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #f5c2e7;
            border-color: #f5c2e7;
        }
        QPushButton:pressed {
            background-color: #eba0ac;
        }
        QPushButton:disabled {
            background-color: #313244;
            color: #6c7086;
            border-color: #313244;
        }
        """
        self.ui.export_btn.setStyleSheet(export_button_style)

        # Enhanced progress bar styling
        progress_style = """
        QProgressBar {
            border: 2px solid #585b70;
            border-radius: 8px;
            text-align: center;
            background-color: #313244;
            color: #cdd6f4;
            font-weight: bold;
            font-size: 10pt;
        }
        QProgressBar::chunk {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #89b4fa, stop:0.5 #f38ba8, stop:1 #a6e3a1);
            border-radius: 6px;
        }
        """
        self.ui.progress_bar.setStyleSheet(progress_style)
        self.ui.progress_bar_detailed.setStyleSheet(progress_style)

        # Status label styling
        status_style = """
        QLabel {
            color: #cdd6f4;
            font-weight: bold;
            font-size: 11pt;
            padding: 4px;
        }
        """
        self.ui.status_label.setStyleSheet(status_style)

        # Statistics labels with different colors
        self.ui.total_label.setStyleSheet("QLabel { color: #a6e3a1; font-weight: bold; }")
        self.ui.uncertain_label.setStyleSheet("QLabel { color: #f38ba8; font-weight: bold; }")

        # Progress statistics with accent colors
        self.ui.elapsed_time_label.setStyleSheet("QLabel { color: #89b4fa; }")
        self.ui.estimated_time_label.setStyleSheet("QLabel { color: #f9e2af; }")
        self.ui.average_confidence_label.setStyleSheet("QLabel { color: #a6e3a1; }")

    def _cleanup_debug_images(self):
        """Clean up debug images from previous sessions"""
        try:
            debug_dir = Path(__file__).parent.parent / "debug_images"
            if debug_dir.exists():
                # Delete all files in debug_images directory
                for file_path in debug_dir.iterdir():
                    if file_path.is_file():
                        file_path.unlink()
                        logger.debug(f"Deleted debug image: {file_path.name}")
                logger.info("Cleaned up debug images from previous session")
            else:
                logger.debug("Debug images directory does not exist, nothing to clean up")
        except Exception as e:
            logger.warning(f"Failed to clean up debug images: {e}")

    def _connect_signals(self):
        """Connect UI signals to slots"""
        # Connection controls
        self.ui.connect_btn.clicked.connect(self._on_connect_clicked)
        self.ui.adb_path_browse.clicked.connect(self._on_adb_browse_clicked)

        # Collection controls
        self.ui.start_collect_btn.clicked.connect(self._on_start_collection_clicked)
        self.ui.stop_collect_btn.clicked.connect(self._on_stop_collection_clicked)

        # Export controls
        self.ui.export_btn.clicked.connect(self._on_export_clicked)

        # Menu actions
        self.ui.actionExport.triggered.connect(self._on_export_clicked)
        self.ui.actionExit.triggered.connect(self._on_exit_clicked)
        self.ui.actionTestConnection.triggered.connect(self._on_test_connection_clicked)
        self.ui.actionAbout.triggered.connect(self._on_about_clicked)

        # Tab switching actions
        self.ui.actionGeneralsTab.triggered.connect(lambda: self.ui.tab_widget.setCurrentIndex(0))
        self.ui.actionProgressTab.triggered.connect(lambda: self.ui.tab_widget.setCurrentIndex(1))
        self.ui.actionLogsTab.triggered.connect(lambda: self.ui.tab_widget.setCurrentIndex(2))

        # Log controls
        self.ui.clear_log_btn.clicked.connect(self.ui.log_display.clear)
        self.ui.save_log_btn.clicked.connect(self._on_save_log_clicked)

        # Settings changes
        self.ui.debug_check.stateChanged.connect(self._on_debug_changed)

    def _load_config(self):
        """Load configuration into UI"""
        config = self.config_manager._config

        # Platform settings
        platform_index = self.ui.platform_combo.findText(config.get('platform_type', 'bluestacks'))
        if platform_index >= 0:
            self.ui.platform_combo.setCurrentIndex(platform_index)

        self.ui.device_id_edit.setText(config.get('device_id', '127.0.0.1:5555'))
        self.ui.adb_path_edit.setText(config.get('adb_path', ''))

        # OCR settings
        ocr_index = self.ui.ocr_engine_combo.findText(config.get('ocr_engine', 'easyocr'))
        if ocr_index >= 0:
            self.ui.ocr_engine_combo.setCurrentIndex(ocr_index)

        self.ui.confidence_spin.setValue(config.get('confidence_threshold', 0.8))
        self.ui.delay_spin.setValue(config.get('screen_transition_delay', 1.5))
        self.ui.debug_check.setChecked(config.get('debug_mode', False))
        self.ui.auto_open_check.setChecked(config.get('auto_open_excel', False))

    def _save_config(self):
        """Save UI settings to configuration"""
        config_updates = {
            'platform_type': self.ui.platform_combo.currentText(),
            'device_id': self.ui.device_id_edit.text(),
            'adb_path': self.ui.adb_path_edit.text(),
            'ocr_engine': self.ui.ocr_engine_combo.currentText(),
            'confidence_threshold': self.ui.confidence_spin.value(),
            'screen_transition_delay': self.ui.delay_spin.value(),
            'debug_mode': self.ui.debug_check.isChecked(),
            'auto_open_excel': self.ui.auto_open_check.isChecked()
        }

        self.config_manager.update(config_updates)
        self.config_manager.save_config()

    def _on_connect_clicked(self):
        """Handle connect button click"""
        try:
            self._save_config()
            config = self.config_manager._config

            # Change button text and disable it
            self.ui.connect_btn.setText("Connecting...")
            self.ui.connect_btn.setEnabled(False)

            # Start connection in background thread
            self.connection_thread = ConnectionWorker(config)
            self.connection_thread.connection_finished.connect(self._on_connection_finished)
            self.connection_thread.connection_failed.connect(self._on_connection_failed)
            self.connection_thread.start()

        except Exception as e:
            logger.error(f"Connection setup error: {e}")
            self._log_message(f"Connection setup error: {e}")
            QMessageBox.critical(self, "Error", f"Connection setup error: {e}")
            # Reset button state
            self.ui.connect_btn.setText("Connect")
            self.ui.connect_btn.setEnabled(True)

    def _on_adb_browse_clicked(self):
        """Handle ADB path browse button"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select ADB Executable", "", "Executable files (*.exe);;All files (*)"
        )
        if file_path:
            self.ui.adb_path_edit.setText(file_path)

    def _on_start_collection_clicked(self):
        """Handle start collection button"""
        if not self.controller:
            QMessageBox.warning(self, "Not Connected", "Please connect to a platform first.")
            return

        # Clear existing data and reset UI
        self.generals_data = []
        self._update_generals_table()
        self.ui.export_btn.setEnabled(False)
        self.ui.status_label.setText("Starting Collection...")

        # Disable controls
        self.ui.start_collect_btn.setEnabled(False)
        self.ui.stop_collect_btn.setEnabled(True)
        self.ui.connect_btn.setEnabled(False)
        self.ui.progress_bar.setVisible(True)

        # Start collection in background thread (no export path needed)
        self.collection_thread = CollectionWorker(self.controller, None)
        self.collection_thread.progress_updated.connect(self._on_progress_updated)
        self.collection_thread.collection_finished.connect(self._on_collection_finished)
        self.collection_thread.error_occurred.connect(self._on_collection_error)
        self.collection_thread.start()

        self._log_message("Starting data collection with automatic Excel export to ./Spreadsheets directory...")

    def _on_stop_collection_clicked(self):
        """Handle stop collection button"""
        if self.collection_thread and self.collection_thread.isRunning():
            self.collection_thread.stop()
            self._log_message("Stopping data collection...")

    def _on_progress_updated(self, progress_info: dict):
        """Handle progress updates"""
        # Update progress bar
        if 'percentage' in progress_info:
            self.ui.progress_bar.setValue(int(progress_info['percentage']))

        # Update detailed progress
        if 'current_general' in progress_info and 'total_generals' in progress_info:
            current = progress_info['current_general']
            total = progress_info['total_generals']
            self.ui.progress_general_label.setText(f"{current} / {total}")
            self.ui.progress_bar_detailed.setValue(int((current / total) * 100) if total > 0 else 0)

        if 'current_step' in progress_info:
            self.ui.progress_step_label.setText(progress_info['current_step'])

        if 'status' in progress_info:
            status = progress_info['status']
            self.ui.progress_status_label.setText(status)

            # Dynamic status color based on status
            if 'idle' in status.lower():
                self.ui.progress_status_label.setStyleSheet("QLabel { color: #6c7086; font-weight: bold; }")
            elif 'complete' in status.lower():
                self.ui.progress_status_label.setStyleSheet("QLabel { color: #a6e3a1; font-weight: bold; }")
            elif 'error' in status.lower() or 'failed' in status.lower():
                self.ui.progress_status_label.setStyleSheet("QLabel { color: #f38ba8; font-weight: bold; }")
            elif 'processing' in status.lower() or 'collecting' in status.lower():
                self.ui.progress_status_label.setStyleSheet("QLabel { color: #89b4fa; font-weight: bold; }")
            else:
                self.ui.progress_status_label.setStyleSheet("QLabel { color: #cdd6f4; font-weight: bold; }")

        if 'elapsed_time' in progress_info:
            self.ui.elapsed_time_label.setText(f"{progress_info['elapsed_time']:.1f} seconds")

        if 'estimated_remaining' in progress_info:
            remaining = progress_info['estimated_remaining']
            if remaining and remaining != 'Unknown':
                self.ui.estimated_time_label.setText(f"{remaining:.1f} seconds")
            else:
                self.ui.estimated_time_label.setText("Unknown")

        if 'average_confidence' in progress_info:
            confidence = progress_info['average_confidence']
            self.ui.average_confidence_label.setText(f"{confidence:.1f}%")

            # Color confidence based on value
            if confidence >= 90:
                self.ui.average_confidence_label.setStyleSheet("QLabel { color: #a6e3a1; font-weight: bold; }")
            elif confidence >= 80:
                self.ui.average_confidence_label.setStyleSheet("QLabel { color: #f9e2af; font-weight: bold; }")
            else:
                self.ui.average_confidence_label.setStyleSheet("QLabel { color: #f38ba8; font-weight: bold; }")

        # Update generals table if data is provided
        if 'generals_data' in progress_info:
            self.generals_data = progress_info['generals_data']
            self._update_generals_table()

    def _on_connection_finished(self, controller: ApplicationController):
        """Handle successful connection"""
        self.controller = controller
        self.ui.connect_btn.setText("Disconnect")
        self.ui.connect_btn.setEnabled(True)
        self.ui.start_collect_btn.setEnabled(True)
        self.ui.status_label.setText("Connected")
        self._log_message("Successfully connected to platform")

    def _on_connection_failed(self, error_msg: str):
        """Handle connection failure"""
        self.ui.connect_btn.setText("Connect")
        self.ui.connect_btn.setEnabled(True)
        self._log_message(f"Failed to connect to platform: {error_msg}")
        QMessageBox.warning(self, "Connection Failed", f"Failed to connect to platform: {error_msg}")

    def _on_collection_finished(self, generals: List[General], excel_path: str = None):
        """Handle collection completion"""
        logger.info(f"Collection finished with {len(generals)} generals, Excel file: {excel_path}")
        self.generals_data = generals

        # Re-enable controls
        self.ui.start_collect_btn.setEnabled(True)
        self.ui.stop_collect_btn.setEnabled(False)
        self.ui.connect_btn.setEnabled(True)
        self.ui.export_btn.setEnabled(True)
        self.ui.progress_bar.setVisible(False)

        # Update UI
        self._update_generals_table()
        self.ui.status_label.setText("Collection Complete")

        self._log_message(f"Collection completed. Found {len(generals)} generals.")

        # Handle Excel file
        if excel_path and os.path.exists(excel_path):
            self._log_message(f"Excel file created: {excel_path}")
            
            reply = QMessageBox.question(
                self, "Collection Complete",
                f"Collection complete! Data has been saved to:\n{excel_path}\n\nWould you like to open this file now?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                os.startfile(excel_path)
        else:
            QMessageBox.information(
                self, "Collection Complete",
                f"Successfully collected data for {len(generals)} generals."
            )

    def _on_collection_error(self, error_msg: str):
        """Handle collection error"""
        # Re-enable controls
        self.ui.start_collect_btn.setEnabled(True)
        self.ui.stop_collect_btn.setEnabled(False)
        self.ui.connect_btn.setEnabled(True)
        self.ui.progress_bar.setVisible(False)

        # Check if collection was stopped by user
        if "stopped by user" in error_msg.lower():
            self.ui.status_label.setText("Collection Stopped")
            self._log_message("Collection stopped by user. Data collected so far is available in the table.")

            QMessageBox.information(
                self, "Collection Stopped",
                "Collection was stopped by user. Data collected so far is available in the table."
            )
        else:
            self.ui.status_label.setText("Collection Failed")
            self._log_message(f"Collection error: {error_msg}")
            QMessageBox.critical(self, "Collection Error", f"Collection failed: {error_msg}")

    def _save_incremental_file(self):
        """Save the incremental export file to a user-selected location"""
        if not hasattr(self, 'incremental_export_path') or not os.path.exists(self.incremental_export_path):
            QMessageBox.warning(self, "No File", "No incremental export file found.")
            return

        # Get save location from user
        default_path = self.config_manager.get('default_export_path', '~/Documents/Evony')
        expanded_path = os.path.expanduser(default_path)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Collected Data", expanded_path,
            "Excel files (*.xlsx);;All files (*)"
        )

        if not file_path:
            return

        try:
            # Copy the incremental file to the selected location
            import shutil
            shutil.copy2(self.incremental_export_path, file_path)

            self._log_message(f"Data saved to {file_path}")
            QMessageBox.information(self, "Save Complete", f"Data saved successfully to {file_path}")

            # Auto-open if enabled
            if self.ui.auto_open_check.isChecked():
                os.startfile(file_path)

        except Exception as e:
            logger.error(f"Save error: {e}")
            self._log_message(f"Save error: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save file: {e}")

    def _update_generals_table(self):
        """Update the generals table with collected data"""
        logger.info(f"Updating generals table with {len(self.generals_data)} generals")
        self.ui.generals_table.setRowCount(len(self.generals_data))

        uncertain_count = 0
        for row, general in enumerate(self.generals_data):
            logger.debug(f"Updating row {row} with general: {general.name}, power: {general.power}, uncertain: {general.is_uncertain}")
            # Name
            self.ui.generals_table.setItem(row, 0, QTableWidgetItem(general.name or ""))

            # Power
            power_item = QTableWidgetItem(f"{general.power:,}" if general.power else "")
            display_role = getattr(Qt, 'DisplayRole', 0)
            power_item.setData(display_role, general.power)
            self.ui.generals_table.setItem(row, 1, power_item)

            # Uncertain flag
            uncertain = "Yes" if general.is_uncertain else "No"
            self.ui.generals_table.setItem(row, 2, QTableWidgetItem(uncertain))

            if general.is_uncertain:
                uncertain_count += 1

        # Update statistics
        self.ui.total_label.setText(f"Total: {len(self.generals_data)}")
        self.ui.uncertain_label.setText(f"Uncertain: {uncertain_count}")

        # Resize columns to content
        self.ui.generals_table.resizeColumnsToContents()

        # Force UI refresh
        self.ui.generals_table.repaint()
        self.ui.generals_table.update()
        logger.info("Generals table update completed")

    def _on_export_clicked(self):
        """Handle export button click"""
        if not self.generals_data:
            QMessageBox.warning(self, "No Data", "No generals data to export. Please collect data first.")
            return

        # Get export path
        default_path = self.config_manager.get('default_export_path', '~/Documents/Evony')
        expanded_path = os.path.expanduser(default_path)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to Excel", expanded_path,
            "Excel files (*.xlsx);;All files (*)"
        )

        if not file_path:
            return

        try:
            # Export data
            success = self.controller.export_to_excel(file_path, self.generals_data, incremental=False)
            if success:
                self._log_message(f"Data exported to {file_path}")
                QMessageBox.information(self, "Export Complete", f"Data exported successfully to {file_path}")

                # Auto-open if enabled
                if self.ui.auto_open_check.isChecked():
                    os.startfile(file_path)
            else:
                QMessageBox.warning(self, "Export Failed", "Failed to export data to Excel.")

        except Exception as e:
            logger.error(f"Export error: {e}")
            self._log_message(f"Export error: {e}")
            QMessageBox.critical(self, "Export Error", f"Export failed: {e}")

    def _on_exit_clicked(self):
        """Handle exit menu action"""
        self.close()

    def _on_test_connection_clicked(self):
        """Handle test connection menu action"""
        # Same as connect but without changing UI state
        try:
            config = self.config_manager._config
            controller = ApplicationController(config)

            if controller.initialize_platform():
                self._log_message("Connection test successful")
                QMessageBox.information(self, "Test Successful", "Connection test passed!")
            else:
                self._log_message("Connection test failed")
                QMessageBox.warning(self, "Test Failed", "Connection test failed.")

        except Exception as e:
            logger.error(f"Connection test error: {e}")
            self._log_message(f"Connection test error: {e}")
            QMessageBox.critical(self, "Test Error", f"Connection test error: {e}")

    def _on_about_clicked(self):
        """Handle about menu action"""
        QMessageBox.about(
            self, "About Evony Active Generals Tracker",
            "Evony Active Generals Tracker v1.0\n\n"
            "A tool for extracting and organizing general information from Evony MMO.\n\n"
            "Built with Python, PyQt5, and OCR technology."
        )

    def _on_save_log_clicked(self):
        """Handle save log button"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Log", "evony_tracker.log",
            "Log files (*.log);;Text files (*.txt);;All files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.ui.log_display.toPlainText())
                QMessageBox.information(self, "Log Saved", f"Log saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save log: {e}")

    def _on_debug_changed(self, state):
        """Handle debug mode checkbox change"""
        checked_state = getattr(Qt, 'Checked', 2)  # 2 is typically Qt.Checked
        debug_mode = state == checked_state
        self.config_manager.set('debug_mode', debug_mode)
        self.config_manager.save_config()

        level = logging.DEBUG if debug_mode else logging.INFO
        logging.getLogger().setLevel(level)

    def _log_message(self, message: str):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.ui.log_display.append(f"[{timestamp}] {message}")

    def closeEvent(self, a0):
        """Handle window close event"""
        # Stop any running collection
        if self.collection_thread and self.collection_thread.isRunning():
            self.collection_thread.stop()
            self.collection_thread.wait()

        # Save configuration
        self._save_config()

        a0.accept()


class CollectionWorker(QThread):
    """Worker thread for data collection"""

    progress_updated = pyqtSignal(dict)
    collection_finished = pyqtSignal(list, str)  # generals list and excel file path
    error_occurred = pyqtSignal(str)

    def __init__(self, controller: ApplicationController, export_path: str = None):
        super().__init__()
        self.controller = controller
        self.export_path = export_path  # Kept for compatibility but not used
        self._stop_flag = False

    def run(self):
        """Run collection in background thread"""
        try:
            def progress_callback(progress_info):
                if self._stop_flag:
                    raise KeyboardInterrupt("Collection stopped by user")
                self.progress_updated.emit(progress_info)

            generals, excel_path = self.controller.collect_all_generals(progress_callback, self.export_path)
            self.collection_finished.emit(generals, excel_path)

        except KeyboardInterrupt:
            self.error_occurred.emit("Collection stopped by user")
        except Exception as e:
            logger.error(f"Collection error: {e}")
            self.error_occurred.emit(str(e))

    def stop(self):
        """Stop the collection"""
        self._stop_flag = True


class ConnectionWorker(QThread):
    """Worker thread for platform connection"""

    connection_finished = pyqtSignal(object)  # ApplicationController
    connection_failed = pyqtSignal(str)

    def __init__(self, config: dict):
        super().__init__()
        self.config = config

    def run(self):
        """Run connection in background thread"""
        try:
            # Initialize controller
            controller = ApplicationController(self.config)

            # Test connection
            if controller.initialize_platform():
                self.connection_finished.emit(controller)
            else:
                self.connection_failed.emit("Failed to connect to platform")

        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connection_failed.emit(str(e))