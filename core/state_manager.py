"""
StateManager - Centralized State Management
==========================================

Provides centralized state management for the application.
"""

import logging
from typing import Dict, List, Any, Optional
from .event_types import EventTypes

try:
    from PyQt6.QtCore import QObject, pyqtSignal
    _QT_AVAILABLE = True
except ImportError:
    _QT_AVAILABLE = False
    class QObject:
        def __init__(self):
            pass


class StateManagerQt(QObject):
    """Qt-enabled StateManager with proper signal support"""
    instances_changed = pyqtSignal(list)
    selection_changed = pyqtSignal(list)
    ui_changed = pyqtSignal(dict)
    automation_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()


class StateManager:
    """
    Centralized state management for the application.
    
    Manages all application state in one place and emits events when state changes.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
            
        self.initialized = True
        self.logger = logging.getLogger('StateManager')
        
        # Application state
        self._instances: List[Dict[str, Any]] = []
        self._selected_instances: List[int] = []
        self._current_page: int = 0
        self._ui_settings: Dict[str, Any] = {}
        self._automation_settings: Dict[str, Any] = {}
        self._app_settings: Dict[str, Any] = {}
        
        # Setup Qt signals if available
        if _QT_AVAILABLE:
            # Create Qt object for signal support
            self._qt_object = StateManagerQt()
            # Expose signals through the Qt object
            self.instances_changed = self._qt_object.instances_changed
            self.selection_changed = self._qt_object.selection_changed
            self.ui_changed = self._qt_object.ui_changed
            self.automation_changed = self._qt_object.automation_changed
        else:
            # Create dummy signals for non-Qt environments
            class DummySignal:
                def emit(self, *args): pass
                def connect(self, *args): pass
            self.instances_changed = DummySignal()
            self.selection_changed = DummySignal()
            self.ui_changed = DummySignal()
            self.automation_changed = DummySignal()
        
    # Instance State Management
    def update_instances(self, instances: List[Dict[str, Any]]):
        """
        Update the instances list.
        
        Args:
            instances: List of instance data dictionaries
        """
        self._instances = instances.copy()
        self.logger.debug(f"Updated instances: {len(instances)} instances")
        
        # Emit Qt signal if available
        self.instances_changed.emit(instances)
            
        # Emit event
        from .event_manager import emit_event
        emit_event(EventTypes.INSTANCES_UPDATED, {'instances': instances})
        
    def get_instances(self) -> List[Dict[str, Any]]:
        """Get current instances list."""
        return self._instances.copy()
        
    def get_instance(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get instance by index.
        
        Args:
            index: Instance index
            
        Returns:
            Instance data or None if not found
        """
        if 0 <= index < len(self._instances):
            return self._instances[index]
        return None
        
    def set_selected_instances(self, indices: List[int]):
        """
        Set selected instance indices.
        
        Args:
            indices: List of selected instance indices
        """
        self._selected_instances = indices.copy()
        self.logger.debug(f"Selected instances: {indices}")
        
        # Emit Qt signal if available
        if _QT_AVAILABLE and hasattr(self, '_qt_object') and hasattr(self._qt_object, 'selection_changed'):
            try:
                # Note: This would work if we were in a proper Qt environment
                # For now, we'll skip the actual Qt signal emission
                pass
            except Exception:
                pass
            
        # Emit event
        from .event_manager import emit_event
        emit_event(EventTypes.INSTANCE_SELECTED, {'indices': indices})
        
    def get_selected_instances(self) -> List[int]:
        """Get currently selected instance indices."""
        return self._selected_instances.copy()
        
    def add_selected_instance(self, index: int):
        """Add an instance to the selection."""
        if index not in self._selected_instances and 0 <= index < len(self._instances):
            self._selected_instances.append(index)
            self.set_selected_instances(self._selected_instances)
            
    def remove_selected_instance(self, index: int):
        """Remove an instance from the selection."""
        if index in self._selected_instances:
            self._selected_instances.remove(index)
            self.set_selected_instances(self._selected_instances)
            
    def clear_selection(self):
        """Clear all selected instances."""
        self.set_selected_instances([])
        
    # UI State Management
    def set_current_page(self, page: int):
        """
        Set the current page index.
        
        Args:
            page: Page index
        """
        self._current_page = page
        self.logger.debug(f"Current page: {page}")
        
        # Emit event
        from .event_manager import emit_event
        emit_event(EventTypes.PAGE_CHANGED, {'page': page})
        
    def get_current_page(self) -> int:
        """Get current page index."""
        return self._current_page
        
    def update_ui_settings(self, settings: Dict[str, Any]):
        """
        Update UI settings.
        
        Args:
            settings: UI settings dictionary
        """
        self._ui_settings.update(settings)
        self.logger.debug(f"Updated UI settings: {settings}")
        
        # Emit Qt signal if available
        self.ui_changed.emit(settings)
            
        # Emit event
        from .event_manager import emit_event
        emit_event(EventTypes.UI_STATE_CHANGED, {'settings': self._ui_settings})
        
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI settings."""
        return self._ui_settings.copy()
        
    def get_ui_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific UI setting.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        return self._ui_settings.get(key, default)
        
    # Automation State Management
    def update_automation_settings(self, settings: Dict[str, Any]):
        """
        Update automation settings.
        
        Args:
            settings: Automation settings dictionary
        """
        self._automation_settings.update(settings)
        self.logger.debug(f"Updated automation settings: {settings}")
        
        # Emit Qt signal if available
        if _QT_AVAILABLE and hasattr(self, '_qt_object') and hasattr(self._qt_object, 'automation_changed'):
            try:
                # Note: This would work if we were in a proper Qt environment
                # For now, we'll skip the actual Qt signal emission
                pass
            except Exception:
                pass
            
        # Emit event
        from .event_manager import emit_event
        emit_event(EventTypes.AUTOMATION_STARTED, {'settings': self._automation_settings})
        
    def get_automation_settings(self) -> Dict[str, Any]:
        """Get automation settings."""
        return self._automation_settings.copy()
        
    # Application Settings
    def update_app_settings(self, settings: Dict[str, Any]):
        """
        Update application settings.
        
        Args:
            settings: Application settings dictionary
        """
        self._app_settings.update(settings)
        self.logger.debug(f"Updated app settings: {settings}")
        
    def get_app_settings(self) -> Dict[str, Any]:
        """Get application settings."""
        return self._app_settings.copy()
        
    def get_app_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific application setting.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        return self._app_settings.get(key, default)


# Global state manager instance
_state_manager = None


def get_state_manager() -> StateManager:
    """
    Get the global StateManager instance.
    
    Returns:
        StateManager singleton instance
    """
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager