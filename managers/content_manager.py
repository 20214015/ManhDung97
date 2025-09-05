"""
Content Manager Module
======================

Quản lý content stack và các trang của ứng dụng MuMu Manager Pro.

Author: GitHub Copilot
Date: September 1, 2025
Version: 1.0
"""

from typing import Dict, Any, Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QLabel,
    QFormLayout, QGroupBox, QHBoxLayout, QLineEdit,
    QPushButton, QTextEdit, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread, QThreadPool, QRunnable, pyqtSlot

from ui import ModernButton
from monokai_automation_page import MonokaiAutomationPage


class PageLoader(QObject, QRunnable):
    """Background loader cho các trang nặng."""

    finished = pyqtSignal()  # Signal khi hoàn thành

    def __init__(self, page_index: int, creator_func: Callable[[], QWidget]):
        QObject.__init__(self)
        QRunnable.__init__(self)
        self.page_index = page_index
        self.creator_func = creator_func
        self.widget = None
        self.error = None

    def run(self):
        """Chạy trong background thread."""
        try:
            self.widget = self.creator_func()
        except Exception as e:
            self.error = str(e)
        finally:
            self.finished.emit()


class ContentManager(QObject):
    """
    Quản lý content stack và lazy loading các trang.

    Features:
    - Lazy loading cho các trang
    - Background preloading cho trang tiếp theo
    - Page caching để tránh recreate
    - Content stack management
    - Page creation và management
    """

    # Signals
    page_loaded = pyqtSignal(int)  # index của page đã được load
    page_requested = pyqtSignal(int)  # index của page được request
    preload_completed = pyqtSignal(int)  # preload hoàn thành

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Khởi tạo ContentManager.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.parent = parent
        self.content_stack: Optional[QStackedWidget] = None
        self.loaded_pages: Dict[int, bool] = {}
        self.cached_pages: Dict[int, QWidget] = {}  # Cache các page đã load
        self.preloaded_pages: Dict[int, QWidget] = {}  # Preloaded pages
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(2)  # Giới hạn 2 thread cho loading

        self._create_content_stack()

    def _create_content_stack(self) -> None:
        """Tạo content stack widget."""
        self.content_stack = QStackedWidget()

        # Tạo placeholder cho các trang
        self._create_placeholders()

    def _create_placeholders(self) -> None:
        """Tạo placeholder widgets cho các trang."""
        page_names = [
            "Dashboard", "Quản lý Apps", "Công cụ ADB",
            "Kịch bản", "Tự động hóa"
        ]

        for i, name in enumerate(page_names):
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            label = QLabel(f"Đang tải {name}...")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.content_stack.addWidget(placeholder)
            self.loaded_pages[i] = False

    def get_content_widget(self) -> QStackedWidget:
        """Trả về content stack widget."""
        if self.content_stack is None:
            raise RuntimeError("Content stack not initialized")
        return self.content_stack

    def load_page(self, index: int) -> None:
        """Load một trang theo index."""
        print(f"🔧 DEBUG: ContentManager.load_page called with index {index}")
        if self.loaded_pages.get(index, False):
            return  # Đã load rồi

        if self.content_stack is None:
            return

        # Kiểm tra cache trước
        if index in self.cached_pages:
            self._use_cached_page(index)
            return

        # Kiểm tra preload
        if index in self.preloaded_pages:
            self._use_preloaded_page(index)
            return

        # Load mới
        self._load_page_sync(index)

        # Preload trang tiếp theo
        self._preload_next_page(index)

    def _load_page_sync(self, index: int) -> None:
        """Load page đồng bộ."""
        # Xác định page creator
        page_creators = {
            0: self._create_dashboard_page,
            1: self._create_apps_page,
            2: self._create_tools_page,
            3: self._create_scripting_page,
            4: self._create_automation_page,
        }

        creator = page_creators.get(index)
        if creator:
            try:
                # Tạo page widget
                page_widget = creator()

                # Cache page
                self.cached_pages[index] = page_widget

                # Thay thế placeholder
                old_widget = self.content_stack.widget(index)
                if old_widget:
                    self.content_stack.removeWidget(old_widget)
                    old_widget.deleteLater()

                self.content_stack.insertWidget(index, page_widget)
                self.loaded_pages[index] = True

                # Emit signal
                self.page_loaded.emit(index)

            except Exception as e:
                print(f"Error loading page {index}: {e}")

    def _use_cached_page(self, index: int) -> None:
        """Sử dụng page từ cache."""
        page_widget = self.cached_pages[index]

        # Thay thế placeholder
        old_widget = self.content_stack.widget(index)
        if old_widget:
            self.content_stack.removeWidget(old_widget)
            old_widget.deleteLater()

        self.content_stack.insertWidget(index, page_widget)
        self.loaded_pages[index] = True
        self.page_loaded.emit(index)

    def _use_preloaded_page(self, index: int) -> None:
        """Sử dụng page đã preload."""
        page_widget = self.preloaded_pages.pop(index)  # Remove from preload

        # Cache page
        self.cached_pages[index] = page_widget

        # Thay thế placeholder
        old_widget = self.content_stack.widget(index)
        if old_widget:
            self.content_stack.removeWidget(old_widget)
            old_widget.deleteLater()

        self.content_stack.insertWidget(index, page_widget)
        self.loaded_pages[index] = True
        self.page_loaded.emit(index)

    def _preload_next_page(self, current_index: int) -> None:
        """Preload trang tiếp theo trong background."""
        next_index = (current_index + 1) % self.content_stack.count()

        if next_index in self.loaded_pages and self.loaded_pages[next_index]:
            return  # Đã load rồi

        if next_index in self.cached_pages or next_index in self.preloaded_pages:
            return  # Đã cache hoặc preload rồi

        # Xác định page creator
        page_creators = {
            0: self._create_dashboard_page,
            1: self._create_apps_page,
            2: self._create_tools_page,
            3: self._create_scripting_page,
            4: self._create_automation_page,
        }

        creator = page_creators.get(next_index)
        if creator:
            # Tạo loader
            loader = PageLoader(next_index, creator)
            loader.finished.connect(lambda: self._on_preload_finished(loader))
            self.thread_pool.start(loader)

    @pyqtSlot()
    def _on_preload_finished(self, loader: PageLoader) -> None:
        """Handle khi preload hoàn thành."""
        if loader.error:
            print(f"Preload error for page {loader.page_index}: {loader.error}")
            return

        if loader.widget:
            self.preloaded_pages[loader.page_index] = loader.widget
            self.preload_completed.emit(loader.page_index)
            print(f"✅ Preloaded page {loader.page_index}")

    def set_current_page(self, index: int) -> None:
        """Đặt trang hiện tại."""
        if self.content_stack:
            self.content_stack.setCurrentIndex(index)
            self.page_requested.emit(index)

    def clear_cache(self) -> None:
        """Xóa cache để giải phóng bộ nhớ."""
        for widget in self.cached_pages.values():
            if widget and not widget.parent():
                widget.deleteLater()
        self.cached_pages.clear()
        print("🧹 Content cache cleared")

    def get_content_widget(self) -> QStackedWidget:
        """Trả về content stack widget."""
        if self.content_stack is None:
            raise RuntimeError("Content stack not initialized")
        return self.content_stack

    def load_page(self, index: int) -> None:
        """Load một trang theo index."""
        print(f"🔧 DEBUG: ContentManager.load_page called with index {index}")
        if self.loaded_pages.get(index, False):
            return  # Đã load rồi

        if self.content_stack is None:
            return

        # Xác định page creator
        page_creators = {
            0: self._create_dashboard_page,
            1: self._create_apps_page,
            2: self._create_tools_page,
            3: self._create_scripting_page,
            4: self._create_automation_page,
        }

        creator = page_creators.get(index)
        if creator:
            try:
                # Tạo page widget
                page_widget = creator()

                # Thay thế placeholder
                old_widget = self.content_stack.widget(index)
                if old_widget:
                    self.content_stack.removeWidget(old_widget)
                    old_widget.deleteLater()

                self.content_stack.insertWidget(index, page_widget)
                self.loaded_pages[index] = True

                # Emit signal
                self.page_loaded.emit(index)

            except Exception as e:
                print(f"Error loading page {index}: {e}")

    def set_current_page(self, index: int) -> None:
        """Đặt trang hiện tại."""
        if self.content_stack:
            self.content_stack.setCurrentIndex(index)
            self.page_requested.emit(index)

    def _create_dashboard_page(self) -> QWidget:
        """Tạo trang dashboard."""
        print("🔧 DEBUG: ContentManager._create_dashboard_page called")
        
        # Use the main window's dashboard creation method instead of placeholder
        if hasattr(self.parent, '_create_dashboard_page') and self.parent:
            print("🔧 DEBUG: Calling main window's _create_dashboard_page method")
            dashboard_widget = self.parent._create_dashboard_page()
            print("🔧 DEBUG: Main window's dashboard creation completed")
            return dashboard_widget
        else:
            print("🔧 DEBUG: Main window doesn't have _create_dashboard_page method, using placeholder")
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(QLabel("Dashboard - Đang phát triển..."))
            return widget

    def _create_apps_page(self) -> QWidget:
        """Tạo trang quản lý apps."""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        # APK Management Group
        apk_group = QGroupBox("Cài đặt / Gỡ bỏ ứng dụng")
        apk_layout = QFormLayout(apk_group)

        apk_path_edit = QLineEdit()
        apk_path_edit.setPlaceholderText("Đường dẫn đến file .apk")
        browse_apk_btn = QPushButton("Chọn APK")
        apk_row = QHBoxLayout()
        apk_row.addWidget(apk_path_edit)
        apk_row.addWidget(browse_apk_btn)

        pkg_name_edit = QLineEdit()
        pkg_name_edit.setPlaceholderText("ví dụ: com.google.android.youtube")

        btn_install_apk = ModernButton("📦 Cài đặt APK", "success", "md")
        btn_uninstall_pkg = ModernButton("🗑️ Gỡ Package", "danger", "md")

        apk_layout.addRow("File APK:", apk_row)
        apk_layout.addRow("Tên Package:", pkg_name_edit)
        btn_row1 = QHBoxLayout()
        btn_row1.addWidget(btn_install_apk)
        btn_row1.addWidget(btn_uninstall_pkg)
        apk_layout.addRow(btn_row1)
        layout.addRow(apk_group)

        # App Control Group
        control_group = QGroupBox("Điều khiển ứng dụng")
        control_layout = QFormLayout(control_group)

        btn_launch_app = ModernButton("🚀 Chạy App", "primary", "md")
        btn_stop_app = ModernButton("🛑 Dừng App", "danger", "md")

        btn_row2 = QHBoxLayout()
        btn_row2.addWidget(btn_launch_app)
        btn_row2.addWidget(btn_stop_app)
        control_layout.addRow(btn_row2)
        layout.addRow(control_group)

        return widget

    def _create_tools_page(self) -> QWidget:
        """Tạo trang công cụ ADB."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # ADB Command Group
        adb_group = QGroupBox("Lệnh ADB tùy chỉnh")
        adb_layout = QFormLayout(adb_group)

        adb_cmd_edit = QLineEdit()
        adb_cmd_edit.setPlaceholderText("shell getprop ro.product.model")
        btn_run_adb = QPushButton("Chạy lệnh cho các VM đã chọn")

        adb_layout.addRow("Lệnh:", adb_cmd_edit)
        adb_layout.addRow(btn_run_adb)
        layout.addRow(adb_group)

        # Tools Group
        tools_group = QGroupBox("Công cụ thường dùng")
        tools_layout = QFormLayout(tools_group)

        btn_screencap = QPushButton("Chụp ảnh màn hình (lưu vào /sdcard/screen.png)")
        tools_layout.addRow(btn_screencap)
        layout.addRow(tools_group)

        return widget

    def _create_scripting_page(self) -> QWidget:
        """Tạo trang kịch bản."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        script_group = QGroupBox("Trình chạy kịch bản ADB")
        script_layout = QVBoxLayout(script_group)

        button_layout = QHBoxLayout()
        btn_load_script = QPushButton(" Mở Kịch bản")
        btn_save_script = QPushButton(" Lưu Kịch bản")

        templates_menu = QMenu("Mẫu Kịch bản", widget)
        templates_menu.addAction("Lấy thông tin thiết bị")
        templates_menu.addAction("Liệt kê ứng dụng đã cài")

        templates_button = QPushButton(" Mẫu Kịch bản")
        templates_button.setMenu(templates_menu)

        button_layout.addWidget(btn_load_script)
        button_layout.addWidget(btn_save_script)
        button_layout.addWidget(templates_button)
        button_layout.addStretch(1)
        script_layout.addLayout(button_layout)

        script_input = QTextEdit()
        script_input.setPlaceholderText("shell pm list packages\nshell getprop ro.product.model\n...")
        script_layout.addWidget(script_input)

        btn_run_script = QPushButton(" Chạy Kịch bản")
        script_layout.addWidget(btn_run_script)

        layout.addWidget(script_group)
        return widget

    def _create_automation_page(self) -> QWidget:
        """Tạo trang tự động hóa."""
        try:
            automation_page = MonokaiAutomationPage(self.parent)
            return automation_page
        except Exception as e:
            print(f"Error creating automation page: {e}")
            # Fallback
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(QLabel("Trang Tự động hóa - Đang phát triển..."))
            return widget
