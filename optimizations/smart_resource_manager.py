#!/usr/bin/env python3
"""
🧠 Smart Resource Manager - Intelligent Memory and Resource Optimization
Automatically manages application resources based on system pressure and usage patterns
"""

import gc
import time
import threading
import weakref
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass
from collections import defaultdict, deque
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from optimizations.app_config import AppConstants
from optimizations.adaptive_config import get_adaptive_config

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class ResourceSnapshot:
    """Resource usage snapshot"""
    timestamp: float
    memory_mb: float
    memory_percent: float
    gc_objects: int
    weak_refs: int
    cache_size: int
    thread_count: int
    open_files: int = 0

@dataclass
class OptimizationAction:
    """Resource optimization action"""
    action_type: str  # "gc", "cache_clear", "weak_ref_cleanup", "memory_compress"
    timestamp: float
    memory_freed_mb: float = 0.0
    objects_cleaned: int = 0
    success: bool = True
    duration_ms: float = 0.0

class SmartResourceManager(QObject):
    """🧠 Intelligent resource management system"""
    
    # Signals
    resource_optimized = pyqtSignal(OptimizationAction)
    memory_pressure_critical = pyqtSignal(float)  # Memory percentage
    resource_leak_detected = pyqtSignal(str, dict)  # Resource type, details
    
    def __init__(self):
        super().__init__()
        self.adaptive_config = get_adaptive_config()
        
        # Resource tracking
        self._resource_snapshots = deque(maxlen=500)
        self._optimization_history = deque(maxlen=200)
        self._weak_refs: Set[weakref.ref] = set()
        self._managed_caches: Dict[str, Any] = {}
        self._memory_pools: Dict[str, List[Any]] = defaultdict(list)
        
        # Leak detection
        self._object_growth_tracking = defaultdict(deque)
        self._growth_threshold = 1000  # Objects
        self._growth_window = 60  # Seconds
        
        # Optimization thresholds
        self._memory_pressure_thresholds = {
            "low": 0.6,      # 60%
            "medium": 0.75,  # 75%
            "high": 0.85,    # 85%
            "critical": 0.95 # 95%
        }
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._stop_event = threading.Event()
        self._enabled = False
        
        # Qt timers
        self._gc_timer = QTimer()
        self._gc_timer.timeout.connect(self._scheduled_gc)
        
        self._leak_check_timer = QTimer()
        self._leak_check_timer.timeout.connect(self._check_for_leaks)
    
    def start_management(self):
        """Start intelligent resource management"""
        if self._enabled:
            return
            
        self._enabled = True
        self._stop_event.clear()
        
        # Start monitoring thread
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitoring_thread.start()
        
        # Start periodic GC (every 30 seconds)
        self._gc_timer.start(30000)
        
        # Start leak detection (every 2 minutes)
        self._leak_check_timer.start(120000)
        
        print("🧠 Smart Resource Manager started")
    
    def stop_management(self):
        """Stop resource management"""
        if not self._enabled:
            return
            
        self._enabled = False
        self._stop_event.set()
        
        # Stop timers
        self._gc_timer.stop()
        self._leak_check_timer.stop()
        
        # Wait for monitoring thread
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=2.0)
            
        print("🧠 Smart Resource Manager stopped")
    
    def _monitoring_loop(self):
        """Resource monitoring loop"""
        while not self._stop_event.wait(5.0):  # Check every 5 seconds
            try:
                snapshot = self._collect_resource_snapshot()
                
                with self._lock:
                    self._resource_snapshots.append(snapshot)
                    
                    # Check for optimization needs
                    self._check_optimization_needs(snapshot)
                    
                    # Track object growth for leak detection
                    self._track_object_growth(snapshot)
                
            except Exception as e:
                print(f"❌ Error in resource monitoring: {e}")
    
    def _collect_resource_snapshot(self) -> ResourceSnapshot:
        """Collect current resource usage snapshot"""
        timestamp = time.time()
        
        # Memory information
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                system_memory = psutil.virtual_memory()
                memory_percent = system_memory.percent
                thread_count = process.num_threads()
                
                try:
                    open_files = len(process.open_files())
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    open_files = 0
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                memory_mb = 0.0
                memory_percent = 0.0
                thread_count = 1
                open_files = 0
        else:
            memory_mb = 0.0
            memory_percent = 0.0
            thread_count = 1
            open_files = 0
        
        # GC information
        gc_objects = len(gc.get_objects())
        
        # Weak references count
        weak_refs = len(self._weak_refs)
        
        # Cache sizes
        cache_size = sum(len(cache) if hasattr(cache, '__len__') else 0 
                        for cache in self._managed_caches.values())
        
        return ResourceSnapshot(
            timestamp=timestamp,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            gc_objects=gc_objects,
            weak_refs=weak_refs,
            cache_size=cache_size,
            thread_count=thread_count,
            open_files=open_files
        )
    
    def _check_optimization_needs(self, snapshot: ResourceSnapshot):
        """Check if resource optimization is needed"""
        memory_pressure = self._get_memory_pressure_level(snapshot.memory_percent)
        
        # Critical memory pressure - immediate action
        if memory_pressure == "critical":
            self._perform_emergency_cleanup(snapshot)
            self.memory_pressure_critical.emit(snapshot.memory_percent)
            
        # High memory pressure - aggressive cleanup
        elif memory_pressure == "high":
            self._perform_aggressive_cleanup(snapshot)
            
        # Medium memory pressure - standard cleanup
        elif memory_pressure == "medium":
            self._perform_standard_cleanup(snapshot)
    
    def _get_memory_pressure_level(self, memory_percent: float) -> str:
        """Determine memory pressure level"""
        if memory_percent >= self._memory_pressure_thresholds["critical"]:
            return "critical"
        elif memory_percent >= self._memory_pressure_thresholds["high"]:
            return "high"
        elif memory_percent >= self._memory_pressure_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _perform_emergency_cleanup(self, snapshot: ResourceSnapshot):
        """Perform emergency resource cleanup"""
        print(f"🚨 Emergency cleanup triggered (Memory: {snapshot.memory_percent:.1f}%)")
        
        actions = []
        
        # 1. Force garbage collection
        actions.append(self._force_garbage_collection())
        
        # 2. Clear all managed caches
        actions.append(self._clear_all_caches())
        
        # 3. Clean weak references
        actions.append(self._cleanup_weak_references())
        
        # 4. Clear memory pools
        actions.append(self._clear_memory_pools())
        
        # Emit all actions
        for action in actions:
            if action:
                self.resource_optimized.emit(action)
    
    def _perform_aggressive_cleanup(self, snapshot: ResourceSnapshot):
        """Perform aggressive resource cleanup"""
        print(f"⚡ Aggressive cleanup triggered (Memory: {snapshot.memory_percent:.1f}%)")
        
        actions = []
        
        # 1. Garbage collection
        actions.append(self._force_garbage_collection())
        
        # 2. Clear large caches
        actions.append(self._clear_large_caches())
        
        # 3. Clean weak references
        actions.append(self._cleanup_weak_references())
        
        # Emit actions
        for action in actions:
            if action:
                self.resource_optimized.emit(action)
    
    def _perform_standard_cleanup(self, snapshot: ResourceSnapshot):
        """Perform standard resource cleanup"""
        print(f"🧹 Standard cleanup triggered (Memory: {snapshot.memory_percent:.1f}%)")
        
        # Only clean expired weak references
        action = self._cleanup_weak_references()
        if action:
            self.resource_optimized.emit(action)
    
    def _force_garbage_collection(self) -> Optional[OptimizationAction]:
        """Force garbage collection and measure impact"""
        start_time = time.time()
        
        try:
            # Collect memory info before GC
            if PSUTIL_AVAILABLE:
                try:
                    process = psutil.Process()
                    memory_before = process.memory_info().rss / (1024 * 1024)
                except:
                    memory_before = 0.0
            else:
                memory_before = 0.0
            
            objects_before = len(gc.get_objects())
            
            # Force GC
            collected = gc.collect()
            
            # Collect memory info after GC
            if PSUTIL_AVAILABLE:
                try:
                    process = psutil.Process()
                    memory_after = process.memory_info().rss / (1024 * 1024)
                except:
                    memory_after = memory_before
            else:
                memory_after = memory_before
            
            objects_after = len(gc.get_objects())
            
            duration_ms = (time.time() - start_time) * 1000
            memory_freed = max(0, memory_before - memory_after)
            objects_cleaned = max(0, objects_before - objects_after)
            
            action = OptimizationAction(
                action_type="gc",
                timestamp=time.time(),
                memory_freed_mb=memory_freed,
                objects_cleaned=objects_cleaned,
                success=True,
                duration_ms=duration_ms
            )
            
            with self._lock:
                self._optimization_history.append(action)
            
            print(f"🗑️ GC: {collected} cycles, {memory_freed:.1f}MB freed, {objects_cleaned} objects cleaned")
            return action
            
        except Exception as e:
            print(f"❌ GC failed: {e}")
            return OptimizationAction(
                action_type="gc",
                timestamp=time.time(),
                success=False,
                duration_ms=(time.time() - start_time) * 1000
            )
    
    def _clear_all_caches(self) -> Optional[OptimizationAction]:
        """Clear all managed caches"""
        start_time = time.time()
        objects_cleaned = 0
        
        try:
            with self._lock:
                for cache_name, cache in self._managed_caches.items():
                    if hasattr(cache, 'clear'):
                        size_before = len(cache) if hasattr(cache, '__len__') else 0
                        cache.clear()
                        objects_cleaned += size_before
                        print(f"🧹 Cleared cache '{cache_name}': {size_before} items")
            
            return OptimizationAction(
                action_type="cache_clear",
                timestamp=time.time(),
                objects_cleaned=objects_cleaned,
                success=True,
                duration_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            print(f"❌ Cache clear failed: {e}")
            return None
    
    def _clear_large_caches(self) -> Optional[OptimizationAction]:
        """Clear only large caches"""
        start_time = time.time()
        objects_cleaned = 0
        threshold = 100  # Clear caches with more than 100 items
        
        try:
            with self._lock:
                for cache_name, cache in self._managed_caches.items():
                    if hasattr(cache, 'clear') and hasattr(cache, '__len__'):
                        size = len(cache)
                        if size > threshold:
                            cache.clear()
                            objects_cleaned += size
                            print(f"🧹 Cleared large cache '{cache_name}': {size} items")
            
            return OptimizationAction(
                action_type="cache_clear",
                timestamp=time.time(),
                objects_cleaned=objects_cleaned,
                success=True,
                duration_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            print(f"❌ Large cache clear failed: {e}")
            return None
    
    def _cleanup_weak_references(self) -> Optional[OptimizationAction]:
        """Clean up dead weak references"""
        start_time = time.time()
        
        try:
            with self._lock:
                dead_refs = set()
                for ref in self._weak_refs:
                    if ref() is None:  # Dead reference
                        dead_refs.add(ref)
                
                self._weak_refs -= dead_refs
                objects_cleaned = len(dead_refs)
            
            if objects_cleaned > 0:
                print(f"🧹 Cleaned {objects_cleaned} dead weak references")
                
                return OptimizationAction(
                    action_type="weak_ref_cleanup",
                    timestamp=time.time(),
                    objects_cleaned=objects_cleaned,
                    success=True,
                    duration_ms=(time.time() - start_time) * 1000
                )
            
            return None
            
        except Exception as e:
            print(f"❌ Weak reference cleanup failed: {e}")
            return None
    
    def _clear_memory_pools(self) -> Optional[OptimizationAction]:
        """Clear memory pools"""
        start_time = time.time()
        objects_cleaned = 0
        
        try:
            with self._lock:
                for pool_name, pool in self._memory_pools.items():
                    size = len(pool)
                    pool.clear()
                    objects_cleaned += size
                    print(f"🧹 Cleared memory pool '{pool_name}': {size} objects")
            
            return OptimizationAction(
                action_type="memory_pool_clear",
                timestamp=time.time(),
                objects_cleaned=objects_cleaned,
                success=True,
                duration_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            print(f"❌ Memory pool clear failed: {e}")
            return None
    
    def _scheduled_gc(self):
        """Scheduled garbage collection"""
        if not self._enabled:
            return
            
        action = self._force_garbage_collection()
        if action:
            self.resource_optimized.emit(action)
    
    def _track_object_growth(self, snapshot: ResourceSnapshot):
        """Track object growth for leak detection"""
        with self._lock:
            current_time = snapshot.timestamp
            
            # Track GC objects growth
            self._object_growth_tracking['gc_objects'].append((current_time, snapshot.gc_objects))
            
            # Track cache growth
            self._object_growth_tracking['cache_size'].append((current_time, snapshot.cache_size))
            
            # Clean old tracking data
            cutoff_time = current_time - self._growth_window
            for resource_type in self._object_growth_tracking:
                while (self._object_growth_tracking[resource_type] and 
                       self._object_growth_tracking[resource_type][0][0] < cutoff_time):
                    self._object_growth_tracking[resource_type].popleft()
    
    def _check_for_leaks(self):
        """Check for potential resource leaks"""
        if not self._enabled:
            return
            
        current_time = time.time()
        
        with self._lock:
            for resource_type, tracking_data in self._object_growth_tracking.items():
                if len(tracking_data) < 2:
                    continue
                
                # Calculate growth over the tracking window
                oldest_count = tracking_data[0][1]
                newest_count = tracking_data[-1][1]
                growth = newest_count - oldest_count
                
                # Check if growth exceeds threshold
                if growth > self._growth_threshold:
                    leak_details = {
                        "resource_type": resource_type,
                        "growth": growth,
                        "oldest_count": oldest_count,
                        "newest_count": newest_count,
                        "window_seconds": self._growth_window,
                        "growth_rate": growth / self._growth_window
                    }
                    
                    print(f"🚨 Potential leak detected: {resource_type} grew by {growth} objects")
                    self.resource_leak_detected.emit(resource_type, leak_details)
    
    # Public API for resource management
    
    def register_cache(self, name: str, cache: Any):
        """Register a cache for management"""
        with self._lock:
            self._managed_caches[name] = cache
        print(f"📋 Registered cache: {name}")
    
    def unregister_cache(self, name: str):
        """Unregister a cache"""
        with self._lock:
            if name in self._managed_caches:
                del self._managed_caches[name]
                print(f"📋 Unregistered cache: {name}")
    
    def add_weak_reference(self, obj: Any) -> weakref.ref:
        """Add a weak reference for tracking"""
        ref = weakref.ref(obj)
        with self._lock:
            self._weak_refs.add(ref)
        return ref
    
    def get_memory_pool(self, pool_name: str) -> List[Any]:
        """Get or create a memory pool"""
        with self._lock:
            return self._memory_pools[pool_name]
    
    def clear_memory_pool(self, pool_name: str) -> int:
        """Clear a specific memory pool"""
        with self._lock:
            if pool_name in self._memory_pools:
                size = len(self._memory_pools[pool_name])
                self._memory_pools[pool_name].clear()
                return size
        return 0
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get comprehensive resource statistics"""
        with self._lock:
            latest_snapshot = self._resource_snapshots[-1] if self._resource_snapshots else None
            
            return {
                "current": {
                    "memory_mb": latest_snapshot.memory_mb if latest_snapshot else 0,
                    "memory_percent": latest_snapshot.memory_percent if latest_snapshot else 0,
                    "gc_objects": latest_snapshot.gc_objects if latest_snapshot else 0,
                    "weak_refs": len(self._weak_refs),
                    "managed_caches": len(self._managed_caches),
                    "memory_pools": len(self._memory_pools),
                },
                "management": {
                    "enabled": self._enabled,
                    "optimizations_count": len(self._optimization_history),
                    "memory_pressure_level": self._get_memory_pressure_level(
                        latest_snapshot.memory_percent if latest_snapshot else 0
                    ),
                },
                "thresholds": self._memory_pressure_thresholds,
                "recent_optimizations": [
                    {
                        "type": action.action_type,
                        "timestamp": action.timestamp,
                        "memory_freed_mb": action.memory_freed_mb,
                        "objects_cleaned": action.objects_cleaned,
                        "success": action.success
                    }
                    for action in list(self._optimization_history)[-10:]  # Last 10 optimizations
                ]
            }

# Global smart resource manager instance
smart_resource_manager = SmartResourceManager()

def get_smart_resource_manager() -> SmartResourceManager:
    """Get the global smart resource manager instance"""
    return smart_resource_manager