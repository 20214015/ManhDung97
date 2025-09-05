"""
Windows Accent Color Detection
==============================

Auto-detects Windows accent color from Registry and maps to QSS themes.
"""

import sys
import os
from typing import Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor

# Windows-specific imports
if sys.platform == "win32":
    try:
        import winreg
        WINREG_AVAILABLE = True
    except ImportError:
        WINREG_AVAILABLE = False
else:
    WINREG_AVAILABLE = False


class WindowsAccentDetector(QObject):
    """Detects Windows accent color and provides theme mapping"""
    
    accent_changed = pyqtSignal(str)  # Emits hex color
    
    def __init__(self):
        super().__init__()
        self.fallback_color = "#0078D4"  # Windows 10/11 default blue
        
    def get_accent_color(self) -> str:
        """Get Windows accent color as hex string"""
        if not WINREG_AVAILABLE or sys.platform != "win32":
            return self.fallback_color
            
        try:
            # Try Windows 10/11 registry path
            accent_color = self._get_accent_from_registry()
            if accent_color:
                return accent_color
                
        except Exception as e:
            print(f"Error reading Windows accent color: {e}")
            
        return self.fallback_color
        
    def _get_accent_from_registry(self) -> Optional[str]:
        """Read accent color from Windows registry"""
        try:
            # Windows 10/11 accent color location
            reg_path = r"SOFTWARE\Microsoft\Windows\DWM"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                # Try to get accent color
                try:
                    accent_color_value, _ = winreg.QueryValueEx(key, "AccentColor")
                    # Convert DWORD to hex color
                    return self._dword_to_hex(accent_color_value)
                except FileNotFoundError:
                    pass
                    
                # Try alternative names
                for value_name in ["ColorizationColor", "AccentColorMenu"]:
                    try:
                        color_value, _ = winreg.QueryValueEx(key, value_name)
                        return self._dword_to_hex(color_value)
                    except FileNotFoundError:
                        continue
                        
        except Exception as e:
            print(f"Registry access error: {e}")
            
        return None
        
    def _dword_to_hex(self, dword_value: int) -> str:
        """Convert DWORD registry value to hex color"""
        # DWORD format: 0xAABBGGRR (Alpha, Blue, Green, Red)
        # We need #RRGGBB format
        
        red = dword_value & 0xFF
        green = (dword_value >> 8) & 0xFF
        blue = (dword_value >> 16) & 0xFF
        
        return f"#{red:02X}{green:02X}{blue:02X}"
        
    def get_complementary_colors(self, accent_hex: str) -> dict:
        """Generate complementary colors for theming"""
        try:
            color = QColor(accent_hex)
            if not color.isValid():
                color = QColor(self.fallback_color)
                
            # Generate color variations
            hue = color.hue()
            saturation = color.saturation()
            value = color.value()
            
            # Create theme color palette
            colors = {
                "accent": accent_hex,
                "accent_light": self._hsv_to_hex(hue, max(0, saturation - 50), min(255, value + 30)),
                "accent_dark": self._hsv_to_hex(hue, min(255, saturation + 30), max(0, value - 30)),
                "accent_hover": self._hsv_to_hex(hue, saturation, min(255, value + 20)),
                "accent_pressed": self._hsv_to_hex(hue, saturation, max(0, value - 20)),
            }
            
            return colors
            
        except Exception:
            # Fallback colors
            return {
                "accent": self.fallback_color,
                "accent_light": "#1E90FF",
                "accent_dark": "#005BB5",
                "accent_hover": "#106EBE",
                "accent_pressed": "#004B97",
            }
            
    def _hsv_to_hex(self, h: int, s: int, v: int) -> str:
        """Convert HSV to hex color"""
        color = QColor()
        color.setHsv(h, s, v)
        return color.name()
        
    def generate_accent_qss(self, accent_hex: str) -> str:
        """Generate QSS with accent color"""
        colors = self.get_complementary_colors(accent_hex)
        
        qss_template = f"""
/* Windows Accent Color Theme */
QPushButton[primary="true"] {{
    background-color: {colors['accent']};
    color: white;
    border: 1px solid {colors['accent_dark']};
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}}

QPushButton[primary="true"]:hover {{
    background-color: {colors['accent_hover']};
    border-color: {colors['accent_dark']};
}}

QPushButton[primary="true"]:pressed {{
    background-color: {colors['accent_pressed']};
}}

QProgressBar::chunk {{
    background-color: {colors['accent']};
}}

QTabBar::tab:selected {{
    border-bottom: 2px solid {colors['accent']};
}}

QLineEdit:focus {{
    border-color: {colors['accent']};
}}

QTableView::item:selected {{
    background-color: {colors['accent']};
}}

QCheckBox::indicator:checked {{
    background-color: {colors['accent']};
    border-color: {colors['accent']};
}}

QCheckBox::indicator:checked:hover {{
    background-color: {colors['accent_hover']};
}}

QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {{
    background-color: {colors['accent_light']};
}}

/* Status pill colors with accent */
.status-pill-accent {{
    background-color: {colors['accent']};
    color: white;
    border-radius: 12px;
    padding: 4px 8px;
    font-weight: bold;
}}
"""
        return qss_template


class AccentThemeManager(QObject):
    """Manages accent-based theming"""
    
    theme_changed = pyqtSignal(str)  # Emits QSS string
    
    def __init__(self):
        super().__init__()
        self.detector = WindowsAccentDetector()
        self.current_accent = self.detector.get_accent_color()
        
    def apply_accent_theme(self, base_qss: str = "") -> str:
        """Apply accent color to base theme"""
        accent_color = self.detector.get_accent_color()
        accent_qss = self.detector.generate_accent_qss(accent_color)
        
        # Combine base theme with accent colors
        combined_qss = base_qss + "\n" + accent_qss
        
        self.theme_changed.emit(combined_qss)
        return combined_qss
        
    def refresh_accent_color(self):
        """Refresh accent color from system"""
        new_accent = self.detector.get_accent_color()
        if new_accent != self.current_accent:
            self.current_accent = new_accent
            self.detector.accent_changed.emit(new_accent)
            
    def get_current_accent(self) -> str:
        """Get current accent color"""
        return self.current_accent


# Global accent theme manager
_global_accent_manager = None

def get_accent_manager() -> AccentThemeManager:
    """Get global accent theme manager"""
    global _global_accent_manager
    if _global_accent_manager is None:
        _global_accent_manager = AccentThemeManager()
    return _global_accent_manager