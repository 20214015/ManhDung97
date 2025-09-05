"""
Resource Manager - Manual QRC Resource Loading
==============================================

Since pyrcc6 is not available, this module provides manual resource loading.
"""

import os
from typing import Dict, Optional
from PyQt6.QtCore import QFile, QIODevice


class ResourceManager:
    """Manual resource manager for QSS and icon files"""
    
    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.resources_path = os.path.join(self.base_path, "resources")
        self._cache: Dict[str, str] = {}
        
    def load_stylesheet(self, name: str) -> Optional[str]:
        """Load stylesheet by name (e.g., 'dark', 'light')"""
        cache_key = f"style_{name}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        style_path = os.path.join(self.resources_path, "styles", f"{name}.qss")
        
        if not os.path.isfile(style_path):
            print(f"Warning: Stylesheet not found: {style_path}")
            return None
            
        try:
            with open(style_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self._cache[cache_key] = content
                return content
        except Exception as e:
            print(f"Error loading stylesheet {name}: {e}")
            return None
            
    def load_icon_data(self, name: str) -> Optional[bytes]:
        """Load icon data by name"""
        cache_key = f"icon_{name}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        # Try different icon formats
        for ext in ['png', 'svg', 'ico']:
            icon_path = os.path.join(self.resources_path, "icons", f"{name}.{ext}")
            if os.path.isfile(icon_path):
                try:
                    with open(icon_path, 'rb') as f:
                        data = f.read()
                        self._cache[cache_key] = data
                        return data
                except Exception as e:
                    print(f"Error loading icon {name}.{ext}: {e}")
                    continue
                    
        print(f"Warning: Icon not found: {name}")
        return None
        
    def get_resource_path(self, resource_type: str, name: str) -> str:
        """Get full path to resource file"""
        if resource_type == "styles":
            return os.path.join(self.resources_path, "styles", f"{name}.qss")
        elif resource_type == "icons":
            # Try to find with any extension
            for ext in ['png', 'svg', 'ico']:
                path = os.path.join(self.resources_path, "icons", f"{name}.{ext}")
                if os.path.isfile(path):
                    return path
            return os.path.join(self.resources_path, "icons", f"{name}.png")  # Default
        else:
            return os.path.join(self.resources_path, resource_type, name)
            
    def list_stylesheets(self) -> list:
        """List available stylesheets"""
        styles_dir = os.path.join(self.resources_path, "styles")
        if not os.path.isdir(styles_dir):
            return []
            
        stylesheets = []
        for file in os.listdir(styles_dir):
            if file.endswith('.qss'):
                stylesheets.append(file[:-4])  # Remove .qss extension
                
        return stylesheets
        
    def ensure_resources_exist(self):
        """Ensure resource directories exist and create default resources if missing"""
        os.makedirs(os.path.join(self.resources_path, "styles"), exist_ok=True)
        os.makedirs(os.path.join(self.resources_path, "icons"), exist_ok=True)
        
        # Create default dark style if missing
        dark_style_path = os.path.join(self.resources_path, "styles", "dark.qss")
        if not os.path.isfile(dark_style_path):
            self._create_default_dark_style(dark_style_path)
            
    def _create_default_dark_style(self, path: str):
        """Create a minimal default dark style"""
        default_style = """
/* Default Dark Theme */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QTableView {
    background-color: #3c3c3c;
    alternate-background-color: #404040;
    selection-background-color: #5a5a5a;
    color: #ffffff;
    gridline-color: #555555;
}

QPushButton {
    background-color: #404040;
    color: #ffffff;
    border: 1px solid #666666;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #4a4a4a;
}
"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(default_style)
        except Exception as e:
            print(f"Error creating default style: {e}")


# Global resource manager instance
_global_resource_manager = None

def get_resource_manager() -> ResourceManager:
    """Get global resource manager instance"""
    global _global_resource_manager
    if _global_resource_manager is None:
        _global_resource_manager = ResourceManager()
        _global_resource_manager.ensure_resources_exist()
    return _global_resource_manager


def load_qss(style_name: str) -> str:
    """Convenience function to load QSS stylesheet"""
    manager = get_resource_manager()
    content = manager.load_stylesheet(style_name)
    return content or ""


def get_style_path(style_name: str) -> str:
    """Get path to stylesheet file"""
    manager = get_resource_manager()
    return manager.get_resource_path("styles", style_name)