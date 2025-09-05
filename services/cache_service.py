"""
Services Layer - Caching and State Management
=============================================

Implements instance list caching with incremental refresh and diff detection.
"""

import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from cli.enhanced_backend import get_enhanced_backend


class InstanceStatus(Enum):
    """Instance status enum for lightweight state tracking"""
    STOPPED = "stopped"
    STARTING = "starting" 
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class InstanceInfo:
    """Lightweight instance info dataclass"""
    index: int
    name: str = ""
    status: InstanceStatus = InstanceStatus.UNKNOWN
    adb_port: int = 0
    disk_usage: str = "0MB"
    disk_size_bytes: int = 0
    last_updated: float = field(default_factory=time.time)
    
    def __eq__(self, other):
        """Compare by index for update detection"""
        if not isinstance(other, InstanceInfo):
            return False
        return self.index == other.index
        
    def has_changed(self, other) -> bool:
        """Check if instance data has changed (excluding last_updated)"""
        if not isinstance(other, InstanceInfo):
            return True
            
        return (self.name != other.name or 
                self.status != other.status or
                self.adb_port != other.adb_port or
                self.disk_usage != other.disk_usage)


class InstanceCache(QObject):
    """Cache manager for instance list with incremental updates"""
    
    # Signals for UI updates
    instances_updated = pyqtSignal(dict)  # Full instance data
    instance_changed = pyqtSignal(int, InstanceInfo)  # Single instance update
    cache_stats_updated = pyqtSignal(dict)  # Cache statistics
    
    def __init__(self, refresh_interval: int = 3):
        super().__init__()
        self.refresh_interval = refresh_interval  # seconds
        self.cached_instances: Dict[int, InstanceInfo] = {}
        self.last_full_refresh = 0
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._perform_refresh)
        
        self.backend = get_enhanced_backend()
        self.backend.instance_list_updated.connect(self._on_instance_list_updated)
        
        # Statistics
        self.stats = {
            "total_refreshes": 0,
            "full_refreshes": 0,
            "incremental_refreshes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "last_refresh_time": 0,
            "avg_refresh_time": 0
        }
        
    def start_auto_refresh(self):
        """Start automatic refresh timer"""
        if not self.refresh_timer.isActive():
            self.refresh_timer.start(self.refresh_interval * 1000)
            self._perform_initial_refresh()
            
    def stop_auto_refresh(self):
        """Stop automatic refresh timer"""
        self.refresh_timer.stop()
        
    def manual_refresh(self):
        """Trigger manual refresh"""
        self._perform_refresh()
        
    def get_cached_instance(self, index: int) -> Optional[InstanceInfo]:
        """Get cached instance info"""
        if index in self.cached_instances:
            self.stats["cache_hits"] += 1
            return self.cached_instances[index]
        else:
            self.stats["cache_misses"] += 1
            return None
            
    def get_all_cached_instances(self) -> Dict[int, InstanceInfo]:
        """Get all cached instances"""
        return self.cached_instances.copy()
        
    def update_instance_status(self, index: int, status: InstanceStatus):
        """Update single instance status (optimistic update)"""
        if index in self.cached_instances:
            old_info = self.cached_instances[index]
            new_info = InstanceInfo(
                index=old_info.index,
                name=old_info.name,
                status=status,
                adb_port=old_info.adb_port,
                disk_usage=old_info.disk_usage,
                disk_size_bytes=old_info.disk_size_bytes,
                last_updated=time.time()
            )
            
            if old_info.has_changed(new_info):
                self.cached_instances[index] = new_info
                self.instance_changed.emit(index, new_info)
                
    def _perform_initial_refresh(self):
        """Perform initial full refresh"""
        self.stats["total_refreshes"] += 1
        self.stats["full_refreshes"] += 1
        start_time = time.time()
        
        self.backend.get_instance_list_async()
        
        self.stats["last_refresh_time"] = time.time() - start_time
        self._update_avg_refresh_time()
        
    def _perform_refresh(self):
        """Perform incremental or full refresh based on timing"""
        current_time = time.time()
        
        # Perform full refresh every 30 seconds, incremental otherwise
        if current_time - self.last_full_refresh > 30:
            self._perform_full_refresh()
        else:
            self._perform_incremental_refresh()
            
    def _perform_full_refresh(self):
        """Perform full refresh of all instances"""
        self.stats["total_refreshes"] += 1
        self.stats["full_refreshes"] += 1
        self.last_full_refresh = time.time()
        start_time = time.time()
        
        self.backend.get_instance_list_async()
        
        self.stats["last_refresh_time"] = time.time() - start_time
        self._update_avg_refresh_time()
        
    def _perform_incremental_refresh(self):
        """Perform incremental refresh of changed instances only"""
        self.stats["total_refreshes"] += 1
        self.stats["incremental_refreshes"] += 1
        start_time = time.time()
        
        # For incremental refresh, we still need to get the full list
        # but we'll do differential update in _on_instance_list_updated
        self.backend.get_instance_list_async()
        
        self.stats["last_refresh_time"] = time.time() - start_time
        self._update_avg_refresh_time()
        
    def _on_instance_list_updated(self, data: dict):
        """Handle instance list update from backend"""
        if not data.get("success", False):
            return
            
        raw_data = data.get("data", {})
        if not isinstance(raw_data, dict):
            return
            
        # Convert raw data to InstanceInfo objects
        new_instances = {}
        changed_instances = {}
        
        for index_str, info_dict in raw_data.items():
            try:
                index = int(index_str)
                
                # Map status string to enum
                status_map = {
                    "running": InstanceStatus.RUNNING,
                    "stopped": InstanceStatus.STOPPED,
                    "starting": InstanceStatus.STARTING,
                    "stopping": InstanceStatus.STOPPING,
                    "error": InstanceStatus.ERROR
                }
                
                status_str = info_dict.get("status", "unknown").lower()
                status = status_map.get(status_str, InstanceStatus.UNKNOWN)
                
                new_info = InstanceInfo(
                    index=index,
                    name=info_dict.get("name", f"VM {index}"),
                    status=status,
                    adb_port=info_dict.get("adb_port", 0),
                    disk_usage=info_dict.get("disk_usage", "0MB"),
                    disk_size_bytes=info_dict.get("disk_size_bytes", 0),
                    last_updated=time.time()
                )
                
                new_instances[index] = new_info
                
                # Check if this instance changed
                if index in self.cached_instances:
                    old_info = self.cached_instances[index]
                    if old_info.has_changed(new_info):
                        changed_instances[index] = new_info
                else:
                    # New instance
                    changed_instances[index] = new_info
                    
            except (ValueError, KeyError) as e:
                # Skip invalid instance data
                continue
                
        # Update cache
        self.cached_instances = new_instances
        
        # Emit signals for changed instances
        for index, instance_info in changed_instances.items():
            self.instance_changed.emit(index, instance_info)
            
        # Emit full update
        self.instances_updated.emit(new_instances)
        
        # Update cache stats
        self.cache_stats_updated.emit(self.stats.copy())
        
    def _update_avg_refresh_time(self):
        """Update average refresh time"""
        if self.stats["total_refreshes"] > 0:
            # Simple moving average
            current_avg = self.stats["avg_refresh_time"]
            new_time = self.stats["last_refresh_time"]
            count = self.stats["total_refreshes"]
            
            self.stats["avg_refresh_time"] = (current_avg * (count - 1) + new_time) / count


class ServicesManager(QObject):
    """Central services manager"""
    
    def __init__(self):
        super().__init__()
        self.instance_cache = InstanceCache()
        self.backend = get_enhanced_backend()
        
    def start_services(self):
        """Start all services"""
        self.instance_cache.start_auto_refresh()
        
    def stop_services(self):
        """Stop all services"""
        self.instance_cache.stop_auto_refresh()
        
    def get_instance_cache(self) -> InstanceCache:
        """Get instance cache service"""
        return self.instance_cache
        
    def get_backend(self):
        """Get backend service"""
        return self.backend


# Global services manager
_global_services_manager = None

def get_services_manager() -> ServicesManager:
    """Get global services manager"""
    global _global_services_manager
    if _global_services_manager is None:
        _global_services_manager = ServicesManager()
    return _global_services_manager