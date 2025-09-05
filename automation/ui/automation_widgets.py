"""
UI Components - Enhanced UI Components for Automation
===================================================
Modern, responsive UI components for the automation system.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from PyQt6.QtCore import (QObject, QTimer, pyqtSignal, QPropertyAnimation, 
                         QEasingCurve, QRect, QSize, Qt, QThread)
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QLabel, QSpinBox, QDoubleSpinBox, QProgressBar,
                           QTextEdit, QListWidget, QPushButton, QFrame,
                           QScrollArea, QGroupBox, QTabWidget, QSplitter,
                           QSlider, QCheckBox, QComboBox, QTableWidget,
                           QTableWidgetItem, QHeaderView, QSizePolicy)
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QIcon, QPainter, QBrush


class AnimatedProgressBar(QProgressBar):
    """Enhanced progress bar with smooth animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Styling
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3d3d3d;
                border-radius: 8px;
                background-color: #2b2b2b;
                text-align: center;
                font-weight: bold;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eff, stop:0.5 #26c6da, stop:1 #00e676);
                border-radius: 6px;
                margin: 1px;
            }
        """)
    
    def setValueAnimated(self, value: int):
        """Set value with animation"""
        self.animation.setStartValue(self.value())
        self.animation.setEndValue(value)
        self.animation.start()


class StatusIndicator(QLabel):
    """Animated status indicator"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFixedSize(16, 16)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Animation timer
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._toggle_blink)
        self.blink_state = True
        
        self.set_status("idle")
    
    def set_status(self, status: str):
        """Set status with appropriate color and animation"""
        self.blink_timer.stop()
        
        if status == "idle":
            self.setStyleSheet("background-color: #666666; border-radius: 8px;")
        elif status == "running":
            self.setStyleSheet("background-color: #00e676; border-radius: 8px;")
            self.blink_timer.start(1000)
        elif status == "paused":
            self.setStyleSheet("background-color: #ff9800; border-radius: 8px;")
        elif status == "error":
            self.setStyleSheet("background-color: #f44336; border-radius: 8px;")
            self.blink_timer.start(500)
        elif status == "warning":
            self.setStyleSheet("background-color: #ffeb3b; border-radius: 8px;")
            self.blink_timer.start(750)
    
    def _toggle_blink(self):
        """Toggle blink animation"""
        self.blink_state = not self.blink_state
        self.setVisible(self.blink_state)


