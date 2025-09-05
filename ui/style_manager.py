"""
Style Manager - Generate consistent stylesheets
==============================================
"""
from .design_tokens import DesignTokens

class StyleSheetManager:
    """Generate consistent stylesheets from design tokens"""
    
    @staticmethod
    def button(variant: str = "primary", size: str = "md") -> str:
        """Generate button stylesheet"""
        colors = {
            "primary": (DesignTokens.PRIMARY, DesignTokens.PRIMARY_HOVER, DesignTokens.TEXT_WHITE),
            "secondary": (DesignTokens.SECONDARY, "#475569", DesignTokens.TEXT_WHITE),
            "success": (DesignTokens.SUCCESS, "#059669", DesignTokens.TEXT_WHITE),
            "danger": (DesignTokens.DANGER, "#dc2626", DesignTokens.TEXT_WHITE),
            "outline": (DesignTokens.BG_PRIMARY, DesignTokens.BG_SECONDARY, DesignTokens.TEXT_PRIMARY),
        }
        
        sizes = {
            "sm": (f"{DesignTokens.SPACE_XS}px {DesignTokens.SPACE_SM}px", DesignTokens.FONT_SIZE_SM, "20px"),
            "md": (f"{DesignTokens.SPACE_SM}px {DesignTokens.SPACE_MD}px", DesignTokens.FONT_SIZE_MD, "32px"),
            "lg": (f"{DesignTokens.SPACE_MD}px {DesignTokens.SPACE_LG}px", DesignTokens.FONT_SIZE_LG, "40px"),
        }
        
        bg_color, hover_color, text_color = colors.get(variant, colors["primary"])
        padding, font_size, min_height = sizes.get(size, sizes["md"])
        
        border_style = ""
        if variant == "outline":
            border_style = f"border: {DesignTokens.BORDER_WIDTH}px solid {DesignTokens.SECONDARY};"
        
        return f"""
        QPushButton {{
            background-color: {bg_color};
            {border_style}
            border-radius: {DesignTokens.BORDER_RADIUS}px;
            color: {text_color};
            font-size: {font_size}px;
            font-weight: 500;
            padding: {padding};
            min-height: {min_height};
            outline: none;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {hover_color};
            margin-top: 1px;
            margin-left: 1px;
        }}
        QPushButton:disabled {{
            background-color: {DesignTokens.BG_TERTIARY};
            color: {DesignTokens.TEXT_MUTED};
            border: none;
        }}
        """

    @staticmethod
    def card(elevated: bool = True) -> str:
        """Generate card stylesheet"""
        shadow = DesignTokens.SHADOW_MD if elevated else "none"
        
        return f"""
        QFrame {{
            background-color: {DesignTokens.BG_PRIMARY};
            border: {DesignTokens.BORDER_WIDTH}px solid {DesignTokens.BG_TERTIARY};
            border-radius: {DesignTokens.BORDER_RADIUS}px;
            padding: {DesignTokens.SPACE_MD}px;
        }}
        """

    @staticmethod
    def progress_bar() -> str:
        """Generate progress bar stylesheet"""
        return f"""
        QProgressBar {{
            border: none;
            border-radius: {DesignTokens.BORDER_RADIUS_SM}px;
            background-color: {DesignTokens.BG_TERTIARY};
            height: 8px;
            text-align: center;
            font-size: {DesignTokens.FONT_SIZE_SM}px;
            color: {DesignTokens.TEXT_SECONDARY};
        }}
        QProgressBar::chunk {{
            border-radius: {DesignTokens.BORDER_RADIUS_SM}px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {DesignTokens.PRIMARY}, stop:1 {DesignTokens.PRIMARY_HOVER});
        }}
        """

    @staticmethod
    def sidebar() -> str:
        """Generate sidebar stylesheet"""
        return f"""
        QWidget {{
            background-color: {DesignTokens.BG_PRIMARY};
            border-right: {DesignTokens.BORDER_WIDTH}px solid {DesignTokens.BG_TERTIARY};
        }}
        """

    @staticmethod
    def nav_item() -> str:
        """Generate navigation item stylesheet"""
        return f"""
        QFrame {{
            border-radius: {DesignTokens.BORDER_RADIUS}px;
            padding: {DesignTokens.SPACE_SM}px;
            margin: {DesignTokens.SPACE_XS}px 0px;
        }}
        QFrame:hover {{
            background-color: {DesignTokens.BG_SECONDARY};
        }}
        QLabel {{
            font-size: {DesignTokens.FONT_SIZE_MD}px;
            color: {DesignTokens.TEXT_SECONDARY};
            font-weight: 500;
        }}
        """

    @staticmethod
    def table() -> str:
        """Generate modern table stylesheet"""
        return f"""
        QTableWidget {{
            background-color: {DesignTokens.BG_PRIMARY};
            alternate-background-color: {DesignTokens.BG_SECONDARY};
            gridline-color: {DesignTokens.BG_TERTIARY};
            border: {DesignTokens.BORDER_WIDTH}px solid {DesignTokens.BG_TERTIARY};
            border-radius: {DesignTokens.BORDER_RADIUS}px;
            selection-background-color: {DesignTokens.PRIMARY};
        }}
        QTableWidget::item {{
            padding: {DesignTokens.SPACE_SM}px;
            border: none;
        }}
        QHeaderView::section {{
            background-color: {DesignTokens.BG_SECONDARY};
            padding: {DesignTokens.SPACE_SM}px;
            border: none;
            font-weight: 600;
            color: {DesignTokens.TEXT_PRIMARY};
        }}
        """

    @staticmethod
    def input_field() -> str:
        """Generate input field stylesheet"""
        return f"""
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {DesignTokens.BG_PRIMARY};
            border: {DesignTokens.BORDER_WIDTH}px solid {DesignTokens.BG_TERTIARY};
            border-radius: {DesignTokens.BORDER_RADIUS}px;
            padding: {DesignTokens.SPACE_SM}px;
            font-size: {DesignTokens.FONT_SIZE_MD}px;
            color: {DesignTokens.TEXT_PRIMARY};
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {DesignTokens.PRIMARY};
            outline: none;
        }}
        """
