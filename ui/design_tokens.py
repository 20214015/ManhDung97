"""
Design Tokens - Centralized design system
========================================
"""
from dataclasses import dataclass

@dataclass
class DesignTokens:
    """Centralized design tokens for consistent styling"""
    
    # Colors
    PRIMARY = "#3b82f6"
    PRIMARY_HOVER = "#2563eb"
    SECONDARY = "#64748b"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    
    # Background
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f8fafc"
    BG_TERTIARY = "#f1f5f9"
    BG_DARK = "#1e293b"
    
    # Text
    TEXT_PRIMARY = "#1e293b"
    TEXT_SECONDARY = "#64748b"
    TEXT_MUTED = "#94a3b8"
    TEXT_WHITE = "#ffffff"
    
    # Spacing
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32
    SPACE_2XL = 48
    
    # Borders
    BORDER_RADIUS = 8
    BORDER_RADIUS_SM = 4
    BORDER_RADIUS_LG = 12
    BORDER_WIDTH = 1
    
    # Shadows
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
    
    # Typography
    FONT_SIZE_XS = 10
    FONT_SIZE_SM = 12
    FONT_SIZE_MD = 14
    FONT_SIZE_LG = 16
    FONT_SIZE_XL = 18
    FONT_SIZE_2XL = 20
    
    # Layout
    SIDEBAR_WIDTH_COLLAPSED = 60
    SIDEBAR_WIDTH_COMPACT = 200
    SIDEBAR_WIDTH_FULL = 280
    HEADER_HEIGHT = 64
    FOOTER_HEIGHT = 48
    
    # Animation
    ANIMATION_FAST = 150
    ANIMATION_NORMAL = 300
    ANIMATION_SLOW = 500
    
    # Z-Index
    Z_DROPDOWN = 1000
    Z_MODAL = 2000
    Z_TOOLTIP = 3000