class EnhancedControlPanel(QGroupBox):
    """Enhanced control panel with modern styling"""
    
    # Signals
    batch_size_changed = pyqtSignal(int)
    batch_delay_changed = pyqtSignal(float)
    start_delay_changed = pyqtSignal(float)
    cpu_threshold_changed = pyqtSignal(float)
    
    start_automation = pyqtSignal()
    stop_automation = pyqtSignal()
    pause_automation = pyqtSignal()
    resume_automation = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Automation Control", parent)
        
        self.is_running = False
        self.is_paused = False
        
        self._setup_ui()
        self._setup_styling()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Status section
        status_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.pause_btn = QPushButton("Pause")
        
        self.start_btn.setObjectName("startButton")
        self.stop_btn.setObjectName("stopButton")
        self.pause_btn.setObjectName("pauseButton")
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.pause_btn)
        
        layout.addLayout(button_layout)
        
        # Configuration section
        config_group = QGroupBox("Configuration")
        config_layout = QGridLayout(config_group)
        
        # Batch size
        config_layout.addWidget(QLabel("Batch Size:"), 0, 0)
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 100)
        self.batch_size_spin.setValue(10)
        config_layout.addWidget(self.batch_size_spin, 0, 1)
        
        # Batch delay
        config_layout.addWidget(QLabel("Batch Delay (s):"), 1, 0)
        self.batch_delay_spin = QDoubleSpinBox()
        self.batch_delay_spin.setRange(0.1, 60.0)
        self.batch_delay_spin.setValue(2.0)
        self.batch_delay_spin.setSingleStep(0.1)
        config_layout.addWidget(self.batch_delay_spin, 1, 1)
        
        # Start delay
        config_layout.addWidget(QLabel("Start Delay (s):"), 2, 0)
        self.start_delay_spin = QDoubleSpinBox()
        self.start_delay_spin.setRange(0.1, 60.0)
        self.start_delay_spin.setValue(3.0)
        self.start_delay_spin.setSingleStep(0.1)
        config_layout.addWidget(self.start_delay_spin, 2, 1)
        
        # CPU threshold
        config_layout.addWidget(QLabel("CPU Threshold (%):"), 3, 0)
        self.cpu_threshold_spin = QSpinBox()
        self.cpu_threshold_spin.setRange(30, 95)
        self.cpu_threshold_spin.setValue(70)
        config_layout.addWidget(self.cpu_threshold_spin, 3, 1)
        
        layout.addWidget(config_group)
        
        # Update button states
        self._update_button_states()
    
    def _setup_styling(self):
        """Setup modern styling"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QPushButton {
                background-color: #404040;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                color: #ffffff;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #777777;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                border-color: #333333;
                color: #666666;
            }
            
            QPushButton#startButton {
                background-color: #2e7d32;
                border-color: #4caf50;
            }
            QPushButton#startButton:hover {
                background-color: #388e3c;
            }
            
            QPushButton#stopButton {
                background-color: #c62828;
                border-color: #f44336;
            }
            QPushButton#stopButton:hover {
                background-color: #d32f2f;
            }
            
            QPushButton#pauseButton {
                background-color: #ef6c00;
                border-color: #ff9800;
            }
            QPushButton#pauseButton:hover {
                background-color: #f57c00;
            }
            
            QSpinBox, QDoubleSpinBox {
                background-color: #404040;
                border: 2px solid #555555;
                border-radius: 4px;
                padding: 4px;
                color: #ffffff;
                min-width: 80px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #4a9eff;
            }
            
            QLabel {
                color: #ffffff;
            }
        """)
    
    def _connect_signals(self):
        """Connect internal signals"""
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        
        self.batch_size_spin.valueChanged.connect(self.batch_size_changed.emit)
        self.batch_delay_spin.valueChanged.connect(self.batch_delay_changed.emit)
        self.start_delay_spin.valueChanged.connect(self.start_delay_changed.emit)
        self.cpu_threshold_spin.valueChanged.connect(
            lambda value: self.cpu_threshold_changed.emit(float(value)))
    
    def _on_start_clicked(self):
        """Handle start button click"""
        if not self.is_running:
            self.start_automation.emit()
        else:
            self.resume_automation.emit()
    
    def _on_stop_clicked(self):
        """Handle stop button click"""
        self.stop_automation.emit()
    
    def _on_pause_clicked(self):
        """Handle pause button click"""
        if self.is_running and not self.is_paused:
            self.pause_automation.emit()
    
    def set_automation_state(self, running: bool, paused: bool = False):
        """Update automation state"""
        self.is_running = running
        self.is_paused = paused
        
        if running:
            if paused:
                self.status_indicator.set_status("paused")
                self.status_label.setText("Paused")
                self.start_btn.setText("Resume")
            else:
                self.status_indicator.set_status("running")
                self.status_label.setText("Running")
                self.start_btn.setText("Start")
        else:
            self.status_indicator.set_status("idle")
            self.status_label.setText("Ready")
            self.start_btn.setText("Start")
        
        self._update_button_states()
    
    def set_error_state(self, error_message: str):
        """Set error state"""
        self.status_indicator.set_status("error")
        self.status_label.setText(f"Error: {error_message}")
        self.is_running = False
        self.is_paused = False
        self._update_button_states()
    
    def _update_button_states(self):
        """Update button enabled states"""
        self.start_btn.setEnabled(not self.is_running or self.is_paused)
        self.stop_btn.setEnabled(self.is_running)
        self.pause_btn.setEnabled(self.is_running and not self.is_paused)


