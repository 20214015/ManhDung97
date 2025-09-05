"""
Enhanced Monokai Automation Page
===============================
Enhanced version of automation page with modern architecture integration.
"""

import logging
from typing import Dict, List, Optional, Any
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget

from automation_integration_patch import apply_automation_patch, is_enhanced_mode_available


class EnhancedMonokaiAutomationPage(QWidget):
    """Enhanced automation page with modern architecture"""
    
    # Signals
    automation_state_changed = pyqtSignal(bool, bool)  # running, paused
    performance_alert = pyqtSignal(str, str)           # message, level
    optimization_applied = pyqtSignal(dict)            # optimization_info
    
    def __init__(self, original_page: QWidget, parent=None):
        super().__init__(parent)
        
        self.original_page = original_page
        self.logger = logging.getLogger(__name__)
        
        # Apply integration patch
        self.automation_patch = apply_automation_patch(original_page)
        
        # Check if enhanced mode is available
        self.enhanced_mode = is_enhanced_mode_available()
        
        if self.enhanced_mode:
            self.logger.info("Enhanced automation mode ENABLED")
        else:
            self.logger.warning("Enhanced automation mode DISABLED - using legacy mode")
        
        # Setup enhanced UI
        self._setup_enhanced_ui()
        
        # Connect signals
        self._connect_enhanced_signals()
        
        # Initialize enhanced features
        self._initialize_enhanced_features()
    
    def _setup_enhanced_ui(self):
        """Setup enhanced UI layout"""
        layout = QVBoxLayout(self)
        
        # Create tab widget for enhanced features
        self.tab_widget = QTabWidget()
        
        # Original automation tab
        self.tab_widget.addTab(self.original_page, "🚀 Automation Control")
        
        if self.enhanced_mode:
            # Enhanced features tabs
            from automation.ui.automation_widgets import ModernAutomationWidget
            
            # Modern automation widget
            self.modern_widget = ModernAutomationWidget()
            self.tab_widget.addTab(self.modern_widget, "⚡ Enhanced Control")
            
            # Performance monitoring tab
            self._create_performance_tab()
            
            # AI optimization tab
            self._create_ai_optimization_tab()
        
        layout.addWidget(self.tab_widget)
    
    def _create_performance_tab(self):
        """Create performance monitoring tab"""
        try:
            from automation.ui.automation_widgets import PerformanceMonitor
            
            performance_widget = QWidget()
            layout = QVBoxLayout(performance_widget)
            
            # Performance monitor
            self.performance_monitor = PerformanceMonitor()
            layout.addWidget(self.performance_monitor)
            
            self.tab_widget.addTab(performance_widget, "📊 Performance")
            
        except Exception as e:
            self.logger.error(f"Failed to create performance tab: {e}")
    
    def _create_ai_optimization_tab(self):
        """Create AI optimization tab"""
        try:
            from PyQt6.QtWidgets import QLabel, QGroupBox, QTextEdit, QPushButton
            
            ai_widget = QWidget()
            layout = QVBoxLayout(ai_widget)
            
            # AI Status
            ai_status_group = QGroupBox("AI Optimization Status")
            ai_status_layout = QVBoxLayout(ai_status_group)
            
            self.ai_status_label = QLabel("AI Optimization: Active")
            self.ai_status_label.setStyleSheet("color: #A6E22E; font-weight: bold;")
            ai_status_layout.addWidget(self.ai_status_label)
            
            # AI Recommendations
            ai_recommendations_group = QGroupBox("AI Recommendations")
            ai_recommendations_layout = QVBoxLayout(ai_recommendations_group)
            
            self.ai_recommendations_text = QTextEdit()
            self.ai_recommendations_text.setReadOnly(True)
            self.ai_recommendations_text.setMaximumHeight(200)
            ai_recommendations_layout.addWidget(self.ai_recommendations_text)
            
            # Update recommendations button
            self.update_recommendations_btn = QPushButton("🔄 Update Recommendations")
            self.update_recommendations_btn.clicked.connect(self._update_ai_recommendations)
            ai_recommendations_layout.addWidget(self.update_recommendations_btn)
            
            layout.addWidget(ai_status_group)
            layout.addWidget(ai_recommendations_group)
            layout.addStretch()
            
            self.tab_widget.addTab(ai_widget, "🤖 AI Optimization")
            
        except Exception as e:
            self.logger.error(f"Failed to create AI optimization tab: {e}")
    
    def _connect_enhanced_signals(self):
        """Connect enhanced signals"""
        try:
            if self.automation_patch and self.automation_patch.enhanced_mode:
                # Connect patch signals
                self.automation_patch.automation_started.connect(
                    lambda: self.automation_state_changed.emit(True, False))
                self.automation_patch.automation_stopped.connect(
                    lambda: self.automation_state_changed.emit(False, False))
                self.automation_patch.automation_paused.connect(
                    lambda: self.automation_state_changed.emit(True, True))
                
                self.automation_patch.log_message.connect(
                    lambda msg, level: self.performance_alert.emit(msg, level))
                
                # Connect to modern widget if available
                if hasattr(self, 'modern_widget'):
                    self._connect_modern_widget_signals()
            
        except Exception as e:
            self.logger.error(f"Error connecting enhanced signals: {e}")
    
    def _connect_modern_widget_signals(self):
        """Connect modern widget signals"""
        try:
            modern_widget = self.modern_widget
            control_panel = modern_widget.get_control_panel()
            
            # Connect control panel to automation patch
            if self.automation_patch:
                control_panel.start_automation.connect(self._start_enhanced_automation)
                control_panel.stop_automation.connect(self._stop_enhanced_automation)
                control_panel.pause_automation.connect(self._pause_enhanced_automation)
                control_panel.resume_automation.connect(self._resume_enhanced_automation)
                
                # Connect configuration changes
                control_panel.batch_size_changed.connect(self._on_batch_size_changed)
                control_panel.batch_delay_changed.connect(self._on_batch_delay_changed)
                control_panel.start_delay_changed.connect(self._on_start_delay_changed)
                control_panel.cpu_threshold_changed.connect(self._on_cpu_threshold_changed)
            
        except Exception as e:
            self.logger.error(f"Error connecting modern widget signals: {e}")
    
    def _initialize_enhanced_features(self):
        """Initialize enhanced features"""
        try:
            if self.enhanced_mode:
                # Start performance monitoring
                if hasattr(self, 'performance_monitor'):
                    self._start_performance_monitoring()
                
                # Initialize AI recommendations
                if hasattr(self, 'ai_recommendations_text'):
                    self._update_ai_recommendations()
                
                # Setup periodic updates
                self.update_timer = QTimer()
                self.update_timer.timeout.connect(self._periodic_update)
                self.update_timer.start(5000)  # Update every 5 seconds
            
        except Exception as e:
            self.logger.error(f"Error initializing enhanced features: {e}")
    
    def _start_performance_monitoring(self):
        """Start performance monitoring"""
        try:
            if hasattr(self, 'performance_monitor'):
                # Connect to integration layer performance updates
                if (self.automation_patch and 
                    self.automation_patch.integration_layer):
                    
                    integration_layer = self.automation_patch.integration_layer
                    integration_layer.metrics_updated.connect(
                        self._on_performance_metrics_updated)
            
        except Exception as e:
            self.logger.error(f"Error starting performance monitoring: {e}")
    
    def _update_ai_recommendations(self):
        """Update AI recommendations display"""
        try:
            if not hasattr(self, 'ai_recommendations_text'):
                return
            
            if (self.automation_patch and 
                self.automation_patch.performance_optimizer):
                
                optimizer = self.automation_patch.performance_optimizer
                report = optimizer.get_performance_report()
                
                # Format recommendations
                recommendations = []
                suggestions = report.get('suggestions', [])
                
                for suggestion in suggestions:
                    priority = suggestion.get('priority', 'medium').upper()
                    category = suggestion.get('category', 'General')
                    description = suggestion.get('description', 'No description')
                    action = suggestion.get('action', 'No action specified')
                    impact = suggestion.get('impact', 'Unknown impact')
                    
                    recommendations.append(
                        f"[{priority}] {category}: {description}\n"
                        f"   → Action: {action}\n"
                        f"   → Impact: {impact}\n"
                    )
                
                if recommendations:
                    text = "\n".join(recommendations)
                else:
                    text = "✅ No optimization recommendations at this time.\nSystem is running optimally."
                
                self.ai_recommendations_text.setPlainText(text)
                self.ai_status_label.setText("AI Optimization: Active - Recommendations Updated")
            
        except Exception as e:
            self.logger.error(f"Error updating AI recommendations: {e}")
            if hasattr(self, 'ai_recommendations_text'):
                self.ai_recommendations_text.setPlainText(f"Error updating recommendations: {e}")
    
    def _periodic_update(self):
        """Periodic update of enhanced features"""
        try:
            # Update performance monitor
            if hasattr(self, 'performance_monitor'):
                import psutil
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                
                # Determine performance level
                if cpu_percent >= 85 or memory_percent >= 90:
                    level = "critical"
                elif cpu_percent >= 70 or memory_percent >= 80:
                    level = "poor"
                elif cpu_percent >= 50 or memory_percent >= 70:
                    level = "moderate"
                elif cpu_percent >= 30 or memory_percent >= 50:
                    level = "good"
                else:
                    level = "excellent"
                
                self.performance_monitor.update_performance(cpu_percent, memory_percent, level)
            
            # Update AI recommendations periodically (every 5 minutes)
            if hasattr(self, '_last_ai_update'):
                import time
                if time.time() - self._last_ai_update > 300:  # 5 minutes
                    self._update_ai_recommendations()
                    self._last_ai_update = time.time()
            else:
                import time
                self._last_ai_update = time.time()
            
        except Exception as e:
            self.logger.error(f"Error in periodic update: {e}")
    
    # Enhanced automation control methods
    def _start_enhanced_automation(self):
        """Start enhanced automation"""
        try:
            if self.automation_patch:
                success = self.automation_patch.start_automation_enhanced()
                
                if success and hasattr(self, 'modern_widget'):
                    control_panel = self.modern_widget.get_control_panel()
                    control_panel.set_automation_state(True, False)
                    
                    log_widget = self.modern_widget.get_automation_log()
                    log_widget.add_log("🚀 Enhanced automation started successfully", "success")
            
        except Exception as e:
            self.logger.error(f"Error starting enhanced automation: {e}")
            if hasattr(self, 'modern_widget'):
                log_widget = self.modern_widget.get_automation_log()
                log_widget.add_log(f"❌ Failed to start enhanced automation: {e}", "error")
    
    def _stop_enhanced_automation(self):
        """Stop enhanced automation"""
        try:
            if self.automation_patch:
                success = self.automation_patch.stop_automation_enhanced()
                
                if success and hasattr(self, 'modern_widget'):
                    control_panel = self.modern_widget.get_control_panel()
                    control_panel.set_automation_state(False, False)
                    
                    log_widget = self.modern_widget.get_automation_log()
                    log_widget.add_log("🛑 Enhanced automation stopped", "warning")
            
        except Exception as e:
            self.logger.error(f"Error stopping enhanced automation: {e}")
    
    def _pause_enhanced_automation(self):
        """Pause enhanced automation"""
        try:
            if self.automation_patch:
                success = self.automation_patch.pause_automation_enhanced()
                
                if success and hasattr(self, 'modern_widget'):
                    control_panel = self.modern_widget.get_control_panel()
                    control_panel.set_automation_state(True, True)
                    
                    log_widget = self.modern_widget.get_automation_log()
                    log_widget.add_log("⏸️ Enhanced automation paused", "warning")
            
        except Exception as e:
            self.logger.error(f"Error pausing enhanced automation: {e}")
    
    def _resume_enhanced_automation(self):
        """Resume enhanced automation"""
        try:
            if self.automation_patch:
                success = self.automation_patch.resume_automation_enhanced()
                
                if success and hasattr(self, 'modern_widget'):
                    control_panel = self.modern_widget.get_control_panel()
                    control_panel.set_automation_state(True, False)
                    
                    log_widget = self.modern_widget.get_automation_log()
                    log_widget.add_log("▶️ Enhanced automation resumed", "success")
            
        except Exception as e:
            self.logger.error(f"Error resuming enhanced automation: {e}")
    
    # Configuration change handlers
    def _on_batch_size_changed(self, value: int):
        """Handle batch size change"""
        try:
            if hasattr(self.original_page, 'automation_settings'):
                self.original_page.automation_settings['batch_size'] = value
            
            if hasattr(self, 'modern_widget'):
                log_widget = self.modern_widget.get_automation_log()
                log_widget.add_log(f"⚙️ Batch size changed to {value}", "info")
            
        except Exception as e:
            self.logger.error(f"Error handling batch size change: {e}")
    
    def _on_batch_delay_changed(self, value: float):
        """Handle batch delay change"""
        try:
            if hasattr(self.original_page, 'automation_settings'):
                self.original_page.automation_settings['batch_delay'] = value
            
            if hasattr(self, 'modern_widget'):
                log_widget = self.modern_widget.get_automation_log()
                log_widget.add_log(f"⚙️ Batch delay changed to {value}s", "info")
            
        except Exception as e:
            self.logger.error(f"Error handling batch delay change: {e}")
    
    def _on_start_delay_changed(self, value: float):
        """Handle start delay change"""
        try:
            if hasattr(self.original_page, 'automation_settings'):
                self.original_page.automation_settings['start_delay'] = value
            
            if hasattr(self, 'modern_widget'):
                log_widget = self.modern_widget.get_automation_log()
                log_widget.add_log(f"⚙️ Start delay changed to {value}s", "info")
            
        except Exception as e:
            self.logger.error(f"Error handling start delay change: {e}")
    
    def _on_cpu_threshold_changed(self, value: float):
        """Handle CPU threshold change"""
        try:
            if hasattr(self.original_page, 'cpu_threshold'):
                self.original_page.cpu_threshold = value
            
            if hasattr(self, 'modern_widget'):
                log_widget = self.modern_widget.get_automation_log()
                log_widget.add_log(f"⚙️ CPU threshold changed to {value}%", "info")
            
        except Exception as e:
            self.logger.error(f"Error handling CPU threshold change: {e}")
    
    def _on_performance_metrics_updated(self, metrics):
        """Handle performance metrics update"""
        try:
            if hasattr(self, 'modern_widget'):
                progress_percentage = getattr(metrics, 'progress_percentage', 0.0)
                self.modern_widget.update_progress(progress_percentage)
            
        except Exception as e:
            self.logger.error(f"Error handling performance metrics update: {e}")
    
    # Public API methods
    def get_automation_status(self) -> Dict[str, Any]:
        """Get automation status"""
        if self.automation_patch:
            return self.automation_patch.get_automation_status_enhanced()
        else:
            return {'mode': 'legacy', 'enhanced': False}
    
    def is_enhanced_mode(self) -> bool:
        """Check if enhanced mode is active"""
        return self.enhanced_mode
    
    def get_original_page(self) -> QWidget:
        """Get original automation page"""
        return self.original_page
    
    def get_modern_widget(self) -> Optional[QWidget]:
        """Get modern automation widget"""
        return getattr(self, 'modern_widget', None)


def create_enhanced_automation_page(original_page: QWidget, parent=None) -> EnhancedMonokaiAutomationPage:
    """Factory function to create enhanced automation page"""
    return EnhancedMonokaiAutomationPage(original_page, parent)
