"""
Integration Layer - Bridge between UI and Core Components
======================================================
Provides seamless integration between existing UI and new modular architecture.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QThread, QMutex
from PyQt6.QtWidgets import QWidget

from .automation_engine import AutomationEngine, AutomationConfig, AutomationMetrics
from .batch_processor import EnhancedBatchProcessor, BatchResult
from ..utils.performance_optimizer import PerformanceOptimizer, SmartResourceMonitor
from ..utils.state_manager import StateManager, get_global_state_manager


class AutomationIntegrationLayer(QObject):
    """Integration layer for automation components"""
    
    # Signals for UI updates
    automation_started = pyqtSignal()
    automation_stopped = pyqtSignal()
    automation_paused = pyqtSignal()
    automation_resumed = pyqtSignal()
    
    batch_started = pyqtSignal(int, int)  # batch_index, batch_size
    batch_completed = pyqtSignal(object)  # BatchResult
    batch_failed = pyqtSignal(int, str)   # batch_index, error
    
    instance_started = pyqtSignal(str)    # instance_name
    instance_completed = pyqtSignal(str, bool)  # instance_name, success
    instance_failed = pyqtSignal(str, str)      # instance_name, error
    
    performance_warning = pyqtSignal(str, float, float)  # resource_type, current, threshold
    optimization_suggested = pyqtSignal(list)            # optimization_suggestions
    emergency_stop_triggered = pyqtSignal(str)           # reason
    
    metrics_updated = pyqtSignal(object)  # AutomationMetrics
    progress_updated = pyqtSignal(float)  # progress_percentage
    
    def __init__(self, ui_component: QWidget = None):
        super().__init__()
        
        self.ui_component = ui_component
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.automation_engine = AutomationEngine()
        self.batch_processor = EnhancedBatchProcessor()
        self.performance_optimizer = PerformanceOptimizer()
        self.state_manager = get_global_state_manager()
        
        # Resource monitoring
        self.resource_monitor = SmartResourceMonitor()
        
        # Integration state
        self._is_integrated = False
        self._ui_callbacks: Dict[str, List[Callable]] = {}
        self._mutex = QMutex()
        
        # Progress tracking
        self._current_progress = 0.0
        self._total_instances = 0
        self._completed_instances = 0
        
        # Connect signals
        self._connect_signals()
        
        # Setup state observers
        self._setup_state_observers()
    
    def integrate_with_ui(self, ui_config: Dict[str, Any]) -> bool:
        """Integrate with existing UI components"""
        try:
            self._mutex.lock()
            
            if self._is_integrated:
                self.logger.warning("Already integrated with UI")
                return True
            
            # Extract UI configuration
            batch_size_widget = ui_config.get('batch_size_widget')
            batch_delay_widget = ui_config.get('batch_delay_widget')
            start_delay_widget = ui_config.get('start_delay_widget')
            progress_bar = ui_config.get('progress_bar')
            status_label = ui_config.get('status_label')
            log_widget = ui_config.get('log_widget')
            
            # Register UI callbacks
            if batch_size_widget:
                self.register_ui_callback('batch_size_changed', 
                    lambda value: self._update_automation_config({'batch_size': value}))
            
            if batch_delay_widget:
                self.register_ui_callback('batch_delay_changed',
                    lambda value: self._update_automation_config({'batch_delay': value}))
            
            if start_delay_widget:
                self.register_ui_callback('start_delay_changed',
                    lambda value: self._update_automation_config({'start_delay': value}))
            
            # Connect progress updates
            if progress_bar:
                self.progress_updated.connect(progress_bar.setValue)
            
            # Connect status updates
            if status_label:
                self.automation_started.connect(lambda: status_label.setText("Running"))
                self.automation_stopped.connect(lambda: status_label.setText("Stopped"))
                self.automation_paused.connect(lambda: status_label.setText("Paused"))
            
            # Connect log updates
            if log_widget:
                self.batch_started.connect(
                    lambda idx, size: self._log_message(log_widget, f"Started batch {idx+1} with {size} instances"))
                self.batch_completed.connect(
                    lambda result: self._log_message(log_widget, f"Batch completed: {result.successful_count}/{result.total_count} successful"))
                self.instance_failed.connect(
                    lambda name, error: self._log_message(log_widget, f"Instance {name} failed: {error}"))
            
            self._is_integrated = True
            self.logger.info("Successfully integrated with UI")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to integrate with UI: {e}")
            return False
        finally:
            self._mutex.unlock()
    
    def start_automation(self, instances: List[str], config: Dict[str, Any] = None) -> bool:
        """Start automation with integration support"""
        try:
            # Create automation config
            automation_config = AutomationConfig()
            if config:
                for key, value in config.items():
                    if hasattr(automation_config, key):
                        setattr(automation_config, key, value)
            
            # Optimize configuration
            optimized_config = self.performance_optimizer.optimize_automation_config(config or {})
            for key, value in optimized_config.items():
                if hasattr(automation_config, key):
                    setattr(automation_config, key, value)
            
            # Start resource monitoring
            self.resource_monitor.start_monitoring()
            
            # Initialize progress tracking
            self._total_instances = len(instances)
            self._completed_instances = 0
            self._update_progress()
            
            # Start automation engine
            success = self.automation_engine.start_automation(instances, automation_config)
            
            if success:
                self.automation_started.emit()
                self.state_manager.set('automation_running', True, 'integration_layer')
                self.logger.info(f"Started automation with {len(instances)} instances")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to start automation: {e}")
            return False
    
    def stop_automation(self, reason: str = "user_request") -> bool:
        """Stop automation with cleanup"""
        try:
            # Stop automation engine
            success = self.automation_engine.stop_automation()
            
            # Stop resource monitoring
            self.resource_monitor.stop_monitoring()
            
            # Stop batch processor
            self.batch_processor.stop_all_batches()
            
            if success:
                self.automation_stopped.emit()
                self.state_manager.set('automation_running', False, 'integration_layer')
                self.state_manager.set('stop_reason', reason, 'integration_layer')
                self.logger.info(f"Stopped automation: {reason}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to stop automation: {e}")
            return False
    
    def pause_automation(self) -> bool:
        """Pause automation"""
        try:
            success = self.automation_engine.pause_automation()
            if success:
                self.automation_paused.emit()
                self.state_manager.set('automation_paused', True, 'integration_layer')
                self.logger.info("Paused automation")
            return success
        except Exception as e:
            self.logger.error(f"Failed to pause automation: {e}")
            return False
    
    def resume_automation(self) -> bool:
        """Resume automation"""
        try:
            success = self.automation_engine.resume_automation()
            if success:
                self.automation_resumed.emit()
                self.state_manager.set('automation_paused', False, 'integration_layer')
                self.logger.info("Resumed automation")
            return success
        except Exception as e:
            self.logger.error(f"Failed to resume automation: {e}")
            return False
    
    def get_automation_status(self) -> Dict[str, Any]:
        """Get comprehensive automation status"""
        try:
            engine_status = self.automation_engine.get_status()
            performance_report = self.performance_optimizer.get_performance_report()
            
            return {
                'engine_status': engine_status,
                'performance_report': performance_report,
                'progress': self._current_progress,
                'total_instances': self._total_instances,
                'completed_instances': self._completed_instances,
                'is_running': self.state_manager.get('automation_running', False),
                'is_paused': self.state_manager.get('automation_paused', False),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get automation status: {e}")
            return {'error': str(e)}
    
    def register_ui_callback(self, event_name: str, callback: Callable):
        """Register UI callback for specific events"""
        if event_name not in self._ui_callbacks:
            self._ui_callbacks[event_name] = []
        self._ui_callbacks[event_name].append(callback)
    
    def trigger_ui_callback(self, event_name: str, *args, **kwargs):
        """Trigger registered UI callbacks"""
        if event_name in self._ui_callbacks:
            for callback in self._ui_callbacks[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error in UI callback {event_name}: {e}")
    
    def _connect_signals(self):
        """Connect internal signals"""
        # Automation engine signals
        self.automation_engine.batch_completed.connect(self._on_batch_completed)
        self.automation_engine.instance_completed.connect(self._on_instance_completed)
        self.automation_engine.automation_finished.connect(self._on_automation_finished)
        self.automation_engine.error_occurred.connect(self._on_automation_error)
        
        # Resource monitor signals
        self.resource_monitor.threshold_exceeded.connect(self._on_threshold_exceeded)
        self.resource_monitor.optimization_suggested.connect(self._on_optimization_suggested)
        self.resource_monitor.emergency_stop_required.connect(self._on_emergency_stop)
        self.resource_monitor.performance_updated.connect(self._on_performance_updated)
    
    def _setup_state_observers(self):
        """Setup state observers for important changes"""
        self.state_manager.add_observer('automation_running', self._on_automation_state_changed)
        self.state_manager.add_observer('automation_paused', self._on_automation_state_changed)
        self.state_manager.add_observer('cpu_threshold', self._on_threshold_changed)
        self.state_manager.add_observer('memory_threshold', self._on_threshold_changed)
    
    def _update_automation_config(self, updates: Dict[str, Any]):
        """Update automation configuration"""
        try:
            current_config = self.automation_engine.get_current_config()
            for key, value in updates.items():
                if hasattr(current_config, key):
                    setattr(current_config, key, value)
            
            self.automation_engine.update_config(current_config)
            self.logger.debug(f"Updated automation config: {updates}")
            
        except Exception as e:
            self.logger.error(f"Failed to update automation config: {e}")
    
    def _update_progress(self):
        """Update progress calculation"""
        if self._total_instances > 0:
            self._current_progress = (self._completed_instances / self._total_instances) * 100
        else:
            self._current_progress = 0.0
        
        self.progress_updated.emit(self._current_progress)
    
    def _log_message(self, log_widget, message: str):
        """Log message to UI widget"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            if hasattr(log_widget, 'append'):
                log_widget.append(formatted_message)
            elif hasattr(log_widget, 'addItem'):
                log_widget.addItem(formatted_message)
            elif hasattr(log_widget, 'setText'):
                current_text = log_widget.text()
                log_widget.setText(current_text + "\n" + formatted_message)
                
        except Exception as e:
            self.logger.error(f"Failed to log message to UI: {e}")
    
    # Signal handlers
    def _on_batch_completed(self, batch_result: BatchResult):
        """Handle batch completion"""
        self.batch_completed.emit(batch_result)
        self._completed_instances += batch_result.successful_count
        self._update_progress()
    
    def _on_instance_completed(self, instance_name: str, success: bool):
        """Handle instance completion"""
        if success:
            self.instance_completed.emit(instance_name, True)
        else:
            self.instance_failed.emit(instance_name, "Unknown error")
    
    def _on_automation_finished(self):
        """Handle automation completion"""
        self.stop_automation("completed")
    
    def _on_automation_error(self, error_message: str):
        """Handle automation error"""
        self.logger.error(f"Automation error: {error_message}")
        self.stop_automation(f"error: {error_message}")
    
    def _on_threshold_exceeded(self, resource_type: str, current: float, threshold: float):
        """Handle resource threshold exceeded"""
        self.performance_warning.emit(resource_type, current, threshold)
        
        # Auto-stop if critical thresholds are exceeded
        if resource_type == "CPU" and current >= 90:
            self.stop_automation(f"Critical CPU usage: {current:.1f}%")
        elif resource_type == "Memory" and current >= 95:
            self.stop_automation(f"Critical memory usage: {current:.1f}%")
    
    def _on_optimization_suggested(self, suggestions: List):
        """Handle optimization suggestions"""
        self.optimization_suggested.emit(suggestions)
    
    def _on_emergency_stop(self, reason: str):
        """Handle emergency stop"""
        self.emergency_stop_triggered.emit(reason)
        self.stop_automation(f"Emergency: {reason}")
    
    def _on_performance_updated(self, metrics):
        """Handle performance metrics update"""
        # Convert to AutomationMetrics if needed
        automation_metrics = self.automation_engine.get_metrics()
        self.metrics_updated.emit(automation_metrics)
    
    def _on_automation_state_changed(self, key: str, old_value: Any, new_value: Any):
        """Handle automation state changes"""
        self.logger.debug(f"Automation state changed: {key} = {new_value}")
    
    def _on_threshold_changed(self, key: str, old_value: Any, new_value: Any):
        """Handle threshold changes"""
        if key == 'cpu_threshold':
            self.resource_monitor.cpu_threshold = new_value
        elif key == 'memory_threshold':
            self.resource_monitor.memory_threshold = new_value
        
        self.logger.info(f"Updated {key} to {new_value}")


