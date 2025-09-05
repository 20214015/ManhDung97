"""
Automation Engine - Core Logic
==============================
Centralized automation logic extracted from monokai_automation_page.py
Provides clean separation of automation logic from UI code.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import psutil
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QThread, QThreadPool
from PyQt6.QtWidgets import QApplication


class AutomationState(Enum):
    """Automation states"""
    IDLE = "idle"
    RUNNING = "running" 
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class AutomationConfig:
    """Automation configuration settings"""
    from_instance: int = 1
    to_instance: int = 1200
    batch_size: int = 20
    batch_delay: float = 20.0
    start_delay: float = 4.0
    cpu_threshold: float = 70.0
    max_retries: int = 3
    enable_ai_optimization: bool = True
    enable_cpu_protection: bool = True


@dataclass
class AutomationMetrics:
    """Real-time automation metrics"""
    total_instances: int = 0
    processed_instances: int = 0
    successful_instances: int = 0
    failed_instances: int = 0
    current_batch: int = 0
    total_batches: int = 0
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    throughput: float = 0.0  # instances per minute
    success_rate: float = 100.0
    system_efficiency: float = 100.0
    
    def update_metrics(self):
        """Update calculated metrics"""
        if self.processed_instances > 0:
            self.success_rate = (self.successful_instances / self.processed_instances) * 100
            
        if self.start_time and self.processed_instances > 0:
            elapsed = datetime.now() - self.start_time
            if elapsed.total_seconds() > 0:
                self.throughput = (self.processed_instances / elapsed.total_seconds()) * 60


class SmartBatchOptimizer:
    """AI-powered batch optimization"""
    
    def __init__(self):
        self.learning_data = []
        self.performance_history = []
        
    def calculate_optimal_batch_size(self, cpu_usage: float, memory_usage: float, 
                                   base_batch_size: int = 20) -> int:
        """Calculate optimal batch size based on system performance"""
        try:
            # AI logic: Adjust batch size based on system load
            if cpu_usage >= 80 or memory_usage >= 85:
                optimal_size = max(5, base_batch_size // 4)  # Slow system
            elif cpu_usage >= 60 or memory_usage >= 70:
                optimal_size = max(10, base_batch_size // 2)  # Moderate system
            elif cpu_usage < 30 and memory_usage < 50:
                optimal_size = min(30, int(base_batch_size * 1.5))  # Fast system
            else:
                optimal_size = base_batch_size  # Standard system
                
            return optimal_size
        except Exception as e:
            logging.error(f"Batch optimization error: {e}")
            return base_batch_size
    
    def calculate_adaptive_delay(self, cpu_usage: float, memory_usage: float, 
                               base_delay: float = 4.0) -> float:
        """Calculate adaptive delay based on system performance"""
        try:
            performance_factor = (cpu_usage + memory_usage) / 200  # 0.0 to 1.0
            adaptive_delay = base_delay * (1 + performance_factor * 2)  # 1x to 3x base delay
            return min(adaptive_delay, 10.0)  # Cap at 10 seconds
        except Exception as e:
            logging.error(f"Adaptive delay calculation error: {e}")
            return base_delay


class AutomationEngine(QObject):
    """
    Enhanced Automation Engine with AI optimization and error handling
    """
    
    # Signals
    state_changed = pyqtSignal(str)  # AutomationState
    progress_updated = pyqtSignal(int, int)  # current, total
    metrics_updated = pyqtSignal(dict)  # metrics data
    batch_started = pyqtSignal(int, list)  # batch_number, instances
    batch_completed = pyqtSignal(int, dict)  # batch_number, results
    instance_processed = pyqtSignal(int, bool, str)  # instance_id, success, message
    error_occurred = pyqtSignal(str, str)  # error_type, message
    log_message = pyqtSignal(str, str)  # message, level
    
    def __init__(self, backend_manager=None, parent=None):
        super().__init__(parent)
        
        # Core components
        self.backend_manager = backend_manager
        self.batch_optimizer = SmartBatchOptimizer()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)
        
        # State management
        self.state = AutomationState.IDLE
        self.config = AutomationConfig()
        self.metrics = AutomationMetrics()
        
        # Runtime data
        self.instance_batches: List[List[int]] = []
        self.current_batch_index = 0
        self.batch_timer = QTimer()
        self.batch_timer.timeout.connect(self._process_next_batch)
        self.batch_timer.setSingleShot(True)
        
        # CPU monitoring
        self.cpu_monitor_timer = QTimer()
        self.cpu_monitor_timer.timeout.connect(self._check_system_resources)
        self.cpu_monitor_timer.start(10000)  # Check every 10 seconds
        
        self.logger = logging.getLogger(__name__)
        
    def start_automation(self, config: AutomationConfig) -> bool:
        """Start automation with given configuration"""
        try:
            if self.state != AutomationState.IDLE:
                self.log_message.emit("❌ Automation is already running", "warning")
                return False
                
            self.config = config
            self.metrics = AutomationMetrics()
            self.metrics.start_time = datetime.now()
            
            # Validate configuration
            if not self._validate_config():
                return False
                
            # Initialize automation
            if not self._initialize_automation():
                return False
                
            # Start first batch
            self._set_state(AutomationState.RUNNING)
            self._schedule_next_batch(delay=self.config.start_delay)
            
            self.log_message.emit(f"✅ Automation started: {self.metrics.total_instances} instances in {self.metrics.total_batches} batches", "success")
            return True
            
        except Exception as e:
            self.error_occurred.emit("start_error", str(e))
            self._set_state(AutomationState.ERROR)
            return False
    
    def pause_automation(self) -> bool:
        """Pause running automation"""
        try:
            if self.state == AutomationState.RUNNING:
                self._set_state(AutomationState.PAUSED)
                self.batch_timer.stop()
                self.log_message.emit("⏸️ Automation paused", "warning")
                return True
            return False
        except Exception as e:
            self.error_occurred.emit("pause_error", str(e))
            return False
    
    def resume_automation(self) -> bool:
        """Resume paused automation"""
        try:
            if self.state == AutomationState.PAUSED:
                self._set_state(AutomationState.RUNNING)
                self._schedule_next_batch(delay=1.0)  # Resume quickly
                self.log_message.emit("▶️ Automation resumed", "info")
                return True
            return False
        except Exception as e:
            self.error_occurred.emit("resume_error", str(e))
            return False
    
    def stop_automation(self) -> bool:
        """Stop running automation"""
        try:
            if self.state in [AutomationState.RUNNING, AutomationState.PAUSED]:
                self._set_state(AutomationState.STOPPING)
                self.batch_timer.stop()
                self.thread_pool.clear()  # Cancel pending tasks
                
                # Allow running tasks to complete
                if self.thread_pool.activeThreadCount() > 0:
                    self.thread_pool.waitForDone(5000)  # Wait max 5 seconds
                
                self._set_state(AutomationState.IDLE)
                self.log_message.emit("⏹️ Automation stopped", "error")
                return True
            return False
        except Exception as e:
            self.error_occurred.emit("stop_error", str(e))
            return False
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current automation metrics"""
        self.metrics.update_metrics()
        return {
            'state': self.state.value,
            'total_instances': self.metrics.total_instances,
            'processed_instances': self.metrics.processed_instances,
            'successful_instances': self.metrics.successful_instances,
            'failed_instances': self.metrics.failed_instances,
            'current_batch': self.metrics.current_batch,
            'total_batches': self.metrics.total_batches,
            'throughput': self.metrics.throughput,
            'success_rate': self.metrics.success_rate,
            'system_efficiency': self.metrics.system_efficiency,
            'eta': self._calculate_eta()
        }
    
    def update_config(self, **kwargs) -> bool:
        """Update automation configuration"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            return True
        except Exception as e:
            self.error_occurred.emit("config_error", str(e))
            return False
    
    # Private methods
    
    def _validate_config(self) -> bool:
        """Validate automation configuration"""
        try:
            if self.config.from_instance > self.config.to_instance:
                self.error_occurred.emit("config_error", "From instance cannot be greater than to instance")
                return False
                
            if self.config.batch_size <= 0:
                self.error_occurred.emit("config_error", "Batch size must be positive")
                return False
                
            if not self.backend_manager:
                self.error_occurred.emit("config_error", "Backend manager not available")
                return False
                
            return True
        except Exception as e:
            self.error_occurred.emit("validation_error", str(e))
            return False
    
    def _initialize_automation(self) -> bool:
        """Initialize automation data structures"""
        try:
            # Create instance range
            instance_range = list(range(self.config.from_instance, self.config.to_instance + 1))
            self.metrics.total_instances = len(instance_range)
            
            if self.metrics.total_instances == 0:
                self.error_occurred.emit("init_error", "No instances in range")
                return False
            
            # Optimize batch size if AI optimization is enabled
            if self.config.enable_ai_optimization:
                cpu_usage = psutil.cpu_percent(interval=1)
                memory_usage = psutil.virtual_memory().percent
                optimized_batch_size = self.batch_optimizer.calculate_optimal_batch_size(
                    cpu_usage, memory_usage, self.config.batch_size
                )
                
                if optimized_batch_size != self.config.batch_size:
                    self.log_message.emit(
                        f"🤖 AI Optimization: Batch size adjusted from {self.config.batch_size} to {optimized_batch_size}",
                        "info"
                    )
                    self.config.batch_size = optimized_batch_size
            
            # Create batches
            self.instance_batches = [
                instance_range[i:i + self.config.batch_size]
                for i in range(0, len(instance_range), self.config.batch_size)
            ]
            
            self.metrics.total_batches = len(self.instance_batches)
            self.current_batch_index = 0
            
            self.log_message.emit(
                f"📦 Initialized {self.metrics.total_batches} batches with {self.config.batch_size} instances each",
                "info"
            )
            
            return True
            
        except Exception as e:
            self.error_occurred.emit("init_error", str(e))
            return False
    
    def _set_state(self, new_state: AutomationState):
        """Update automation state and emit signal"""
        if self.state != new_state:
            self.state = new_state
            self.state_changed.emit(new_state.value)
    
    def _schedule_next_batch(self, delay: float = None):
        """Schedule next batch processing"""
        if delay is None:
            delay = self.config.batch_delay
            
        self.batch_timer.start(int(delay * 1000))
    
    def _process_next_batch(self):
        """Process the next batch of instances"""
        try:
            if self.state != AutomationState.RUNNING:
                return
                
            if self.current_batch_index >= len(self.instance_batches):
                # All batches completed
                self._complete_automation()
                return
            
            current_batch = self.instance_batches[self.current_batch_index]
            self.metrics.current_batch = self.current_batch_index + 1
            
            self.batch_started.emit(self.current_batch_index + 1, current_batch)
            self.log_message.emit(
                f"🔄 Processing batch {self.current_batch_index + 1}/{self.metrics.total_batches}: {len(current_batch)} instances",
                "info"
            )
            
            # Process batch asynchronously
            self._process_batch_async(current_batch)
            
        except Exception as e:
            self.error_occurred.emit("batch_error", str(e))
    
    def _process_batch_async(self, instances: List[int]):
        """Process batch instances asynchronously"""
        # This would be implemented with actual MuMu Manager calls
        # For now, simulate the processing
        from PyQt6.QtCore import QTimer
        
        def simulate_batch_processing():
            try:
                batch_results = {}
                for instance_id in instances:
                    # Simulate instance processing
                    success = True  # In real implementation, call backend
                    message = f"Instance {instance_id} started successfully"
                    
                    batch_results[instance_id] = {
                        'success': success,
                        'message': message
                    }
                    
                    if success:
                        self.metrics.successful_instances += 1
                    else:
                        self.metrics.failed_instances += 1
                    
                    self.metrics.processed_instances += 1
                    self.instance_processed.emit(instance_id, success, message)
                
                # Batch completed
                self.batch_completed.emit(self.current_batch_index + 1, batch_results)
                self.current_batch_index += 1
                
                # Update progress
                self.progress_updated.emit(self.metrics.processed_instances, self.metrics.total_instances)
                self.metrics_updated.emit(self.get_current_metrics())
                
                # Schedule next batch
                if self.current_batch_index < len(self.instance_batches):
                    self._schedule_next_batch()
                else:
                    self._complete_automation()
                    
            except Exception as e:
                self.error_occurred.emit("processing_error", str(e))
        
        # Simulate async processing with timer
        QTimer.singleShot(int(self.config.start_delay * 1000), simulate_batch_processing)
    
    def _complete_automation(self):
        """Complete automation and update final metrics"""
        try:
            self._set_state(AutomationState.IDLE)
            self.metrics.update_metrics()
            
            completion_time = datetime.now()
            total_time = completion_time - self.metrics.start_time if self.metrics.start_time else timedelta(0)
            
            self.log_message.emit(
                f"🎉 Automation completed! Processed {self.metrics.processed_instances} instances in {total_time}",
                "success"
            )
            
            self.metrics_updated.emit(self.get_current_metrics())
            
        except Exception as e:
            self.error_occurred.emit("completion_error", str(e))
    
    def _check_system_resources(self):
        """Monitor system resources and apply protection if needed"""
        try:
            if not self.config.enable_cpu_protection:
                return
                
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            
            if cpu_usage >= self.config.cpu_threshold:
                self.log_message.emit(
                    f"🚨 CPU threshold exceeded: {cpu_usage:.1f}% (limit: {self.config.cpu_threshold}%)",
                    "error"
                )
                self.stop_automation()
                self.error_occurred.emit("resource_protection", f"CPU usage too high: {cpu_usage:.1f}%")
                
            # Update system efficiency metric
            self.metrics.system_efficiency = max(0, 100 - max(cpu_usage, memory_usage))
            
        except Exception as e:
            self.logger.error(f"Resource monitoring error: {e}")
    
    def _calculate_eta(self) -> str:
        """Calculate estimated time to completion"""
        try:
            if (self.metrics.start_time and 
                self.metrics.processed_instances > 0 and 
                self.metrics.total_instances > 0):
                
                elapsed = datetime.now() - self.metrics.start_time
                progress_ratio = self.metrics.processed_instances / self.metrics.total_instances
                
                if progress_ratio > 0:
                    total_estimated = elapsed / progress_ratio
                    remaining = total_estimated - elapsed
                    
                    remaining_minutes = int(remaining.total_seconds() // 60)
                    remaining_seconds = int(remaining.total_seconds() % 60)
                    
                    return f"{remaining_minutes:02d}:{remaining_seconds:02d}"
                    
        except Exception as e:
            self.logger.error(f"ETA calculation error: {e}")
            
        return "Calculating..."
