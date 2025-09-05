"""
Simple Log Settings Dialog - Phiên bản đơn giản cho MumuManagerPRO
Làm lại từ log_settings_dialog.py phức tạp thành giao diện đơn giản, dễ sử dụng
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QCheckBox, QComboBox, QSpinBox, QSlider, QPushButton, QLabel,
    QLineEdit, QFileDialog, QMessageBox, QTabWidget, QWidget,
    QTextEdit, QFrame, QFontDialog, QColorDialog
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from enhanced_log_system import LogLevel
import os
from datetime import datetime

class LogSettingsDialog(QDialog):
    """Dialog đơn giản cho cấu hình log settings"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, log_widget=None, parent=None):
        super().__init__(parent)
        self.log_widget = log_widget
        self.settings = QSettings("MumuManagerPRO", "LogSettings")
        
        self.setWindowTitle("🔧 Log Settings")
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        # Variables
        self.selected_font = QFont("Consolas", 10)
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup giao diện đơn giản"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📊 Log Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tabs cho tổ chức tốt hơn
        self.tabs = QTabWidget()
        
        # Basic Settings Tab
        self.create_basic_tab()
        self.tabs.addTab(self.basic_tab, "🔧 Basic")
        
        # Display Tab
        self.create_display_tab()
        self.tabs.addTab(self.display_tab, "🎨 Display")
        
        # Actions Tab
        self.create_actions_tab()
        self.tabs.addTab(self.actions_tab, "⚡ Actions")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        self.create_buttons()
        layout.addLayout(self.button_layout)
        
    def create_basic_tab(self):
        """Tab cài đặt cơ bản"""
        self.basic_tab = QWidget()
        layout = QVBoxLayout(self.basic_tab)
        
        # Log Level Settings
        level_group = QGroupBox("📊 Log Levels")
        level_layout = QFormLayout(level_group)
        
        self.min_level_combo = QComboBox()
        for level in LogLevel:
            self.min_level_combo.addItem(f"{level.value[1]} {level.name}", level)
        level_layout.addRow("Minimum Level:", self.min_level_combo)
        
        self.enable_debug_cb = QCheckBox("Show DEBUG messages")
        self.enable_debug_cb.setToolTip("Debug messages can slow down the app")
        level_layout.addRow("Debug Mode:", self.enable_debug_cb)
        
        layout.addWidget(level_group)
        
        # Display Options
        display_group = QGroupBox("🖥️ Display Options")
        display_layout = QFormLayout(display_group)
        
        self.auto_scroll_cb = QCheckBox("Auto-scroll to new messages")
        display_layout.addRow("Auto Scroll:", self.auto_scroll_cb)
        
        self.show_timestamp_cb = QCheckBox("Show timestamps")
        display_layout.addRow("Timestamps:", self.show_timestamp_cb)
        
        self.show_categories_cb = QCheckBox("Show categories")
        display_layout.addRow("Categories:", self.show_categories_cb)
        
        layout.addWidget(display_group)
        
        # Performance Settings
        perf_group = QGroupBox("⚡ Performance")
        perf_layout = QFormLayout(perf_group)
        
        self.max_entries_spin = QSpinBox()
        self.max_entries_spin.setRange(100, 10000)
        self.max_entries_spin.setValue(2000)
        self.max_entries_spin.setSuffix(" entries")
        perf_layout.addRow("Max Log Entries:", self.max_entries_spin)
        
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(50, 1000)
        self.update_interval_spin.setValue(100)
        self.update_interval_spin.setSuffix(" ms")
        perf_layout.addRow("Update Interval:", self.update_interval_spin)
        
        layout.addWidget(perf_group)
        layout.addStretch()
        
    def create_display_tab(self):
        """Tab cài đặt hiển thị"""
        self.display_tab = QWidget()
        layout = QVBoxLayout(self.display_tab)
        
        # Font Settings
        font_group = QGroupBox("🔤 Font Settings")
        font_layout = QFormLayout(font_group)
        
        # Font selection
        font_select_layout = QHBoxLayout()
        self.font_label = QLabel("Consolas, 10pt")
        font_select_layout.addWidget(self.font_label)
        self.font_select_btn = QPushButton("Change...")
        self.font_select_btn.clicked.connect(self.select_font)
        font_select_layout.addWidget(self.font_select_btn)
        font_layout.addRow("Font:", font_select_layout)
        
        # Font size
        font_size_layout = QHBoxLayout()
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_size_slider.setRange(8, 16)
        self.font_size_slider.setValue(10)
        self.font_size_slider.valueChanged.connect(self.update_font_size_label)
        font_size_layout.addWidget(self.font_size_slider)
        self.font_size_label = QLabel("10pt")
        font_size_layout.addWidget(self.font_size_label)
        font_layout.addRow("Size:", font_size_layout)
        
        layout.addWidget(font_group)
        
        # Layout Settings
        layout_group = QGroupBox("📐 Layout")
        layout_layout = QFormLayout(layout_group)
        
        self.word_wrap_cb = QCheckBox("Wrap long lines")
        layout_layout.addRow("Word Wrap:", self.word_wrap_cb)
        
        self.alternating_rows_cb = QCheckBox("Alternating colors")
        layout_layout.addRow("Row Colors:", self.alternating_rows_cb)
        
        self.compact_mode_cb = QCheckBox("Compact display")
        layout_layout.addRow("Compact Mode:", self.compact_mode_cb)
        
        layout.addWidget(layout_group)
        
        # Color Preview
        preview_group = QGroupBox("🎨 Color Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.color_preview = QTextEdit()
        self.color_preview.setMaximumHeight(120)
        self.color_preview.setReadOnly(True)
        self.update_color_preview()
        preview_layout.addWidget(self.color_preview)
        
        layout.addWidget(preview_group)
        layout.addStretch()
        
    def create_actions_tab(self):
        """Tab các hành động"""
        self.actions_tab = QWidget()
        layout = QVBoxLayout(self.actions_tab)
        
        # Log Control
        control_group = QGroupBox("🎛️ Log Control")
        control_layout = QVBoxLayout(control_group)
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Level Filter:"))
        self.level_filter_combo = QComboBox()
        self.level_filter_combo.addItem("All Levels", None)
        for level in LogLevel:
            self.level_filter_combo.addItem(f"{level.value[1]} {level.name}", level)
        self.level_filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.level_filter_combo)
        control_layout.addLayout(filter_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.toggled.connect(self.toggle_pause)
        action_layout.addWidget(self.pause_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_logs)
        action_layout.addWidget(self.clear_btn)
        
        control_layout.addLayout(action_layout)
        layout.addWidget(control_group)
        
        # Export Settings
        export_group = QGroupBox("📤 Export")
        export_layout = QFormLayout(export_group)
        
        # Export path
        export_path_layout = QHBoxLayout()
        self.export_path_edit = QLineEdit()
        self.export_path_edit.setPlaceholderText("Select export folder...")
        export_path_layout.addWidget(self.export_path_edit)
        self.browse_btn = QPushButton("📂")
        self.browse_btn.clicked.connect(self.browse_export_path)
        export_path_layout.addWidget(self.browse_btn)
        export_layout.addRow("Export Path:", export_path_layout)
        
        # Export options
        self.include_timestamp_cb = QCheckBox("Add timestamp to filename")
        export_layout.addRow("Options:", self.include_timestamp_cb)
        
        # Export button
        self.export_btn = QPushButton("📤 Export Logs")
        self.export_btn.clicked.connect(self.export_logs)
        export_layout.addRow("", self.export_btn)
        
        layout.addWidget(export_group)
        
        # Log Status
        status_group = QGroupBox("📊 Status")
        status_layout = QFormLayout(status_group)
        
        self.total_logs_label = QLabel("0")
        status_layout.addRow("Total Logs:", self.total_logs_label)
        
        self.current_filter_label = QLabel("All Levels")
        status_layout.addRow("Current Filter:", self.current_filter_label)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
        
    def create_buttons(self):
        """Tạo buttons"""
        self.button_layout = QHBoxLayout()
        
        # Preview button
        self.preview_btn = QPushButton("👁️ Preview")
        self.preview_btn.clicked.connect(self.preview_settings)
        self.button_layout.addWidget(self.preview_btn)
        
        self.button_layout.addStretch()
        
        # Reset button
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_settings)
        self.button_layout.addWidget(self.reset_btn)
        
        # OK/Cancel buttons
        self.ok_btn = QPushButton("✅ OK")
        self.ok_btn.clicked.connect(self.accept_settings)
        self.button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_btn)
        
    def select_font(self):
        """Chọn font"""
        font, ok = QFontDialog.getFont(self.selected_font, self)
        if ok:
            self.selected_font = font
            self.font_label.setText(f"{font.family()}, {font.pointSize()}pt")
            self.font_size_slider.setValue(font.pointSize())
            self.update_color_preview()
            
    def update_font_size_label(self, value):
        """Cập nhật label font size"""
        self.font_size_label.setText(f"{value}pt")
        self.selected_font.setPointSize(value)
        self.font_label.setText(f"{self.selected_font.family()}, {value}pt")
        self.update_color_preview()
        
    def update_color_preview(self):
        """Cập nhật preview màu sắc"""
        preview_text = ""
        for level in LogLevel:
            color = level.value[2]
            preview_text += f'<span style="color: {color}; font-family: {self.selected_font.family()}; font-size: {self.selected_font.pointSize()}pt;">{level.value[1]} {level.name}: Sample log message</span><br>'
        
        self.color_preview.setHtml(preview_text)
        
    def browse_export_path(self):
        """Chọn thư mục export"""
        path = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if path:
            self.export_path_edit.setText(path)
            
    def apply_filter(self):
        """Áp dụng filter"""
        current_text = self.level_filter_combo.currentText()
        self.current_filter_label.setText(current_text)
        
        if self.log_widget and hasattr(self.log_widget, 'level_filter'):
            current_data = self.level_filter_combo.currentData()
            index = self.log_widget.level_filter.findData(current_data)
            if index >= 0:
                self.log_widget.level_filter.setCurrentIndex(index)
                if hasattr(self.log_widget, 'apply_filters'):
                    self.log_widget.apply_filters()
        
        self.update_log_count()
        
    def toggle_pause(self, checked):
        """Tạm dừng/tiếp tục logging"""
        if self.log_widget and hasattr(self.log_widget, 'paused'):
            self.log_widget.paused = checked
            
        if checked:
            self.pause_btn.setText("▶️ Resume")
        else:
            self.pause_btn.setText("⏸️ Pause")
            
    def clear_logs(self):
        """Xóa logs"""
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Clear all logs?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.log_widget and hasattr(self.log_widget, 'clear_logs'):
                self.log_widget.clear_logs()
            self.update_log_count()
            
    def export_logs(self):
        """Export logs"""
        if not self.export_path_edit.text():
            QMessageBox.warning(self, "Warning", "Please select an export path first.")
            return
            
        try:
            export_path = self.export_path_edit.text()
            
            # Tạo tên file
            if self.include_timestamp_cb.isChecked():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"mumu_logs_{timestamp}.txt"
            else:
                filename = "mumu_logs.txt"
                
            full_path = os.path.join(export_path, filename)
            
            # Export logs (simplified version)
            if self.log_widget and hasattr(self.log_widget, 'storage'):
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(f"MumuManagerPRO Log Export\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for entry in self.log_widget.storage.entries:
                        f.write(f"[{entry.timestamp.strftime('%H:%M:%S')}] ")
                        f.write(f"{entry.level.value[1]} {entry.level.name}: ")
                        f.write(f"{entry.message}\n")
                        
                QMessageBox.information(self, "Success", f"Logs exported to:\n{full_path}")
            else:
                QMessageBox.warning(self, "Warning", "No log data available to export.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export logs:\n{e}")
            
    def update_log_count(self):
        """Cập nhật số lượng logs"""
        if self.log_widget and hasattr(self.log_widget, 'storage'):
            count = len(self.log_widget.storage.entries)
            self.total_logs_label.setText(str(count))
        else:
            self.total_logs_label.setText("0")
            
    def preview_settings(self):
        """Preview settings"""
        self.apply_settings_to_widget(preview=True)
        QMessageBox.information(self, "Preview", "Settings applied temporarily.\nCheck the log display to see changes.")
        
    def apply_settings_to_widget(self, preview=False):
        """Áp dụng settings vào log widget"""
        if not self.log_widget:
            return
            
        try:
            # Font settings
            if hasattr(self.log_widget, 'change_font_size'):
                self.log_widget.change_font_size(self.font_size_slider.value())
                
            # Auto-scroll
            if hasattr(self.log_widget, 'auto_scroll'):
                self.log_widget.auto_scroll = self.auto_scroll_cb.isChecked()
                
            # Word wrap
            if hasattr(self.log_widget, 'toggle_word_wrap'):
                self.log_widget.toggle_word_wrap(self.word_wrap_cb.isChecked())
                
            # Max entries
            if hasattr(self.log_widget, 'storage'):
                self.log_widget.storage.max_entries = self.max_entries_spin.value()
                
            # Update interval
            if hasattr(self.log_widget, 'update_timer'):
                self.log_widget.update_timer.setInterval(self.update_interval_spin.value())
                
            if not preview:
                self.settings_changed.emit()
                
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Some settings could not be applied:\n{e}")
            
    def load_settings(self):
        """Load settings"""
        # Basic settings
        self.enable_debug_cb.setChecked(self.settings.value("enable_debug", False, type=bool))
        self.auto_scroll_cb.setChecked(self.settings.value("auto_scroll", True, type=bool))
        self.show_timestamp_cb.setChecked(self.settings.value("show_timestamp", True, type=bool))
        self.show_categories_cb.setChecked(self.settings.value("show_categories", True, type=bool))
        
        # Display settings
        font_size = self.settings.value("font_size", 10, type=int)
        self.font_size_slider.setValue(font_size)
        self.selected_font.setPointSize(font_size)
        self.update_font_size_label(font_size)
        
        self.word_wrap_cb.setChecked(self.settings.value("word_wrap", True, type=bool))
        self.alternating_rows_cb.setChecked(self.settings.value("alternating_rows", True, type=bool))
        self.compact_mode_cb.setChecked(self.settings.value("compact_mode", False, type=bool))
        
        # Performance settings
        self.max_entries_spin.setValue(self.settings.value("max_entries", 2000, type=int))
        self.update_interval_spin.setValue(self.settings.value("update_interval", 100, type=int))
        
        # Export settings
        export_path = self.settings.value("export_path", "")
        if not export_path:
            export_path = os.path.join(os.path.expanduser("~"), "Desktop", "MumuLogs")
        self.export_path_edit.setText(export_path)
        self.include_timestamp_cb.setChecked(self.settings.value("include_timestamp", True, type=bool))
        
        self.update_log_count()
        self.update_color_preview()
        
    def save_settings(self):
        """Save settings"""
        # Basic settings
        self.settings.setValue("enable_debug", self.enable_debug_cb.isChecked())
        self.settings.setValue("auto_scroll", self.auto_scroll_cb.isChecked())
        self.settings.setValue("show_timestamp", self.show_timestamp_cb.isChecked())
        self.settings.setValue("show_categories", self.show_categories_cb.isChecked())
        
        # Display settings
        self.settings.setValue("font_size", self.font_size_slider.value())
        self.settings.setValue("word_wrap", self.word_wrap_cb.isChecked())
        self.settings.setValue("alternating_rows", self.alternating_rows_cb.isChecked())
        self.settings.setValue("compact_mode", self.compact_mode_cb.isChecked())
        
        # Performance settings
        self.settings.setValue("max_entries", self.max_entries_spin.value())
        self.settings.setValue("update_interval", self.update_interval_spin.value())
        
        # Export settings
        self.settings.setValue("export_path", self.export_path_edit.text())
        self.settings.setValue("include_timestamp", self.include_timestamp_cb.isChecked())
        
    def reset_settings(self):
        """Reset về mặc định"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Reset all settings to default?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear settings
            for key in self.settings.allKeys():
                self.settings.remove(key)
                
            # Reload defaults
            self.load_settings()
            QMessageBox.information(self, "Reset", "Settings reset to default.")
            
    def accept_settings(self):
        """Chấp nhận và đóng"""
        self.save_settings()
        self.apply_settings_to_widget()
        self.accept()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = LogSettingsDialog()
    dialog.show()
    sys.exit(app.exec())
