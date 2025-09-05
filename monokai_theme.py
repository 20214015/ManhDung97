"""
Monokai Theme Manager - Quản lý theme Monokai toàn diện cho MumuManagerPRO
Cung cấp màu sắc và styling nhất quán cho toàn bộ ứng dụng
"""

from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

class MonokaiTheme:
    """Theme manager cho Monokai với màu sắc đặc trưng"""
    
    # Monokai Color Palette
    COLORS = {
        # Core colors
        'bg': '#272822',           # Background chính
        'bg_alt': '#2D2A2E',       # Background phụ  
        'bg_dark': '#1D1E19',      # Background tối hơn
        'fg': '#F8F8F2',           # Text chính
        'fg_dim': '#75715E',       # Text mờ/comment
        
        # Accent colors
        'pink': '#F92672',         # Hot pink - primary accent
        'green': '#A6E22E',        # Lime green - success
        'orange': '#FD971F',       # Orange - warning
        'blue': '#66D9EF',         # Cyan blue - info
        'purple': '#AE81FF',       # Purple - special
        'yellow': '#E6DB74',       # Yellow - string/highlight
        
        # UI elements
        'border': '#49483E',       # Border color
        'selection': '#3E3D32',    # Selection background
        'hover': '#5A5950',        # Hover state
        'active': '#75715E',       # Active state
        'disabled': '#3C3C3C',     # Disabled state
        
        # Status colors
        'success': '#A6E22E',      # Success green
        'warning': '#FD971F',      # Warning orange
        'error': '#F92672',        # Error pink
        'info': '#66D9EF',         # Info blue
    }
    
    @staticmethod
    def get_palette() -> QPalette:
        """Tạo QPalette cho Monokai theme"""
        palette = QPalette()
        colors = MonokaiTheme.COLORS
        
        # Basic colors
        palette.setColor(QPalette.ColorRole.Window, QColor(colors['bg']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['fg']))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['bg_alt']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['selection']))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors['bg_alt']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors['fg']))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['fg']))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['border']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['fg']))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['pink']))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(colors['fg_dim']))
        
        # Selection colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['pink']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors['fg']))
        
        return palette
    
    @staticmethod
    def get_fonts():
        """Lấy fonts cho Monokai theme"""
        # Primary font (monospace cho coding feel)
        primary_font = QFont("Consolas", 10)
        if not primary_font.exactMatch():
            primary_font = QFont("Monaco", 10)
            if not primary_font.exactMatch():
                primary_font = QFont("Courier New", 10)
        
        # UI font (sans-serif cho UI elements)
        ui_font = QFont("Segoe UI", 9)
        if not ui_font.exactMatch():
            ui_font = QFont("Arial", 9)
            
        # Title font (bold cho headers)
        title_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        
        return {
            'primary': primary_font,
            'ui': ui_font,
            'title': title_font
        }
    
    @staticmethod
    def get_complete_stylesheet():
        """Lấy stylesheet hoàn chỉnh cho toàn bộ app"""
        colors = MonokaiTheme.COLORS
        
        return f"""
        /* =================================
           MONOKAI THEME - GLOBAL STYLES
           ================================= */
        
        /* Main Application */
        QWidget {{
            background-color: {colors['bg']};
            color: {colors['fg']};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 9pt;
            selection-background-color: {colors['pink']};
            selection-color: {colors['fg']};
        }}
        
        /* Main Window */
        QMainWindow {{
            background-color: {colors['bg']};
            color: {colors['fg']};
        }}
        
        /* ===== SIDEBAR ===== */
        QWidget#Sidebar {{
            background-color: {colors['bg_dark']};
            border-right: 2px solid {colors['border']};
        }}
        
        /* Sidebar Buttons */
        QPushButton#SidebarButton {{
            background-color: transparent;
            border: none;
            color: {colors['fg_dim']};
            padding: 12px 15px;
            text-align: left;
            font-weight: bold;
            font-size: 11pt;
            border-radius: 0px;
        }}
        
        QPushButton#SidebarButton:hover {{
            background-color: {colors['hover']};
            color: {colors['fg']};
        }}
        
        QPushButton#SidebarButton:checked {{
            background-color: {colors['pink']};
            color: {colors['fg']};
            border-left: 4px solid {colors['yellow']};
        }}
        
        /* Sidebar Title */
        QLabel#SidebarTitle {{
            background-color: {colors['pink']};
            color: {colors['fg']};
            font-size: 14pt;
            font-weight: bold;
            padding: 15px;
            border-bottom: 2px solid {colors['border']};
        }}
        
        /* ===== CONTENT AREA ===== */
        QStackedWidget {{
            background-color: {colors['bg']};
            border: none;
        }}
        
        /* ===== TABLES ===== */
        QTableWidget, QTableView {{
            background-color: {colors['bg']};
            alternate-background-color: {colors['bg_alt']};
            color: {colors['fg']};
            border: 1px solid {colors['border']};
            gridline-color: {colors['border']};
            selection-background-color: {colors['pink']};
            selection-color: {colors['fg']};
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 10pt;
        }}
        
        QTableWidget::item, QTableView::item {{
            padding: 8px;
            border-bottom: 1px solid {colors['border']};
        }}
        
        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: {colors['pink']};
            color: {colors['fg']};
        }}
        
        QTableWidget::item:hover, QTableView::item:hover {{
            background-color: {colors['hover']};
        }}
        
        /* Table Headers */
        QHeaderView::section {{
            background-color: {colors['border']};
            color: {colors['fg']};
            padding: 10px 8px;
            border: 1px solid {colors['fg_dim']};
            font-weight: bold;
            font-size: 10pt;
        }}
        
        QHeaderView::section:hover {{
            background-color: {colors['hover']};
        }}
        
        /* ===== BUTTONS ===== */
        QPushButton {{
            background-color: {colors['border']};
            border: 1px solid {colors['fg_dim']};
            border-radius: 4px;
            padding: 8px 16px;
            color: {colors['fg']};
            font-weight: bold;
            font-size: 10pt;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['hover']};
            border-color: {colors['pink']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['pink']};
            border-color: {colors['pink']};
        }}
        
        QPushButton:checked {{
            background-color: {colors['green']};
            border-color: {colors['green']};
        }}
        
        QPushButton:disabled {{
            background-color: {colors['disabled']};
            color: {colors['fg_dim']};
            border-color: {colors['disabled']};
        }}
        
        /* Primary Buttons */
        QPushButton#PrimaryButton {{
            background-color: {colors['pink']};
            border-color: {colors['pink']};
            color: {colors['fg']};
        }}
        
        QPushButton#PrimaryButton:hover {{
            background-color: #FF4081;
            border-color: #FF4081;
        }}
        
        /* Success Buttons */
        QPushButton#SuccessButton {{
            background-color: {colors['green']};
            border-color: {colors['green']};
        }}
        
        /* Warning Buttons */
        QPushButton#WarningButton {{
            background-color: {colors['orange']};
            border-color: {colors['orange']};
        }}
        
        /* Info Buttons */
        QPushButton#InfoButton {{
            background-color: {colors['blue']};
            border-color: {colors['blue']};
        }}
        
        /* ===== INPUT FIELDS ===== */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['bg_alt']};
            border: 2px solid {colors['border']};
            border-radius: 4px;
            padding: 8px;
            color: {colors['fg']};
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 10pt;
            selection-background-color: {colors['pink']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors['blue']};
        }}
        
        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
            border-color: {colors['hover']};
        }}
        
        /* ===== COMBOBOX ===== */
        QComboBox {{
            background-color: {colors['bg_alt']};
            border: 2px solid {colors['border']};
            border-radius: 4px;
            padding: 6px 12px;
            color: {colors['fg']};
            font-size: 10pt;
            min-width: 80px;
        }}
        
        QComboBox:hover {{
            border-color: {colors['hover']};
        }}
        
        QComboBox:focus {{
            border-color: {colors['blue']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 25px;
            background-color: {colors['border']};
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid {colors['fg_dim']};
            margin: 0px 6px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['bg_alt']};
            border: 2px solid {colors['border']};
            color: {colors['fg']};
            selection-background-color: {colors['pink']};
            padding: 4px;
        }}
        
        /* ===== LABELS ===== */
        QLabel {{
            color: {colors['fg']};
            background-color: transparent;
        }}
        
        QLabel#TitleLabel {{
            font-size: 16pt;
            font-weight: bold;
            color: {colors['pink']};
            padding: 10px;
        }}
        
        QLabel#HeaderLabel {{
            font-size: 14pt;
            font-weight: bold;
            color: {colors['yellow']};
            padding: 8px;
        }}
        
        QLabel#SubLabel {{
            color: {colors['fg_dim']};
            font-size: 9pt;
        }}
        
        /* ===== GROUP BOXES ===== */
        QGroupBox {{
            color: {colors['fg']};
            border: 2px solid {colors['border']};
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
            font-size: 11pt;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 10px 0 10px;
            color: {colors['orange']};
            background-color: {colors['bg']};
        }}
        
        /* ===== TABS ===== */
        QTabWidget::pane {{
            border: 2px solid {colors['border']};
            background-color: {colors['bg']};
        }}
        
        QTabBar::tab {{
            background-color: {colors['bg_alt']};
            color: {colors['fg_dim']};
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-weight: bold;
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors['hover']};
            color: {colors['fg']};
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['pink']};
            color: {colors['fg']};
        }}
        
        /* ===== SCROLLBARS ===== */
        QScrollBar:vertical {{
            background-color: {colors['bg_alt']};
            width: 14px;
            border-radius: 7px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 7px;
            min-height: 25px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['hover']};
        }}
        
        QScrollBar::handle:vertical:pressed {{
            background-color: {colors['pink']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors['bg_alt']};
            height: 14px;
            border-radius: 7px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors['border']};
            border-radius: 7px;
            min-width: 25px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['hover']};
        }}
        
        QScrollBar::handle:horizontal:pressed {{
            background-color: {colors['pink']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 0px;
        }}
        
        /* ===== PROGRESS BARS ===== */
        QProgressBar {{
            border: 2px solid {colors['border']};
            border-radius: 6px;
            background-color: {colors['bg_alt']};
            text-align: center;
            color: {colors['fg']};
            font-weight: bold;
            font-size: 10pt;
            height: 20px;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['green']};
            border-radius: 4px;
            margin: 1px;
        }}
        
        /* ===== CHECKBOXES ===== */
        QCheckBox {{
            color: {colors['fg']};
            font-size: 10pt;
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid {colors['border']};
            border-radius: 3px;
            background-color: {colors['bg_alt']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {colors['blue']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['green']};
            border-color: {colors['green']};
            image: none;
        }}
        
        /* ===== RADIO BUTTONS ===== */
        QRadioButton {{
            color: {colors['fg']};
            font-size: 10pt;
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid {colors['border']};
            border-radius: 8px;
            background-color: {colors['bg_alt']};
        }}
        
        QRadioButton::indicator:hover {{
            border-color: {colors['blue']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors['pink']};
            border-color: {colors['pink']};
        }}
        
        /* ===== SLIDERS ===== */
        QSlider::groove:horizontal {{
            border: 1px solid {colors['border']};
            height: 8px;
            background: {colors['bg_alt']};
            border-radius: 4px;
        }}
        
        QSlider::handle:horizontal {{
            background: {colors['pink']};
            border: 2px solid {colors['border']};
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {colors['yellow']};
        }}
        
        /* ===== SPLITTERS ===== */
        QSplitter::handle {{
            background-color: {colors['border']};
        }}
        
        QSplitter::handle:horizontal {{
            width: 3px;
        }}
        
        QSplitter::handle:vertical {{
            height: 3px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {colors['pink']};
        }}
        
        /* ===== MENUS ===== */
        QMenuBar {{
            background-color: {colors['bg_dark']};
            color: {colors['fg']};
            border-bottom: 1px solid {colors['border']};
            font-size: 10pt;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
        }}
        
        QMenuBar::item:hover {{
            background-color: {colors['hover']};
        }}
        
        QMenuBar::item:pressed {{
            background-color: {colors['pink']};
        }}
        
        QMenu {{
            background-color: {colors['bg_alt']};
            color: {colors['fg']};
            border: 2px solid {colors['border']};
            padding: 5px;
        }}
        
        QMenu::item {{
            padding: 8px 20px;
            border-radius: 3px;
        }}
        
        QMenu::item:hover {{
            background-color: {colors['pink']};
        }}
        
        /* ===== TOOLTIPS ===== */
        QToolTip {{
            background-color: {colors['yellow']};
            color: {colors['bg']};
            border: 2px solid {colors['border']};
            border-radius: 4px;
            padding: 8px;
            font-size: 10pt;
            font-weight: bold;
        }}
        
        /* ===== STATUS BAR ===== */
        QStatusBar {{
            background-color: {colors['bg_dark']};
            color: {colors['fg']};
            border-top: 1px solid {colors['border']};
            font-size: 9pt;
        }}
        
        QStatusBar::item {{
            border: none;
        }}
        
        /* ===== CUSTOM CLASSES ===== */
        
        /* Dashboard specific */
        QWidget#MonokaiDashboard {{
            background-color: {colors['bg']};
            color: {colors['fg']};
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        
        /* Log widget */
        QTextEdit#LogWidget {{
            background-color: {colors['bg_dark']};
            border: 2px solid {colors['border']};
            border-radius: 4px;
            color: {colors['fg']};
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 9pt;
        }}
        
        /* Control panels */
        QWidget#ControlPanel {{
            background-color: {colors['bg_alt']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 8px;
        }}
        
        /* Modern components compatibility */
        QPushButton#ModernButton {{
            font-weight: bold;
            border-radius: 6px;
            padding: 10px 20px;
        }}
        
        QPushButton#ModernButton:hover {{
            padding: 8px 16px;
            border: 2px solid #66d9ef;
        }}
        """

def apply_monokai_theme(app: QApplication):
    """Áp dụng theme Monokai cho toàn bộ ứng dụng"""
    # Set palette
    app.setPalette(MonokaiTheme.get_palette())
    
    # Set stylesheet
    app.setStyleSheet(MonokaiTheme.get_complete_stylesheet())
    
    # Set fonts
    fonts = MonokaiTheme.get_fonts()
    app.setFont(fonts['ui'])
    
    print("✅ Monokai theme applied successfully!")

if __name__ == "__main__":
    print("🎨 Monokai Theme Manager")
    print("📋 Available functions:")
    print("   • MonokaiTheme.get_palette() - Get QPalette")
    print("   • MonokaiTheme.get_complete_stylesheet() - Get full CSS")
    print("   • apply_monokai_theme(app) - Apply to QApplication")
    print("")
    print("🎯 Usage:")
    print("   from monokai_theme import apply_monokai_theme")
    print("   apply_monokai_theme(app)")
