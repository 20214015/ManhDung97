#!/usr/bin/env python3
"""
Cache System Demo for MuMu Manager Backend
Test cache functionality với auto refresh và manual refresh
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QHBoxLayout, QSpinBox, QCheckBox
from PyQt6.QtCore import QTimer, pyqtSignal, QThread
import time

# Add parent directory to path để import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import MumuManager

class CacheDemoWindow(QMainWindow):
    """Demo window cho cache system."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MuMu Manager Cache System Demo")
        self.setGeometry(100, 100, 800, 600)

        # Initialize backend
        self.backend = MumuManager(r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe")

        # Setup UI
        self.setup_ui()

        # Connect cache callbacks
        self.backend.add_cache_callback(self.on_cache_updated)

        # Initial cache refresh
        self.manual_refresh()

    def setup_ui(self):
        """Setup UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Control panel
        control_layout = QHBoxLayout()

        # Auto refresh controls
        self.auto_refresh_checkbox = QCheckBox("Auto Refresh")
        self.auto_refresh_checkbox.setChecked(False)
        self.auto_refresh_checkbox.stateChanged.connect(self.toggle_auto_refresh)

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 10)
        self.interval_spinbox.setValue(3)
        self.interval_spinbox.setSuffix("s")
        self.interval_spinbox.valueChanged.connect(self.change_refresh_interval)

        # Manual refresh button
        self.refresh_button = QPushButton("Manual Refresh")
        self.refresh_button.clicked.connect(self.manual_refresh)

        # Clear cache button
        self.clear_button = QPushButton("Clear Cache")
        self.clear_button.clicked.connect(self.clear_cache)

        control_layout.addWidget(self.auto_refresh_checkbox)
        control_layout.addWidget(QLabel("Interval:"))
        control_layout.addWidget(self.interval_spinbox)
        control_layout.addWidget(self.refresh_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addStretch()

        layout.addLayout(control_layout)

        # Status label
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)

        # Cache info
        self.cache_info_label = QLabel("Cache Info: Not loaded")
        layout.addWidget(self.cache_info_label)

        # Log area
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)

        # Instance list
        self.instance_text = QTextEdit()
        layout.addWidget(self.instance_text)

    def toggle_auto_refresh(self, state: int) -> None:
        """Toggle auto refresh on/off."""
        if state:
            interval_ms = self.interval_spinbox.value() * 1000
            self.backend.start_auto_refresh(interval_ms)
            self.log_message(f"🔄 Auto refresh started with {interval_ms}ms interval")
        else:
            self.backend.stop_auto_refresh()
            self.log_message("⏹️ Auto refresh stopped")

    def change_refresh_interval(self, value: int) -> None:
        """Change refresh interval."""
        if self.auto_refresh_checkbox.isChecked():
            interval_ms = value * 1000
            self.backend.set_refresh_interval(interval_ms)
            self.log_message(f"🔄 Refresh interval changed to {interval_ms}ms")

    def manual_refresh(self):
        """Manual cache refresh."""
        self.log_message("🔄 Manual refresh triggered...")
        self.status_label.setText("Status: Refreshing...")

        success, message = self.backend.refresh_cache()
        if success:
            self.status_label.setText("Status: Refreshed successfully")
            self.log_message(f"✅ Cache refreshed: {message}")
        else:
            self.status_label.setText("Status: Refresh failed")
            self.log_message(f"❌ Cache refresh failed: {message}")

        self.update_display()

    def clear_cache(self):
        """Clear cache."""
        self.backend.clear_cache()
        self.log_message("🗑️ Cache cleared")
        self.update_display()

    def on_cache_updated(self):
        """Callback khi cache được cập nhật."""
        self.log_message("📡 Cache updated callback triggered")
        self.update_display()

    def update_display(self):
        """Update display với cache info."""
        # Update cache info
        cache = self.backend.get_cached_instances()
        cache_count = len(cache)
        is_valid = self.backend.is_cache_valid()

        self.cache_info_label.setText(f"Cache Info: {cache_count} instances, Valid: {is_valid}")

        # Update instance list
        if cache:
            instance_text = "Cached Instances:\n"
            for vm_index, data in sorted(cache.items()):
                name = data.get('name', 'Unknown')
                status = data.get('status', 'Unknown')
                cpu = data.get('cpu', 'N/A')
                memory = data.get('memory', 'N/A')
                disk = data.get('disk_usage', 'N/A')
                running = data.get('running', False)

                status_icon = "🟢" if running else "🔴"
                instance_text += f"{status_icon} VM{vm_index}: {name} | Status: {status} | CPU: {cpu} | Mem: {memory} | Disk: {disk}\n"

            self.instance_text.setText(instance_text)
        else:
            self.instance_text.setText("No cached instances")

    def log_message(self, message):
        """Add message to log."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

        # Auto scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

def main():
    """Main function."""
    app = QApplication(sys.argv)

    # Create and show demo window
    window = CacheDemoWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
