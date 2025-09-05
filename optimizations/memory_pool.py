#!/usr/bin/env python3
"""
🔥 ADVANCED MEMORY POOL OPTIMIZATION - Phase 2 Implementation
Memory compression và predictive allocation cho dataset siêu lớn
"""

import sys
import gc
import weakref
import zlib
import pickle
import lzma
from typing import Dict, List, Optional, Any, Type, Tuple
from collections import deque, OrderedDict
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QTableWidgetItem, QWidget
import psutil
import time
import threading

class CompressionManager:
    """🗜️ Advanced compression system cho memory optimization"""

    def __init__(self):
        self.compression_level = 6  # Balanced speed/compression
        self.compression_stats = {
            'total_compressed': 0,
            'total_decompressed': 0,
            'compression_ratio': 0.0,
            'bytes_saved': 0
        }

    def compress_data(self, data: Any, method: str = 'zlib') -> Tuple[bytes, str]:
        """Compress data với multiple methods"""
        try:
            # Serialize data
            serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)

            if method == 'zlib':
                compressed = zlib.compress(serialized, level=self.compression_level)
            elif method == 'lzma':
                compressed = lzma.compress(serialized, preset=self.compression_level)
            else:
                compressed = serialized  # No compression

            # Calculate compression ratio
            ratio = len(compressed) / len(serialized) if len(serialized) > 0 else 1.0
            self.compression_stats['compression_ratio'] = ratio
            self.compression_stats['bytes_saved'] += (len(serialized) - len(compressed))
            self.compression_stats['total_compressed'] += 1

            return compressed, method

        except Exception as e:
            print(f"⚠️ Compression failed: {e}")
            return pickle.dumps(data), 'none'

    def decompress_data(self, compressed_data: bytes, method: str) -> Any:
        """Decompress data"""
        try:
            if method == 'zlib':
                decompressed = zlib.decompress(compressed_data)
            elif method == 'lzma':
                decompressed = lzma.decompress(compressed_data)
            else:
                decompressed = compressed_data

            data = pickle.loads(decompressed)
            self.compression_stats['total_decompressed'] += 1
            return data

        except Exception as e:
            print(f"⚠️ Decompression failed: {e}")
            return None

