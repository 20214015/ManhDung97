"""
State Manager - Centralized State Management for Automation System
===============================================================
Advanced state management with persistence, validation, and event-driven updates.
"""

import json
import pickle
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable, TypeVar, Generic
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QMutex
from PyQt6.QtWidgets import QApplication


T = TypeVar('T')


class StateChangeType(Enum):
    """Types of state changes"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESET = "reset"
    BATCH_UPDATE = "batch_update"


@dataclass
class StateChange:
    """Represents a state change event"""
    change_type: StateChangeType
    key: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateValidator:
    """State validation and constraint checking"""
    
    def __init__(self):
        self.validators: Dict[str, List[Callable]] = {}
        self.constraints: Dict[str, Dict[str, Any]] = {}
        
    def add_validator(self, key: str, validator_func: Callable[[Any], bool]):
        """Add validation function for a state key"""
        if key not in self.validators:
            self.validators[key] = []
        self.validators[key].append(validator_func)
    
    def add_constraint(self, key: str, constraint_type: str, value: Any):
        """Add constraint for a state key"""
        if key not in self.constraints:
            self.constraints[key] = {}
        self.constraints[key][constraint_type] = value
    
    def validate(self, key: str, value: Any) -> tuple[bool, str]:
        """Validate a value for a given key"""
        try:
            # Run custom validators
            if key in self.validators:
                for validator in self.validators[key]:
                    if not validator(value):
                        return False, f"Custom validation failed for key '{key}'"
            
            # Check constraints
            if key in self.constraints:
                constraints = self.constraints[key]
                
                # Type constraint
                if 'type' in constraints:
                    expected_type = constraints['type']
                    if not isinstance(value, expected_type):
                        return False, f"Expected type {expected_type.__name__}, got {type(value).__name__}"
                
                # Range constraint (for numbers)
                if isinstance(value, (int, float)):
                    if 'min' in constraints and value < constraints['min']:
                        return False, f"Value {value} is below minimum {constraints['min']}"
                    if 'max' in constraints and value > constraints['max']:
                        return False, f"Value {value} is above maximum {constraints['max']}"
                
                # Length constraint (for sequences)
                if hasattr(value, '__len__'):
                    if 'min_length' in constraints and len(value) < constraints['min_length']:
                        return False, f"Length {len(value)} is below minimum {constraints['min_length']}"
                    if 'max_length' in constraints and len(value) > constraints['max_length']:
                        return False, f"Length {len(value)} is above maximum {constraints['max_length']}"
                
                # Allowed values constraint
                if 'allowed_values' in constraints:
                    allowed = constraints['allowed_values']
                    if value not in allowed:
                        return False, f"Value {value} not in allowed values {allowed}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class StatePersistence:
    """Handle state persistence to disk"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Save state to disk"""
        try:
            # Create backup
            if self.file_path.exists():
                backup_path = self.file_path.with_suffix('.bak')
                self.file_path.rename(backup_path)
            
            # Save current state
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=self._json_serializer)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to save state: {e}")
            return False
    
    def load_state(self) -> Dict[str, Any]:
        """Load state from disk"""
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
            
        except Exception as e:
            logging.error(f"Failed to load state: {e}")
            # Try backup
            backup_path = self.file_path.with_suffix('.bak')
            if backup_path.exists():
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    pass
            return {}
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for special types"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)


class StateSnapshot:
    """Immutable state snapshot for rollback"""
    
    def __init__(self, state: Dict[str, Any], timestamp: datetime = None):
        self.state = state.copy()
        self.timestamp = timestamp or datetime.now()
        self._hash = hash(json.dumps(state, sort_keys=True, default=str))
    
    def __hash__(self):
        return self._hash
    
    def __eq__(self, other):
        return isinstance(other, StateSnapshot) and self._hash == other._hash


