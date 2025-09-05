"""
Reactive State Management System
================================

Thread-safe reactive state management cho MuMuManager Pro.
Tự động cập nhật UI khi data thay đổi.
"""

from typing import Any, Dict, Callable, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ReactiveState(QObject):
    """
    Reactive state management với thread-safe operations.

    Features:
    - Thread-safe state mutations
    - Automatic UI updates via signals
    - Computed properties
    - State history & undo/redo
    - Validation & constraints
    """

    # Signals for state changes
    state_changed = pyqtSignal(str, object, object)  # key, new_value, old_value
    state_validated = pyqtSignal(str, bool)  # key, is_valid
    state_computed = pyqtSignal(str, object)  # computed_key, value

    def __init__(self):
        super().__init__()
        self._data: Dict[str, Any] = {}
        self._listeners: Dict[str, List[Callable[..., Any]]] = defaultdict(list)
        self._computed: Dict[str, Callable[..., Any]] = {}
        self._validators: Dict[str, Callable[..., Any]] = {}
        self._constraints: Dict[str, Callable[..., Any]] = {}
        self._history: List[Dict[str, Any]] = []
        self._history_index = -1
        self._mutex = QMutex()

    def set(self, key: str, value: Any, skip_validation: bool = False) -> bool:
        """
        Set state value với validation và thread safety.

        Args:
            key: State key
            value: New value
            skip_validation: Skip validation if True

        Returns:
            bool: True if value was set successfully
        """
        with QMutexLocker(self._mutex):
            # Validate value if validator exists
            if not skip_validation and key in self._validators:
                if not self._validators[key](value):
                    self.state_validated.emit(key, False)
                    logger.warning(f"Validation failed for {key}: {value}")
                    return False

            # Check constraints
            if key in self._constraints:
                constrained_value = self._constraints[key](value, self._data)
                if constrained_value != value:
                    value = constrained_value
                    logger.info(f"Value constrained for {key}: {value}")

            # Store old value for history
            old_value = self._data.get(key)

            # Update value
            self._data[key] = value

            # Add to history
            self._add_to_history(key, value, old_value)

            # Emit signal
            self.state_changed.emit(key, value, old_value)

            # Notify listeners
            self._notify_listeners(key, value, old_value)

            # Update computed properties
            self._update_computed_properties(key)

            self.state_validated.emit(key, True)
            return True

    def get(self, key: str, default: Any = None) -> Any:
        """Get state value thread-safely."""
        with QMutexLocker(self._mutex):
            return self._data.get(key, default)

    def subscribe(self, key: str, callback: Callable[..., Any]) -> None:
        """Subscribe to state changes."""
        with QMutexLocker(self._mutex):
            self._listeners[key].append(callback)

    def unsubscribe(self, key: str, callback: Callable[..., Any]) -> None:
        """Unsubscribe from state changes."""
        with QMutexLocker(self._mutex):
            if key in self._listeners and callback in self._listeners[key]:
                self._listeners[key].remove(callback)

    def add_validator(self, key: str, validator: Callable) -> None:
        """Add validation function for a key."""
        with QMutexLocker(self._mutex):
            self._validators[key] = validator

    def add_constraint(self, key: str, constraint: Callable) -> None:
        """Add constraint function for a key."""
        with QMutexLocker(self._mutex):
            self._constraints[key] = constraint

    def add_computed(self, key: str, compute_func: Callable) -> None:
        """Add computed property."""
        with QMutexLocker(self._mutex):
            self._computed[key] = compute_func
            # Compute initial value
            try:
                value = compute_func(self._data)
                self.state_computed.emit(key, value)
            except Exception as e:
                logger.error(f"Error computing {key}: {e}")

    def undo(self) -> bool:
        """Undo last state change."""
        with QMutexLocker(self._mutex):
            if self._history_index > 0:
                self._history_index -= 1
                state = self._history[self._history_index]
                self._data.update(state)
                return True
            return False

    def redo(self) -> bool:
        """Redo next state change."""
        with QMutexLocker(self._mutex):
            if self._history_index < len(self._history) - 1:
                self._history_index += 1
                state = self._history[self._history_index]
                self._data.update(state)
                return True
            return False

    def _notify_listeners(self, key: str, new_value: Any, old_value: Any) -> None:
        """Notify all listeners of state change."""
        for callback in self._listeners[key]:
            try:
                callback(key, new_value, old_value)
            except Exception as e:
                logger.error(f"Error in listener for {key}: {e}")

    def _update_computed_properties(self, changed_key: str) -> None:
        """Update computed properties that depend on changed key."""
        for computed_key, compute_func in self._computed.items():
            try:
                new_value = compute_func(self._data)
                self.state_computed.emit(computed_key, new_value)
            except Exception as e:
                logger.error(f"Error updating computed {computed_key}: {e}")

    def _add_to_history(self, key: str, new_value: Any, old_value: Any) -> None:
        """Add state change to history."""
        # Remove any redo history
        self._history = self._history[:self._history_index + 1]

        # Create snapshot of current state
        state_snapshot = self._data.copy()
        self._history.append(state_snapshot)
        self._history_index = len(self._history) - 1

        # Limit history size
        max_history = 50
        if len(self._history) > max_history:
            self._history = self._history[-max_history:]
            self._history_index = len(self._history) - 1

# Global reactive state instance
global_reactive_state = ReactiveState()

# Convenience functions
def set_state(key: str, value: Any) -> bool:
    """Global set state function."""
    return global_reactive_state.set(key, value)

def get_state(key: str, default: Any = None) -> Any:
    """Global get state function."""
    return global_reactive_state.get(key, default)

def subscribe_state(key: str, callback: Callable[..., Any]) -> None:
    """Global subscribe function."""
    global_reactive_state.subscribe(key, callback)

# Example usage in MainWindow
class ReactiveMainWindow:
    """Example of reactive MainWindow integration."""

    def __init__(self):
        # Subscribe to reactive state changes
        subscribe_state('selected_instances', self._on_selection_changed)
        subscribe_state('theme_mode', self._on_theme_changed)
        subscribe_state('auto_refresh_enabled', self._on_auto_refresh_changed)

        # Add validators
        global_reactive_state.add_validator('instance_count',
            lambda x: isinstance(x, int) and 0 <= x <= 1000)

        # Add computed properties
        global_reactive_state.add_computed('total_memory_usage',
            lambda data: sum(inst.get('memory', 0) for inst in data.get('instances', [])))

    def _on_selection_changed(self, key: str, new_value: Any, old_value: Any):
        """Handle selection changes reactively."""
        self.status_bar_manager.update_selection_info(len(new_value) if new_value else 0)

    def _on_theme_changed(self, key: str, new_value: Any, old_value: Any):
        """Handle theme changes reactively."""
        self.theme_manager.apply_theme(new_value)

    def _on_auto_refresh_changed(self, key: str, new_value: Any, old_value: Any):
        """Handle auto refresh changes reactively."""
        if new_value:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()</content>
<parameter name="filePath">c:\Users\SuperMan\Desktop\UPDate-copilot-fix-732b2fcf-f918-4cc5-846e-27adffe93778\UPDate-copilot-fix-732b2fcf-f918-4cc5-846e-27adffe93778\core\reactive_state.py
