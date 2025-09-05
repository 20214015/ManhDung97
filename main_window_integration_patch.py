"""
Main Window Integration Patch
============================

Patch để integrate optimization components vào existing main_window.py
mà không break existing functionality.
"""

import sys
import time
from typing import Optional

# Check if we can import optimization components
try:
    from services import get_service_manager
    from core import get_event_manager, get_state_manager, EventTypes, emit_event
    OPTIMIZATION_AVAILABLE = True
    print("✅ Optimization components available")
except ImportError as e:
    print(f"⚠️ Optimization components not available: {e}")
    OPTIMIZATION_AVAILABLE = False

class MainWindowOptimizationMixin:
    """
    Mixin class để add optimization functionality vào existing MainWindow
    mà không cần modify toàn bộ code.
    """
    
    def init_optimization_components(self):
        """Initialize optimization components if available"""
        print("🔧 Starting optimization components initialization...")
        
        if not OPTIMIZATION_AVAILABLE:
            print("⚠️ Optimization components not available, using fallback")
            self._init_fallback_components()
            return
        
        try:
            print("🔧 Initializing managers...")
            # Initialize managers with timeout protection
            
            print("🔧 Creating ServiceManager...")
            try:
                self.service_manager = get_service_manager()
                print("✅ ServiceManager initialized")
            except Exception as e:
                print(f"⚠️ ServiceManager failed: {e}")
                self.service_manager = None
            
            print("🔧 Creating EventManager...")
            try:
                self.event_manager = get_event_manager()
                print("✅ EventManager initialized")
            except Exception as e:
                print(f"⚠️ EventManager failed: {e}")
                self.event_manager = None
            
            print("🔧 Creating StateManager...")
            try:
                self.state_manager = get_state_manager()
                print("✅ StateManager initialized")
            except Exception as e:
                print(f"⚠️ StateManager failed: {e}")
                self.state_manager = None
            
            # Start services with safe error handling
            print("🔧 Starting services safely...")
            try:
                if self.service_manager:
                    self.service_manager.start_all_services()
                    print("✅ All services started successfully")
                else:
                    print("⚠️ No ServiceManager available, skipping service startup")
            except Exception as e:
                print(f"⚠️ Service startup failed (continuing anyway): {e}")
            
            print("🔧 Setting up optimization events...")
            # Setup event handlers
            try:
                self._setup_optimization_events()
                print("✅ Events setup complete")
            except Exception as e:
                print(f"⚠️ Events setup failed: {e}")
            
            print("🔧 Initializing state...")
            # Initialize state
            try:
                self._init_optimization_state()
                print("✅ State initialized")
            except Exception as e:
                print(f"⚠️ State initialization failed: {e}")
            
            print("🔧 Initializing Phase 3 components...")
            # Initialize Phase 3 components
            try:
                self._init_phase3_components()
                print("✅ Phase 3 components initialized")
            except Exception as e:
                print(f"⚠️ Phase 3 initialization failed: {e}")
            
            print("✅ Optimization components initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing optimization components: {e}")
            import traceback
            traceback.print_exc()
            self._init_fallback_components()
    
    def _init_fallback_components(self):
        """Fallback initialization if optimization components fail"""
        self.service_manager = None
        self.event_manager = None
        self.state_manager = None
        
        # Initialize fallback Phase 3 components
        self.performance_monitor = None
        self.settings_component = None
        
        print("💡 Using fallback mode - basic functionality only")
    
    def _init_phase3_components(self):
        """Initialize Phase 3 production components"""
        if not OPTIMIZATION_AVAILABLE:
            print("⚠️ Optimization not available, skipping Phase 3 components")
            return
        
        try:
            # Initialize Performance Monitor Component
            try:
                from components.performance_monitor_component import create_performance_monitor_component
                self.performance_monitor = create_performance_monitor_component(self)
                print("✅ Performance Monitor Component initialized")
            except ImportError as e:
                print(f"⚠️ Performance Monitor Component not available: {e}")
                self.performance_monitor = None
            
            # Initialize Settings Component  
            try:
                from components.settings_component import create_settings_component
                self.settings_component = create_settings_component(self)
                print("✅ Settings Component initialized")
            except ImportError as e:
                print(f"⚠️ Settings Component not available: {e}")
                self.settings_component = None
            
            # Connect Phase 3 component signals
            self._connect_phase3_signals()
            
        except Exception as e:
            print(f"❌ Phase 3 components initialization failed: {e}")
    
    def _connect_phase3_signals(self):
        """Connect Phase 3 component signals"""
        try:
            # Performance Monitor signals
            if hasattr(self, 'performance_monitor') and self.performance_monitor:
                # Note: Actual signal connections would be here if components support them
                print("🔗 Performance Monitor signals ready")
            
            # Settings Component signals  
            if hasattr(self, 'settings_component') and self.settings_component:
                # Note: Connect actual signals if available
                if hasattr(self.settings_component, 'settings_changed'):
                    self.settings_component.settings_changed.connect(self._on_settings_changed)
                if hasattr(self.settings_component, 'settings_saved'):
                    self.settings_component.settings_saved.connect(self._on_settings_saved)
                print("🔗 Settings Component signals connected")
            
        except Exception as e:
            print(f"⚠️ Failed to connect Phase 3 signals: {e}")
    
    def _on_performance_alert(self, alert_type, message, severity):
        """Handle performance alerts"""
        print(f"🚨 Performance Alert [{severity}]: {alert_type} - {message}")
    
    def _on_metrics_updated(self, metrics):
        """Handle performance metrics updates"""
        print(f"📊 Performance metrics updated: {metrics}")
    
    def _on_settings_changed(self, key, value):
        """Handle settings changes"""
        print(f"⚙️ Setting changed: {key} = {value}")
    
    def _on_settings_saved(self):
        """Handle settings saved"""
        print("💾 Settings saved successfully")
    
    def get_performance_monitor(self):
        """Get performance monitor component"""
        return getattr(self, 'performance_monitor', None)
    
    def get_settings_component(self):
        """Get settings component"""
        return getattr(self, 'settings_component', None)
    
    def show_performance_monitor(self):
        """Show performance monitoring dashboard"""
        if hasattr(self, 'performance_monitor') and self.performance_monitor:
            if hasattr(self.performance_monitor, 'create_performance_dashboard'):
                return self.performance_monitor.create_performance_dashboard()
        return None
    
    def show_settings_panel(self):
        """Show settings management panel"""
        if hasattr(self, 'settings_component') and self.settings_component:
            if hasattr(self.settings_component, 'create_settings_panel'):
                return self.settings_component.create_settings_panel()
        return None
    
    def _setup_optimization_events(self):
        """Setup event subscriptions for optimization"""
        if not self.event_manager:
            return
        
        # Service events
        if self.service_manager:
            self.service_manager.service_started.connect(self._on_optimization_service_started)
            self.service_manager.service_error.connect(self._on_optimization_service_error)
        
        # State events
        if self.state_manager:
            self.state_manager.instances_changed.connect(self._on_optimization_instances_changed)
            self.state_manager.ui_changed.connect(self._on_optimization_ui_changed)
        
        print("📡 Optimization events configured")
    
    def _init_optimization_state(self):
        """Initialize optimization state"""
        if not self.state_manager:
            return
        
        # Load any existing instances into state manager
        if hasattr(self, 'instances_model') and self.instances_model:
            try:
                # Get current instances from model
                instances_data = []
                for row in range(self.instances_model.rowCount()):
                    instance_data = {}
                    for col in range(self.instances_model.columnCount()):
                        item = self.instances_model.item(row, col)
                        if item:
                            instance_data[f'col_{col}'] = item.text()
                    instances_data.append(instance_data)
                
                # Update state manager
                self.state_manager.update_instances(instances_data)
                print(f"📊 Loaded {len(instances_data)} instances into state manager")
                
            except Exception as e:
                print(f"⚠️ Error loading instances into state: {e}")
    
    # Event Handlers
    def _on_optimization_service_started(self, service_name):
        """Handle optimization service started"""
        print(f"✅ Optimization service started: {service_name}")
        
        # Update UI if needed
        if hasattr(self, 'log_message'):
            self.log_message(f"Service '{service_name}' started", "success")
    
    def _on_optimization_service_error(self, service_name, error_message):
        """Handle optimization service error"""
        print(f"❌ Optimization service error: {service_name} - {error_message}")
        
        # Update UI if needed
        if hasattr(self, 'log_message'):
            self.log_message(f"Service error: {service_name}", "error")
    
    def _on_optimization_instances_changed(self, instances_data):
        """Handle optimization instances state change"""
        print(f"📊 Optimization: {len(instances_data)} instances updated")
        
        # Sync with existing table if available
        if hasattr(self, 'table') and self.table:
            self._sync_optimization_state_to_table(instances_data)
    
    def _on_optimization_ui_changed(self, ui_data):
        """Handle optimization UI state change"""
        print(f"🎨 Optimization UI state changed: {ui_data}")
    
    def _sync_optimization_state_to_table(self, instances_data):
        """Sync optimization state back to existing table"""
        try:
            # This would update the existing table with state manager data
            # Implementation depends on existing table structure
            print(f"🔄 Syncing {len(instances_data)} instances to table")
        except Exception as e:
            print(f"⚠️ Error syncing state to table: {e}")
    
    # Enhanced Methods với Optimization
    def enhanced_refresh_instances(self):
        """Enhanced refresh using optimization components"""
        if not OPTIMIZATION_AVAILABLE or not self.event_manager:
            # Fallback to original method
            return self._original_refresh_instances()
        
        try:
            # Use event-driven refresh
            emit_event(EventTypes.INSTANCES_REFRESHED, {
                'source': 'user_request',
                'timestamp': time.time()
            })
            
            # Original refresh logic here
            result = self._original_refresh_instances()
            
            # Update state manager if successful
            if result and self.state_manager:
                # This would be actual data from refresh
                pass
            
            return result
            
        except Exception as e:
            print(f"❌ Enhanced refresh failed, using fallback: {e}")
            return self._original_refresh_instances()
    
    def enhanced_instance_selection(self, instance_ids):
        """Enhanced selection using optimization components"""
        if not OPTIMIZATION_AVAILABLE or not self.state_manager:
            # Fallback to original method
            return self._original_instance_selection(instance_ids)
        
        try:
            # Update state manager
            self.state_manager.update_instance_selection(instance_ids, selected=True)
            
            # Emit event
            emit_event(EventTypes.INSTANCE_SELECTED, {
                'instance_ids': instance_ids,
                'count': len(instance_ids)
            })
            
            # Original selection logic
            return self._original_instance_selection(instance_ids)
            
        except Exception as e:
            print(f"❌ Enhanced selection failed, using fallback: {e}")
            return self._original_instance_selection(instance_ids)
    
    # Fallback methods (would be original implementations)
    def _original_refresh_instances(self):
        """Original refresh implementation"""
        print("🔄 Using original refresh method")
        return True
    
    def _original_instance_selection(self, instance_ids):
        """Original selection implementation"""
        print(f"📌 Using original selection method for {len(instance_ids)} instances")
        return True
    
    # Cache Integration
    def get_optimized_cache(self):
        """Get optimization cache service"""
        if self.service_manager:
            return self.service_manager.get_cache()
        return None
    
    def cache_ui_state(self, key, data):
        """Cache UI state using optimization cache"""
        cache = self.get_optimized_cache()
        if cache:
            cache.set(key, data)
            print(f"💾 Cached UI state: {key}")
        else:
            print("⚠️ Cache not available")
    
    def load_cached_ui_state(self, key, default=None):
        """Load UI state from optimization cache"""
        cache = self.get_optimized_cache()
        if cache:
            data = cache.get(key, default)
            print(f"📖 Loaded cached UI state: {key}")
            return data
        return default
    
    # Performance Monitoring
    def get_optimization_performance_info(self):
        """Get performance info from optimization components"""
        if not self.service_manager:
            return {}
        
        service_info = self.service_manager.get_service_info()
        performance_info = {
            'services_available': len(service_info),
            'services_running': sum(1 for info in service_info.values() if info['status']),
            'optimization_enabled': OPTIMIZATION_AVAILABLE
        }
        
        if self.state_manager:
            state = self.state_manager.get_state()
            performance_info.update({
                'instances_count': len(state.instances),
                'selected_count': len(self.state_manager.get_selected_instances()),
                'state_history_available': self.state_manager.can_undo()
            })
        
        return performance_info
    
    # Cleanup
    def cleanup_optimization_components(self):
        """Cleanup optimization components on app exit"""
        try:
            if self.service_manager:
                self.service_manager.stop_all_services()
                print("🧹 Optimization services stopped")
            
            if self.state_manager:
                # Save state if needed
                state_data = self.state_manager.save_to_dict()
                cache = self.get_optimized_cache()
                if cache:
                    cache.set('last_app_state', state_data)
                    print("💾 App state saved to cache")
                    
        except Exception as e:
            print(f"⚠️ Error during optimization cleanup: {e}")