class StateManager(QObject):
    """Centralized state management with validation, persistence, and rollback"""
    
    # Signals
    state_changed = pyqtSignal(str, object, object)  # key, old_value, new_value
    state_validated = pyqtSignal(str, bool, str)     # key, is_valid, message
    state_persisted = pyqtSignal(bool)               # success
    rollback_completed = pyqtSignal(object)          # snapshot
    
    def __init__(self, persistence_file: Optional[Path] = None, auto_save_interval: int = 300):
        super().__init__()
        
        # Core state storage
        self._state: Dict[str, Any] = {}
        self._mutex = QMutex()
        
        # Components
        self.validator = StateValidator()
        self.persistence = StatePersistence(persistence_file) if persistence_file else None
        
        # Change tracking
        self._change_history: List[StateChange] = []
        self._snapshots: List[StateSnapshot] = []
        self._max_history_size = 100
        self._max_snapshots = 20
        
        # Observers and computed states
        self._observers: Dict[str, List[Callable]] = {}
        self._computed_states: Dict[str, Callable] = {}
        
        # Auto-save functionality
        self.auto_save_interval = auto_save_interval
        self._auto_save_timer = QTimer()
        self._auto_save_timer.timeout.connect(self._auto_save)
        if auto_save_interval > 0:
            self._auto_save_timer.start(auto_save_interval * 1000)
        
        # Load initial state
        self._load_initial_state()
        
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        self._mutex.lock()
        try:
            return self._state.get(key, default)
        finally:
            self._mutex.unlock()
    
    def set(self, key: str, value: Any, source: str = "unknown", validate: bool = True) -> bool:
        """Set state value with validation"""
        self._mutex.lock()
        try:
            # Validate if requested
            if validate:
                is_valid, error_msg = self.validator.validate(key, value)
                if not is_valid:
                    self.state_validated.emit(key, False, error_msg)
                    return False
                self.state_validated.emit(key, True, "")
            
            # Get old value
            old_value = self._state.get(key)
            
            # Set new value
            self._state[key] = value
            
            # Record change
            change = StateChange(
                change_type=StateChangeType.UPDATE if key in self._state else StateChangeType.CREATE,
                key=key,
                old_value=old_value,
                new_value=value,
                timestamp=datetime.now(),
                source=source
            )
            self._add_change(change)
            
            # Emit signal
            self.state_changed.emit(key, old_value, value)
            
            # Notify observers
            self._notify_observers(key, old_value, value)
            
            # Update computed states
            self._update_computed_states()
            
            return True
            
        finally:
            self._mutex.unlock()
    
    def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple state values"""
        self._mutex.lock()
        try:
            return {key: self._state.get(key) for key in keys}
        finally:
            self._mutex.unlock()
    
    def set_multiple(self, updates: Dict[str, Any], source: str = "batch", validate: bool = True) -> bool:
        """Set multiple state values in a batch"""
        self._mutex.lock()
        try:
            # Validate all values first
            if validate:
                for key, value in updates.items():
                    is_valid, error_msg = self.validator.validate(key, value)
                    if not is_valid:
                        self.state_validated.emit(key, False, error_msg)
                        return False
            
            # Create snapshot before changes
            self._create_snapshot()
            
            # Apply all changes
            old_values = {}
            for key, value in updates.items():
                old_values[key] = self._state.get(key)
                self._state[key] = value
            
            # Record batch change
            change = StateChange(
                change_type=StateChangeType.BATCH_UPDATE,
                key="batch",
                old_value=old_values,
                new_value=updates,
                timestamp=datetime.now(),
                source=source,
                metadata={'count': len(updates)}
            )
            self._add_change(change)
            
            # Emit signals for all changes
            for key, value in updates.items():
                old_value = old_values[key]
                self.state_changed.emit(key, old_value, value)
                self._notify_observers(key, old_value, value)
            
            # Update computed states
            self._update_computed_states()
            
            return True
            
        finally:
            self._mutex.unlock()
    
    def delete(self, key: str, source: str = "unknown") -> bool:
        """Delete state key"""
        self._mutex.lock()
        try:
            if key not in self._state:
                return False
            
            old_value = self._state[key]
            del self._state[key]
            
            # Record change
            change = StateChange(
                change_type=StateChangeType.DELETE,
                key=key,
                old_value=old_value,
                new_value=None,
                timestamp=datetime.now(),
                source=source
            )
            self._add_change(change)
            
            # Emit signal
            self.state_changed.emit(key, old_value, None)
            
            # Notify observers
            self._notify_observers(key, old_value, None)
            
            return True
            
        finally:
            self._mutex.unlock()
    
    def reset(self, source: str = "reset") -> bool:
        """Reset all state"""
        self._mutex.lock()
        try:
            # Create snapshot
            self._create_snapshot()
            
            old_state = self._state.copy()
            self._state.clear()
            
            # Record change
            change = StateChange(
                change_type=StateChangeType.RESET,
                key="all",
                old_value=old_state,
                new_value={},
                timestamp=datetime.now(),
                source=source
            )
            self._add_change(change)
            
            # Emit signals for all deleted keys
            for key, old_value in old_state.items():
                self.state_changed.emit(key, old_value, None)
                self._notify_observers(key, old_value, None)
            
            return True
            
        finally:
            self._mutex.unlock()
    
    def keys(self) -> Set[str]:
        """Get all state keys"""
        self._mutex.lock()
        try:
            return set(self._state.keys())
        finally:
            self._mutex.unlock()
    
    def has(self, key: str) -> bool:
        """Check if key exists in state"""
        self._mutex.lock()
        try:
            return key in self._state
        finally:
            self._mutex.unlock()
    
    def size(self) -> int:
        """Get state size"""
        self._mutex.lock()
        try:
            return len(self._state)
        finally:
            self._mutex.unlock()
    
    def to_dict(self) -> Dict[str, Any]:
        """Get state as dictionary"""
        self._mutex.lock()
        try:
            return self._state.copy()
        finally:
            self._mutex.unlock()
    
    def add_observer(self, key: str, callback: Callable[[str, Any, Any], None]):
        """Add observer for state key changes"""
        if key not in self._observers:
            self._observers[key] = []
        self._observers[key].append(callback)
    
    def remove_observer(self, key: str, callback: Callable):
        """Remove observer for state key"""
        if key in self._observers:
            try:
                self._observers[key].remove(callback)
                if not self._observers[key]:
                    del self._observers[key]
            except ValueError:
                pass
    
    def add_computed_state(self, key: str, compute_func: Callable[[], Any]):
        """Add computed state that updates automatically"""
        self._computed_states[key] = compute_func
        # Compute initial value
        try:
            initial_value = compute_func()
            self.set(key, initial_value, source="computed", validate=False)
        except Exception as e:
            self.logger.error(f"Error computing initial value for {key}: {e}")
    
    def create_snapshot(self) -> StateSnapshot:
        """Create state snapshot manually"""
        return self._create_snapshot()
    
    def rollback_to_snapshot(self, snapshot: StateSnapshot) -> bool:
        """Rollback state to a snapshot"""
        self._mutex.lock()
        try:
            # Create current snapshot first
            self._create_snapshot()
            
            old_state = self._state.copy()
            self._state = snapshot.state.copy()
            
            # Record rollback
            change = StateChange(
                change_type=StateChangeType.RESET,
                key="rollback",
                old_value=old_state,
                new_value=snapshot.state,
                timestamp=datetime.now(),
                source="rollback",
                metadata={'snapshot_time': snapshot.timestamp.isoformat()}
            )
            self._add_change(change)
            
            # Emit signals for all changes
            all_keys = set(old_state.keys()) | set(snapshot.state.keys())
            for key in all_keys:
                old_value = old_state.get(key)
                new_value = snapshot.state.get(key)
                if old_value != new_value:
                    self.state_changed.emit(key, old_value, new_value)
                    self._notify_observers(key, old_value, new_value)
            
            self.rollback_completed.emit(snapshot)
            return True
            
        finally:
            self._mutex.unlock()
    
    def get_snapshots(self) -> List[StateSnapshot]:
        """Get all snapshots"""
        return self._snapshots.copy()
    
    def get_change_history(self) -> List[StateChange]:
        """Get change history"""
        return self._change_history.copy()
    
    def save_to_disk(self) -> bool:
        """Manually save state to disk"""
        if self.persistence:
            state_dict = self.to_dict()
            success = self.persistence.save_state(state_dict)
            self.state_persisted.emit(success)
            return success
        return False
    
    def _load_initial_state(self):
        """Load initial state from disk"""
        if self.persistence:
            try:
                loaded_state = self.persistence.load_state()
                if loaded_state:
                    self._state.update(loaded_state)
                    self.logger.info(f"Loaded {len(loaded_state)} state entries from disk")
            except Exception as e:
                self.logger.error(f"Failed to load initial state: {e}")
    
    def _auto_save(self):
        """Auto-save state to disk"""
        if self.persistence:
            self.save_to_disk()
    
    def _add_change(self, change: StateChange):
        """Add change to history"""
        self._change_history.append(change)
        if len(self._change_history) > self._max_history_size:
            self._change_history.pop(0)
    
    def _create_snapshot(self) -> StateSnapshot:
        """Create state snapshot"""
        snapshot = StateSnapshot(self._state)
        self._snapshots.append(snapshot)
        if len(self._snapshots) > self._max_snapshots:
            self._snapshots.pop(0)
        return snapshot
    
    def _notify_observers(self, key: str, old_value: Any, new_value: Any):
        """Notify observers of state change"""
        if key in self._observers:
            for callback in self._observers[key]:
                try:
                    callback(key, old_value, new_value)
                except Exception as e:
                    self.logger.error(f"Error notifying observer for {key}: {e}")
    
    def _update_computed_states(self):
        """Update all computed states"""
        for key, compute_func in self._computed_states.items():
            try:
                new_value = compute_func()
                current_value = self._state.get(key)
                if new_value != current_value:
                    self.set(key, new_value, source="computed", validate=False)
            except Exception as e:
                self.logger.error(f"Error updating computed state {key}: {e}")


# Global state manager instance
_global_state_manager: Optional[StateManager] = None


def get_global_state_manager() -> StateManager:
    """Get global state manager instance"""
    global _global_state_manager
    if _global_state_manager is None:
        # Default persistence to user data directory
        app_name = QApplication.applicationName() or "AutomationApp"
        state_file = Path.home() / ".config" / app_name / "state.json"
        _global_state_manager = StateManager(state_file)
    return _global_state_manager


def set_global_state_manager(state_manager: StateManager):
    """Set global state manager instance"""
    global _global_state_manager
    _global_state_manager = state_manager


# Convenience functions for global state
def get_state(key: str, default: Any = None) -> Any:
    """Get state from global manager"""
    return get_global_state_manager().get(key, default)


def set_state(key: str, value: Any, source: str = "global") -> bool:
    """Set state in global manager"""
    return get_global_state_manager().set(key, value, source)


def observe_state(key: str, callback: Callable[[str, Any, Any], None]):
    """Observe state changes in global manager"""
    get_global_state_manager().add_observer(key, callback)