class PerformanceMonitor(QGroupBox):
    """Performance monitoring widget"""
    
    def __init__(self, parent=None):
        super().__init__("Performance Monitor", parent)
        
        self._setup_ui()
        self._setup_styling()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(1000)  # Update every second
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # CPU usage
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU:"))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_label = QLabel("0%")
        self.cpu_label.setMinimumWidth(40)
        
        cpu_layout.addWidget(self.cpu_progress)
        cpu_layout.addWidget(self.cpu_label)
        layout.addLayout(cpu_layout)
        
        # Memory usage
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory:"))
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_label = QLabel("0%")
        self.memory_label.setMinimumWidth(40)
        
        memory_layout.addWidget(self.memory_progress)
        memory_layout.addWidget(self.memory_label)
        layout.addLayout(memory_layout)
        
        # Performance level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Level:"))
        self.level_label = QLabel("Unknown")
        self.level_indicator = StatusIndicator()
        
        level_layout.addWidget(self.level_label)
        level_layout.addWidget(self.level_indicator)
        level_layout.addStretch()
        layout.addLayout(level_layout)
    
    def _setup_styling(self):
        """Setup styling"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QProgressBar {
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                background-color: #2b2b2b;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4caf50, stop:0.7 #ff9800, stop:1 #f44336);
                border-radius: 2px;
            }
            
            QLabel {
                color: #ffffff;
            }
        """)
    
    def update_performance(self, cpu_percent: float, memory_percent: float, level: str):
        """Update performance display"""
        self.cpu_progress.setValue(int(cpu_percent))
        self.cpu_label.setText(f"{cpu_percent:.1f}%")
        
        self.memory_progress.setValue(int(memory_percent))
        self.memory_label.setText(f"{memory_percent:.1f}%")
        
        self.level_label.setText(level.title())
        
        # Update level indicator color
        if level == "excellent":
            self.level_indicator.set_status("idle")
        elif level == "good":
            self.level_indicator.set_status("running")
        elif level == "moderate":
            self.level_indicator.set_status("warning")
        else:
            self.level_indicator.set_status("error")
    
    def _update_display(self):
        """Update display with current system performance"""
        try:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            
            # Determine level
            if cpu >= 85 or memory >= 90:
                level = "critical"
            elif cpu >= 70 or memory >= 80:
                level = "poor"
            elif cpu >= 50 or memory >= 70:
                level = "moderate"
            elif cpu >= 30 or memory >= 50:
                level = "good"
            else:
                level = "excellent"
            
            self.update_performance(cpu, memory, level)
            
        except ImportError:
            # Fallback if psutil not available
            pass


