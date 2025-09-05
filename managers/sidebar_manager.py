"""
Sidebar Manager Module
======================

Quản lý sidebar và navigation của ứng dụng MuMu Manager Pro.

Author: GitHub Copilot
Date: September 1, 2025
Version: 1.0
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel, QPushButton,
    QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont

from ui import ModernButton
from constants import APP_NAME


class SidebarManager(QObject):
    """
    Quản lý sidebar navigation và các button controls.

    Features:
    - Modern sidebar với navigation buttons
    - Settings và theme toggle buttons
    - Signal-based communication với main window
    """

    # Signals
    navigation_requested = pyqtSignal(int)  # index của page được request
    settings_requested = pyqtSignal()
    theme_toggle_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Khởi tạo SidebarManager.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.parent = parent
        self.sidebar: Optional[QFrame] = None
        self.sidebar_buttons: Dict[str, QPushButton] = {}
        self.settings_btn: Optional[ModernButton] = None
        self.theme_toggle_btn: Optional[ModernButton] = None

        self._create_sidebar()

    def _create_sidebar(self) -> None:
        """Tạo sidebar widget với navigation buttons."""
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)

        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Title
        title = QLabel(APP_NAME)
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        layout.addSpacing(10)

        # Navigation buttons
        self.sidebar_buttons_map = {
            "dashboard": (" Dashboard", 0),
            "apps": (" Quản lý Apps", 1),
            "adb": (" Công cụ ADB", 2),
            "script": (" Kịch bản", 3),
            "automation": (" Tự động hóa", 4)
        }

        self.sidebar_buttons = {}
        for name, (text, index) in self.sidebar_buttons_map.items():
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, idx=index: self._handle_navigation(idx))
            layout.addWidget(btn)
            self.sidebar_buttons[name] = btn

        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Settings buttons
        self.settings_btn = ModernButton("Cài đặt", "secondary", "md")
        self.theme_toggle_btn = ModernButton("Giao diện", "secondary", "md")

        layout.addWidget(self.settings_btn)
        layout.addWidget(self.theme_toggle_btn)

        # Connect signals
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Kết nối signals cho các buttons."""
        if self.settings_btn:
            self.settings_btn.clicked.connect(self._handle_settings)
        if self.theme_toggle_btn:
            self.theme_toggle_btn.clicked.connect(self._handle_theme_toggle)

    def _handle_navigation(self, index: int) -> None:
        """Xử lý navigation request."""
        self.navigation_requested.emit(index)

    def _handle_settings(self) -> None:
        """Xử lý settings request."""
        self.settings_requested.emit()

    def _handle_theme_toggle(self) -> None:
        """Xử lý theme toggle request."""
        self.theme_toggle_requested.emit()

    def get_sidebar_widget(self) -> QFrame:
        """Trả về sidebar widget."""
        if self.sidebar is None:
            raise RuntimeError("Sidebar not initialized")
        return self.sidebar

    def update_button_styles(self) -> None:
        """Cập nhật style cho các buttons."""
        # Có thể thêm logic cập nhật style ở đây
        pass

    def update_automation_button_states(self, automation_buttons: Dict[str, QPushButton]) -> None:
        """
        Cập nhật trạng thái của các automation buttons.
        
        Args:
            automation_buttons: Dictionary chứa các automation buttons
        """
        for button_name, button in automation_buttons.items():
            if button is None:
                continue
                
            if not button.isEnabled():
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #555555;
                        color: #888888;
                        border: 1px solid #333333;
                        border-radius: 5px;
                        padding: 8px 12px;
                    }
                """)
            else:
                # Reset về style mặc định dựa trên button name
                if button_name == 'btn_auto_pause':
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #f39c12;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            padding: 8px 12px;
                        }
                        QPushButton:hover {
                            background-color: #e67e22;
                        }
                        QPushButton:pressed {
                            background-color: #d35400;
                        }
                    """)
                elif button_name == 'btn_auto_stop':
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            padding: 8px 12px;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                        QPushButton:pressed {
                            background-color: #a93226;
                        }
                    """)
                elif button_name == 'btn_auto_start':
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #27ae60;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            padding: 8px 12px;
                        }
                        QPushButton:hover {
                            background-color: #229954;
                        }
                        QPushButton:pressed {
                            background-color: #1e8449;
                        }
                    """)
                
                button.update()

    def set_active_page(self, index: int) -> None:
        """Đặt trang active trong sidebar."""
        # Reset tất cả buttons
        for btn in self.sidebar_buttons.values():
            if btn:
                btn.setProperty("active", False)
                style = btn.style()
                if style:
                    style.unpolish(btn)
                    style.polish(btn)

        # Tìm button tương ứng với index và set active
        for name, (_, btn_index) in self.sidebar_buttons_map.items():
            if btn_index == index:
                if name in self.sidebar_buttons and self.sidebar_buttons[name]:
                    btn = self.sidebar_buttons[name]
                    btn.setProperty("active", True)
                    style = btn.style()
                    if style:
                        style.unpolish(btn)
                        style.polish(btn)
                break