class ObjectPool:
    """🚀 High-performance object pooling system"""

    def __init__(self, object_type: Type, max_size: int = 1000):
        self.object_type = object_type
        self.max_size = max_size
        self.pool: deque = deque()
        self.active_objects = 0
        self.total_created = 0
        self.total_reused = 0

    def acquire(self, *args, **kwargs) -> Any:
        """Acquire object from pool or create new one"""
        if self.pool:
            obj = self.pool.popleft()
            self.total_reused += 1
            # Reset object state if needed
            if hasattr(obj, 'reset'):
                obj.reset()
        else:
            obj = self.object_type(*args, **kwargs)
            self.total_created += 1

        self.active_objects += 1
        return obj

    def release(self, obj: Any) -> None:
        """Return object to pool"""
        if len(self.pool) < self.max_size:
            # Clean object state before returning to pool
            if hasattr(obj, 'clear'):
                obj.clear()
            self.pool.append(obj)

        self.active_objects -= 1

    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics"""
        return {
            'pool_size': len(self.pool),
            'active_objects': self.active_objects,
            'total_created': self.total_created,
            'total_reused': self.total_reused,
            'reuse_rate': (self.total_reused / max(1, self.total_created + self.total_reused)) * 100
        }

class CompressedObjectPool(ObjectPool):
    """🚀 Compressed object pool với memory optimization"""

    def __init__(self, object_type, max_size=1000, compression_threshold=1024):
        """Initialize compressed object pool"""
        # Initialize parent class manually
        self.object_type = object_type
        self.max_size = max_size
        self.pool = deque()
        self.active_objects = 0
        self.total_created = 0
        self.total_reused = 0
        
        # Initialize compression-specific attributes
        self.compression_manager = CompressionManager()
        self.compression_threshold = compression_threshold  # Compress objects > 1KB
        self.compressed_pool = deque()
        self.compression_stats = {
            'objects_compressed': 0,
            'objects_decompressed': 0,
            'memory_saved': 0
        }

    def acquire(self, *args, **kwargs) -> Any:
        """Acquire object từ pool hoặc tạo mới với compression support"""
        # Try compressed pool first
        if self.compressed_pool:
            compressed_data, method = self.compressed_pool.popleft()
            try:
                obj = self.compression_manager.decompress_data(compressed_data, method)
                if obj is not None:
                    self.compression_stats['objects_decompressed'] += 1
                    self.total_reused += 1
                    self.active_objects += 1
                    return obj
            except Exception as e:
                print(f"⚠️ Failed to decompress object: {e}")

        # Try regular pool
        if self.pool:
            obj = self.pool.popleft()
            self.total_reused += 1
        else:
            obj = self.object_type(*args, **kwargs)
            self.total_created += 1

        self.active_objects += 1
        return obj

    def release(self, obj: Any) -> None:
        """Return object to pool với smart compression"""
        if len(self.pool) + len(self.compressed_pool) >= self.max_size:
            return  # Pool is full

        # Estimate object size
        try:
            obj_size = sys.getsizeof(obj)
            if obj_size > self.compression_threshold:
                # Compress large objects
                compressed_data, method = self.compression_manager.compress_data(obj)
                self.compressed_pool.append((compressed_data, method))
                self.compression_stats['objects_compressed'] += 1
                self.compression_stats['memory_saved'] += obj_size - len(compressed_data)
            else:
                # Store uncompressed for small objects
                if hasattr(obj, 'clear'):
                    obj.clear()
                self.pool.append(obj)
        except Exception as e:
            print(f"⚠️ Failed to process object for pool: {e}")

        self.active_objects -= 1
    """🚀 High-performance object pooling system"""
    
    def __init__(self, object_type: Type, max_size: int = 1000):
        self.object_type = object_type
        self.max_size = max_size
        self.pool: deque = deque()
        self.active_objects = 0
        self.total_created = 0
        self.total_reused = 0
        
    def acquire(self, *args, **kwargs) -> Any:
        """Acquire object from pool or create new one"""
        if self.pool:
            obj = self.pool.popleft()
            self.total_reused += 1
            # Reset object state if needed
            if hasattr(obj, 'reset'):
                obj.reset()
        else:
            obj = self.object_type(*args, **kwargs)
            self.total_created += 1
            
        self.active_objects += 1
        return obj
    
    def release(self, obj: Any) -> None:
        """Return object to pool"""
        if len(self.pool) < self.max_size:
            # Clean object state before returning to pool
            if hasattr(obj, 'clear'):
                obj.clear()
            self.pool.append(obj)
        
        self.active_objects -= 1
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics"""
        return {
            'pool_size': len(self.pool),
            'active_objects': self.active_objects,
            'total_created': self.total_created,
            'total_reused': self.total_reused,
            'reuse_rate': (self.total_reused / max(1, self.total_created + self.total_reused)) * 100
        }