class AutomationLog(QGroupBox):
    """Enhanced logging widget"""
    
    def __init__(self, parent=None):
        super().__init__("Automation Log", parent)
        
        self._setup_ui()
        self._setup_styling()
        
        self.max_lines = 1000
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Log controls
        controls_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_log)
        
        self.auto_scroll_check = QCheckBox("Auto Scroll")
        self.auto_scroll_check.setChecked(True)
        
        controls_layout.addWidget(self.clear_btn)
        controls_layout.addWidget(self.auto_scroll_check)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        
        layout.addWidget(self.log_text)
    
    def _setup_styling(self):
        """Setup styling"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QTextEdit {
                background-color: #1e1e1e;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            
            QPushButton {
                background-color: #404040;
                border: 2px solid #555555;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #555555;
                border-radius: 3px;
                background-color: #404040;
            }
            QCheckBox::indicator:checked {
                background-color: #4a9eff;
                border-color: #4a9eff;
            }
        """)
    
    def add_log(self, message: str, level: str = "info"):
        """Add log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color based on level
        color_map = {
            "info": "#ffffff",
            "warning": "#ff9800", 
            "error": "#f44336",
            "success": "#4caf50",
            "debug": "#9e9e9e"
        }
        
        color = color_map.get(level, "#ffffff")
        
        formatted_message = f'<span style="color: #888888;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'
        
        self.log_text.append(formatted_message)
        
        # Auto scroll if enabled
        if self.auto_scroll_check.isChecked():
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        # Limit lines
        self._limit_lines()
    
    def clear_log(self):
        """Clear log display"""
        self.log_text.clear()
    
    def _limit_lines(self):
        """Limit number of lines in log"""
        document = self.log_text.document()
        if document.blockCount() > self.max_lines:
            # Remove excess lines from the beginning
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            for _ in range(document.blockCount() - self.max_lines):
                cursor.select(cursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()  # Remove the newline


class ModernAutomationWidget(QWidget):
    """Main automation widget with modern UI"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._setup_ui()
        self._setup_styling()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup main UI layout"""
        main_layout = QHBoxLayout(self)
        
        # Left panel
        left_panel = QVBoxLayout()
        
        self.control_panel = EnhancedControlPanel()
        self.performance_monitor = PerformanceMonitor()
        
        left_panel.addWidget(self.control_panel)
        left_panel.addWidget(self.performance_monitor)
        left_panel.addStretch()
        
        # Right panel
        right_panel = QVBoxLayout()
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = AnimatedProgressBar()
        self.progress_label = QLabel("Ready to start")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        
        # Log section
        self.automation_log = AutomationLog()
        
        right_panel.addWidget(progress_group)
        right_panel.addWidget(self.automation_log)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMinimumWidth(300)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
    
    def _setup_styling(self):
        """Setup main styling"""
        self.setStyleSheet("""
            ModernAutomationWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QSplitter::handle {
                background-color: #555555;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #777777;
            }
        """)
    
    def _connect_signals(self):
        """Connect internal signals"""
        # Control panel signals
        self.control_panel.start_automation.connect(self._on_start_automation)
        self.control_panel.stop_automation.connect(self._on_stop_automation)
        self.control_panel.pause_automation.connect(self._on_pause_automation)
        self.control_panel.resume_automation.connect(self._on_resume_automation)
    
    def _on_start_automation(self):
        """Handle start automation"""
        self.automation_log.add_log("Starting automation...", "info")
        self.control_panel.set_automation_state(True, False)
        self.progress_label.setText("Initializing...")
    
    def _on_stop_automation(self):
        """Handle stop automation"""
        self.automation_log.add_log("Stopping automation...", "warning")
        self.control_panel.set_automation_state(False, False)
        self.progress_label.setText("Stopped")
        self.progress_bar.setValue(0)
    
    def _on_pause_automation(self):
        """Handle pause automation"""
        self.automation_log.add_log("Pausing automation...", "warning")
        self.control_panel.set_automation_state(True, True)
        self.progress_label.setText("Paused")
    
    def _on_resume_automation(self):
        """Handle resume automation"""
        self.automation_log.add_log("Resuming automation...", "info")
        self.control_panel.set_automation_state(True, False)
        self.progress_label.setText("Running...")
    
    def update_progress(self, percentage: float, message: str = ""):
        """Update progress display"""
        self.progress_bar.setValueAnimated(int(percentage))
        if message:
            self.progress_label.setText(message)
    
    def add_log_message(self, message: str, level: str = "info"):
        """Add message to log"""
        self.automation_log.add_log(message, level)
    
    def get_control_panel(self) -> EnhancedControlPanel:
        """Get control panel for external connections"""
        return self.control_panel
    
    def get_performance_monitor(self) -> PerformanceMonitor:
        """Get performance monitor for external updates"""
        return self.performance_monitor
    
    def get_automation_log(self) -> AutomationLog:
        """Get automation log for external logging"""
        return self.automation_log