class UIBridge:
    """Bridge for backward compatibility with existing UI"""
    
    def __init__(self, integration_layer: AutomationIntegrationLayer):
        self.integration_layer = integration_layer
        self.logger = logging.getLogger(__name__)
    
    def start_automation_batch(self, instances: List[str], batch_size: int = 10, 
                              batch_delay: float = 2.0, start_delay: float = 3.0) -> bool:
        """Start automation with batch parameters (backward compatibility)"""
        config = {
            'batch_size': batch_size,
            'batch_delay': batch_delay,
            'start_delay': start_delay
        }
        return self.integration_layer.start_automation(instances, config)
    
    def stop_all_automation(self) -> bool:
        """Stop all automation (backward compatibility)"""
        return self.integration_layer.stop_automation("stop_all_request")
    
    def get_automation_progress(self) -> float:
        """Get automation progress (backward compatibility)"""
        status = self.integration_layer.get_automation_status()
        return status.get('progress', 0.0)
    
    def is_automation_running(self) -> bool:
        """Check if automation is running (backward compatibility)"""
        status = self.integration_layer.get_automation_status()
        return status.get('is_running', False)
    
    def pause_automation_batch(self) -> bool:
        """Pause automation (backward compatibility)"""
        return self.integration_layer.pause_automation()
    
    def resume_automation_batch(self) -> bool:
        """Resume automation (backward compatibility)"""
        return self.integration_layer.resume_automation()
    
    def get_system_performance(self) -> Dict[str, float]:
        """Get system performance metrics (backward compatibility)"""
        status = self.integration_layer.get_automation_status()
        performance = status.get('performance_report', {})
        current_perf = performance.get('current_performance', {})
        
        return {
            'cpu_percent': current_perf.get('cpu', 0.0),
            'memory_percent': current_perf.get('memory', 0.0),
            'performance_level': current_perf.get('level', 'unknown')
        }


# Factory functions for easy integration
def create_integration_layer(ui_component: QWidget = None) -> AutomationIntegrationLayer:
    """Create and configure integration layer"""
    return AutomationIntegrationLayer(ui_component)


def create_ui_bridge(integration_layer: AutomationIntegrationLayer) -> UIBridge:
    """Create UI bridge for backward compatibility"""
    return UIBridge(integration_layer)
