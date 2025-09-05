#!/usr/bin/env python3
"""
🚀 Optimization Integration - Integration point for all performance optimizations
Seamlessly integrates adaptive configuration and enhanced monitoring with existing components
"""

from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from optimizations.adaptive_config import get_adaptive_config
from optimizations.enhanced_performance_monitor import get_enhanced_performance_monitor
from optimizations.smart_resource_manager import get_smart_resource_manager

class OptimizationIntegrator(QObject):
    """🚀 Central integration point for all optimization systems"""
    
    # Signals for UI updates
    optimization_status_changed = pyqtSignal(dict)  # Status updates for UI
    performance_alert = pyqtSignal(str, str)  # Alert type, message
    resource_pressure_changed = pyqtSignal(str)  # "low", "medium", "high", "critical"
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        
        # Get optimization components
        self.adaptive_config = get_adaptive_config()
        self.enhanced_monitor = get_enhanced_performance_monitor()
        self.resource_manager = get_smart_resource_manager()
        
        # Connect signals
        self._connect_optimization_signals()
        
        # Status update timer
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._emit_status_update)
        self._status_timer.start(10000)  # Update every 10 seconds
        
        # Integration state
        self._initialized = False
    
    def _connect_optimization_signals(self):
        """Connect optimization system signals"""
        try:
            # Enhanced monitor signals
            self.enhanced_monitor.performance_alert.connect(self._handle_performance_alert)
            self.enhanced_monitor.memory_pressure_changed.connect(self._handle_memory_pressure_change)
            self.enhanced_monitor.adaptive_optimization_applied.connect(self._handle_optimization_applied)
            
            # Resource manager signals
            self.resource_manager.memory_pressure_critical.connect(self._handle_critical_memory_pressure)
            self.resource_manager.resource_leak_detected.connect(self._handle_resource_leak)
            
        except Exception as e:
            print(f"⚠️ Error connecting optimization signals: {e}")
    
    def initialize(self) -> bool:
        """Initialize optimization integration"""
        if self._initialized:
            return True
            
        try:
            print("🚀 Initializing optimization integration...")
            
            # Register main window caches with resource manager if available
            if self.main_window:
                self._register_main_window_resources()
            
            # Apply initial adaptive configuration
            self.adaptive_config.apply_to_app_constants()
            
            self._initialized = True
            print("✅ Optimization integration initialized")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize optimization integration: {e}")
            return False
    
    def _register_main_window_resources(self):
        """Register main window resources for management"""
        try:
            # Register smart cache if available
            if hasattr(self.main_window, 'smart_cache'):
                self.resource_manager.register_cache('smart_cache', self.main_window.smart_cache)
            
            # Register other caches
            cache_attributes = [
                'instances_cache', 'settings_cache', 'log_cache', 
                'automation_cache', 'dashboard_cache'
            ]
            
            for attr_name in cache_attributes:
                if hasattr(self.main_window, attr_name):
                    cache = getattr(self.main_window, attr_name)
                    self.resource_manager.register_cache(attr_name, cache)
                    
            print("📋 Registered main window resources for optimization")
            
        except Exception as e:
            print(f"⚠️ Error registering main window resources: {e}")
    
    def _handle_performance_alert(self, alert):
        """Handle performance alerts from enhanced monitor"""
        try:
            # Convert alert to readable format
            alert_message = f"{alert.message} ({alert.severity})"
            self.performance_alert.emit(alert.alert_type, alert_message)
            
            # Log to main window if available
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"🎯 Performance Alert: {alert_message}",
                    level="WARNING" if alert.severity in ["medium", "high"] else "INFO",
                    category="Optimization"
                )
                
        except Exception as e:
            print(f"⚠️ Error handling performance alert: {e}")
    
    def _handle_memory_pressure_change(self, pressure_level: str):
        """Handle memory pressure level changes"""
        try:
            self.resource_pressure_changed.emit(pressure_level)
            
            # Log significant pressure changes
            if pressure_level in ["high", "critical"] and self.main_window:
                if hasattr(self.main_window, 'log_message'):
                    self.main_window.log_message(
                        f"🧠 Memory pressure: {pressure_level}",
                        level="WARNING" if pressure_level == "high" else "ERROR",
                        category="Resource Management"
                    )
                    
        except Exception as e:
            print(f"⚠️ Error handling memory pressure change: {e}")
    
    def _handle_optimization_applied(self, optimization_data: dict):
        """Handle when adaptive optimization is applied"""
        try:
            degradation = optimization_data.get('degradation_percent', 0)
            
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"🎯 Adaptive optimization applied (degradation: {degradation:.1f}%)",
                    level="INFO",
                    category="Optimization"
                )
                
        except Exception as e:
            print(f"⚠️ Error handling optimization applied: {e}")
    
    def _handle_critical_memory_pressure(self, memory_percent: float):
        """Handle critical memory pressure"""
        try:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"🚨 Critical memory pressure: {memory_percent:.1f}%",
                    level="ERROR",
                    category="Resource Management"
                )
                
        except Exception as e:
            print(f"⚠️ Error handling critical memory pressure: {e}")
    
    def _handle_resource_leak(self, resource_type: str, details: dict):
        """Handle resource leak detection"""
        try:
            growth = details.get('growth', 0)
            
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(
                    f"🚨 Resource leak detected: {resource_type} (+{growth} objects)",
                    level="WARNING",
                    category="Resource Management"
                )
                
        except Exception as e:
            print(f"⚠️ Error handling resource leak: {e}")
    
    def _emit_status_update(self):
        """Emit periodic status updates"""
        try:
            status = {
                "adaptive_config": self.adaptive_config.get_stats(),
                "performance_monitor": self.enhanced_monitor.get_performance_stats(),
                "resource_manager": self.resource_manager.get_resource_stats(),
                "timestamp": self.enhanced_monitor._snapshots[-1].timestamp if self.enhanced_monitor._snapshots else 0
            }
            
            self.optimization_status_changed.emit(status)
            
        except Exception as e:
            print(f"⚠️ Error emitting status update: {e}")
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get comprehensive optimization summary"""
        try:
            adaptive_stats = self.adaptive_config.get_stats()
            performance_stats = self.enhanced_monitor.get_performance_stats()
            resource_stats = self.resource_manager.get_resource_stats()
            
            return {
                "system_profile": adaptive_stats["system_profile"],
                "current_performance": performance_stats.get("current", {}),
                "resource_usage": resource_stats.get("current", {}),
                "optimization_status": {
                    "adaptive_enabled": True,
                    "monitoring_enabled": self.enhanced_monitor.monitoring_enabled,
                    "resource_management_enabled": resource_stats["management"]["enabled"],
                    "memory_pressure": resource_stats["management"]["memory_pressure_level"],
                },
                "recent_optimizations": resource_stats.get("recent_optimizations", [])
            }
            
        except Exception as e:
            print(f"⚠️ Error getting optimization summary: {e}")
            return {}
    
    def force_optimization_refresh(self):
        """Force refresh of optimization systems"""
        try:
            # Refresh adaptive configuration
            self.adaptive_config.refresh_system_profile()
            self.adaptive_config.apply_to_app_constants()
            
            print("🔄 Optimization systems refreshed")
            
        except Exception as e:
            print(f"⚠️ Error refreshing optimization systems: {e}")
    
    def cleanup(self):
        """Cleanup optimization integration"""
        try:
            self._status_timer.stop()
            
            # Disconnect signals
            try:
                self.enhanced_monitor.performance_alert.disconnect()
                self.enhanced_monitor.memory_pressure_changed.disconnect()
                self.enhanced_monitor.adaptive_optimization_applied.disconnect()
                self.resource_manager.memory_pressure_critical.disconnect()
                self.resource_manager.resource_leak_detected.disconnect()
            except:
                pass
                
            print("🚀 Optimization integration cleaned up")
            
        except Exception as e:
            print(f"⚠️ Error cleaning up optimization integration: {e}")

# Global optimization integrator instance
_global_optimization_integrator: Optional[OptimizationIntegrator] = None

def get_optimization_integrator(main_window=None) -> OptimizationIntegrator:
    """Get or create the global optimization integrator"""
    global _global_optimization_integrator
    
    if _global_optimization_integrator is None:
        _global_optimization_integrator = OptimizationIntegrator(main_window)
        
    return _global_optimization_integrator

def initialize_optimizations(main_window=None) -> bool:
    """Initialize optimization systems for the application"""
    integrator = get_optimization_integrator(main_window)
    return integrator.initialize()

def cleanup_optimizations():
    """Cleanup optimization systems"""
    global _global_optimization_integrator
    
    if _global_optimization_integrator:
        _global_optimization_integrator.cleanup()
        _global_optimization_integrator = None