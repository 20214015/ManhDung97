"""
Enhanced Theme Manager
======================

Integrates resource bundling, Windows accent detection, and theme management.
"""

import os
from typing import Optional
from PyQt6.QtCore import QObject, QSettings, pyqtSignal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

from resources.resource_manager import get_resource_manager, load_qss
from ui.accent_detection import get_accent_manager


class EnhancedThemeManager(QObject):
    """Enhanced theme manager with resource bundling and accent detection"""
    
    theme_changed = pyqtSignal(str)  # theme name
    accent_changed = pyqtSignal(str)  # accent color
    
    def __init__(self):
        super().__init__()
        self.resource_manager = get_resource_manager()
        self.accent_manager = get_accent_manager()
        self.current_theme = "dark"
        self.accent_enabled = True
        
        # Connect accent manager signals
        self.accent_manager.theme_changed.connect(self._on_accent_theme_changed)
        
    def apply_theme(self, app: QApplication, theme_name: str = None, 
                   enable_accent: bool = True):
        """Apply theme to application"""
        if theme_name:
            self.current_theme = theme_name
            
        self.accent_enabled = enable_accent
        
        # Load base stylesheet
        base_qss = self.resource_manager.load_stylesheet(self.current_theme)
        if not base_qss:
            # Fallback to built-in theme
            base_qss = self._get_fallback_theme(self.current_theme)
            
        # Apply Windows accent if enabled
        if self.accent_enabled:
            final_qss = self.accent_manager.apply_accent_theme(base_qss)
        else:
            final_qss = base_qss
            
        # Apply to application
        app.setStyleSheet(final_qss)
        
        # Apply palette for better integration
        if self.current_theme == "dark":
            app.setPalette(self._get_dark_palette())
        else:
            app.setPalette(self._get_light_palette())
            
        self.theme_changed.emit(self.current_theme)
        
    def set_theme(self, app: QApplication, theme_name: str):
        """Set and apply new theme"""
        self.apply_theme(app, theme_name, self.accent_enabled)
        
    def toggle_accent(self, app: QApplication, enabled: bool):
        """Toggle Windows accent integration"""
        self.accent_enabled = enabled
        self.apply_theme(app, self.current_theme, enabled)
        
    def refresh_accent(self, app: QApplication):
        """Refresh Windows accent color"""
        if self.accent_enabled:
            self.accent_manager.refresh_accent_color()
            self.apply_theme(app, self.current_theme, True)
            
    def get_available_themes(self) -> list:
        """Get list of available themes"""
        themes = self.resource_manager.list_stylesheets()
        # Add built-in themes if not found in resources
        built_in = ["dark", "light"]
        for theme in built_in:
            if theme not in themes:
                themes.append(theme)
        return sorted(themes)
        
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.current_theme
        
    def is_accent_enabled(self) -> bool:
        """Check if Windows accent is enabled"""
        return self.accent_enabled
        
    def save_settings(self, settings: QSettings):
        """Save theme settings"""
        settings.setValue("theme/name", self.current_theme)
        settings.setValue("theme/accent_enabled", self.accent_enabled)
        
    def load_settings(self, settings: QSettings, app: QApplication):
        """Load theme settings"""
        theme_name = settings.value("theme/name", "dark")
        accent_enabled = settings.value("theme/accent_enabled", True, type=bool)
        
        self.apply_theme(app, theme_name, accent_enabled)
        
    def _on_accent_theme_changed(self, qss: str):
        """Handle accent theme changes"""
        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)
            
    def _get_fallback_theme(self, theme_name: str) -> str:
        """Get fallback theme if resource not found"""
        if theme_name == "dark":
            return self._get_dark_fallback()
        else:
            return self._get_light_fallback()
            
    def _get_dark_fallback(self) -> str:
        """Built-in dark theme fallback"""
        return """
/* Built-in Dark Theme */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QTableView {
    background-color: #3c3c3c;
    alternate-background-color: #404040;
    selection-background-color: #5a5a5a;
    gridline-color: #555555;
    color: #ffffff;
    border: 1px solid #555555;
}

QTableView::item {
    padding: 8px;
    border: none;
}

QTableView::item:selected {
    background-color: #5a5a5a;
}

QHeaderView::section {
    background-color: #4a4a4a;
    color: #ffffff;
    padding: 8px;
    border: 1px solid #555555;
    font-weight: bold;
}

QPushButton {
    background-color: #404040;
    color: #ffffff;
    border: 1px solid #666666;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #777777;
}

QPushButton:pressed {
    background-color: #353535;
}

QProgressBar {
    background-color: #3c3c3c;
    border: 1px solid #666666;
    border-radius: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #007acc;
    border-radius: 3px;
}

QStatusBar {
    background-color: #3a3a3a;
    color: #ffffff;
    border-top: 1px solid #555555;
}
"""
        
    def _get_light_fallback(self) -> str:
        """Built-in light theme fallback"""
        return """
/* Built-in Light Theme */
QMainWindow {
    background-color: #ffffff;
    color: #000000;
}

QTableView {
    background-color: #ffffff;
    alternate-background-color: #f5f5f5;
    selection-background-color: #0078d4;
    gridline-color: #d0d0d0;
    color: #000000;
    border: 1px solid #d0d0d0;
}

QTableView::item:selected {
    background-color: #0078d4;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #f0f0f0;
    color: #000000;
    padding: 8px;
    border: 1px solid #d0d0d0;
    font-weight: bold;
}

QPushButton {
    background-color: #f0f0f0;
    color: #000000;
    border: 1px solid #d0d0d0;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #e0e0e0;
    border-color: #b0b0b0;
}

QProgressBar {
    background-color: #f0f0f0;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 3px;
}

QStatusBar {
    background-color: #f8f8f8;
    color: #000000;
    border-top: 1px solid #d0d0d0;
}
"""

    def _get_dark_palette(self) -> QPalette:
        """Get dark color palette"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(60, 60, 60))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(64, 64, 64))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(64, 64, 64))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 68, 68))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(136, 136, 136))
        return palette
        
    def _get_light_palette(self) -> QPalette:
        """Get light color palette"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(17, 17, 17))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(17, 17, 17))
        palette.setColor(QPalette.ColorRole.Text, QColor(17, 17, 17))
        palette.setColor(QPalette.ColorRole.Button, QColor(225, 225, 225))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(17, 17, 17))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(136, 136, 136))
        return palette


# Global enhanced theme manager
_global_theme_manager = None

def get_theme_manager() -> EnhancedThemeManager:
    """Get global enhanced theme manager"""
    global _global_theme_manager
    if _global_theme_manager is None:
        _global_theme_manager = EnhancedThemeManager()
    return _global_theme_manager


def apply_enhanced_theme(app: QApplication, settings: QSettings):
    """Convenience function to apply enhanced theme"""
    theme_manager = get_theme_manager()
    theme_manager.load_settings(settings, app)