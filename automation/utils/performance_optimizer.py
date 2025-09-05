"""
Performance Optimizer - System Performance Management
===================================================
Intelligent performance monitoring and optimization for automation processes.
"""

import psutil
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, NamedTuple
from dataclasses import dataclass
from collections import deque
from enum import Enum
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class SystemPerformance(Enum):
    """System performance levels"""
    EXCELLENT = "excellent"  # <30% CPU, <50% Memory
    GOOD = "good"           # <50% CPU, <70% Memory  
    MODERATE = "moderate"   # <70% CPU, <80% Memory
    POOR = "poor"          # <85% CPU, <90% Memory
    CRITICAL = "critical"   # >=85% CPU, >=90% Memory


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: float
    process_count: int
    timestamp: datetime
    performance_level: SystemPerformance
    
    @classmethod
    def collect_current(cls) -> 'SystemMetrics':
        """Collect current system metrics"""
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0
        
        # Network I/O (simplified)
        network = 0
        try:
            net_io = psutil.net_io_counters()
            network = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB
        except:
            pass
        
        process_count = len(psutil.pids())
        
        # Determine performance level
        if cpu >= 85 or memory >= 90:
            performance = SystemPerformance.CRITICAL
        elif cpu >= 70 or memory >= 80:
            performance = SystemPerformance.POOR
        elif cpu >= 50 or memory >= 70:
            performance = SystemPerformance.MODERATE
        elif cpu >= 30 or memory >= 50:
            performance = SystemPerformance.GOOD
        else:
            performance = SystemPerformance.EXCELLENT
        
        return cls(
            cpu_percent=cpu,
            memory_percent=memory,
            disk_percent=disk,
            network_io=network,
            process_count=process_count,
            timestamp=datetime.now(),
            performance_level=performance
        )


class OptimizationSuggestion(NamedTuple):
    """Performance optimization suggestion"""
    category: str
    priority: str  # high, medium, low
    description: str
    recommended_action: str
    expected_impact: str


@dataclass
class AutomationProfile:
    """Automation performance profile"""
    optimal_batch_size: int
    optimal_batch_delay: float
    optimal_start_delay: float
    max_concurrent_batches: int
    cpu_threshold: float
    memory_threshold: float
    recommended_schedule: str
    confidence_score: float


class PerformancePredictor:
    """ML-inspired performance prediction"""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.performance_history: deque = deque(maxlen=history_size)
        self.pattern_cache: Dict[str, Any] = {}
        
    def add_metrics(self, metrics: SystemMetrics):
        """Add metrics to history for analysis"""
        self.performance_history.append(metrics)
        self._update_patterns()
    
    def predict_performance_trend(self, minutes_ahead: int = 30) -> SystemPerformance:
        """Predict system performance trend"""
        if len(self.performance_history) < 10:
            return SystemPerformance.MODERATE
        
        # Simple trend analysis
        recent_metrics = list(self.performance_history)[-10:]
        cpu_trend = self._calculate_trend([m.cpu_percent for m in recent_metrics])
        memory_trend = self._calculate_trend([m.memory_percent for m in recent_metrics])
        
        # Project trends forward
        current_cpu = recent_metrics[-1].cpu_percent
        current_memory = recent_metrics[-1].memory_percent
        
        projected_cpu = current_cpu + (cpu_trend * minutes_ahead)
        projected_memory = current_memory + (memory_trend * minutes_ahead)
        
        # Determine predicted performance level
        if projected_cpu >= 85 or projected_memory >= 90:
            return SystemPerformance.CRITICAL
        elif projected_cpu >= 70 or projected_memory >= 80:
            return SystemPerformance.POOR
        elif projected_cpu >= 50 or projected_memory >= 70:
            return SystemPerformance.MODERATE
        elif projected_cpu >= 30 or projected_memory >= 50:
            return SystemPerformance.GOOD
        else:
            return SystemPerformance.EXCELLENT
    
    def get_optimal_automation_timing(self) -> Tuple[datetime, float]:
        """Get optimal timing for automation based on patterns"""
        if len(self.performance_history) < 24:  # Need at least 24 data points
            return datetime.now(), 0.5
        
        # Analyze hourly patterns
        hourly_performance = {}
        for metrics in self.performance_history:
            hour = metrics.timestamp.hour
            if hour not in hourly_performance:
                hourly_performance[hour] = []
            hourly_performance[hour].append(metrics.cpu_percent + metrics.memory_percent)
        
        # Find optimal hour (lowest average resource usage)
        optimal_hour = min(hourly_performance.keys(), 
                          key=lambda h: sum(hourly_performance[h]) / len(hourly_performance[h]))
        
        # Calculate confidence based on data consistency
        optimal_data = hourly_performance[optimal_hour]
        variance = sum((x - sum(optimal_data)/len(optimal_data))**2 for x in optimal_data) / len(optimal_data)
        confidence = max(0.1, min(1.0, 1.0 - (variance / 1000)))
        
        # Next occurrence of optimal hour
        now = datetime.now()
        next_optimal = now.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
        if next_optimal <= now:
            next_optimal += timedelta(days=1)
        
        return next_optimal, confidence
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate linear trend in values"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(i * values[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))
        
        # Linear regression slope
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def _update_patterns(self):
        """Update pattern analysis cache"""
        if len(self.performance_history) >= 10:
            recent = list(self.performance_history)[-10:]
            
            # Update moving averages
            self.pattern_cache['avg_cpu'] = sum(m.cpu_percent for m in recent) / len(recent)
            self.pattern_cache['avg_memory'] = sum(m.memory_percent for m in recent) / len(recent)
            
            # Update volatility measures
            cpu_values = [m.cpu_percent for m in recent]
            self.pattern_cache['cpu_volatility'] = max(cpu_values) - min(cpu_values)


