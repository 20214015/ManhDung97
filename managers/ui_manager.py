"""
UI Manager
==========

Handles all UI state management and page creation logic extracted from main_window.py.
Provides a clean separation of UI management from business logic.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, 
    QLabel, QProgressBar, QPushButton, QFrame
)

from core import get_event_manager, get_state_manager, EventTypes, emit_event


class UIManager(QObject):
    """
    Manages all UI-related operations including:
    - Page creation and management
    - UI state management
    - Lazy loading of UI components
    - Theme and styling management
    """
    
    # Signals for UI updates
    page_changed = pyqtSignal(int)           # page_index
    page_loaded = pyqtSignal(int, QWidget)   # page_index, widget
    theme_changed = pyqtSignal(str)          # theme_name
    ui_state_changed = pyqtSignal(dict)      # ui_state
    progress_updated = pyqtSignal(int, str)  # progress, message
    status_updated = pyqtSignal(str, str)    # message, level
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('UIManager')
        
        # State management
        self.state_manager = get_state_manager()
        self.event_manager = get_event_manager()
        
        # UI state
        self._current_page: int = 0
        self._loaded_pages: Dict[int, bool] = {}
        self._page_widgets: Dict[int, QWidget] = {}
        self._page_factories: Dict[int, Callable[[], QWidget]] = {}
        self._ui_settings: Dict[str, Any] = {}
        
        # Progress and status
        self._current_progress: int = 0
        self._current_status: str = ""
        self._status_level: str = "info"
        
        # Timers
        self._auto_refresh_timer = QTimer()
        self._status_clear_timer = QTimer()
        
        # Setup
        self._setup_event_subscriptions()
        self._setup_timers()
        
    def _setup_event_subscriptions(self):
        """Setup event subscriptions for UI events"""
        self.event_manager.subscribe(EventTypes.PAGE_CHANGED, self._on_page_changed_event)
        self.event_manager.subscribe(EventTypes.UI_STATE_CHANGED, self._on_ui_state_changed_event)
        self.event_manager.subscribe(EventTypes.THEME_CHANGED, self._on_theme_changed_event)
        
    def _on_page_changed_event(self, data: Dict[str, Any]):
        """Handle page changed event"""
        page = data.get('page', 0)
        self._current_page = page
        self.page_changed.emit(page)
        
    def _on_ui_state_changed_event(self, data: Dict[str, Any]):
        """Handle UI state changed event"""
        settings = data.get('settings', {})
        self._ui_settings.update(settings)
        self.ui_state_changed.emit(self._ui_settings)
        
    def _on_theme_changed_event(self, data: Dict[str, Any]):
        """Handle theme changed event"""
        theme_name = data.get('theme', 'default')
        self.theme_changed.emit(theme_name)
        
    def _setup_timers(self):
        """Setup UI timers"""
        self._status_clear_timer.setSingleShot(True)
        self._status_clear_timer.timeout.connect(self._clear_status)
        
    # Page Management
    def register_page_factory(self, page_index: int, factory: Callable[[], QWidget]):
        """
        Register a page factory for lazy loading.
        
        Args:
            page_index: Index of the page
            factory: Function that creates the page widget
        """
        self._page_factories[page_index] = factory
        self._loaded_pages[page_index] = False
        self.logger.debug(f"Registered page factory for index {page_index}")
        
    def load_page(self, page_index: int) -> Optional[QWidget]:
        """
        Load a page widget, creating it if necessary.
        
        Args:
            page_index: Index of the page to load
            
        Returns:
            The page widget or None if not found
        """
        try:
            # Return cached widget if already loaded
            if page_index in self._page_widgets:
                return self._page_widgets[page_index]
                
            # Create widget using factory if available
            if page_index in self._page_factories:
                self.logger.debug(f"Creating page {page_index}")
                widget = self._page_factories[page_index]()
                
                if widget:
                    self._page_widgets[page_index] = widget
                    self._loaded_pages[page_index] = True
                    self.page_loaded.emit(page_index, widget)
                    self.logger.info(f"Page {page_index} loaded successfully")
                    return widget
                else:
                    self.logger.error(f"Page factory for {page_index} returned None")
                    
            else:
                self.logger.warning(f"No factory registered for page {page_index}")
                
            return None
            
        except Exception as e:
            error_msg = f"Failed to load page {page_index}: {e}"
            self.logger.error(error_msg)
            return None
            
    def is_page_loaded(self, page_index: int) -> bool:
        """Check if a page is loaded"""
        return self._loaded_pages.get(page_index, False)
        
    def get_page_widget(self, page_index: int) -> Optional[QWidget]:
        """Get a page widget if it's loaded"""
        return self._page_widgets.get(page_index)
        
    def unload_page(self, page_index: int):
        """Unload a page to free memory"""
        try:
            if page_index in self._page_widgets:
                widget = self._page_widgets[page_index]
                widget.deleteLater()
                del self._page_widgets[page_index]
                self._loaded_pages[page_index] = False
                self.logger.info(f"Page {page_index} unloaded")
                
        except Exception as e:
            self.logger.error(f"Error unloading page {page_index}: {e}")
            
    def set_current_page(self, page_index: int):
        """
        Set the current active page.
        
        Args:
            page_index: Index of the page to activate
        """
        if page_index != self._current_page:
            self._current_page = page_index
            self.state_manager.set_current_page(page_index)
            emit_event(EventTypes.PAGE_CHANGED, {'page': page_index})
            
    def get_current_page(self) -> int:
        """Get the current active page index"""
        return self._current_page
        
    # UI State Management
    def update_ui_setting(self, key: str, value: Any):
        """Update a single UI setting"""
        self._ui_settings[key] = value
        self.state_manager.update_ui_settings({key: value})
        
    def update_ui_settings(self, settings: Dict[str, Any]):
        """Update multiple UI settings"""
        self._ui_settings.update(settings)
        self.state_manager.update_ui_settings(settings)
        
    def get_ui_setting(self, key: str, default: Any = None) -> Any:
        """Get a UI setting value"""
        return self._ui_settings.get(key, default)
        
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get all UI settings"""
        return self._ui_settings.copy()
        
    # Progress Management
    def set_progress(self, value: int, message: str = ""):
        """
        Set progress value and message.
        
        Args:
            value: Progress value (0-100)
            message: Progress message
        """
        self._current_progress = max(0, min(100, value))
        self.progress_updated.emit(self._current_progress, message)
        
    def increment_progress(self, increment: int = 1, message: str = ""):
        """Increment progress by a certain amount"""
        new_value = self._current_progress + increment
        self.set_progress(new_value, message)
        
    def reset_progress(self, message: str = ""):
        """Reset progress to 0"""
        self.set_progress(0, message)
        
    def complete_progress(self, message: str = "Completed"):
        """Set progress to 100%"""
        self.set_progress(100, message)
        
    def get_current_progress(self) -> int:
        """Get current progress value"""
        return self._current_progress
        
    # Status Management
    def set_status(self, message: str, level: str = "info", auto_clear: bool = True, clear_after: int = 5000):
        """
        Set status message.
        
        Args:
            message: Status message
            level: Status level (info, warning, error, success)
            auto_clear: Whether to auto-clear the status
            clear_after: Time in milliseconds before auto-clearing
        """
        self._current_status = message
        self._status_level = level
        self.status_updated.emit(message, level)
        
        if auto_clear and clear_after > 0:
            self._status_clear_timer.stop()
            self._status_clear_timer.start(clear_after)
            
    def clear_status(self):
        """Clear the current status"""
        self._clear_status()
        
    def _clear_status(self):
        """Internal method to clear status"""
        self._current_status = ""
        self._status_level = "info"
        self.status_updated.emit("", "info")
        
    def get_current_status(self) -> tuple[str, str]:
        """Get current status message and level"""
        return self._current_status, self._status_level
        
    # Theme Management
    def set_theme(self, theme_name: str):
        """
        Set application theme.
        
        Args:
            theme_name: Name of the theme to apply
        """
        self.update_ui_setting('theme', theme_name)
        emit_event(EventTypes.THEME_CHANGED, {'theme': theme_name})
        
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.get_ui_setting('theme', 'default')
        
    # Lazy Loading Utilities
    def create_placeholder_widget(self, page_name: str) -> QWidget:
        """
        Create a placeholder widget for unloaded pages.
        
        Args:
            page_name: Name of the page
            
        Returns:
            Placeholder widget
        """
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Loading message
        label = QLabel(f"Loading {page_name}...")
        label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                text-align: center;
            }
        """)
        layout.addWidget(label)
        
        # Progress bar (optional)
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminate progress
        progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(progress)
        
        return placeholder
        
    def create_error_widget(self, error_message: str) -> QWidget:
        """
        Create an error widget for failed page loads.
        
        Args:
            error_message: Error message to display
            
        Returns:
            Error widget
        """
        error_widget = QWidget()
        layout = QVBoxLayout(error_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Error icon (using text)
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                text-align: center;
                color: #ff6b6b;
            }
        """)
        layout.addWidget(icon_label)
        
        # Error message
        message_label = QLabel(f"Failed to load page:\n{error_message}")
        message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                text-align: center;
                margin: 10px;
            }
        """)
        layout.addWidget(message_label)
        
        # Retry button
        retry_button = QPushButton("Retry")
        retry_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        layout.addWidget(retry_button)
        
        return error_widget
        
    # Auto-refresh Management
    def setup_auto_refresh(self, interval: int = 30000, callback: Callable = None):
        """
        Setup auto-refresh timer.
        
        Args:
            interval: Refresh interval in milliseconds
            callback: Callback function to call on refresh
        """
        self._auto_refresh_timer.stop()
        
        if callback:
            self._auto_refresh_timer.timeout.connect(callback)
            
        self._auto_refresh_timer.start(interval)
        self.logger.info(f"Auto-refresh setup with {interval}ms interval")
        
    def stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        self._auto_refresh_timer.stop()
        self.logger.info("Auto-refresh stopped")
        
    def is_auto_refresh_active(self) -> bool:
        """Check if auto-refresh is active"""
        return self._auto_refresh_timer.isActive()
        
    # Layout Utilities
    def create_separator(self) -> QFrame:
        """Create a horizontal separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("""
            QFrame {
                color: #ccc;
                background-color: #ccc;
                height: 1px;
                border: none;
            }
        """)
        return separator
        
    def create_vertical_separator(self) -> QFrame:
        """Create a vertical separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("""
            QFrame {
                color: #ccc;
                background-color: #ccc;
                width: 1px;
                border: none;
            }
        """)
        return separator
        
    # Responsive Design Utilities
    def get_optimal_column_count(self, container_width: int, min_item_width: int = 200) -> int:
        """
        Calculate optimal column count for responsive layouts.
        
        Args:
            container_width: Width of the container
            min_item_width: Minimum width per item
            
        Returns:
            Optimal number of columns
        """
        return max(1, container_width // min_item_width)
        
    def calculate_responsive_spacing(self, container_width: int) -> int:
        """Calculate responsive spacing based on container width"""
        if container_width < 600:
            return 5
        elif container_width < 1200:
            return 10
        else:
            return 15
            
    # Cleanup
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop timers
            self._auto_refresh_timer.stop()
            self._status_clear_timer.stop()
            
            # Clear page widgets
            for widget in self._page_widgets.values():
                widget.deleteLater()
                
            self._page_widgets.clear()
            self._loaded_pages.clear()
            
        except Exception as e:
            self.logger.error(f"Error during UI cleanup: {e}")
            
    # Debug and Monitoring
    def get_ui_status(self) -> Dict[str, Any]:
        """Get current UI status for debugging"""
        return {
            'current_page': self._current_page,
            'loaded_pages': list(self._loaded_pages.keys()),
            'page_count': len(self._page_factories),
            'current_progress': self._current_progress,
            'current_status': self._current_status,
            'auto_refresh_active': self.is_auto_refresh_active(),
            'ui_settings_count': len(self._ui_settings)
        }