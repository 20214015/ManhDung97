"""
Example Plugin: System Monitor
==============================

A demonstration plugin that adds system monitoring capabilities
to MuMuManager Pro.
"""

import psutil
import time
from typing import Dict, Any, Optional
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QProgressBar, QGroupBox

from core.plugin_system import MonitoringPlugin

class SystemMonitorPlugin(MonitoringPlugin):
    """System monitoring plugin for MuMuManager Pro"""

    def __init__(self):
        self.main_window: Optional[Any] = None
        self.monitor_widget: Optional[QGroupBox] = None
        self.update_timer: Optional[QTimer] = None
        self.cpu_label: Optional[QLabel] = None
        self.memory_label: Optional[QLabel] = None
        self.cpu_progress: Optional[QProgressBar] = None
        self.memory_progress: Optional[QProgressBar] = None

    @property
    def name(self) -> str:
        return "System Monitor"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Real-time system monitoring with CPU and memory usage"

    def initialize(self, main_window: Any) -> bool:
        """Initialize the system monitor plugin"""
        try:
            self.main_window = main_window

            # Create monitoring widget
            self._create_monitor_widget()

            # Add to main window
            if hasattr(main_window, 'add_dock_widget'):
                main_window.add_dock_widget(
                    self.monitor_widget,
                    "System Monitor",
                    "bottom"
                )

            # Start monitoring
            self._start_monitoring()

            print("✅ System Monitor plugin initialized")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize System Monitor plugin: {e}")
            return False

    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        if self.update_timer:
            self.update_timer.stop()
            self.update_timer = None

        if self.monitor_widget and self.main_window:
            if hasattr(self.main_window, 'remove_dock_widget'):
                self.main_window.remove_dock_widget(self.monitor_widget)

        print("🧹 System Monitor plugin cleaned up")

    def get_monitoring_data(self) -> Dict[str, Any]:
        """Get current system monitoring data"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used": psutil.virtual_memory().used,
            "memory_total": psutil.virtual_memory().total,
            "timestamp": time.time()
        }

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return {
            "update_interval": 2000,  # milliseconds
            "show_cpu": True,
            "show_memory": True
        }

    def _create_monitor_widget(self) -> None:
        """Create the monitoring widget"""
        self.monitor_widget = QGroupBox("System Monitor")
        layout = QVBoxLayout(self.monitor_widget)

        # CPU monitoring
        cpu_group = QGroupBox("CPU Usage")
        cpu_layout = QVBoxLayout(cpu_group)

        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setValue(0)

        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_progress)
        layout.addWidget(cpu_group)

        # Memory monitoring
        memory_group = QGroupBox("Memory Usage")
        memory_layout = QVBoxLayout(memory_group)

        self.memory_label = QLabel("Memory: 0%")
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setValue(0)

        memory_layout.addWidget(self.memory_label)
        memory_layout.addWidget(self.memory_progress)
        layout.addWidget(memory_group)

        # Set fixed width for the widget
        self.monitor_widget.setFixedWidth(300)
        self.monitor_widget.setFixedHeight(200)

    def _start_monitoring(self) -> None:
        """Start the monitoring timer"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_monitoring)
        self.update_timer.start(2000)  # Update every 2 seconds

    def _update_monitoring(self) -> None:
        """Update monitoring data"""
        try:
            data = self.get_monitoring_data()

            # Update CPU
            cpu_percent = data["cpu_percent"]
            if self.cpu_label is not None:
                self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
            if self.cpu_progress is not None:
                self.cpu_progress.setValue(int(cpu_percent))

            # Update Memory
            memory_percent = data["memory_percent"]
            memory_used = data["memory_used"] / (1024**3)  # Convert to GB
            memory_total = data["memory_total"] / (1024**3)

            if self.memory_label is not None:
                self.memory_label.setText(
                    f"Memory: {memory_percent:.1f}% ({memory_used:.1f}GB / {memory_total:.1f}GB)"
                )
            if self.memory_progress is not None:
                self.memory_progress.setValue(int(memory_percent))

        except Exception as e:
            print(f"Error updating monitoring data: {e}")</content>
<parameter name="filePath">c:\Users\SuperMan\Desktop\UPDate-copilot-fix-732b2fcf-f918-4cc5-846e-27adffe93778\UPDate-copilot-fix-732b2fcf-f918-4cc5-846e-27adffe93778\plugins\system_monitor.py