class SmartResourceMonitor(QObject):
    """Smart resource monitoring with adaptive thresholds"""
    
    # Signals
    performance_updated = pyqtSignal(object)  # SystemMetrics
    threshold_exceeded = pyqtSignal(str, float, float)  # resource_type, current, threshold
    optimization_suggested = pyqtSignal(list)  # List[OptimizationSuggestion]
    emergency_stop_required = pyqtSignal(str)  # reason
    
    def __init__(self, monitoring_interval: int = 10):
        super().__init__()
        
        self.monitoring_interval = monitoring_interval
        self.predictor = PerformancePredictor()
        
        # Adaptive thresholds
        self.cpu_threshold = 70.0
        self.memory_threshold = 80.0
        self.emergency_cpu_threshold = 90.0
        self.emergency_memory_threshold = 95.0
        
        # Monitoring state
        self.is_monitoring = False
        self.consecutive_warnings = 0
        self.last_optimization_time = datetime.now()
        
        # Timer for monitoring
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._check_system_performance)
        
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self):
        """Start system performance monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_timer.start(self.monitoring_interval * 1000)
            self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop system performance monitoring"""
        if self.is_monitoring:
            self.is_monitoring = False
            self.monitor_timer.stop()
            self.logger.info("Performance monitoring stopped")
    
    def get_optimization_profile(self) -> AutomationProfile:
        """Generate optimization profile based on current system state"""
        current_metrics = SystemMetrics.collect_current()
        self.predictor.add_metrics(current_metrics)
        
        # Calculate optimal parameters based on performance level
        perf_level = current_metrics.performance_level
        
        if perf_level == SystemPerformance.CRITICAL:
            profile = AutomationProfile(
                optimal_batch_size=5,
                optimal_batch_delay=5.0,
                optimal_start_delay=8.0,
                max_concurrent_batches=1,
                cpu_threshold=60.0,
                memory_threshold=70.0,
                recommended_schedule="Schedule during low-usage hours",
                confidence_score=0.9
            )
        elif perf_level == SystemPerformance.POOR:
            profile = AutomationProfile(
                optimal_batch_size=10,
                optimal_batch_delay=4.0,
                optimal_start_delay=6.0,
                max_concurrent_batches=1,
                cpu_threshold=65.0,
                memory_threshold=75.0,
                recommended_schedule="Use smaller batches",
                confidence_score=0.8
            )
        elif perf_level == SystemPerformance.MODERATE:
            profile = AutomationProfile(
                optimal_batch_size=20,
                optimal_batch_delay=3.0,
                optimal_start_delay=4.0,
                max_concurrent_batches=2,
                cpu_threshold=70.0,
                memory_threshold=80.0,
                recommended_schedule="Standard automation",
                confidence_score=0.7
            )
        elif perf_level == SystemPerformance.GOOD:
            profile = AutomationProfile(
                optimal_batch_size=25,
                optimal_batch_delay=2.0,
                optimal_start_delay=3.0,
                max_concurrent_batches=2,
                cpu_threshold=75.0,
                memory_threshold=85.0,
                recommended_schedule="Optimal for automation",
                confidence_score=0.8
            )
        else:  # EXCELLENT
            profile = AutomationProfile(
                optimal_batch_size=30,
                optimal_batch_delay=1.5,
                optimal_start_delay=2.0,
                max_concurrent_batches=3,
                cpu_threshold=80.0,
                memory_threshold=90.0,
                recommended_schedule="Maximum performance mode",
                confidence_score=0.9
            )
        
        return profile
    
    def generate_optimization_suggestions(self) -> List[OptimizationSuggestion]:
        """Generate performance optimization suggestions"""
        current_metrics = SystemMetrics.collect_current()
        suggestions = []
        
        # CPU optimization suggestions
        if current_metrics.cpu_percent > 80:
            suggestions.append(OptimizationSuggestion(
                category="CPU",
                priority="high",
                description=f"High CPU usage detected: {current_metrics.cpu_percent:.1f}%",
                recommended_action="Reduce batch size or increase delays",
                expected_impact="30-50% CPU reduction"
            ))
        
        # Memory optimization suggestions
        if current_metrics.memory_percent > 85:
            suggestions.append(OptimizationSuggestion(
                category="Memory",
                priority="high",
                description=f"High memory usage detected: {current_metrics.memory_percent:.1f}%",
                recommended_action="Reduce concurrent processes",
                expected_impact="20-40% memory reduction"
            ))
        
        # Batch size optimization
        predicted_perf = self.predictor.predict_performance_trend(30)
        if predicted_perf in [SystemPerformance.POOR, SystemPerformance.CRITICAL]:
            suggestions.append(OptimizationSuggestion(
                category="Automation",
                priority="medium",
                description="System performance degradation predicted",
                recommended_action="Use adaptive batch sizing",
                expected_impact="Prevent system overload"
            ))
        
        # Timing optimization
        optimal_time, confidence = self.predictor.get_optimal_automation_timing()
        if confidence > 0.7:
            suggestions.append(OptimizationSuggestion(
                category="Scheduling",
                priority="low",
                description=f"Optimal automation time: {optimal_time.strftime('%H:%M')}",
                recommended_action=f"Schedule automation for {optimal_time.strftime('%H:%M')}",
                expected_impact=f"Up to 40% better performance (confidence: {confidence:.1%})"
            ))
        
        return suggestions
    
    def _check_system_performance(self):
        """Check current system performance and emit signals"""
        try:
            current_metrics = SystemMetrics.collect_current()
            self.predictor.add_metrics(current_metrics)
            
            # Emit performance update
            self.performance_updated.emit(current_metrics)
            
            # Check thresholds
            self._check_thresholds(current_metrics)
            
            # Generate optimization suggestions periodically
            if (datetime.now() - self.last_optimization_time).total_seconds() > 300:  # Every 5 minutes
                suggestions = self.generate_optimization_suggestions()
                if suggestions:
                    self.optimization_suggested.emit(suggestions)
                self.last_optimization_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error checking system performance: {e}")
    
    def _check_thresholds(self, metrics: SystemMetrics):
        """Check if system metrics exceed thresholds"""
        try:
            # Emergency thresholds
            if (metrics.cpu_percent >= self.emergency_cpu_threshold or 
                metrics.memory_percent >= self.emergency_memory_threshold):
                reason = f"Emergency: CPU {metrics.cpu_percent:.1f}%, Memory {metrics.memory_percent:.1f}%"
                self.emergency_stop_required.emit(reason)
                return
            
            # Warning thresholds
            if metrics.cpu_percent >= self.cpu_threshold:
                self.threshold_exceeded.emit("CPU", metrics.cpu_percent, self.cpu_threshold)
                self.consecutive_warnings += 1
            elif metrics.memory_percent >= self.memory_threshold:
                self.threshold_exceeded.emit("Memory", metrics.memory_percent, self.memory_threshold)
                self.consecutive_warnings += 1
            else:
                self.consecutive_warnings = 0
            
            # Adaptive threshold adjustment
            if self.consecutive_warnings >= 3:
                self._adjust_thresholds_down()
                self.consecutive_warnings = 0
            
        except Exception as e:
            self.logger.error(f"Error checking thresholds: {e}")
    
    def _adjust_thresholds_down(self):
        """Adjust thresholds down when system is consistently overloaded"""
        self.cpu_threshold = max(50.0, self.cpu_threshold - 5.0)
        self.memory_threshold = max(60.0, self.memory_threshold - 5.0)
        
        self.logger.info(f"Adjusted thresholds: CPU {self.cpu_threshold}%, Memory {self.memory_threshold}%")


