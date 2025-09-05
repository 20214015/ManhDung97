"""
Instance Manager
================

Handles all instance-related operations extracted from main_window.py.
Provides a clean separation of instance management logic from UI code.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QInputDialog

from backend import MumuManager
from workers import GenericWorker
from core import get_event_manager, get_state_manager, EventTypes, emit_event


class InstanceManager(QObject):
    """
    Manages all instance-related operations including:
    - Creating, cloning, deleting instances
    - Starting, stopping, restarting instances
    - Instance data refreshing and updating
    - Instance selection management
    """
    
    # Signals for UI updates
    instance_created = pyqtSignal(dict)
    instance_deleted = pyqtSignal(int)
    instance_updated = pyqtSignal(int, dict)
    instances_refreshed = pyqtSignal(list)
    selection_changed = pyqtSignal(list)
    operation_started = pyqtSignal(str)
    operation_completed = pyqtSignal(str, bool, str)
    
    def __init__(self, mumu_manager: MumuManager, parent=None):
        super().__init__(parent)
        self.mumu_manager = mumu_manager
        self.logger = logging.getLogger('InstanceManager')
        
        # State management
        self.state_manager = get_state_manager()
        self.event_manager = get_event_manager()
        
        # Instance cache
        self._instances_cache: List[Dict[str, Any]] = []
        self._failed_indices: set = set()
        
        # Worker management
        self.current_worker: Optional[GenericWorker] = None
        self.refresh_worker: Optional[GenericWorker] = None
        
        # Setup event subscriptions
        self._setup_event_subscriptions()
        
    def _setup_event_subscriptions(self):
        """Setup event subscriptions for state changes"""
        self.event_manager.subscribe(EventTypes.INSTANCES_UPDATED, self._on_instances_updated_event)
        self.event_manager.subscribe(EventTypes.INSTANCE_SELECTED, self._on_instance_selected_event)
        
    def _on_instances_updated_event(self, data: Dict[str, Any]):
        """Handle instances updated event"""
        instances = data.get('instances', [])
        self._instances_cache = instances
        self.instances_refreshed.emit(instances)
        
    def _on_instance_selected_event(self, data: Dict[str, Any]):
        """Handle instance selection event"""
        indices = data.get('indices', [])
        self.selection_changed.emit(indices)
        
    # Instance Creation and Management
    def create_instance(self, count: int = 1) -> Tuple[bool, str]:
        """
        Create new instances.
        
        Args:
            count: Number of instances to create
            
        Returns:
            Tuple of (success, message)
        """
        try:
            self.operation_started.emit(f"Creating {count} instance(s)")
            
            success, message = self.mumu_manager.create_instance(count)
            
            if success:
                emit_event(EventTypes.INSTANCE_CREATED, {'count': count})
                self.operation_completed.emit("create", True, message)
                # Refresh instances after creation
                self.refresh_instances()
            else:
                self.operation_completed.emit("create", False, message)
                
            return success, message
            
        except Exception as e:
            error_msg = f"Failed to create instances: {e}"
            self.logger.error(error_msg)
            self.operation_completed.emit("create", False, error_msg)
            return False, error_msg
            
    def clone_instance(self, source_index: int, count: int = 1) -> Tuple[bool, str]:
        """
        Clone an existing instance.
        
        Args:
            source_index: Index of instance to clone
            count: Number of clones to create
            
        Returns:
            Tuple of (success, message)
        """
        try:
            self.operation_started.emit(f"Cloning instance {source_index} ({count} clone(s))")
            
            success, message = self.mumu_manager.clone_instance(source_index, count)
            
            if success:
                emit_event(EventTypes.INSTANCE_CLONED, {
                    'source_index': source_index,
                    'count': count
                })
                self.operation_completed.emit("clone", True, message)
                # Refresh instances after cloning
                self.refresh_instances()
            else:
                self.operation_completed.emit("clone", False, message)
                
            return success, message
            
        except Exception as e:
            error_msg = f"Failed to clone instance: {e}"
            self.logger.error(error_msg)
            self.operation_completed.emit("clone", False, error_msg)
            return False, error_msg
            
    def delete_instances(self, indices: List[int]) -> Tuple[bool, str]:
        """
        Delete selected instances.
        
        Args:
            indices: List of instance indices to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not indices:
                return False, "No instances selected for deletion"
                
            # Confirm deletion
            count = len(indices)
            indices_str = ", ".join(map(str, indices))
            
            self.operation_started.emit(f"Deleting {count} instance(s): {indices_str}")
            
            success_count = 0
            failed_indices = []
            
            for index in indices:
                try:
                    success, message = self.mumu_manager.delete_instance(index)
                    if success:
                        success_count += 1
                        emit_event(EventTypes.INSTANCE_DELETED, {'index': index})
                    else:
                        failed_indices.append(index)
                        self.logger.warning(f"Failed to delete instance {index}: {message}")
                except Exception as e:
                    failed_indices.append(index)
                    self.logger.error(f"Error deleting instance {index}: {e}")
                    
            # Generate result message
            if success_count == count:
                result_msg = f"Successfully deleted {success_count} instance(s)"
                self.operation_completed.emit("delete", True, result_msg)
                # Refresh instances after deletion
                self.refresh_instances()
                return True, result_msg
            elif success_count > 0:
                result_msg = f"Deleted {success_count}/{count} instances. Failed: {failed_indices}"
                self.operation_completed.emit("delete", False, result_msg)
                # Refresh instances after partial deletion
                self.refresh_instances()
                return False, result_msg
            else:
                result_msg = f"Failed to delete any instances: {failed_indices}"
                self.operation_completed.emit("delete", False, result_msg)
                return False, result_msg
                
        except Exception as e:
            error_msg = f"Error during instance deletion: {e}"
            self.logger.error(error_msg)
            self.operation_completed.emit("delete", False, error_msg)
            return False, error_msg
            
    # Instance Control Operations
    def start_instances(self, indices: List[int]) -> Tuple[bool, str]:
        """Start selected instances"""
        return self._control_instances(indices, "start")
        
    def stop_instances(self, indices: List[int]) -> Tuple[bool, str]:
        """Stop selected instances"""
        return self._control_instances(indices, "stop")
        
    def restart_instances(self, indices: List[int]) -> Tuple[bool, str]:
        """Restart selected instances"""
        return self._control_instances(indices, "restart")
        
    def _control_instances(self, indices: List[int], action: str) -> Tuple[bool, str]:
        """
        Control instances with the specified action.
        
        Args:
            indices: List of instance indices
            action: Action to perform ('start', 'stop', 'restart')
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not indices:
                return False, f"No instances selected for {action}"
                
            self.operation_started.emit(f"{action.capitalize()}ing {len(indices)} instance(s)")
            
            success_count = 0
            failed_indices = []
            
            for index in indices:
                try:
                    if action == "start":
                        success, message = self.mumu_manager.start_instance(index)
                    elif action == "stop":
                        success, message = self.mumu_manager.stop_instance(index)
                    elif action == "restart":
                        success, message = self.mumu_manager.restart_instance(index)
                    else:
                        continue
                        
                    if success:
                        success_count += 1
                        if action == "start":
                            emit_event(EventTypes.INSTANCE_STARTED, {'index': index})
                        elif action == "stop":
                            emit_event(EventTypes.INSTANCE_STOPPED, {'index': index})
                    else:
                        failed_indices.append(index)
                        self.logger.warning(f"Failed to {action} instance {index}: {message}")
                        
                except Exception as e:
                    failed_indices.append(index)
                    self.logger.error(f"Error {action}ing instance {index}: {e}")
                    
            # Generate result message
            total_count = len(indices)
            if success_count == total_count:
                result_msg = f"Successfully {action}ed {success_count} instance(s)"
                self.operation_completed.emit(action, True, result_msg)
                return True, result_msg
            elif success_count > 0:
                result_msg = f"{action.capitalize()}ed {success_count}/{total_count} instances. Failed: {failed_indices}"
                self.operation_completed.emit(action, False, result_msg)
                return False, result_msg
            else:
                result_msg = f"Failed to {action} any instances: {failed_indices}"
                self.operation_completed.emit(action, False, result_msg)
                return False, result_msg
                
        except Exception as e:
            error_msg = f"Error during instance {action}: {e}"
            self.logger.error(error_msg)
            self.operation_completed.emit(action, False, error_msg)
            return False, error_msg
            
    # Instance Data Management
    def refresh_instances(self, silent: bool = False):
        """
        Refresh instance data from backend.
        
        Args:
            silent: Whether to perform silent refresh without UI updates
        """
        try:
            self.operation_started.emit("Refreshing instances")
            
            def refresh_task(worker: GenericWorker, manager: MumuManager, params: dict) -> dict:
                """Background task for fetching instance data"""
                if not silent:
                    worker.started.emit("Fetching instance data...")
                
                success, data = manager.get_all_info()
                
                if not silent:
                    worker.progress.emit(100)
                    
                return {"success": success, "data": data}
                
            # Create worker
            self.refresh_worker = GenericWorker(refresh_task, self.mumu_manager, {})
            
            # Connect signals
            if silent:
                self.refresh_worker.finished.connect(
                    lambda result: self._on_instances_refreshed(result, silent=True)
                )
            else:
                self.refresh_worker.finished.connect(
                    lambda result: self._on_instances_refreshed(result, silent=False)
                )
                
            self.refresh_worker.error.connect(
                lambda error: self._on_refresh_error(error, silent)
            )
            
            # Start worker
            self.refresh_worker.start()
            
        except Exception as e:
            error_msg = f"Failed to start instance refresh: {e}"
            self.logger.error(error_msg)
            self.operation_completed.emit("refresh", False, error_msg)
            
    def _on_instances_refreshed(self, result: dict, silent: bool = False):
        """Handle instances refresh completion"""
        try:
            success = result.get("success", False)
            data = result.get("data", [])
            
            if success:
                # Update state
                self.state_manager.update_instances(data)
                self._instances_cache = data
                self._failed_indices.clear()
                
                if not silent:
                    self.operation_completed.emit("refresh", True, f"Refreshed {len(data)} instances")
                    
                self.instances_refreshed.emit(data)
                
            else:
                error_msg = "Failed to refresh instances"
                if not silent:
                    self.operation_completed.emit("refresh", False, error_msg)
                    
        except Exception as e:
            error_msg = f"Error processing refresh result: {e}"
            self.logger.error(error_msg)
            if not silent:
                self.operation_completed.emit("refresh", False, error_msg)
                
    def _on_refresh_error(self, error: str, silent: bool = False):
        """Handle refresh error"""
        self.logger.error(f"Instance refresh error: {error}")
        if not silent:
            self.operation_completed.emit("refresh", False, f"Refresh failed: {error}")
            
    # Instance Selection Management
    def set_selected_instances(self, indices: List[int]):
        """Update selected instance indices"""
        self.state_manager.set_selected_instances(indices)
        
    def get_selected_instances(self) -> List[int]:
        """Get currently selected instance indices"""
        return self.state_manager.get_selected_instances()
        
    def add_to_selection(self, index: int):
        """Add instance to selection"""
        current_selection = self.get_selected_instances()
        if index not in current_selection:
            current_selection.append(index)
            self.set_selected_instances(current_selection)
            
    def remove_from_selection(self, index: int):
        """Remove instance from selection"""
        current_selection = self.get_selected_instances()
        if index in current_selection:
            current_selection.remove(index)
            self.set_selected_instances(current_selection)
            
    def clear_selection(self):
        """Clear all selected instances"""
        self.set_selected_instances([])
        
    # Utility Methods
    def get_instances(self) -> List[Dict[str, Any]]:
        """Get current instances list"""
        return self._instances_cache.copy()
        
    def get_instance(self, index: int) -> Optional[Dict[str, Any]]:
        """Get instance by index"""
        if 0 <= index < len(self._instances_cache):
            return self._instances_cache[index]
        return None
        
    def get_instance_count(self) -> int:
        """Get total number of instances"""
        return len(self._instances_cache)
        
    def is_instance_running(self, index: int) -> bool:
        """Check if instance is running"""
        instance = self.get_instance(index)
        if instance:
            return instance.get('status', '').lower() == 'running'
        return False
        
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop any running workers
            if self.current_worker and self.current_worker.isRunning():
                self.current_worker.terminate()
                self.current_worker.wait(3000)
                
            if self.refresh_worker and self.refresh_worker.isRunning():
                self.refresh_worker.terminate()
                self.refresh_worker.wait(3000)
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")