"""
Plugin System Architecture for MuMuManager Pro
==============================================

This module provides a comprehensive plugin system that enables:
- Third-party integrations
- Custom automation scripts
- UI extensions
- Custom themes
- Monitoring and analytics plugins

The system supports both directory-based and single-file plugins
with automatic discovery, dynamic loading, and lifecycle management.
"""

import abc
import importlib.util
import inspect
import logging
import os
import sys
from typing import Dict, Any, List, Optional, Type
from PyQt6.QtCore import QObject, pyqtSignal

# Configure logging
logger = logging.getLogger(__name__)

class PluginInterface(abc.ABC):
    """Base interface for all plugins"""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass

    @abc.abstractmethod
    def initialize(self, main_window: Any) -> bool:
        """Initialize the plugin with the main window"""
        pass

    @abc.abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass

class AutomationPlugin(PluginInterface):
    """Plugin for automation features"""

    @abc.abstractmethod
    def get_automation_actions(self) -> List[Dict[str, Any]]:
        """Return list of automation actions provided by this plugin"""
        pass

    @abc.abstractmethod
    def execute_action(self, action_id: str, parameters: Dict[str, Any]) -> bool:
        """Execute a specific automation action"""
        pass

class UIPlugin(PluginInterface):
    """Plugin for UI extensions"""

    @abc.abstractmethod
    def get_ui_components(self) -> List[Dict[str, Any]]:
        """Return list of UI components provided by this plugin"""
        pass

    @abc.abstractmethod
    def create_component(self, component_id: str, parent: Any) -> Optional[Any]:
        """Create a UI component instance"""
        pass

class MonitoringPlugin(PluginInterface):
    """Plugin for monitoring and analytics"""

    @abc.abstractmethod
    def get_monitoring_data(self) -> Dict[str, Any]:
        """Get current monitoring data"""
        pass

    @abc.abstractmethod
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        pass

class PluginManager(QObject):
    """Central plugin manager for MuMuManager Pro"""

    plugin_loaded = pyqtSignal(str)  # plugin_name
    plugin_unloaded = pyqtSignal(str)  # plugin_name
    plugin_error = pyqtSignal(str, str)  # plugin_name, error_message

    def __init__(self, plugins_dir: str = "plugins"):
        super().__init__()
        self.plugins_dir = plugins_dir
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.plugin_modules: Dict[str, Any] = {}

        # Ensure plugins directory exists
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir)
            logger.info(f"Created plugins directory: {plugins_dir}")

    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory"""
        plugins = []

        if not os.path.exists(self.plugins_dir):
            logger.warning(f"Plugins directory does not exist: {self.plugins_dir}")
            return plugins

        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                plugin_name = filename[:-3]  # Remove .py extension
                plugins.append(plugin_name)

        logger.info(f"Discovered {len(plugins)} plugins: {plugins}")
        return plugins

    def load_plugin(self, plugin_name: str, main_window: Any) -> bool:
        """Load a specific plugin"""
        try:
            plugin_path = os.path.join(self.plugins_dir, f"{plugin_name}.py")

            if not os.path.exists(plugin_path):
                logger.error(f"Plugin file not found: {plugin_path}")
                return False

            # Load the module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                logger.error(f"Could not load plugin spec for {plugin_name}")
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            self.plugin_modules[plugin_name] = module

            # Find the plugin class
            plugin_class = self._find_plugin_class(module)
            if plugin_class is None:
                logger.error(f"No plugin class found in {plugin_name}")
                return False

            # Instantiate and initialize the plugin
            plugin_instance = plugin_class()
            if not plugin_instance.initialize(main_window):
                logger.error(f"Plugin {plugin_name} failed to initialize")
                return False

            self.loaded_plugins[plugin_name] = plugin_instance
            self.plugin_loaded.emit(plugin_name)

            logger.info(f"Successfully loaded plugin: {plugin_name}")
            return True

        except Exception as e:
            error_msg = f"Failed to load plugin {plugin_name}: {str(e)}"
            logger.error(error_msg)
            self.plugin_error.emit(plugin_name, error_msg)
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        try:
            if plugin_name not in self.loaded_plugins:
                logger.warning(f"Plugin {plugin_name} is not loaded")
                return False

            plugin = self.loaded_plugins[plugin_name]
            plugin.cleanup()

            # Remove from loaded plugins
            del self.loaded_plugins[plugin_name]

            # Remove module if it exists
            if plugin_name in self.plugin_modules:
                del sys.modules[plugin_name]
                del self.plugin_modules[plugin_name]

            self.plugin_unloaded.emit(plugin_name)
            logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            error_msg = f"Failed to unload plugin {plugin_name}: {str(e)}"
            logger.error(error_msg)
            self.plugin_error.emit(plugin_name, error_msg)
            return False

    def load_all_plugins(self, main_window: Any) -> int:
        """Load all discovered plugins"""
        plugins = self.discover_plugins()
        loaded_count = 0

        for plugin_name in plugins:
            if self.load_plugin(plugin_name, main_window):
                loaded_count += 1

        logger.info(f"Loaded {loaded_count}/{len(plugins)} plugins")
        return loaded_count

    def unload_all_plugins(self) -> int:
        """Unload all loaded plugins"""
        plugin_names = list(self.loaded_plugins.keys())
        unloaded_count = 0

        for plugin_name in plugin_names:
            if self.unload_plugin(plugin_name):
                unloaded_count += 1

        logger.info(f"Unloaded {unloaded_count} plugins")
        return unloaded_count

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Get a loaded plugin instance"""
        return self.loaded_plugins.get(plugin_name)

    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin names"""
        return list(self.loaded_plugins.keys())

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a plugin"""
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            return None

        return {
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "type": type(plugin).__name__
        }

    def _find_plugin_class(self, module: Any) -> Optional[Type[PluginInterface]]:
        """Find the plugin class in a module"""
        for _, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and
                issubclass(obj, PluginInterface) and
                obj != PluginInterface and
                obj != AutomationPlugin and
                obj != UIPlugin and
                obj != MonitoringPlugin):
                return obj
        return None
