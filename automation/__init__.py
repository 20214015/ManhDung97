"""
Automation Module Initialization
===============================
Initialize the automation module and provide public interfaces.
"""

from .core.automation_engine import AutomationEngine, AutomationConfig, AutomationMetrics
from .core.batch_processor import EnhancedBatchProcessor, BatchResult, RetryManager
from .core.integration_layer import AutomationIntegrationLayer, UIBridge, create_integration_layer, create_ui_bridge
from .ui.automation_widgets import ModernAutomationWidget, EnhancedControlPanel, PerformanceMonitor, AutomationLog
from .utils.performance_optimizer import PerformanceOptimizer, SmartResourceMonitor, SystemMetrics
from .utils.state_manager import StateManager, get_global_state_manager, get_state, set_state, observe_state

# Version information
__version__ = "1.0.0"
__author__ = "Automation Team"
__description__ = "Modern automation system with AI optimization and performance monitoring"

# Public API
__all__ = [
    # Core components
    "AutomationEngine",
    "AutomationConfig", 
    "AutomationMetrics",
    "EnhancedBatchProcessor",
    "BatchResult",
    "RetryManager",
    
    # Integration layer
    "AutomationIntegrationLayer",
    "UIBridge",
    "create_integration_layer",
    "create_ui_bridge",
    
    # UI components
    "ModernAutomationWidget",
    "EnhancedControlPanel",
    "PerformanceMonitor",
    "AutomationLog",
    
    # Utils
    "PerformanceOptimizer",
    "SmartResourceMonitor",
    "SystemMetrics",
    "StateManager",
    "get_global_state_manager",
    "get_state",
    "set_state",
    "observe_state",
]

def get_version():
    """Get module version"""
    return __version__

def get_module_info():
    """Get module information"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "core": ["AutomationEngine", "BatchProcessor", "IntegrationLayer"],
            "ui": ["ModernAutomationWidget", "ControlPanel", "PerformanceMonitor"],
            "utils": ["PerformanceOptimizer", "StateManager"]
        }
    }
