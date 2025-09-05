# theme.py - Manages the application's visual theme and stylesheet
# Updated with comprehensive Monokai theme integration

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

# Import comprehensive Monokai theme
try:
    from monokai_theme import MonokaiTheme, apply_monokai_theme
    MONOKAI_AVAILABLE = True
except ImportError:
    MONOKAI_AVAILABLE = False

# Placeholder for the accent color in the stylesheet template
ACCENT_COLOR_PLACEHOLDER = "{{ACCENT_COLOR}}"

class AppTheme:
    """Manages the application's color palette and stylesheet for a modern look."""

    @staticmethod
    def get_dark_palette() -> QPalette:
        """Creates the palette for Dark Mode."""
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
        p.setColor(QPalette.ColorRole.WindowText, QColor("#e0e0e0"))
        p.setColor(QPalette.ColorRole.Base, QColor("#2a2a2a"))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor("#313131"))
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2a2a2a"))
        p.setColor(QPalette.ColorRole.ToolTipText, QColor("#e0e0e0"))
        p.setColor(QPalette.ColorRole.Text, QColor("#e0e0e0"))
        p.setColor(QPalette.ColorRole.Button, QColor("#3c3c3c"))
        p.setColor(QPalette.ColorRole.ButtonText, QColor("#e0e0e0"))
        p.setColor(QPalette.ColorRole.BrightText, QColor("#ff4444"))
        p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#888888"))
        return p

    @staticmethod
    def get_light_palette() -> QPalette:
        """Creates the palette for Light Mode."""
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
        p.setColor(QPalette.ColorRole.WindowText, QColor("#111111"))
        p.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor("#f5f5f5"))
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.ToolTipText, QColor("#111111"))
        p.setColor(QPalette.ColorRole.Text, QColor("#111111"))
        p.setColor(QPalette.ColorRole.Button, QColor("#e1e1e1"))
        p.setColor(QPalette.ColorRole.ButtonText, QColor("#111111"))
        p.setColor(QPalette.ColorRole.BrightText, QColor("#ff0000"))
        p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#a0a0a0"))
        return p

    @staticmethod
    def get_monokai_palette() -> QPalette:
        """Creates the palette for Monokai Theme."""
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor("#272822")) # Background
        p.setColor(QPalette.ColorRole.WindowText, QColor("#F8F8F2")) # Foreground
        p.setColor(QPalette.ColorRole.Base, QColor("#2D2A2E")) # Input background
        p.setColor(QPalette.ColorRole.AlternateBase, QColor("#3E3D32")) # Alternate
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2D2A2E"))
        p.setColor(QPalette.ColorRole.ToolTipText, QColor("#F8F8F2"))
        p.setColor(QPalette.ColorRole.Text, QColor("#F8F8F2"))
        p.setColor(QPalette.ColorRole.Button, QColor("#49483E"))
        p.setColor(QPalette.ColorRole.ButtonText, QColor("#F8F8F2"))
        p.setColor(QPalette.ColorRole.BrightText, QColor("#F92672")) # Pink
        p.setColor(QPalette.ColorRole.PlaceholderText, QColor("#75715E"))
        return p

    @staticmethod
    def get_stylesheet_template(theme_name: str, accent_color: str) -> str:
        """Generates a detailed stylesheet template based on the theme name."""
        
        # Color definitions based on theme
        if theme_name == "dark":
            bg_color = "#1e1e1e"
            text_color = "#e0e0e0"
            base_color = "#2a2a2a"
            border_color = "#333"
            header_color = "#3c3c3c"
            button_color = "#3c3c3c"
            button_hover = "#4a4a4a"
            sidebar_color = "#252526"
        elif theme_name == "light":
            bg_color = "#f0f0f0"
            text_color = "#111111"
            base_color = "#ffffff"
            border_color = "#ccc"
            header_color = "#f0f0f0"
            button_color = "#e1e1e1"
            button_hover = "#d1d1d1"
            sidebar_color = "#e1e1e1"
        elif theme_name == "monokai":
            bg_color = "#272822"
            text_color = "#F8F8F2"
            base_color = "#2D2A2E"
            border_color = "#49483E"
            header_color = "#3E3D32"
            button_color = "#49483E"
            button_hover = "#5a5950"
            sidebar_color = "#1D1E19"
        else: # Default to dark
            bg_color, text_color, base_color, border_color, header_color, button_color, button_hover, sidebar_color = ("#1e1e1e", "#e0e0e0", "#2a2a2a", "#333", "#3c3c3c", "#3c3c3c", "#4a4a4a", "#252526")

        return f"""
            /* --- GENERAL --- */
            QWidget {{
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 10pt;
                color: {text_color};
            }}
            QMainWindow, QDialog {{ background-color: {bg_color}; }}
            QFrame#sidebar {{
                background-color: {sidebar_color};
                border-right: 1px solid {border_color};
            }}
            QGroupBox {{
                border: 1px solid {border_color};
                border-radius: 6px;
                margin-top: 8px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }}

            /* --- INPUTS & CONTROLS --- */
            QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QComboBox {{
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 7px;
                background-color: {base_color};
            }}
            QPushButton {{
                border: 1px solid transparent;
                border-radius: 5px;
                padding: 8px 12px;
                background-color: {button_color};
            }}
            QPushButton:hover {{ background-color: {button_hover}; }}
            QPushButton:pressed {{ background-color: {border_color}; }}
            QPushButton:disabled {{
                background-color: {border_color};
                color: #888;
            }}
            
            /* ModernButton color variants */
            QPushButton[variant="success"] {{
                background-color: #10b981;
                color: white;
            }}
            QPushButton[variant="success"]:hover {{
                background-color: #059669;
            }}
            QPushButton[variant="success"]:disabled {{
                background-color: {border_color} !important;
                color: #888 !important;
            }}
            QPushButton[variant="warning"] {{
                background-color: #f59e0b;
                color: white;
            }}
            QPushButton[variant="warning"]:hover {{
                background-color: #d97706;
            }}
            QPushButton[variant="warning"]:disabled {{
                background-color: {border_color} !important;
                color: #888 !important;
            }}
            QPushButton[variant="danger"] {{
                background-color: #ef4444;
                color: white;
            }}
            QPushButton[variant="danger"]:hover {{
                background-color: #dc2626;
            }}
            QPushButton[variant="danger"]:disabled {{
                background-color: {border_color} !important;
                color: #888 !important;
            }}
            QPushButton[variant="secondary"] {{
                background-color: {button_color};
                color: {text_color};
                border: 1px solid {border_color};
            }}
            QPushButton[variant="secondary"]:hover {{
                background-color: {button_hover};
            }}
            QPushButton[variant="secondary"]:disabled {{
                background-color: {border_color} !important;
                color: #888 !important;
            }}
            QPushButton[variant="primary"] {{
                background-color: {accent_color};
                color: white;
            }}
            QPushButton[variant="primary"]:hover {{
                background-color: {accent_color};
                opacity: 0.9;
            }}
            QPushButton[variant="primary"]:disabled {{
                background-color: {border_color} !important;
                color: #888 !important;
            }}
            
            /* --- TABLE --- */
            QTableWidget {{
                gridline-color: {border_color};
                background-color: {base_color};
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
            QHeaderView::section {{
                background-color: {header_color};
                border: none;
                padding: 6px;
                border-bottom: 1px solid {border_color};
            }}
            QTableWidget::item:selected {{
                background-color: {accent_color};
                color: #ffffff;
            }}

            /* --- OTHER WIDGETS --- */
            QTabWidget::pane {{ border: none; }}
            QProgressBar {{
                text-align: center;
                border-radius: 8px;
                border: 1px solid {border_color};
                background-color: {base_color};
            }}
            QProgressBar::chunk {{
                border-radius: 7px;
                background-color: {accent_color};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {bg_color};
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {button_color};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {bg_color};
                height: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {button_color};
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """

    # Theme cache để tránh recompute stylesheet 
    _theme_cache = {}
    
    @staticmethod
    def apply_theme(app: QApplication, settings):
        """Applies the theme and accent color với caching và error handling"""
        theme_name = settings.value("theme/name", "monokai")  # Default to monokai
        accent_color = settings.value("theme/accent_color", "#F92672")  # Monokai pink
        
        # Generate cache key
        cache_key = f"{theme_name}_{accent_color}"
        
        try:
            app.setStyle("Fusion")
            
            # Use comprehensive Monokai theme if available and selected
            if theme_name == "monokai" and MONOKAI_AVAILABLE:
                try:
                    apply_monokai_theme(app)
                    print("✅ Comprehensive Monokai theme applied")
                    return
                except Exception as e:
                    print(f"⚠️ Failed to apply comprehensive Monokai theme: {e}")
                    # Fall back to basic monokai
            
            # Check cache first for other themes
            if cache_key in AppTheme._theme_cache:
                cached_palette, cached_stylesheet = AppTheme._theme_cache[cache_key]
                app.setPalette(cached_palette)
                app.setStyleSheet(cached_stylesheet)
                return
            
            # Fallback to basic theme system
            if theme_name == "light":
                palette = AppTheme.get_light_palette()
            elif theme_name == "monokai":
                palette = AppTheme.get_monokai_palette()
            else:
                palette = AppTheme.get_dark_palette()
            
            palette.setColor(QPalette.ColorRole.Highlight, QColor(accent_color))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            
            final_stylesheet = AppTheme.get_stylesheet_template(theme_name, accent_color)
            
            # Cache the theme
            AppTheme._theme_cache[cache_key] = (palette, final_stylesheet)
            
            app.setPalette(palette)
            app.setStyleSheet(final_stylesheet)
            
        except Exception as e:
            print(f"⚠️ Theme application failed: {e}, using fallback")
            # Apply safe fallback theme
            try:
                app.setPalette(AppTheme.get_dark_palette())
                app.setStyleSheet("")  # Clear any problematic stylesheet
            except Exception:
                pass  # Silent fail for ultimate fallback