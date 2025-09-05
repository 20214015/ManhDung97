#!/usr/bin/env python3
"""
🎯 Enhanced Performance Monitor with Adaptive Optimization
Real-time performance monitoring with automatic optimization adjustments
"""

import time
import threading
import statistics
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from optimizations.app_config import AppConstants
from optimizations.adaptive_config import get_adaptive_config

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class PerformanceSnapshot:
    """Enhanced performance snapshot with more metrics"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    thread_count: int
    worker_count: int = 0
    operation_name: str = ""
    duration_ms: float = 0.0
    ui_responsiveness: float = 0.0  # Response time for UI operations
    cache_hit_rate: float = 0.0
    memory_pressure: str = "low"
    adaptive_tier: str = "medium"

@dataclass
class PerformanceAlert:
    """Performance alert data structure"""
    alert_type: str  # "memory", "cpu", "responsiveness", "degradation"
    severity: str  # "low", "medium", "high", "critical"
    message: str
    timestamp: float
    suggested_action: str = ""
    auto_resolved: bool = False

class EnhancedPerformanceMonitor(QObject):
    """🚀 Enhanced Performance Monitor with adaptive optimization"""
    
    # Enhanced signals
    performance_alert = pyqtSignal(PerformanceAlert)
    adaptive_optimization_applied = pyqtSignal(dict)
    memory_pressure_changed = pyqtSignal(str)  # "low", "medium", "high", "critical"
    performance_degraded = pyqtSignal(float)  # degradation percentage
    
    def __init__(self):
        super().__init__()
        self.monitoring_enabled = False
        self.adaptive_config = get_adaptive_config()
        
        # Enhanced monitoring data
        self._snapshots = deque(maxlen=1000)  # Last 1000 snapshots
        self._operation_stats = {}
        self._ui_response_times = deque(maxlen=100)
        self._cache_metrics = deque(maxlen=100)
        self._alerts_history = deque(maxlen=500)
        
        # Performance baselines
        self._baseline_cpu = 0.0
        self._baseline_memory = 0.0
        self._baseline_ui_response = 0.0
        self._baseline_established = False
        
        # Adaptive optimization state
        self._last_optimization = 0.0
        self._optimization_cooldown = 30.0  # 30 seconds between optimizations
        self._performance_degradation_threshold = 0.3  # 30% degradation triggers optimization
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._stop_event = threading.Event()
        
        # Qt timers for UI updates
        self._ui_update_timer = QTimer()
        self._ui_update_timer.timeout.connect(self._emit_periodic_updates)
        
    def start_monitoring(self):
        """Start enhanced performance monitoring"""
        if self.monitoring_enabled:
            return
            
        self.monitoring_enabled = True
        self._stop_event.clear()
        
        # Start monitoring thread
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitoring_thread.start()
        
        # Start UI update timer
        self._ui_update_timer.start(5000)  # Update every 5 seconds
        
        print("🎯 Enhanced Performance Monitor started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        if not self.monitoring_enabled:
            return
            
        self.monitoring_enabled = False
        self._stop_event.set()
        
        # Stop timers
        self._ui_update_timer.stop()
        
        # Wait for monitoring thread
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=2.0)
            
        print("🎯 Enhanced Performance Monitor stopped")
    
    def _monitoring_loop(self):
        """Enhanced monitoring loop with adaptive optimization"""
        baseline_samples = 0
        baseline_target = 10  # Collect 10 samples for baseline
        
        while not self._stop_event.wait(1.0):  # Monitor every second
            try:
                snapshot = self._collect_performance_snapshot()
                
                with self._lock:
                    self._snapshots.append(snapshot)
                    
                    # Establish baseline
                    if not self._baseline_established and baseline_samples < baseline_target:
                        self._update_baseline(snapshot)
                        baseline_samples += 1
                        if baseline_samples >= baseline_target:
                            self._baseline_established = True
                            print(f"🎯 Performance baseline established: CPU={self._baseline_cpu:.1f}%, Memory={self._baseline_memory:.1f}MB")
                    
                    # Check for performance issues
                    elif self._baseline_established:
                        self._analyze_performance(snapshot)
                        self._check_adaptive_optimization(snapshot)
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
    
    def _collect_performance_snapshot(self) -> PerformanceSnapshot:
        """Collect enhanced performance snapshot"""
        timestamp = time.time()
        
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                memory_percent = process.memory_percent()
                thread_count = process.num_threads()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                cpu_percent = 0.0
                memory_mb = 0.0
                memory_percent = 0.0
                thread_count = 1
        else:
            cpu_percent = 0.0
            memory_mb = 0.0
            memory_percent = 0.0
            thread_count = 1
        
        # Calculate UI responsiveness
        ui_responsiveness = self._calculate_ui_responsiveness()
        
        # Get cache hit rate
        cache_hit_rate = self._calculate_cache_hit_rate()
        
        # Get memory pressure and adaptive tier
        memory_pressure = self.adaptive_config.get_memory_pressure_level()
        adaptive_tier = self.adaptive_config.system_profile.performance_tier
        
        return PerformanceSnapshot(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            thread_count=thread_count,
            ui_responsiveness=ui_responsiveness,
            cache_hit_rate=cache_hit_rate,
            memory_pressure=memory_pressure,
            adaptive_tier=adaptive_tier
        )
    
    def _update_baseline(self, snapshot: PerformanceSnapshot):
        """Update performance baseline"""
        if self._baseline_cpu == 0:
            self._baseline_cpu = snapshot.cpu_percent
            self._baseline_memory = snapshot.memory_mb
            self._baseline_ui_response = snapshot.ui_responsiveness
        else:
            # Running average
            alpha = 0.1
            self._baseline_cpu = (1 - alpha) * self._baseline_cpu + alpha * snapshot.cpu_percent
            self._baseline_memory = (1 - alpha) * self._baseline_memory + alpha * snapshot.memory_mb
            self._baseline_ui_response = (1 - alpha) * self._baseline_ui_response + alpha * snapshot.ui_responsiveness
    
    def _analyze_performance(self, snapshot: PerformanceSnapshot):
        """Analyze performance and generate alerts"""
        alerts = []
        
        # Memory pressure analysis
        if snapshot.memory_pressure == "critical":
            alerts.append(PerformanceAlert(
                alert_type="memory",
                severity="critical",
                message=f"Critical memory pressure detected: {snapshot.memory_percent:.1f}%",
                timestamp=snapshot.timestamp,
                suggested_action="Reduce batch sizes and enable aggressive cleanup"
            ))
        elif snapshot.memory_pressure == "high":
            alerts.append(PerformanceAlert(
                alert_type="memory",
                severity="high",
                message=f"High memory pressure: {snapshot.memory_percent:.1f}%",
                timestamp=snapshot.timestamp,
                suggested_action="Consider reducing worker count and cache size"
            ))
        
        # CPU performance analysis
        cpu_increase = (snapshot.cpu_percent - self._baseline_cpu) / max(self._baseline_cpu, 1.0)
        if cpu_increase > 2.0:  # 200% increase
            alerts.append(PerformanceAlert(
                alert_type="cpu",
                severity="high",
                message=f"High CPU usage detected: {snapshot.cpu_percent:.1f}% (baseline: {self._baseline_cpu:.1f}%)",
                timestamp=snapshot.timestamp,
                suggested_action="Reduce worker count and increase operation intervals"
            ))
        
        # UI responsiveness analysis
        if snapshot.ui_responsiveness > self._baseline_ui_response * 3:
            alerts.append(PerformanceAlert(
                alert_type="responsiveness",
                severity="medium",
                message=f"UI responsiveness degraded: {snapshot.ui_responsiveness:.1f}ms (baseline: {self._baseline_ui_response:.1f}ms)",
                timestamp=snapshot.timestamp,
                suggested_action="Increase UI refresh intervals"
            ))
        
        # Cache performance analysis
        if snapshot.cache_hit_rate < 0.7:  # Less than 70% hit rate
            alerts.append(PerformanceAlert(
                alert_type="cache",
                severity="low",
                message=f"Low cache hit rate: {snapshot.cache_hit_rate:.1%}",
                timestamp=snapshot.timestamp,
                suggested_action="Increase cache TTL or review caching strategy"
            ))
        
        # Store and emit alerts
        for alert in alerts:
            with self._lock:
                self._alerts_history.append(alert)
            self.performance_alert.emit(alert)
    
    def _check_adaptive_optimization(self, snapshot: PerformanceSnapshot):
        """Check if adaptive optimization should be triggered"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self._last_optimization < self._optimization_cooldown:
            return
        
        # Calculate overall performance degradation
        cpu_degradation = max(0, (snapshot.cpu_percent - self._baseline_cpu) / max(self._baseline_cpu, 1.0))
        memory_degradation = max(0, (snapshot.memory_mb - self._baseline_memory) / max(self._baseline_memory, 1.0))
        ui_degradation = max(0, (snapshot.ui_responsiveness - self._baseline_ui_response) / max(self._baseline_ui_response, 1.0))
        
        overall_degradation = (cpu_degradation + memory_degradation + ui_degradation) / 3.0
        
        # Trigger optimization if degradation exceeds threshold
        if overall_degradation > self._performance_degradation_threshold:
            self._apply_adaptive_optimization(overall_degradation, snapshot)
            self._last_optimization = current_time
    
    def _apply_adaptive_optimization(self, degradation: float, snapshot: PerformanceSnapshot):
        """Apply adaptive performance optimization"""
        print(f"🎯 Applying adaptive optimization (degradation: {degradation:.1%})")
        
        # Refresh system profile
        profile_changed = self.adaptive_config.refresh_system_profile()
        
        if profile_changed:
            print(f"🎯 System profile updated to: {self.adaptive_config.system_profile.performance_tier}")
        
        # Apply optimizations based on current pressure
        if snapshot.memory_pressure in ["high", "critical"]:
            self._apply_memory_optimization()
        
        if snapshot.cpu_percent > self._baseline_cpu * 2:
            self._apply_cpu_optimization()
        
        if snapshot.ui_responsiveness > self._baseline_ui_response * 2:
            self._apply_ui_optimization()
        
        # Apply the new configuration
        self.adaptive_config.apply_to_app_constants()
        
        # Emit optimization signal
        optimization_data = {
            "degradation_percent": degradation * 100,
            "optimization_type": "adaptive",
            "memory_pressure": snapshot.memory_pressure,
            "new_config": self.adaptive_config.get_optimized_config()
        }
        self.adaptive_optimization_applied.emit(optimization_data)
        self.performance_degraded.emit(degradation)
    
    def _apply_memory_optimization(self):
        """Apply memory-specific optimizations"""
        config = self.adaptive_config._optimized_config
        
        # Reduce memory-intensive settings
        config["max_concurrent_workers"] = max(1, config["max_concurrent_workers"] - 1)
        config["table_update_batch_size"] = max(10, config["table_update_batch_size"] // 2)
        config["max_log_entries"] = max(1000, config["max_log_entries"] // 2)
        config["cache_ttl_seconds"] = max(10, config["cache_ttl_seconds"] - 10)
        
        print("🎯 Applied memory optimization")
    
    def _apply_cpu_optimization(self):
        """Apply CPU-specific optimizations"""
        config = self.adaptive_config._optimized_config
        
        # Reduce CPU-intensive settings
        config["ui_refresh_interval"] = min(500, config["ui_refresh_interval"] + 50)
        config["auto_refresh_interval"] = min(120, config["auto_refresh_interval"] + 15)
        config["worker_check_interval"] = min(200, config["worker_check_interval"] + 25)
        
        print("🎯 Applied CPU optimization")
    
    def _apply_ui_optimization(self):
        """Apply UI-specific optimizations"""
        config = self.adaptive_config._optimized_config
        
        # Optimize UI responsiveness
        config["table_refresh_interval"] = min(1000, config["table_refresh_interval"] + 100)
        config["progress_update_interval"] = min(500, config["progress_update_interval"] + 50)
        config["ui_refresh_interval"] = min(300, config["ui_refresh_interval"] + 25)
        
        print("🎯 Applied UI optimization")
    
    def _calculate_ui_responsiveness(self) -> float:
        """Calculate UI responsiveness metric"""
        with self._lock:
            if not self._ui_response_times:
                return 0.0
            return statistics.mean(self._ui_response_times)
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        with self._lock:
            if not self._cache_metrics:
                return 1.0  # Assume good performance if no data
            return statistics.mean(self._cache_metrics)
    
    def record_ui_response_time(self, response_time_ms: float):
        """Record UI response time for monitoring"""
        with self._lock:
            self._ui_response_times.append(response_time_ms)
    
    def record_cache_hit_rate(self, hit_rate: float):
        """Record cache hit rate for monitoring"""
        with self._lock:
            self._cache_metrics.append(hit_rate)
    
    def _emit_periodic_updates(self):
        """Emit periodic updates for UI"""
        if not self._snapshots:
            return
            
        latest_snapshot = self._snapshots[-1]
        
        # Check for memory pressure changes
        current_pressure = latest_snapshot.memory_pressure
        if hasattr(self, '_last_memory_pressure') and current_pressure != self._last_memory_pressure:
            self.memory_pressure_changed.emit(current_pressure)
        self._last_memory_pressure = current_pressure
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        with self._lock:
            if not self._snapshots:
                return {}
            
            recent_snapshots = list(self._snapshots)[-60:]  # Last 60 snapshots (1 minute)
            
            return {
                "current": {
                    "cpu_percent": recent_snapshots[-1].cpu_percent,
                    "memory_mb": recent_snapshots[-1].memory_mb,
                    "memory_percent": recent_snapshots[-1].memory_percent,
                    "ui_responsiveness": recent_snapshots[-1].ui_responsiveness,
                    "cache_hit_rate": recent_snapshots[-1].cache_hit_rate,
                    "memory_pressure": recent_snapshots[-1].memory_pressure,
                    "adaptive_tier": recent_snapshots[-1].adaptive_tier,
                },
                "baseline": {
                    "cpu_percent": self._baseline_cpu,
                    "memory_mb": self._baseline_memory,
                    "ui_responsiveness": self._baseline_ui_response,
                    "established": self._baseline_established,
                },
                "trends": {
                    "avg_cpu": statistics.mean(s.cpu_percent for s in recent_snapshots),
                    "avg_memory": statistics.mean(s.memory_mb for s in recent_snapshots),
                    "avg_ui_response": statistics.mean(s.ui_responsiveness for s in recent_snapshots),
                },
                "alerts": {
                    "total_count": len(self._alerts_history),
                    "recent_count": len([a for a in self._alerts_history if time.time() - a.timestamp < 300]),  # Last 5 minutes
                },
                "adaptive_config": self.adaptive_config.get_stats(),
            }

# Global enhanced performance monitor instance
enhanced_performance_monitor = EnhancedPerformanceMonitor()

def get_enhanced_performance_monitor() -> EnhancedPerformanceMonitor:
    """Get the global enhanced performance monitor instance"""
    return enhanced_performance_monitor