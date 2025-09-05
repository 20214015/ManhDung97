#!/usr/bin/env python3
"""
🧠 MEMORY OPTIMIZER - Phase 4.4
Advanced memory management for large datasets (516+ instances)
"""

import gc
import weakref
from typing import Dict, Any, Optional
from collections import deque
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
import psutil
import os

class MemoryOptimizer(QObject):
    """🧠 Advanced memory optimizer for large datasets"""

    memory_optimized = pyqtSignal(str, int)  # operation, bytes_saved
    memory_warning = pyqtSignal(str)  # warning_message
    memory_critical = pyqtSignal(str)  # critical_message

    def __init__(self, parent: Optional[QObject] = None, max_memory_mb: int = 512):
        super().__init__(parent)
        self.max_memory_mb = max_memory_mb
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._monitor_memory)
        self.monitor_timer.setInterval(30000)  # Check every 30 seconds

        self.instance_cache: Dict[int, weakref.ref] = {}
        self.table_rows_cache: deque[Dict[str, Any]] = deque(maxlen=100)  # Cache last 100 table operations
        self.compression_enabled = True

        # Memory thresholds
        self.warning_threshold = 0.7  # 70% of max
        self.critical_threshold = 0.85  # 85% of max

    def start_monitoring(self):
        """Start memory monitoring"""
        self.monitor_timer.start()
        print("🧠 Memory optimizer started")

    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitor_timer.stop()

    def _monitor_memory(self):
        """Monitor memory usage and trigger optimizations"""
        try:
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_percent = memory_mb / self.max_memory_mb

            if memory_percent > self.critical_threshold:
                self._perform_critical_optimization()
                self.memory_critical.emit(f"Critical memory usage: {memory_mb:.1f}MB")
            elif memory_percent > self.warning_threshold:
                self._perform_warning_optimization()
        except Exception as e:
            print(f"Memory monitoring error: {e}")

    def _perform_warning_optimization(self):
        """Perform warning-level memory optimization"""
        bytes_saved = 0

        # Clear unused table row cache
        old_size = len(self.table_rows_cache)
        self.table_rows_cache.clear()
        bytes_saved += old_size * 1000  # Estimate 1KB per cached row

        # Force garbage collection
        collected = gc.collect()
        bytes_saved += collected * 500  # Estimate 500 bytes per collected object

        # Clear weak references to dead objects
        dead_refs = [k for k, ref in self.instance_cache.items() if ref() is None]
        for k in dead_refs:
            del self.instance_cache[k]

        if bytes_saved > 0:
            self.memory_optimized.emit("warning_optimization", bytes_saved)

    def _perform_critical_optimization(self):
        """Perform critical memory optimization"""
        bytes_saved = 0

        # Aggressive garbage collection
        for i in range(3):
            collected = gc.collect(i)
            bytes_saved += collected * 1000

        # Clear all non-essential caches
        self.table_rows_cache.clear()
        self.instance_cache.clear()

        # Force Python to return memory to OS
        import ctypes
        try:
            ctypes.CDLL('libc.so.6').malloc_trim(0)
        except:
            pass  # Not available on Windows

        if bytes_saved > 0:
            self.memory_optimized.emit("critical_optimization", bytes_saved)

    def optimize_table_data(self, instances_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize table data for memory efficiency"""
        if not self.compression_enabled:
            return instances_data

        optimized = {}
        for key, data in instances_data.items():
            # Compress string data
            optimized_data = {}
            for field, value in data.items():
                if isinstance(value, str) and len(value) > 50:
                    # Store long strings as compressed
                    optimized_data[field] = self._compress_string(value)
                else:
                    optimized_data[field] = value
            optimized[key] = optimized_data

        return optimized

    def _compress_string(self, text: str) -> bytes:
        """Compress long strings to save memory"""
        import zlib
        return zlib.compress(text.encode('utf-8'))

    def decompress_string(self, compressed: bytes) -> str:
        """Decompress compressed strings"""
        import zlib
        return zlib.decompress(compressed).decode('utf-8')

    def cache_table_row(self, row_data: Dict[str, Any]):
        """Cache table row data for quick access"""
        self.table_rows_cache.append(row_data)

    def get_cached_row(self, index: int) -> Optional[Dict[str, Any]]:
        """Get cached row data"""
        try:
            return self.table_rows_cache[index]
        except IndexError:
            return None

    def register_instance(self, instance_id: int, instance_obj: Any):
        """Register instance with weak reference for memory tracking"""
        self.instance_cache[instance_id] = weakref.ref(instance_obj)

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get detailed memory statistics"""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'cached_instances': len(self.instance_cache),
                'cached_rows': len(self.table_rows_cache),
                'compression_enabled': self.compression_enabled
            }
        except Exception as e:
            return {'error': str(e)}
