"""
Plugin System Integration Script
=================================

This script demonstrates how to integrate the plugin system
into MuMuManager Pro's main application.

Usage:
1. Import this module in main.py
2. Call initialize_plugin_system() after MainWindow creation
3. Call cleanup_plugin_system() during application shutdown
"""

import os
import sys
from typing import Optional, Any

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from core.plugin_system import PluginManager
except ImportError as e:
    print(f"❌ Failed to import PluginManager: {e}")
    PluginManager = None

# Global plugin manager instance
_global_plugin_manager: Optional[PluginManager] = None

def initialize_plugin_system(main_window: Any) -> bool:
    """
    Initialize the plugin system with the main window.

    Args:
        main_window: The main application window instance

    Returns:
        bool: True if initialization successful, False otherwise
    """
    global _global_plugin_manager

    if PluginManager is None:
        print("❌ PluginManager not available")
        return False

    try:
        print("🔌 Initializing Plugin System...")

        # Create plugin manager
        plugins_dir = os.path.join(current_dir, "plugins")
        _global_plugin_manager = PluginManager(plugins_dir)

        # Connect signals
        _global_plugin_manager.plugin_loaded.connect(_on_plugin_loaded)
        _global_plugin_manager.plugin_unloaded.connect(_on_plugin_unloaded)
        _global_plugin_manager.plugin_error.connect(_on_plugin_error)

        # Load all plugins
        loaded_count = _global_plugin_manager.load_all_plugins(main_window)

        print(f"✅ Plugin System initialized with {loaded_count} plugins loaded")
        return True

    except Exception as e:
        print(f"❌ Failed to initialize plugin system: {e}")
        return False

def cleanup_plugin_system() -> None:
    """Cleanup the plugin system on application shutdown."""
    global _global_plugin_manager

    if _global_plugin_manager is not None:
        try:
            print("🔌 Cleaning up Plugin System...")
            unloaded_count = _global_plugin_manager.unload_all_plugins()
            print(f"✅ Unloaded {unloaded_count} plugins")
        except Exception as e:
            print(f"❌ Error during plugin cleanup: {e}")
        finally:
            _global_plugin_manager = None

def get_plugin_manager() -> Optional[PluginManager]:
    """Get the global plugin manager instance."""
    return _global_plugin_manager

def reload_plugins(main_window: Any) -> int:
    """
    Reload all plugins. Useful for development.

    Args:
        main_window: The main application window instance

    Returns:
        int: Number of plugins loaded
    """
    global _global_plugin_manager

    if _global_plugin_manager is None:
        print("❌ Plugin system not initialized")
        return 0

    try:
        print("🔄 Reloading plugins...")

        # Unload all plugins
        _global_plugin_manager.unload_all_plugins()

        # Reload all plugins
        loaded_count = _global_plugin_manager.load_all_plugins(main_window)

        print(f"✅ Reloaded {loaded_count} plugins")
        return loaded_count

    except Exception as e:
        print(f"❌ Failed to reload plugins: {e}")
        return 0

def _on_plugin_loaded(plugin_name: str) -> None:
    """Handle plugin loaded signal."""
    print(f"📦 Plugin loaded: {plugin_name}")

def _on_plugin_unloaded(plugin_name: str) -> None:
    """Handle plugin unloaded signal."""
    print(f"📦 Plugin unloaded: {plugin_name}")

def _on_plugin_error(plugin_name: str, error_message: str) -> None:
    """Handle plugin error signal."""
    print(f"❌ Plugin error [{plugin_name}]: {error_message}")

# Example usage in main.py:
"""
# In main.py, after creating MainWindow:

from plugin_integration import initialize_plugin_system, cleanup_plugin_system

# After window creation
if not initialize_plugin_system(window):
    print("Warning: Plugin system failed to initialize")

# In cleanup section
cleanup_plugin_system()
"""