class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self):
        self.monitor = SmartResourceMonitor()
        self.predictor = PerformancePredictor()
        self.logger = logging.getLogger(__name__)
    
    def optimize_automation_config(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize automation configuration based on current system state"""
        try:
            profile = self.monitor.get_optimization_profile()
            
            optimized_config = base_config.copy()
            optimized_config.update({
                'batch_size': profile.optimal_batch_size,
                'batch_delay': profile.optimal_batch_delay,
                'start_delay': profile.optimal_start_delay,
                'cpu_threshold': profile.cpu_threshold,
                'max_concurrent_batches': profile.max_concurrent_batches
            })
            
            self.logger.info(f"Configuration optimized with {profile.confidence_score:.1%} confidence")
            return optimized_config
            
        except Exception as e:
            self.logger.error(f"Error optimizing configuration: {e}")
            return base_config
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            current_metrics = SystemMetrics.collect_current()
            profile = self.monitor.get_optimization_profile()
            suggestions = self.monitor.generate_optimization_suggestions()
            
            optimal_time, confidence = self.predictor.get_optimal_automation_timing()
            predicted_perf = self.predictor.predict_performance_trend(30)
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'current_performance': {
                    'cpu': current_metrics.cpu_percent,
                    'memory': current_metrics.memory_percent,
                    'level': current_metrics.performance_level.value
                },
                'optimization_profile': {
                    'batch_size': profile.optimal_batch_size,
                    'batch_delay': profile.optimal_batch_delay,
                    'confidence': profile.confidence_score
                },
                'predictions': {
                    'trend_30min': predicted_perf.value,
                    'optimal_time': optimal_time.strftime('%H:%M'),
                    'timing_confidence': confidence
                },
                'suggestions': [
                    {
                        'category': s.category,
                        'priority': s.priority,
                        'description': s.description,
                        'action': s.recommended_action,
                        'impact': s.expected_impact
                    }
                    for s in suggestions
                ]
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
