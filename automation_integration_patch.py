"""
Integration Patch for Monokai Automation Page
============================================
Patch to integrate new modular architecture with existing UI.
"""

import logging
from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget

# Import new automation modules
try:
    from automation.core.integration_layer import AutomationIntegrationLayer, UIBridge
    from automation.core.automation_engine import AutomationConfig
    from automation.utils.performance_optimizer import PerformanceOptimizer
    from automation.utils.state_manager import get_global_state_manager
    AUTOMATION_MODULES_AVAILABLE = True
except ImportError:
    AUTOMATION_MODULES_AVAILABLE = False


class MonokaiAutomationPatch(QObject):
    """Patch class to enhance existing MonokaiAutomationPage with new modules"""
    
    # Signals for backward compatibility
    automation_started = pyqtSignal()
    automation_stopped = pyqtSignal()
    automation_paused = pyqtSignal()
    progress_updated = pyqtSignal(float)
    log_message = pyqtSignal(str, str)  # message, level
    
    def __init__(self, automation_page: QWidget):
        super().__init__()
        
        self.automation_page = automation_page
        self.logger = logging.getLogger(__name__)
        
        # Check if new modules are available
        if not AUTOMATION_MODULES_AVAILABLE:
            self.logger.warning("New automation modules not available, falling back to legacy mode")
            self.enhanced_mode = False
            return
        
        self.enhanced_mode = True
        
        # Initialize new components
        self.integration_layer = None
        self.ui_bridge = None
        self.performance_optimizer = None
        self.state_manager = None
        
        # Setup integration
        self._setup_integration()
        
        # Migrate existing settings
        self._migrate_settings()
        
        # Connect signals
        self._connect_signals()
        
        self.logger.info("Successfully patched MonokaiAutomationPage with new modules")
    
    def _setup_integration(self):
        """Setup integration layer and components"""
        try:
            # Create integration layer
            self.integration_layer = AutomationIntegrationLayer(self.automation_page)
            
            # Create UI bridge for backward compatibility
            self.ui_bridge = UIBridge(self.integration_layer)
            
            # Get performance optimizer
            self.performance_optimizer = PerformanceOptimizer()
            
            # Get state manager
            self.state_manager = get_global_state_manager()
            
            # Configure integration with existing UI components
            ui_config = self._extract_ui_config()
            self.integration_layer.integrate_with_ui(ui_config)
            
        except Exception as e:
            self.logger.error(f"Failed to setup integration: {e}")
            self.enhanced_mode = False
    
    def _extract_ui_config(self) -> Dict[str, Any]:
        """Extract UI configuration from existing automation page"""
        ui_config = {}
        
        try:
            page = self.automation_page
            
            # Extract common UI elements
            if hasattr(page, 'batch_size_spin'):
                ui_config['batch_size_widget'] = page.batch_size_spin
                
            if hasattr(page, 'batch_delay_spin'):
                ui_config['batch_delay_widget'] = page.batch_delay_spin
                
            if hasattr(page, 'start_delay_spin'):
                ui_config['start_delay_widget'] = page.start_delay_spin
                
            if hasattr(page, 'progress_bar'):
                ui_config['progress_bar'] = page.progress_bar
                
            if hasattr(page, 'status_label'):
                ui_config['status_label'] = page.status_label
                
            if hasattr(page, 'log_text') or hasattr(page, 'log_list'):
                ui_config['log_widget'] = getattr(page, 'log_text', getattr(page, 'log_list', None))
            
        except Exception as e:
            self.logger.error(f"Error extracting UI config: {e}")
        
        return ui_config
    
    def _migrate_settings(self):
        """Migrate existing automation settings to new state manager"""
        try:
            if not hasattr(self.automation_page, 'automation_settings'):
                return
            
            old_settings = self.automation_page.automation_settings
            
            # Migrate to new state manager
            for key, value in old_settings.items():
                self.state_manager.set(f'automation_{key}', value, source='migration')
            
            # Migrate automation state
            if hasattr(self.automation_page, 'automation_state'):
                old_state = self.automation_page.automation_state
                for key, value in old_state.items():
                    self.state_manager.set(f'automation_state_{key}', value, source='migration')
            
            # Migrate AI predictions if available
            if hasattr(self.automation_page, 'ai_predictions'):
                ai_data = self.automation_page.ai_predictions
                for key, value in ai_data.items():
                    self.state_manager.set(f'ai_{key}', value, source='migration')
            
            self.logger.info("Successfully migrated existing settings to new state manager")
            
        except Exception as e:
            self.logger.error(f"Error migrating settings: {e}")
    
    def _connect_signals(self):
        """Connect signals between old and new systems"""
        try:
            if not self.integration_layer:
                return
            
            # Connect integration layer signals to automation page methods
            self.integration_layer.automation_started.connect(self._on_automation_started)
            self.integration_layer.automation_stopped.connect(self._on_automation_stopped)
            self.integration_layer.automation_paused.connect(self._on_automation_paused)
            self.integration_layer.progress_updated.connect(self._on_progress_updated)
            self.integration_layer.performance_warning.connect(self._on_performance_warning)
            self.integration_layer.emergency_stop_triggered.connect(self._on_emergency_stop)
            
            # Connect our signals to automation page if it has corresponding methods
            page = self.automation_page
            
            self.automation_started.connect(
                lambda: self._call_page_method('on_automation_started'))
            self.automation_stopped.connect(
                lambda: self._call_page_method('on_automation_stopped'))
            self.automation_paused.connect(
                lambda: self._call_page_method('on_automation_paused'))
            self.progress_updated.connect(
                lambda progress: self._call_page_method('update_progress', progress))
            self.log_message.connect(
                lambda msg, level: self._call_page_method('add_log', msg, level))
            
        except Exception as e:
            self.logger.error(f"Error connecting signals: {e}")
    
    def _call_page_method(self, method_name: str, *args, **kwargs):
        """Safely call method on automation page"""
        try:
            if hasattr(self.automation_page, method_name):
                method = getattr(self.automation_page, method_name)
                if callable(method):
                    method(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error calling page method {method_name}: {e}")
    
    # Enhanced automation methods
    def start_automation_enhanced(self, instances: list = None, **kwargs) -> bool:
        """Enhanced automation start with new modules"""
        if not self.enhanced_mode:
            return self._fallback_start_automation()
        
        try:
            # Get instances from automation page if not provided
            if instances is None:
                instances = self._get_instances_from_page()
            
            # Create configuration from current settings
            config = self._create_automation_config()
            
            # Start with integration layer
            success = self.integration_layer.start_automation(instances, config)
            
            if success:
                # Update page state
                self._update_page_automation_state(True, False)
                self.log_message.emit("✅ Enhanced automation started", "success")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error starting enhanced automation: {e}")
            self.log_message.emit(f"❌ Failed to start enhanced automation: {e}", "error")
            return False
    
    def stop_automation_enhanced(self, reason: str = "user_request") -> bool:
        """Enhanced automation stop"""
        if not self.enhanced_mode:
            return self._fallback_stop_automation()
        
        try:
            success = self.integration_layer.stop_automation(reason)
            
            if success:
                self._update_page_automation_state(False, False)
                self.log_message.emit(f"🛑 Enhanced automation stopped: {reason}", "warning")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error stopping enhanced automation: {e}")
            return False
    
    def pause_automation_enhanced(self) -> bool:
        """Enhanced automation pause"""
        if not self.enhanced_mode:
            return self._fallback_pause_automation()
        
        try:
            success = self.integration_layer.pause_automation()
            
            if success:
                self._update_page_automation_state(True, True)
                self.log_message.emit("⏸️ Enhanced automation paused", "warning")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error pausing enhanced automation: {e}")
            return False
    
    def resume_automation_enhanced(self) -> bool:
        """Enhanced automation resume"""
        if not self.enhanced_mode:
            return self._fallback_resume_automation()
        
        try:
            success = self.integration_layer.resume_automation()
            
            if success:
                self._update_page_automation_state(True, False)
                self.log_message.emit("▶️ Enhanced automation resumed", "success")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error resuming enhanced automation: {e}")
            return False
    
    def get_automation_status_enhanced(self) -> Dict[str, Any]:
        """Get enhanced automation status"""
        if not self.enhanced_mode:
            return self._fallback_get_status()
        
        try:
            return self.integration_layer.get_automation_status()
        except Exception as e:
            self.logger.error(f"Error getting enhanced status: {e}")
            return {'error': str(e)}
    
    def _create_automation_config(self) -> Dict[str, Any]:
        """Create automation config from current page settings"""
        try:
            page = self.automation_page
            
            config = {}
            
            # Extract settings from UI
            if hasattr(page, 'automation_settings'):
                settings = page.automation_settings
                config.update({
                    'batch_size': settings.get('batch_size', 10),
                    'batch_delay': settings.get('batch_delay', 2.0),
                    'start_delay': settings.get('start_delay', 3.0),
                })
            
            # Extract from spinboxes if available
            if hasattr(page, 'batch_size_spin'):
                config['batch_size'] = page.batch_size_spin.value()
            if hasattr(page, 'batch_delay_spin'):
                config['batch_delay'] = page.batch_delay_spin.value()
            if hasattr(page, 'start_delay_spin'):
                config['start_delay'] = page.start_delay_spin.value()
            
            # CPU threshold
            if hasattr(page, 'cpu_threshold'):
                config['cpu_threshold'] = page.cpu_threshold
            else:
                config['cpu_threshold'] = 70.0
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error creating automation config: {e}")
            return {'batch_size': 10, 'batch_delay': 2.0, 'start_delay': 3.0, 'cpu_threshold': 70.0}
    
    def _get_instances_from_page(self) -> list:
        """Get instances list from automation page"""
        try:
            page = self.automation_page
            
            # Try to get from common sources
            if hasattr(page, 'get_selected_instances'):
                return page.get_selected_instances()
            
            if hasattr(page, 'automation_settings'):
                settings = page.automation_settings
                from_instance = settings.get('from_instance', 0)
                to_instance = settings.get('to_instance', 10)
                return list(range(from_instance, to_instance + 1))
            
            # Default fallback
            return list(range(0, 10))
            
        except Exception as e:
            self.logger.error(f"Error getting instances from page: {e}")
            return list(range(0, 10))
    
    def _update_page_automation_state(self, running: bool, paused: bool):
        """Update automation page state"""
        try:
            page = self.automation_page
            
            # Update legacy properties
            if hasattr(page, 'automation_running'):
                page.automation_running = running
            if hasattr(page, 'automation_paused'):
                page.automation_paused = paused
            
            # Update automation_state dict if available
            if hasattr(page, 'automation_state'):
                page.automation_state.update({
                    'running': running,
                    'paused': paused
                })
            
        except Exception as e:
            self.logger.error(f"Error updating page automation state: {e}")
    
    # Signal handlers
    def _on_automation_started(self):
        """Handle automation started signal"""
        self.automation_started.emit()
    
    def _on_automation_stopped(self):
        """Handle automation stopped signal"""
        self.automation_stopped.emit()
    
    def _on_automation_paused(self):
        """Handle automation paused signal"""
        self.automation_paused.emit()
    
    def _on_progress_updated(self, progress: float):
        """Handle progress updated signal"""
        self.progress_updated.emit(progress)
    
    def _on_performance_warning(self, resource_type: str, current: float, threshold: float):
        """Handle performance warning"""
        message = f"⚠️ {resource_type} usage high: {current:.1f}% (threshold: {threshold:.1f}%)"
        self.log_message.emit(message, "warning")
    
    def _on_emergency_stop(self, reason: str):
        """Handle emergency stop"""
        message = f"🚨 Emergency stop triggered: {reason}"
        self.log_message.emit(message, "error")
    
    # Fallback methods for non-enhanced mode
    def _fallback_start_automation(self) -> bool:
        """Fallback start automation using existing methods"""
        try:
            if hasattr(self.automation_page, 'start_automation'):
                return self.automation_page.start_automation()
            return False
        except Exception as e:
            self.logger.error(f"Fallback start automation error: {e}")
            return False
    
    def _fallback_stop_automation(self) -> bool:
        """Fallback stop automation"""
        try:
            if hasattr(self.automation_page, 'stop_automation'):
                return self.automation_page.stop_automation()
            return False
        except Exception as e:
            self.logger.error(f"Fallback stop automation error: {e}")
            return False
    
    def _fallback_pause_automation(self) -> bool:
        """Fallback pause automation"""
        try:
            if hasattr(self.automation_page, 'pause_automation'):
                return self.automation_page.pause_automation()
            return False
        except Exception as e:
            self.logger.error(f"Fallback pause automation error: {e}")
            return False
    
    def _fallback_resume_automation(self) -> bool:
        """Fallback resume automation"""
        try:
            if hasattr(self.automation_page, 'resume_automation'):
                return self.automation_page.resume_automation()
            return False
        except Exception as e:
            self.logger.error(f"Fallback resume automation error: {e}")
            return False
    
    def _fallback_get_status(self) -> Dict[str, Any]:
        """Fallback get status"""
        try:
            page = self.automation_page
            return {
                'is_running': getattr(page, 'automation_running', False),
                'is_paused': getattr(page, 'automation_paused', False),
                'progress': getattr(page, 'current_progress', 0),
                'mode': 'legacy'
            }
        except Exception as e:
            return {'error': str(e), 'mode': 'legacy'}


def apply_automation_patch(automation_page: QWidget) -> MonokaiAutomationPatch:
    """Apply automation patch to existing MonokaiAutomationPage"""
    return MonokaiAutomationPatch(automation_page)


def is_enhanced_mode_available() -> bool:
    """Check if enhanced mode is available"""
    return AUTOMATION_MODULES_AVAILABLE