class MemoryManager(QObject):
    """🧠 Advanced memory management system"""

    memory_warning = pyqtSignal(float)  # Memory usage percentage
    memory_critical = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Object pools for different types
        self.pools: Dict[str, ObjectPool] = {
            'table_items': ObjectPool(QTableWidgetItem, 5000),
            'widgets': ObjectPool(QWidget, 1000),
            'byte_arrays': ObjectPool(bytearray, 2000),
            'lists': ObjectPool(list, 1000),
            'dicts': ObjectPool(dict, 1000)
        }

        # Memory monitoring
        self.memory_threshold_warning = 80.0  # 80% RAM usage
        self.memory_threshold_critical = 90.0  # 90% RAM usage
        self.monitor_timer = None
        self.monitoring_started = False

        # Performance tracking
        self.gc_stats = {
            'manual_collections': 0,
            'objects_freed': 0,
            'memory_saved': 0
        }

    def start_monitoring(self, interval: int = 10000):
        """Start memory monitoring (10 seconds default)"""
        if not self.monitoring_started and self.parent():
            self.monitor_timer = QTimer(self.parent())
            self.monitor_timer.timeout.connect(self._check_memory)
            self.monitor_timer.start(interval)
            self.monitoring_started = True

    def _check_memory(self):
        """Check memory usage và emit signals if needed"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent

            if usage_percent >= self.memory_threshold_critical:
                self.memory_critical.emit(usage_percent)
            elif usage_percent >= self.memory_threshold_warning:
                self.memory_warning.emit(usage_percent)

        except Exception as e:
            print(f"⚠️ Memory check failed: {e}")

    def allocate_chunk(self, chunk_id: str, data: List[Dict], estimated_size_mb: float) -> bool:
        """Allocate memory cho một data chunk"""
        try:
            # Calculate actual size
            data_size = sys.getsizeof(data)

            # For now, just return True (basic implementation)
            return True

        except Exception as e:
            print(f"⚠️ Failed to allocate chunk {chunk_id}: {e}")
            return False

class AdvancedMemoryManager(MemoryManager):
    """🧠 Advanced memory management với compression và predictive allocation"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Upgrade to compressed pools
        self.pools: Dict[str, CompressedObjectPool] = {
            'table_items': CompressedObjectPool(QTableWidgetItem, 5000),  # 2KB threshold
            'widgets': CompressedObjectPool(QWidget, 1000),  # 1KB threshold
            'byte_arrays': CompressedObjectPool(bytearray, 2000),  # 4KB threshold
            'lists': CompressedObjectPool(list, 1000),
            'dicts': CompressedObjectPool(dict, 1000),
            'instances_data': CompressedObjectPool(list, 500)  # Special pool for large datasets
        }

        # Predictive allocation system
        self.predictive_allocator = PredictiveAllocator()
        self.allocation_history = OrderedDict()
        self.allocation_patterns = {}

        # Advanced monitoring
        self.compression_monitor = CompressionMonitor()
        self.memory_predictor = MemoryPredictor()

    def allocate_chunk(self, chunk_id: str, data: List[Dict], estimated_size_mb: float) -> bool:
        """Allocate memory chunk với compression và predictive sizing"""
        try:
            # Calculate actual size
            data_size = sys.getsizeof(data)

            # Check if we need compression
            should_compress = data_size > (estimated_size_mb * 1024 * 1024)

            if should_compress:
                # Use compressed pool
                pool = self.pools.get('instances_data')
                if pool:
                    # Store compressed data
                    compressed_data, method = pool.compression_manager.compress_data(data)
                    pool.compressed_pool.append((compressed_data, method))

                    # Update allocation history
                    self.allocation_history[chunk_id] = {
                        'size': data_size,
                        'compressed_size': len(compressed_data),
                        'method': method,
                        'timestamp': time.time()
                    }

                    print(f"🗜️ Compressed chunk {chunk_id}: {data_size} -> {len(compressed_data)} bytes")
                    return True

            # Regular allocation
            return super().allocate_chunk(chunk_id, data, estimated_size_mb)

        except Exception as e:
            print(f"⚠️ Failed to allocate chunk {chunk_id}: {e}")
            return False

    def get_compression_stats(self) -> Dict[str, Any]:
        """Get comprehensive compression statistics"""
        total_compressed = 0
        total_saved = 0

        for pool_name, pool in self.pools.items():
            if hasattr(pool, 'compression_stats'):
                total_compressed += pool.compression_stats['objects_compressed']
                total_saved += pool.compression_stats['memory_saved']

        return {
            'total_objects_compressed': total_compressed,
            'total_memory_saved': total_saved,
            'compression_ratio': self.compression_monitor.get_average_ratio(),
            'pools_info': {name: pool.get_stats() for name, pool in self.pools.items()}
        }

class PredictiveAllocator:
    """🔮 Predictive memory allocation system"""

    def __init__(self):
        self.allocation_patterns = {}
        self.usage_predictions = {}
        self.learning_rate = 0.1

    def predict_allocation_size(self, data_type: str, current_size: int) -> int:
        """Predict optimal allocation size based on patterns"""
        if data_type in self.allocation_patterns:
            pattern = self.allocation_patterns[data_type]
            predicted = pattern['average_size'] * (1 + pattern['growth_rate'])
            return max(current_size, int(predicted))

        return current_size

    def update_pattern(self, data_type: str, size: int):
        """Update allocation pattern với new data"""
        if data_type not in self.allocation_patterns:
            self.allocation_patterns[data_type] = {
                'average_size': size,
                'growth_rate': 0.0,
                'samples': 1
            }
        else:
            pattern = self.allocation_patterns[data_type]
            old_avg = pattern['average_size']
            pattern['average_size'] = (old_avg * (1 - self.learning_rate)) + (size * self.learning_rate)
            pattern['growth_rate'] = (pattern['average_size'] - old_avg) / max(old_avg, 1)
            pattern['samples'] += 1

class CompressionMonitor:
    """📊 Monitor compression performance"""

    def __init__(self):
        self.compression_history = []
        self.ratios = []

    def get_average_ratio(self) -> float:
        """Get average compression ratio"""
        return sum(self.ratios) / len(self.ratios) if self.ratios else 1.0

