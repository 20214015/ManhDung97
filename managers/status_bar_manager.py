"""
Status Bar Manager Module
========================

Quản lý status bar của ứng dụng MuMu Manager Pro.

Author: GitHub Copilot
Date: September 1, 2025
Version: 1.0
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QStatusBar, QLabel, QProgressBar, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from ui import ModernProgressBar


class StatusBarManager(QObject):
    """
    Quản lý status bar và các thành phần liên quan.

    Features:
    - Status labels management
    - Progress bar management
    - Status updates
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Khởi tạo StatusBarManager.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.parent = parent
        self.status_bar: Optional[QStatusBar] = None
        self.selection_label: Optional[QLabel] = None
        self.auto_refresh_status_label: Optional[QLabel] = None
        self.global_progress_bar: Optional[ModernProgressBar] = None
        self.summary_status_label: Optional[QLabel] = None

        self._create_status_bar()

    def _create_status_bar(self) -> None:
        """Tạo status bar với các components."""
        self.status_bar = QStatusBar()

        # Selection label
        self.selection_label = QLabel("Đã chọn: 0")
        self.selection_label.setContentsMargins(10, 0, 10, 0)
        self.status_bar.addPermanentWidget(self.selection_label)

        # Auto refresh status label
        self.auto_refresh_status_label = QLabel()
        self.auto_refresh_status_label.setContentsMargins(10, 0, 10, 0)
        self.status_bar.addPermanentWidget(self.auto_refresh_status_label)

        # Global progress bar
        self.global_progress_bar = ModernProgressBar()
        self.global_progress_bar.setVisible(False)
        self.global_progress_bar.setFormat("%p%")
        self.global_progress_bar.setFixedWidth(200)
        self.status_bar.addPermanentWidget(self.global_progress_bar)

        # Summary status label
        self.summary_status_label = QLabel("🚀 Sẵn sàng - UI hiện đại đã được tối ưu!")
        self.status_bar.addWidget(self.summary_status_label)

    def get_status_bar(self) -> QStatusBar:
        """Trả về status bar widget."""
        if self.status_bar is None:
            raise RuntimeError("Status bar not initialized")
        return self.status_bar

    def update_selection_info(self, selected_count: int) -> None:
        """Cập nhật thông tin selection."""
        if self.selection_label:
            self.selection_label.setText(f"Đã chọn: {selected_count}")

    def update_auto_refresh_status(self, status: str) -> None:
        """Cập nhật trạng thái auto refresh."""
        if self.auto_refresh_status_label:
            self.auto_refresh_status_label.setText(status)

    def update_progress(self, value: int, visible: bool = True) -> None:
        """Cập nhật progress bar."""
        if self.global_progress_bar:
            self.global_progress_bar.setValue(value)
            self.global_progress_bar.setVisible(visible)

    def update_summary_status(self, status: str) -> None:
        """Cập nhật summary status."""
        if self.summary_status_label:
            self.summary_status_label.setText(status)

    def show_message(self, message: str, timeout: int = 0) -> None:
        """Hiển thị message tạm thời."""
        if self.status_bar:
            self.status_bar.showMessage(message, timeout)

    def clear_message(self) -> None:
        """Xóa message hiện tại."""
        if self.status_bar:
            self.status_bar.clearMessage()
