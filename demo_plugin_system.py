"""
Plugin System Demo Script
=========================

This script demonstrates the plugin system functionality
by loading and testing the example plugins.
"""

import os
import sys
from typing import Any

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def demo_plugin_system():
    """Demonstrate the plugin system functionality."""
    print("🚀 Starting Plugin System Demo")
    print("=" * 50)

    try:
        from core.plugin_system import PluginManager
    except ImportError as e:
        print(f"❌ Failed to import PluginManager: {e}")
        return

    # Create a mock main window for demo
    class MockMainWindow:
        def __init__(self):
            self.dock_widgets = {}

        def add_dock_widget(self, widget, title, position):
            """Mock method to add dock widget."""
            self.dock_widgets[title] = widget
            print(f"📌 Added dock widget: {title} at {position}")

        def remove_dock_widget(self, widget):
            """Mock method to remove dock widget."""
            for title, w in self.dock_widgets.items():
                if w == widget:
                    del self.dock_widgets[title]
                    print(f"📌 Removed dock widget: {title}")
                    break

    main_window = MockMainWindow()

    # Create plugin manager
    plugins_dir = os.path.join(current_dir, "plugins")
    plugin_manager = PluginManager(plugins_dir)

    print(f"🔍 Plugins directory: {plugins_dir}")
    print(f"📁 Directory exists: {os.path.exists(plugins_dir)}")

    # Discover plugins
    print("\n🔍 Discovering plugins...")
    discovered_plugins = plugin_manager.discover_plugins()
    print(f"📦 Found {len(discovered_plugins)} plugins: {discovered_plugins}")

    if not discovered_plugins:
        print("❌ No plugins found. Creating example plugins...")
        return

    # Load plugins
    print("\n📦 Loading plugins...")
    loaded_count = 0
    for plugin_name in discovered_plugins:
        print(f"  Loading {plugin_name}...")
        if plugin_manager.load_plugin(plugin_name, main_window):
            loaded_count += 1
            print(f"  ✅ {plugin_name} loaded successfully")
        else:
            print(f"  ❌ Failed to load {plugin_name}")

    print(f"\n✅ Loaded {loaded_count}/{len(discovered_plugins)} plugins")

    # Show loaded plugins info
    print("\n📋 Loaded Plugins Info:")
    loaded_plugins = plugin_manager.get_loaded_plugins()
    for plugin_name in loaded_plugins:
        info = plugin_manager.get_plugin_info(plugin_name)
        if info:
            print(f"  📦 {plugin_name}: {info['description']} (v{info['version']})")

    # Test plugin functionality
    print("\n🧪 Testing Plugin Functionality:")

    # Test System Monitor
    system_monitor = plugin_manager.get_plugin("system_monitor")
    if system_monitor:
        print("  🖥️ Testing System Monitor...")
        data = system_monitor.get_monitoring_data()
        print(f"    CPU: {data.get('cpu_percent', 'N/A'):.1f}%")
        print(f"    Memory: {data.get('memory_percent', 'N/A'):.1f}%")

    # Test File Organizer
    file_organizer = plugin_manager.get_plugin("file_organizer")
    if file_organizer:
        print("  📁 Testing File Organizer...")
        actions = file_organizer.get_automation_actions()
        print(f"    Available actions: {len(actions)}")
        for action in actions:
            print(f"      - {action['name']}: {action['description']}")

    # Test Quick Notes
    quick_notes = plugin_manager.get_plugin("quick_notes")
    if quick_notes:
        print("  📝 Testing Quick Notes...")
        components = quick_notes.get_ui_components()
        print(f"    Available components: {len(components)}")
        for component in components:
            print(f"      - {component['name']}: {component['description']}")

    # Unload plugins
    print("\n🔄 Unloading plugins...")
    unloaded_count = plugin_manager.unload_all_plugins()
    print(f"✅ Unloaded {unloaded_count} plugins")

    print("\n🎉 Plugin System Demo completed successfully!")

if __name__ == "__main__":
    demo_plugin_system()
