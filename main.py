import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFontDatabase

# Import optimized modules
# EXE-specific initialization
if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller bundle
        import os
        
        # Fix Qt platform plugin path
        app_dir = os.path.dirname(sys.executable)
        platforms_dir = os.path.join(app_dir, 'platforms')
        
        # Ensure platforms directory exists
        if not os.path.exists(platforms_dir):
            os.makedirs(platforms_dir, exist_ok=True)
        
        # Set Qt environment for EXE
        os.environ['QT_PLUGIN_PATH'] = platforms_dir
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platforms_dir
        
        print(f"EXE Mode: Qt plugins path set to {platforms_dir}")

try:
    from optimizations.app_config import AppConstants, app_config
    from optimizations.adaptive_config import apply_adaptive_optimizations
    from optimizations.enhanced_performance_monitor import get_enhanced_performance_monitor
    from optimizations.smart_resource_manager import get_smart_resource_manager
    from optimizations.optimization_integration import initialize_optimizations, cleanup_optimizations
    from error_handler import global_error_handler, setup_global_exception_handler
    from optimizations.worker_manager import get_global_worker_manager
    from optimizations.performance_monitor import global_performance_monitor
    from constants import ORG_NAME, APP_NAME
    from main_window import MainWindow

    # Import theme module
    from theme import AppTheme

    # Import plugin system
    from core.plugin_system import PluginManager

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def load_fonts():
    """Load custom fonts from assets folder."""
    try:
        # Determine relative path to assets/fonts folder
        # Works for both direct execution and PyInstaller packaging
        if getattr(sys, 'frozen', False):
            # Running in packaged environment
            base_path = sys._MEIPASS
        else:
            # Running in normal development environment
            base_path = os.path.dirname(__file__)

        font_dir = os.path.join(base_path, 'assets', 'fonts')
        
        if not os.path.isdir(font_dir):
            print(f"Warning: Font directory not found at '{font_dir}'")
            return

        # List of essential and optional font files
        essential_fonts = [
            'Inter-Regular.ttf',
            'Inter-Bold.ttf',
            'JetBrainsMono-Regular.ttf',
            'JetBrainsMono-Bold.ttf'
        ]
        
        optional_fonts = [
            'JetBrainsMono-Medium.ttf',
            'JetBrainsMono-Italic.ttf',
            'JetBrainsMono-Bold-Italic.ttf',
            'JetBrainsMono-Medium-Italic.ttf',
            'JetBrainsMono-ExtraBold.ttf',
            'JetBrainsMono-ExtraBold-Italic.ttf'
        ]

        loaded_count = 0
        total_fonts = len(essential_fonts) + len(optional_fonts)
        
        # Load essential fonts first
        for font_file in essential_fonts:
            font_path = os.path.join(font_dir, font_file)
            if os.path.isfile(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    loaded_count += 1
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    print(f"✅ Loaded essential font: {font_file} -> {font_families}")
                else:
                    print(f"❌ Failed to load essential font: {font_file}")
            else:
                print(f"⚠️ Essential font not found: {font_path}")
        
        # Load optional fonts silently
        for font_file in optional_fonts:
            font_path = os.path.join(font_dir, font_file)
            if os.path.isfile(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    loaded_count += 1

        print(f"Successfully loaded {loaded_count}/{total_fonts} fonts ({len(essential_fonts)} essential, {loaded_count - len(essential_fonts)} optional)")
        
    except Exception as e:
        print(f"Error loading fonts: {e}")

if __name__ == "__main__":
    # Setup global error handling first
    setup_global_exception_handler()
    
    # Initialize Qt application
    app = QApplication(sys.argv)
    
    # Set organization and application info for QSettings
    app.setOrganizationName(AppConstants.ORG_NAME)
    app.setApplicationName(AppConstants.APP_NAME)
    app.setOrganizationDomain(AppConstants.ORG_DOMAIN)
    
    # Initialize settings and load config
    settings = QSettings()
    app_config.update_from_qsettings(settings)
    
    # Apply theme
    print("✅ Applying theme...")
    AppTheme.apply_theme(app, settings)
    
    # Apply adaptive optimizations
    print("🎯 Applying adaptive optimizations...")
    optimization_stats = apply_adaptive_optimizations()
    print(f"🎯 Optimized for {optimization_stats['system_profile']['performance_tier']} performance tier")
    print(f"🎯 System: {optimization_stats['system_profile']['cpu_cores']} cores, {optimization_stats['system_profile']['memory_gb']:.1f}GB RAM")
    
    try:
        # Initialize enhanced monitoring systems
        enhanced_monitor = get_enhanced_performance_monitor()
        resource_manager = get_smart_resource_manager()
        
        # Initialize worker manager
        worker_manager = None
        
        # Create main window
        print("🚀 Creating MainWindow instance...")
        window = MainWindow()
        print("✅ MainWindow created successfully")
        
        # Initialize integrated optimization systems
        print("🚀 Initializing integrated optimization systems...")
        optimization_success = initialize_optimizations(window)
        if optimization_success:
            print("✅ Integrated optimization systems initialized")
        else:
            print("⚠️ Some optimization systems failed to initialize")
        
        # Set up error handler parent for dialogs
        global_error_handler.set_parent_widget(window)
        
        # Start enhanced monitoring systems
        print("🎯 Starting enhanced performance monitoring...")
        enhanced_monitor.start_monitoring()
        
        print("🧠 Starting smart resource management...")
        resource_manager.start_management()
        
        # Start legacy performance monitoring if enabled
        if app_config.get("performance.monitoring_enabled", True):
            global_performance_monitor.start_monitoring()
        
        global_error_handler.log_info(f"{AppConstants.APP_NAME} {AppConstants.APP_VERSION} started with adaptive optimizations", "Application")
        
        # Show window and run app
        print("🖥️ Showing MainWindow...")
        window.show()
        print("✅ MainWindow shown, starting app loop...")

        # Defer font loading to a background thread for faster startup
        worker_manager = get_global_worker_manager(app)
        worker_manager.submit_task("load_fonts", load_fonts)

        exit_code = app.exec()
        
    except Exception as e:
        print(f"❌ Exception in ApplicationStartup: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        global_error_handler.handle_exception(type(e), e, e.__traceback__, operation="ApplicationStartup")
        exit_code = 1
    
    finally:
        try:
            # Cleanup on exit
            global_error_handler.log_info("Application shutting down", "Application")
            
            # Save configuration
            app_config.save_to_qsettings(settings)
            
            # Stop enhanced monitoring systems
            try:
                enhanced_monitor.stop_monitoring()
                resource_manager.stop_management()
                cleanup_optimizations()
            except:
                pass
            
            # Cleanup workers
            try:
                if 'worker_manager' in globals() and globals()['worker_manager'] is not None:
                    globals()['worker_manager'].cleanup()
            except (NameError, KeyError):
                # worker_manager was not defined
                pass
            
            # Stop performance monitoring
            global_performance_monitor.stop_monitoring()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    sys.exit(exit_code)
