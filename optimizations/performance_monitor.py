# performance_monitor.py - Application performance monitoring system

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from optimizations.app_config import AppConstants, get_config
from error_handler import global_error_handler

# Try to import psutil, fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    global_error_handler.log_warning("psutil not available, using basic monitoring", "PerformanceMonitor")

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    thread_count: int
    worker_count: int = 0
    operation_name: str = ""
    duration_ms: float = 0.0

@dataclass  
class OperationStats:
    """Statistics for a specific operation"""
    name: str
    call_count: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    avg_duration: float = 0.0
    error_count: int = 0
    last_called: float = 0.0
    
    def add_measurement(self, duration: float, success: bool = True):
        """Add a new measurement"""
        self.call_count += 1
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
        self.avg_duration = self.total_duration / self.call_count
        self.last_called = time.time()
        
        if not success:
            self.error_count += 1

class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str, monitor: 'PerformanceMonitor'):
        self.operation_name = operation_name
        self.monitor = monitor
        self.start_time = 0.0
        self.success = True
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.perf_counter() - self.start_time) * 1000  # Convert to ms
        self.success = exc_type is None
        self.monitor.record_operation(self.operation_name, duration, self.success)
        
    def mark_error(self):
        """Mark this operation as failed"""
        self.success = False

class PerformanceMonitor(QObject):
    """Advanced performance monitoring system"""
    
    metrics_updated = pyqtSignal(object)  # PerformanceMetric
    alert_triggered = pyqtSignal(str, str)  # alert_type, message
    
    def __init__(self):
        super().__init__()
        self.enabled = get_config("performance.monitoring_enabled", True)
        self.metrics_history: deque = deque(maxlen=1000)  # Keep last 1000 metrics
        self.operation_stats: Dict[str, OperationStats] = {}
        
        # Performance thresholds
        self.cpu_threshold = 80.0  # CPU usage percentage
        self.memory_threshold = 500.0  # Memory usage in MB
        self.operation_time_threshold = 5000.0  # Operation time in ms
        
        # Monitoring timer (lazy initialization)
        self.monitor_timer = None
        self.monitor_interval = get_config("performance.monitor_interval", 5000)  # 5 seconds
        self._monitoring_started = False
        
        # Current process
        if PSUTIL_AVAILABLE:
            try:
                self.process = psutil.Process()
            except Exception as e:
                global_error_handler.log_warning(f"Failed to get process info: {e}", "PerformanceMonitor")
                self.process = None
        else:
            self.process = None
            global_error_handler.log_info("Using basic monitoring (psutil not available)", "PerformanceMonitor")
            
        if self.enabled:
            # Don't auto-start monitoring, use lazy initialization
            pass
    
    def _ensure_monitoring_started(self, parent=None):
        """🔧 Lazy initialization of monitoring timer"""
        if not self._monitoring_started and parent and self.enabled:
            self.monitor_timer = QTimer(parent)
            self.monitor_timer.timeout.connect(self._collect_metrics)
            interval = self.monitor_interval
            if isinstance(interval, (int, float)):
                self.monitor_timer.start(int(interval))
            else:
                self.monitor_timer.start(5000)  # Default 5 seconds
            self._monitoring_started = True
            global_error_handler.log_info("Performance monitoring started", "PerformanceMonitor")
    
    def start_monitoring(self, parent=None):
        """Start performance monitoring with parent context"""
        if not self.enabled or not self.process:
            return
            
        self._ensure_monitoring_started(parent)
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        if self.monitor_timer:
            self.monitor_timer.stop()
        global_error_handler.log_info("Performance monitoring stopped", "PerformanceMonitor")
    
    def record_operation(self, operation_name: str, duration_ms: float, success: bool = True):
        """Record an operation's performance"""
        if not self.enabled:
            return
            
        # Update operation statistics
        if operation_name not in self.operation_stats:
            self.operation_stats[operation_name] = OperationStats(operation_name)
            
        self.operation_stats[operation_name].add_measurement(duration_ms, success)
        
        # Check for slow operations
        if duration_ms > self.operation_time_threshold:
            self.alert_triggered.emit(
                "slow_operation",
                f"Operation '{operation_name}' took {duration_ms:.2f}ms"
            )
    
    def create_timer(self, operation_name: str) -> PerformanceTimer:
        """Create a performance timer for an operation"""
        return PerformanceTimer(operation_name, self)
    
    def time_function(self, operation_name: str):
        """Decorator to time function execution"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                with self.create_timer(operation_name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_operation_stats(self, operation_name: str) -> Optional[OperationStats]:
        """Get statistics for a specific operation"""
        return self.operation_stats.get(operation_name)
    
    def get_all_operation_stats(self) -> Dict[str, OperationStats]:
        """Get all operation statistics"""
        return self.operation_stats.copy()
    
    def get_recent_metrics(self, count: int = 10) -> List[PerformanceMetric]:
        """Get recent performance metrics"""
        return list(self.metrics_history)[-count:]
    
    def get_average_metrics(self, seconds: int = 60) -> Optional[PerformanceMetric]:
        """Get average metrics over the last N seconds"""
        if not self.metrics_history:
            return None
            
        cutoff_time = time.time() - seconds
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return None
            
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory_mb = sum(m.memory_mb for m in recent_metrics) / len(recent_metrics)
        avg_memory_percent = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_threads = sum(m.thread_count for m in recent_metrics) / len(recent_metrics)
        
        return PerformanceMetric(
            timestamp=time.time(),
            cpu_percent=avg_cpu,
            memory_mb=avg_memory_mb,
            memory_percent=avg_memory_percent,
            thread_count=int(avg_threads)
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a comprehensive performance summary"""
        if not self.metrics_history:
            return {}
            
        latest_metric = self.metrics_history[-1] if self.metrics_history else None
        avg_60s = self.get_average_metrics(60)
        
        # Top slow operations
        slow_operations = sorted(
            [(name, stats) for name, stats in self.operation_stats.items()],
            key=lambda x: x[1].avg_duration,
            reverse=True
        )[:5]
        
        # Operations with most errors
        error_operations = sorted(
            [(name, stats) for name, stats in self.operation_stats.items() if stats.error_count > 0],
            key=lambda x: x[1].error_count,
            reverse=True
        )[:5]
        
        return {
            "current": {
                "cpu_percent": latest_metric.cpu_percent if latest_metric else 0,
                "memory_mb": latest_metric.memory_mb if latest_metric else 0,
                "memory_percent": latest_metric.memory_percent if latest_metric else 0,
                "thread_count": latest_metric.thread_count if latest_metric else 0,
            },
            "average_60s": {
                "cpu_percent": avg_60s.cpu_percent if avg_60s else 0,
                "memory_mb": avg_60s.memory_mb if avg_60s else 0,
                "memory_percent": avg_60s.memory_percent if avg_60s else 0,
            },
            "operations": {
                "total_operations": len(self.operation_stats),
                "total_calls": sum(stats.call_count for stats in self.operation_stats.values()),
                "total_errors": sum(stats.error_count for stats in self.operation_stats.values()),
                "slowest": [(name, f"{stats.avg_duration:.2f}ms") for name, stats in slow_operations],
                "most_errors": [(name, stats.error_count) for name, stats in error_operations],
            }
        }
    
    def _collect_metrics(self):
        """Collect current performance metrics"""
        try:
            # Get current metrics
            if PSUTIL_AVAILABLE and self.process:
                cpu_percent = self.process.cpu_percent()
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
                memory_percent = self.process.memory_percent()
                thread_count = self.process.num_threads()
            else:
                # Basic fallback metrics
                cpu_percent = 0.0  # Can't measure without psutil
                memory_mb = 0.0    # Can't measure without psutil
                memory_percent = 0.0
                thread_count = threading.active_count()
            
            # Create metric
            metric = PerformanceMetric(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                thread_count=thread_count
            )
            
            # Store metric
            self.metrics_history.append(metric)
            
            # Emit update
            self.metrics_updated.emit(metric)
            
            # Check thresholds (only if we have real data)
            if PSUTIL_AVAILABLE and self.process:
                self._check_performance_alerts(metric)
            
        except Exception as e:
            global_error_handler.log_warning(f"Failed to collect metrics: {e}", "PerformanceMonitor")
    
    def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check for performance alerts"""
        if metric.cpu_percent > self.cpu_threshold:
            self.alert_triggered.emit(
                "high_cpu",
                f"High CPU usage: {metric.cpu_percent:.1f}%"
            )
            
        if metric.memory_mb > self.memory_threshold:
            self.alert_triggered.emit(
                "high_memory",
                f"High memory usage: {metric.memory_mb:.1f}MB"
            )
    
    def reset_stats(self):
        """Reset all operation statistics"""
        self.operation_stats.clear()
        global_error_handler.log_info("Performance statistics reset", "PerformanceMonitor")
    
    def export_stats(self) -> Dict[str, Any]:
        """Export all statistics for analysis"""
        return {
            "metrics_history": [
                {
                    "timestamp": m.timestamp,
                    "cpu_percent": m.cpu_percent,
                    "memory_mb": m.memory_mb,
                    "memory_percent": m.memory_percent,
                    "thread_count": m.thread_count,
                    "worker_count": m.worker_count,
                    "operation_name": m.operation_name,
                    "duration_ms": m.duration_ms
                }
                for m in self.metrics_history
            ],
            "operation_stats": {
                name: {
                    "call_count": stats.call_count,
                    "total_duration": stats.total_duration,
                    "min_duration": stats.min_duration,
                    "max_duration": stats.max_duration,
                    "avg_duration": stats.avg_duration,
                    "error_count": stats.error_count,
                    "last_called": stats.last_called
                }
                for name, stats in self.operation_stats.items()
            }
        }

# Global performance monitor instance
global_performance_monitor = PerformanceMonitor()

# Convenience functions
def time_operation(operation_name: str):
    """Decorator to time an operation"""
    return global_performance_monitor.time_function(operation_name)

def create_timer(operation_name: str) -> PerformanceTimer:
    """Create a performance timer"""
    return global_performance_monitor.create_timer(operation_name)

def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary"""
    return global_performance_monitor.get_performance_summary()

def record_operation(operation_name: str, duration_ms: float, success: bool = True):
    """Record an operation's performance"""
    global_performance_monitor.record_operation(operation_name, duration_ms, success)