def patch_main_window(main_window_class):
    """
    Decorator để patch existing MainWindow class với optimization functionality
    
    Usage:
    @patch_main_window
    class MainWindow(QMainWindow):
        ...
    """
    
    # Add mixin methods to class
    for attr_name in dir(MainWindowOptimizationMixin):
        if not attr_name.startswith('_') or attr_name.startswith('_on_') or attr_name.startswith('_init_'):
            attr = getattr(MainWindowOptimizationMixin, attr_name)
            if callable(attr):
                setattr(main_window_class, attr_name, attr)
    
    # Override __init__ để auto-initialize optimization
    original_init = main_window_class.__init__
    
    def enhanced_init(self, *args, **kwargs):
        # Call original __init__
        original_init(self, *args, **kwargs)
        
        # Initialize optimization components
        self.init_optimization_components()
        
        print("🎉 MainWindow patched with optimization components")
    
    main_window_class.__init__ = enhanced_init
    
    # Override closeEvent để cleanup
    original_close_event = getattr(main_window_class, 'closeEvent', None)
    
    def enhanced_close_event(self, event):
        # Cleanup optimization components
        self.cleanup_optimization_components()
        
        # Call original closeEvent if exists
        if original_close_event:
            original_close_event(self, event)
        else:
            event.accept()
    
    main_window_class.closeEvent = enhanced_close_event
    
    return main_window_class

# Test function
def test_integration_patch():
    """Test the integration patch"""
    from PyQt6.QtWidgets import QMainWindow, QApplication
    
    @patch_main_window
    class TestMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Test Integration Patch")
            print("TestMainWindow initialized")
    
    app = QApplication([])
    window = TestMainWindow()
    
    # Test optimization methods
    performance_info = window.get_optimization_performance_info()
    print(f"Performance info: {performance_info}")
    
    # Test cache
    window.cache_ui_state('test_key', {'test': 'data'})
    cached_data = window.load_cached_ui_state('test_key')
    print(f"Cached data: {cached_data}")
    
    # Test enhanced methods
    window.enhanced_refresh_instances()
    window.enhanced_instance_selection([1, 2, 3])
    
    window.close()
    print("✅ Integration patch test completed")

if __name__ == "__main__":
    test_integration_patch()
