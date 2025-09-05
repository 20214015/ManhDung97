"""
Demo Script - Testing Enhanced Automation Integration
===================================================
Demo script to test the integration of new modular architecture.
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import QTimer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AutomationDemo(QMainWindow):
    """Demo application for testing enhanced automation"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Automation Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup UI
        self._setup_ui()
        
        # Test automation modules
        self._test_automation_modules()
    
    def _setup_ui(self):
        """Setup demo UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Status label
        self.status_label = QLabel("🚀 Enhanced Automation Demo - Loading...")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #A6E22E; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Test buttons
        test_layout = QVBoxLayout()
        
        self.test_modules_btn = QPushButton("🧪 Test Core Modules")
        self.test_modules_btn.clicked.connect(self._test_core_modules)
        test_layout.addWidget(self.test_modules_btn)
        
        self.test_ui_btn = QPushButton("🎨 Test UI Components") 
        self.test_ui_btn.clicked.connect(self._test_ui_components)
        test_layout.addWidget(self.test_ui_btn)
        
        self.test_integration_btn = QPushButton("🔗 Test Integration Layer")
        self.test_integration_btn.clicked.connect(self._test_integration_layer)
        test_layout.addWidget(self.test_integration_btn)
        
        self.test_performance_btn = QPushButton("📊 Test Performance Optimizer")
        self.test_performance_btn.clicked.connect(self._test_performance_optimizer)
        test_layout.addWidget(self.test_performance_btn)
        
        layout.addLayout(test_layout)
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.results_text)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #404040;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                color: #ffffff;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #777777;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def _test_automation_modules(self):
        """Test if automation modules are available"""
        try:
            # Test core modules
            from automation.core.automation_engine import AutomationEngine
            from automation.core.batch_processor import EnhancedBatchProcessor
            from automation.utils.performance_optimizer import PerformanceOptimizer
            from automation.utils.state_manager import StateManager
            
            self.log_result("✅ Core automation modules loaded successfully")
            self.status_label.setText("✅ Enhanced Automation Demo - Modules Loaded")
            
        except ImportError as e:
            self.log_result(f"❌ Failed to load automation modules: {e}")
            self.status_label.setText("❌ Enhanced Automation Demo - Module Load Failed")
    
    def _test_core_modules(self):
        """Test core automation modules"""
        self.log_result("\n🧪 TESTING CORE MODULES")
        self.log_result("=" * 50)
        
        try:
            # Test AutomationEngine
            from automation.core.automation_engine import AutomationEngine, AutomationConfig
            
            engine = AutomationEngine()
            config = AutomationConfig()
            
            self.log_result("✅ AutomationEngine created successfully")
            self.log_result(f"   - Default batch size: {config.batch_size}")
            self.log_result(f"   - Default batch delay: {config.batch_delay}")
            self.log_result(f"   - CPU threshold: {config.cpu_threshold}")
            
            # Test BatchProcessor
            from automation.core.batch_processor import EnhancedBatchProcessor
            
            processor = EnhancedBatchProcessor()
            self.log_result("✅ EnhancedBatchProcessor created successfully")
            
            # Test PerformanceOptimizer
            from automation.utils.performance_optimizer import PerformanceOptimizer, SystemMetrics
            
            optimizer = PerformanceOptimizer()
            metrics = SystemMetrics.collect_current()
            
            self.log_result("✅ PerformanceOptimizer created successfully")
            self.log_result(f"   - Current CPU: {metrics.cpu_percent:.1f}%")
            self.log_result(f"   - Current Memory: {metrics.memory_percent:.1f}%")
            self.log_result(f"   - Performance Level: {metrics.performance_level.value}")
            
            # Test StateManager
            from automation.utils.state_manager import get_global_state_manager
            
            state_manager = get_global_state_manager()
            state_manager.set('test_key', 'test_value', 'demo')
            retrieved = state_manager.get('test_key')
            
            self.log_result("✅ StateManager created successfully")
            self.log_result(f"   - Test state set/get: {retrieved}")
            
        except Exception as e:
            self.log_result(f"❌ Core modules test failed: {e}")
    
    def _test_ui_components(self):
        """Test UI components"""
        self.log_result("\n🎨 TESTING UI COMPONENTS")
        self.log_result("=" * 50)
        
        try:
            from automation.ui.automation_widgets import (
                ModernAutomationWidget, EnhancedControlPanel, 
                PerformanceMonitor, AutomationLog
            )
            
            # Test ModernAutomationWidget
            modern_widget = ModernAutomationWidget()
            self.log_result("✅ ModernAutomationWidget created successfully")
            
            # Test EnhancedControlPanel
            control_panel = EnhancedControlPanel()
            self.log_result("✅ EnhancedControlPanel created successfully")
            
            # Test PerformanceMonitor
            perf_monitor = PerformanceMonitor()
            self.log_result("✅ PerformanceMonitor created successfully")
            
            # Test AutomationLog
            automation_log = AutomationLog()
            self.log_result("✅ AutomationLog created successfully")
            
            # Test adding log messages
            automation_log.add_log("Test info message", "info")
            automation_log.add_log("Test warning message", "warning")
            automation_log.add_log("Test error message", "error")
            automation_log.add_log("Test success message", "success")
            
            self.log_result("✅ Log messages added successfully")
            
        except Exception as e:
            self.log_result(f"❌ UI components test failed: {e}")
    
    def _test_integration_layer(self):
        """Test integration layer"""
        self.log_result("\n🔗 TESTING INTEGRATION LAYER")
        self.log_result("=" * 50)
        
        try:
            from automation.core.integration_layer import AutomationIntegrationLayer, UIBridge
            
            # Create mock UI component
            mock_ui = QWidget()
            
            # Test AutomationIntegrationLayer
            integration_layer = AutomationIntegrationLayer(mock_ui)
            self.log_result("✅ AutomationIntegrationLayer created successfully")
            
            # Test UIBridge
            ui_bridge = UIBridge(integration_layer)
            self.log_result("✅ UIBridge created successfully")
            
            # Test configuration
            test_instances = ['instance_1', 'instance_2', 'instance_3']
            config = {
                'batch_size': 5,
                'batch_delay': 2.0,
                'start_delay': 3.0,
                'cpu_threshold': 70.0
            }
            
            self.log_result(f"✅ Test configuration created: {len(test_instances)} instances")
            
            # Test status
            status = integration_layer.get_automation_status()
            self.log_result("✅ Status retrieved successfully")
            self.log_result(f"   - Running: {status.get('is_running', False)}")
            self.log_result(f"   - Paused: {status.get('is_paused', False)}")
            
        except Exception as e:
            self.log_result(f"❌ Integration layer test failed: {e}")
    
    def _test_performance_optimizer(self):
        """Test performance optimizer features"""
        self.log_result("\n📊 TESTING PERFORMANCE OPTIMIZER")
        self.log_result("=" * 50)
        
        try:
            from automation.utils.performance_optimizer import (
                PerformanceOptimizer, SmartResourceMonitor, SystemMetrics
            )
            
            # Create optimizer
            optimizer = PerformanceOptimizer()
            
            # Test performance report
            report = optimizer.get_performance_report()
            self.log_result("✅ Performance report generated")
            
            current_perf = report.get('current_performance', {})
            self.log_result(f"   - CPU: {current_perf.get('cpu', 0):.1f}%")
            self.log_result(f"   - Memory: {current_perf.get('memory', 0):.1f}%")
            self.log_result(f"   - Level: {current_perf.get('level', 'unknown')}")
            
            # Test optimization profile
            profile = optimizer.monitor.get_optimization_profile()
            self.log_result("✅ Optimization profile generated")
            self.log_result(f"   - Optimal batch size: {profile.optimal_batch_size}")
            self.log_result(f"   - Optimal batch delay: {profile.optimal_batch_delay}")
            self.log_result(f"   - Confidence: {profile.confidence_score:.1%}")
            
            # Test optimization suggestions
            suggestions = optimizer.monitor.generate_optimization_suggestions()
            self.log_result(f"✅ Generated {len(suggestions)} optimization suggestions")
            
            for i, suggestion in enumerate(suggestions[:3], 1):  # Show first 3
                self.log_result(f"   {i}. [{suggestion.priority.upper()}] {suggestion.category}: {suggestion.description}")
            
            # Test configuration optimization
            base_config = {
                'batch_size': 10,
                'batch_delay': 2.0,
                'start_delay': 3.0
            }
            
            optimized_config = optimizer.optimize_automation_config(base_config)
            self.log_result("✅ Configuration optimized")
            self.log_result(f"   - Original batch size: {base_config['batch_size']}")
            self.log_result(f"   - Optimized batch size: {optimized_config.get('batch_size', 'unchanged')}")
            
        except Exception as e:
            self.log_result(f"❌ Performance optimizer test failed: {e}")
    
    def log_result(self, message: str):
        """Log result to text widget"""
        self.results_text.append(message)
        
        # Auto scroll to bottom
        scrollbar = self.results_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Process events to update UI
        QApplication.processEvents()


def main():
    """Main demo function"""
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Automation Demo")
    
    # Create and show demo window
    demo = AutomationDemo()
    demo.show()
    
    # Auto-run all tests after a short delay
    QTimer.singleShot(1000, demo._test_core_modules)
    QTimer.singleShot(2000, demo._test_ui_components)
    QTimer.singleShot(3000, demo._test_integration_layer)
    QTimer.singleShot(4000, demo._test_performance_optimizer)
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
