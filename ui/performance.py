"""
Performance Optimization Components
==================================
"""
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QApplication
from typing import Dict, Any, Optional, Callable, List
import time
import threading
import json
import os
from collections import defaultdict

class SmartCache(QObject):
    """Intelligent caching system with TTL, LRU eviction, and persistence"""
    
    cache_hit = pyqtSignal(str)
    cache_miss = pyqtSignal(str)
    cache_cleared = pyqtSignal()
    
    def __init__(self, max_size: int = 1000, persistent: bool = True):
        super().__init__()
        self.cache: Dict[str, Any] = {}
        self.timestamps: Dict[str, float] = {}
        self.access_count: Dict[str, int] = defaultdict(int)
        self.access_order: List[str] = []
        self.max_size = max_size
        self.persistent = persistent
        self.cache_file = os.path.expanduser("~/.mumu_cache.json")
        
        self.ttl_config = {
            'instance_static': 900,    # 15 minutes - static info like name, path (tăng TTL)
            'instance_dynamic': 120,   # 2 minutes - dynamic info like status (tăng TTL)
            'instance_status': 30,     # 30 seconds - real-time status (tăng TTL)
            'settings': 1800,          # 30 minutes - app settings (tăng TTL)
            'presets': 900,           # 15 minutes - automation presets (tăng TTL)
            'default': 300            # 5 minutes - default TTL (tăng TTL)
        }
        
        # 🚀 LOAD PERSISTENT CACHE on startup
        if self.persistent:
            self.load_cache()
    
    def load_cache(self):
        """Load cache from disk to eliminate cold start cache misses"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.cache = cache_data.get('cache', {})
                    self.timestamps = cache_data.get('timestamps', {})
                    # Convert string timestamps back to float
                    for key in self.timestamps:
                        self.timestamps[key] = float(self.timestamps[key])
                    
                    # Clean expired items immediately
                    current_time = time.time()
                    expired_keys = []
                    for key in self.timestamps:
                        if current_time - self.timestamps[key] > self.ttl_config.get('instance_dynamic', 300):
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        self.cache.pop(key, None)
                        self.timestamps.pop(key, None)
                        
        except Exception as e:
            print(f"Cache load error (non-critical): {e}")
    
    def save_cache(self):
        """Save cache to disk for persistence across app restarts"""
        try:
            if self.persistent:
                cache_data = {
                    'cache': self.cache,
                    'timestamps': {k: str(v) for k, v in self.timestamps.items()}
                }
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Cache save error (non-critical): {e}")
    
    def get(self, key: str, cache_type: str = 'default') -> Optional[Any]:
        """Get cached value if valid"""
        if not self.is_valid(key, cache_type):
            self.cache_miss.emit(key)
            return None
        
        # Update access tracking for LRU
        self.access_count[key] += 1
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        self.cache_hit.emit(key)
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, cache_type: str = 'default'):
        """Set cached value with timestamp, LRU tracking, and auto-persistence"""
        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
        self.access_count[key] = 1
        
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        # Store cache type for TTL lookup
        self.cache[f"{key}_type"] = cache_type
        
        # 🚀 AUTO-SAVE for persistence to eliminate future cache misses
        if self.persistent:
            self.save_cache()
    
    def is_valid(self, key: str, cache_type: str) -> bool:
        """Check if cached value is still valid"""
        if key not in self.cache or key not in self.timestamps:
            return False
        
        stored_type = self.cache.get(f"{key}_type", cache_type)
        ttl = self.ttl_config.get(stored_type, self.ttl_config['default'])
        
        elapsed = time.time() - self.timestamps[key]
        return elapsed < ttl
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries"""
        if pattern:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k and not k.endswith('_type')]
            for key in keys_to_remove:
                self._remove_key(key)
        else:
            self.cache.clear()
            self.timestamps.clear()
            self.access_count.clear()
            self.access_order.clear()
            self.cache_cleared.emit()
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if self.access_order:
            lru_key = self.access_order[0]
            self._remove_key(lru_key)
    
    def _remove_key(self, key: str):
        """Remove key and its metadata"""
        self.cache.pop(key, None)
        self.cache.pop(f"{key}_type", None)
        self.timestamps.pop(key, None)
        self.access_count.pop(key, None)
        if key in self.access_order:
            self.access_order.remove(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_accesses = sum(self.access_count.values())
        return {
            'size': len([k for k in self.cache.keys() if not k.endswith('_type')]),
            'max_size': self.max_size,
            'total_accesses': total_accesses,
            'hit_rate': len(self.access_count) / max(total_accesses, 1),
            'keys': list(self.cache.keys())
        }

class AsyncTaskManager(QObject):
    """Advanced async task management with prioritization and queuing"""
    
    task_started = pyqtSignal(str)
    task_progress = pyqtSignal(str, int)  # task_id, progress_percent
    task_completed = pyqtSignal(str, object)
    task_failed = pyqtSignal(str, str)
    queue_updated = pyqtSignal(int)  # queue_size
    
    def __init__(self, max_workers: int = 4):
        super().__init__()
        self.max_workers = max_workers
        self.active_tasks: Dict[str, QThread] = {}
        self.task_queue: List[tuple] = []  # (priority, task_id, worker)
        self.worker_pool = []
        
        # Initialize worker pool
        for i in range(max_workers):
            worker = AsyncWorker(f"worker_{i}")
            worker.signals.started.connect(self.on_task_started)
            worker.signals.progress.connect(self.on_task_progress)
            worker.signals.finished.connect(self.on_task_completed)
            worker.signals.error.connect(self.on_task_failed)
            self.worker_pool.append(worker)
    
    def submit_task(self, task_id: str, func: Callable, priority: int = 0, *args, **kwargs) -> bool:
        """Submit task with priority (higher number = higher priority)"""
        # Check if task already exists
        if task_id in self.active_tasks:
            return False
        
        # Find available worker
        available_worker = None
        for worker in self.worker_pool:
            if not worker.isRunning():
                available_worker = worker
                break
        
        if available_worker:
            # Execute immediately
            available_worker.setup_task(task_id, func, *args, **kwargs)
            available_worker.start()
            self.active_tasks[task_id] = available_worker
            return True
        else:
            # Add to queue with priority
            self.task_queue.append((priority, task_id, func, args, kwargs))
            self.task_queue.sort(key=lambda x: x[0], reverse=True)  # Sort by priority
            self.queue_updated.emit(len(self.task_queue))
            return True
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel running or queued task"""
        # Cancel running task
        if task_id in self.active_tasks:
            worker = self.active_tasks[task_id]
            worker.terminate()
            worker.wait()
            del self.active_tasks[task_id]
            return True
        
        # Remove from queue
        for i, (priority, queued_id, func, args, kwargs) in enumerate(self.task_queue):
            if queued_id == task_id:
                del self.task_queue[i]
                self.queue_updated.emit(len(self.task_queue))
                return True
        
        return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue and task status"""
        return {
            'active_tasks': list(self.active_tasks.keys()),
            'queued_tasks': [task_id for _, task_id, _, _, _ in self.task_queue],
            'available_workers': sum(1 for w in self.worker_pool if not w.isRunning()),
            'queue_size': len(self.task_queue)
        }
    
    def on_task_started(self, task_id: str):
        """Handle task start"""
        self.task_started.emit(task_id)
    
    def on_task_progress(self, task_id: str, progress: int):
        """Handle task progress update"""
        self.task_progress.emit(task_id, progress)
    
    def on_task_completed(self, task_id: str, result: Any):
        """Handle task completion"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
        
        self.task_completed.emit(task_id, result)
        self._process_queue()
    
    def on_task_failed(self, task_id: str, error: str):
        """Handle task failure"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
        
        self.task_failed.emit(task_id, error)
        self._process_queue()
    
    def _process_queue(self):
        """Process next task in queue if workers available"""
        if not self.task_queue:
            return
        
        # Find available worker
        for worker in self.worker_pool:
            if not worker.isRunning() and self.task_queue:
                priority, task_id, func, args, kwargs = self.task_queue.pop(0)
                worker.setup_task(task_id, func, *args, **kwargs)
                worker.start()
                self.active_tasks[task_id] = worker
                self.queue_updated.emit(len(self.task_queue))
                break

class AsyncWorker(QThread):
    """Enhanced async worker with progress reporting"""
    
    def __init__(self, worker_id: str):
        super().__init__()
        self.worker_id = worker_id
        self.task_id = ""
        self.func = None
        self.args = ()
        self.kwargs = {}
        self.signals = AsyncWorkerSignals()
    
    def setup_task(self, task_id: str, func: Callable, *args, **kwargs):
        """Setup task for execution"""
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Execute the task with error handling"""
        if not self.func:
            return
        
        try:
            self.signals.started.emit(self.task_id)
            
            # Execute function
            result = self.func(*self.args, **self.kwargs)
            
            self.signals.finished.emit(self.task_id, result)
            
        except Exception as e:
            self.signals.error.emit(self.task_id, str(e))
    
    def report_progress(self, progress: int):
        """Report progress from within task"""
        self.signals.progress.emit(self.task_id, progress)

class AsyncWorkerSignals(QObject):
    """Signals for async worker communication"""
    started = pyqtSignal(str)
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(str, object)
    error = pyqtSignal(str, str)

class PerformanceMonitor(QObject):
    """Monitor application performance metrics"""
    
    metrics_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        self.metrics = {
            'memory_usage': 0,
            'cpu_usage': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'active_tasks': 0,
            'completed_tasks': 0,
            'uptime': 0
        }
        
        # Setup monitoring timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(5000)  # Update every 5 seconds
    
    def update_metrics(self):
        """Update performance metrics"""
        try:
            import psutil
            process = psutil.Process()
            
            self.metrics.update({
                'memory_usage': process.memory_info().rss / 1024 / 1024,  # MB
                'cpu_usage': process.cpu_percent(),
                'uptime': time.time() - self.start_time
            })
            
            self.metrics_updated.emit(self.metrics.copy())
            
        except ImportError:
            # Fallback if psutil not available
            self.metrics['uptime'] = time.time() - self.start_time
            self.metrics_updated.emit(self.metrics.copy())
    
    def increment_counter(self, counter_name: str):
        """Increment a performance counter"""
        if counter_name in self.metrics:
            self.metrics[counter_name] += 1
    
    def set_gauge(self, gauge_name: str, value: float):
        """Set a gauge metric value"""
        self.metrics[gauge_name] = value

class BackgroundTaskScheduler(QObject):
    """Schedule and manage recurring background tasks"""
    
    def __init__(self, task_manager: AsyncTaskManager):
        super().__init__()
        self.task_manager = task_manager
        self.scheduled_tasks: Dict[str, QTimer] = {}
    
    def schedule_recurring(self, task_id: str, func: Callable, interval_ms: int, *args, **kwargs):
        """Schedule a recurring background task"""
        if task_id in self.scheduled_tasks:
            self.unschedule(task_id)
        
        timer = QTimer()
        timer.timeout.connect(
            lambda: self.task_manager.submit_task(
                f"{task_id}_{int(time.time())}", func, priority=-1, *args, **kwargs
            )
        )
        timer.start(interval_ms)
        self.scheduled_tasks[task_id] = timer
    
    def schedule_delayed(self, task_id: str, func: Callable, delay_ms: int, *args, **kwargs):
        """Schedule a one-time delayed task"""
        QTimer.singleShot(
            delay_ms,
            lambda: self.task_manager.submit_task(task_id, func, *args, **kwargs)
        )
    
    def unschedule(self, task_id: str):
        """Stop a scheduled task"""
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id].stop()
            del self.scheduled_tasks[task_id]
    
    def unschedule_all(self):
        """Stop all scheduled tasks"""
        for timer in self.scheduled_tasks.values():
            timer.stop()
        self.scheduled_tasks.clear()
