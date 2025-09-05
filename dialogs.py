# dialogs.py - Custom dialog boxes for the application

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QGroupBox, QHBoxLayout, QLineEdit,
    QPushButton, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QFileDialog, QWidget,
    QColorDialog, QLabel, QComboBox, QFrame
)
from PyQt6.QtGui import QPalette, QColor, QPixmap, QFont
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.settings = parent.settings
        
        # Apply custom title bar styling
        self._setup_custom_title_bar()
        
        self.setMinimumWidth(600)
        self._setup_main_content()
        
    def _setup_custom_title_bar(self):
        """Create custom title bar to match main app"""
        # Remove default title bar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main container
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom title bar
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #333333;
            }
        """)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        
        # Title label
        self.title_label = QLabel("🎨 Cài đặt Giao diện - MumuManager")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
                background: transparent;
            }
        """)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e81123;
                color: white;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)
        
        main_layout.addWidget(self.title_bar)
        
        # Content container
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
        """)
        main_layout.addWidget(self.content_widget)
        
        # Enable dragging
        self.dragging = False
        self.drag_position = None

    def _setup_main_content(self):
        """Setup the main dialog content focused on UI/appearance settings"""
        layout = QVBoxLayout(self.content_widget)
        layout.setSpacing(15)
        
        # MuMu Path
        path_group = QGroupBox("📁 Đường dẫn MuMuManager")
        path_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #444444;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
        """)
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self.settings.value("manager_path", ""))
        self.path_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QLineEdit:hover {
                border-color: #007acc;
            }
        """)
        browse_btn = QPushButton("🔍 Duyệt...")
        browse_btn.clicked.connect(self.browse_path)
        browse_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #444444;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007acc;
                border-color: #007acc;
            }
        """)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # Enhanced Appearance Settings
        appearance_group = QGroupBox("🎨 Giao diện & Chủ đề")
        appearance_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #444444;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
        """)
        appearance_form = QFormLayout(appearance_group)
        
        # Theme selection with emojis
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["🌙 Dark", "☀️ Light", "🎯 Monokai"])
        current_theme = self.settings.value("theme/name", "dark")
        theme_map = {"dark": "🌙 Dark", "light": "☀️ Light", "monokai": "🎯 Monokai"}
        self.theme_combo.setCurrentText(theme_map.get(current_theme, "🌙 Dark"))
        self.theme_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
        """)
        appearance_form.addRow("Chủ đề:", self.theme_combo)

        # Accent color with preview
        accent_layout = QHBoxLayout()
        self.accent_color_preview = QLabel()
        self.accent_color_preview.setFixedSize(24, 24)
        self.accent_color_btn = QPushButton("🎨 Chọn màu nhấn...")
        self.accent_color_btn.clicked.connect(self.choose_accent_color)
        self.accent_color_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #444444;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007acc;
                border-color: #007acc;
            }
        """)
        accent_layout.addWidget(self.accent_color_preview)
        accent_layout.addWidget(self.accent_color_btn)
        appearance_form.addRow("Màu nhấn:", accent_layout)
        layout.addWidget(appearance_group)
        
        # Load initial accent color
        self.current_accent_color = QColor(self.settings.value("theme/accent_color", "#007acc"))
        self.update_color_preview()

        # Performance Settings
        performance_group = QGroupBox("⚡ Hiệu suất & Tối ưu")
        performance_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #444444;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
        """)
        performance_form = QFormLayout(performance_group)
        
        self.auto_refresh_interval = QSpinBox()
        self.auto_refresh_interval.setMinimum(5)
        self.auto_refresh_interval.setMaximum(300)
        self.auto_refresh_interval.setSuffix(" giây")
        self.auto_refresh_interval.setValue(int(self.settings.value("auto_refresh/interval", 30)))
        self.auto_refresh_interval.setToolTip("Thời gian tự động làm mới danh sách instances (5-300 giây)")
        self.auto_refresh_interval.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QSpinBox:hover {
                border-color: #007acc;
            }
        """)
        performance_form.addRow("🔄 Khoảng thời gian làm mới:", self.auto_refresh_interval)
        
        layout.addWidget(performance_group)

        # Advanced UI Settings
        advanced_group = QGroupBox("🔧 Cài đặt Nâng cao")
        advanced_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #444444;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
        """)
        advanced_form = QFormLayout(advanced_group)
        
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["📐 Nhỏ", "📏 Trung bình", "📊 Lớn"])
        current_font = self.settings.value('ui/font_size', 'Trung bình')
        font_map = {"Nhỏ": "📐 Nhỏ", "Trung bình": "📏 Trung bình", "Lớn": "📊 Lớn"}
        self.font_size_combo.setCurrentText(font_map.get(current_font, "📏 Trung bình"))
        self.font_size_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
        """)
        advanced_form.addRow("Kích thước chữ:", self.font_size_combo)
        
        self.animation_enabled = QComboBox()
        self.animation_enabled.addItems(["✨ Bật", "⭕ Tắt"])
        is_enabled = self.settings.value("ui/animations", True, bool)
        self.animation_enabled.setCurrentText("✨ Bật" if is_enabled else "⭕ Tắt")
        self.animation_enabled.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
        """)
        advanced_form.addRow("Hiệu ứng chuyển động:", self.animation_enabled)
        
        self.transparency_combo = QComboBox()
        self.transparency_combo.addItems(["🔳 Không trong suốt", "🔲 Nhẹ", "⬜ Trung bình", "⚪ Cao"])
        current_transparency = self.settings.value("ui/transparency", "Không trong suốt")
        transparency_map = {
            "Không trong suốt": "🔳 Không trong suốt",
            "Nhẹ": "🔲 Nhẹ", 
            "Trung bình": "⬜ Trung bình",
            "Cao": "⚪ Cao"
        }
        self.transparency_combo.setCurrentText(transparency_map.get(current_transparency, "🔳 Không trong suốt"))
        self.transparency_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
        """)
        advanced_form.addRow("Độ trong suốt:", self.transparency_combo)
        
        layout.addWidget(advanced_group)
        
        # Dialog Buttons with enhanced styling
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_and_accept)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet("""
            QDialogButtonBox QPushButton {
                padding: 10px 20px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #444444;
                color: #ffffff;
                font-weight: bold;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #007acc;
                border-color: #007acc;
            }
        """)
        layout.addWidget(buttons)

    def browse_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn MuMuManager.exe", "", "Executable (*.exe)")
        if path: self.path_edit.setText(path)

    def choose_accent_color(self):
        color = QColorDialog.getColor(self.current_accent_color, self, "Chọn màu nhấn")
        if color.isValid():
            self.current_accent_color = color
            self.update_color_preview()

    def update_color_preview(self):
        pixmap = QPixmap(24, 24)
        pixmap.fill(self.current_accent_color)
        self.accent_color_preview.setPixmap(pixmap)

    def save_and_accept(self):
        """Save all UI/appearance settings only"""
        self.settings.setValue("manager_path", self.path_edit.text())
        
        # Save theme (extract theme name from emoji text)
        theme_text = self.theme_combo.currentText()
        if "Dark" in theme_text:
            theme = "dark"
        elif "Light" in theme_text:
            theme = "light"
        elif "Monokai" in theme_text:
            theme = "monokai"
        else:
            theme = "dark"
        self.settings.setValue("theme/name", theme)
        
        # Save accent color
        self.settings.setValue("theme/accent_color", self.current_accent_color.name())
        
        # Save performance settings
        self.settings.setValue("auto_refresh/interval", self.auto_refresh_interval.value())
        
        # Save advanced UI settings
        font_size_text = self.font_size_combo.currentText()
        if "Nhỏ" in font_size_text:
            font_size = "Nhỏ"
        elif "Lớn" in font_size_text:
            font_size = "Lớn"
        else:
            font_size = "Trung bình"
        self.settings.setValue("ui/font_size", font_size)
        
        animation_enabled = "Bật" in self.animation_enabled.currentText()
        self.settings.setValue("ui/animations", animation_enabled)
        
        transparency_text = self.transparency_combo.currentText()
        if "Nhẹ" in transparency_text:
            transparency = "Nhẹ"
        elif "Trung bình" in transparency_text:
            transparency = "Trung bình"
        elif "Cao" in transparency_text:
            transparency = "Cao"
        else:
            transparency = "Không trong suốt"
        self.settings.setValue("ui/transparency", transparency)
        
        self.accept()

    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton and self.title_bar.geometry().contains(event.position().toPoint()):
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragging and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging"""
        self.dragging = False
        self.drag_position = None