class MemoryPredictor:
    """🔮 Memory usage prediction system"""

    def __init__(self):
        self.usage_history = []
        self.prediction_model = {}

    def predict_peak_usage(self, timeframe_minutes: int = 60) -> float:
        """Predict peak memory usage trong timeframe"""
        if len(self.usage_history) < 10:
            return psutil.virtual_memory().percent

        # Simple moving average prediction
        recent_usage = self.usage_history[-10:]
        avg_usage = sum(recent_usage) / len(recent_usage)

        # Add trend factor
        trend = (recent_usage[-1] - recent_usage[0]) / len(recent_usage)
        predicted = avg_usage + (trend * timeframe_minutes)

        return max(0, min(100, predicted))
        
    def start_monitoring(self, interval: int = 10000):
        """Start memory monitoring (10 seconds default)"""
        if not self.monitoring_started and self.parent():
            self.monitor_timer = QTimer(self.parent())
            self.monitor_timer.timeout.connect(self._check_memory)
            self.monitor_timer.start(interval)
            self.monitoring_started = True
            print("🔍 Memory monitoring started")
    
    def _check_memory(self):
        """Check current memory usage"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            system_memory = psutil.virtual_memory()
            
            # Calculate memory usage percentage
            usage_percent = (memory_info.rss / system_memory.total) * 100
            
            if usage_percent > self.memory_threshold_critical:
                self.memory_critical.emit(usage_percent)
                self._emergency_cleanup()
            elif usage_percent > self.memory_threshold_warning:
                self.memory_warning.emit(usage_percent)
                self._smart_cleanup()
                
        except Exception as e:
            print(f"❌ Memory monitoring error: {e}")
    
    def _smart_cleanup(self):
        """Smart memory cleanup"""
        print("🧹 Performing smart memory cleanup...")
        
        # Force garbage collection
        before = self._get_memory_usage()
        collected = gc.collect()
        after = self._get_memory_usage()
        
        memory_freed = before - after
        self.gc_stats['manual_collections'] += 1
        self.gc_stats['objects_freed'] += collected
        self.gc_stats['memory_saved'] += memory_freed
        
        print(f"🗑️ Freed {collected} objects, saved {memory_freed:.2f} MB")
    
    def _emergency_cleanup(self):
        """Emergency memory cleanup"""
        print("🚨 Emergency memory cleanup!")
        
        # Clear all pools
        for pool_name, pool in self.pools.items():
            cleared = len(pool.pool)
            pool.pool.clear()
            print(f"🗑️ Cleared {cleared} objects from {pool_name} pool")
        
        # Force aggressive garbage collection
        for _ in range(3):
            gc.collect()
        
        print("🧹 Emergency cleanup complete")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def get_pool(self, pool_name: str) -> Optional[ObjectPool]:
        """Get object pool by name"""
        return self.pools.get(pool_name)
    
    def get_memory_report(self) -> Dict[str, Any]:
        """Get comprehensive memory report"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            system_memory = psutil.virtual_memory()
            
            report = {
                'process_memory_mb': memory_info.rss / 1024 / 1024,
                'system_memory_usage_percent': system_memory.percent,
                'gc_stats': self.gc_stats.copy(),
                'pool_stats': {name: pool.get_stats() for name, pool in self.pools.items()},
                'total_objects_pooled': sum(len(pool.pool) for pool in self.pools.values()),
                'total_active_objects': sum(pool.active_objects for pool in self.pools.values())
            }
            
            return report
            
        except Exception as e:
            return {'error': str(e)}

# Global memory manager instance
global_memory_manager = None

def get_memory_manager(parent=None) -> MemoryManager:
    """Get or create global memory manager"""
    global global_memory_manager
    if global_memory_manager is None:
        global_memory_manager = MemoryManager(parent)
    return global_memory_manager

def get_object_pool(pool_name: str) -> Optional[ObjectPool]:
    """Get object pool by name"""
    manager = get_memory_manager()
    return manager.get_pool(pool_name)

if __name__ == "__main__":
    # Test memory management
    print("🧪 Testing Memory Management System")
    
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    manager = get_memory_manager(app)
    manager.start_monitoring(5000)  # 5 second intervals
    
    # Test object pooling
    table_pool = get_object_pool('table_items')
    
    # Create and release objects
    items = []
    for i in range(1000):
        item = table_pool.acquire(f"Item {i}")
        items.append(item)
    
    for item in items:
        table_pool.release(item)
    
    print("📊 Pool Stats:", table_pool.get_stats())
    print("📊 Memory Report:", manager.get_memory_report())
    
    print("✅ Memory management system ready!")
