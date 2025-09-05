"""
Modern UI Components - Ready to use replacements
===============================================
"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional, List
from .design_tokens import DesignTokens
from .style_manager import StyleSheetManager

class ModernButton(QPushButton):
    """Modern button with design system integration"""
    
    def __init__(self, text: str, variant: str = "primary", size: str = "md", icon: Optional[str] = None):
        super().__init__(text)
        self.variant = variant
        self.size = size
        self.icon_name = icon
        
        # Set variant as property for CSS selector
        self.setProperty("variant", variant)
        
        self.setup_style()
        self.setup_animations()
        self.setup_cursor()
        
        if icon:
            self.setup_icon(icon)
    
    def setup_style(self):
        """Apply design system styles"""
        # Update property for CSS selector
        self.setProperty("variant", self.variant)
        self.setStyleSheet(StyleSheetManager.button(self.variant, self.size))
    
    def setup_animations(self):
        """Setup hover animations"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(DesignTokens.ANIMATION_FAST)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def setup_cursor(self):
        """Setup cursor"""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def setup_icon(self, icon_name: str):
        """Add icon to button"""
        # Placeholder for icon system
        pass

class ModernCard(QFrame):
    """Modern card component with shadow and animations"""
    
    def __init__(self, title: str = "", subtitle: str = "", elevated: bool = True):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.elevated = elevated
        
        self.setup_ui()
        self.setup_style()
        if elevated:
            self.setup_shadow()
    
    def setup_ui(self):
        """Setup card UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(DesignTokens.SPACE_SM)
        self.layout.setContentsMargins(
            DesignTokens.SPACE_MD, DesignTokens.SPACE_MD,
            DesignTokens.SPACE_MD, DesignTokens.SPACE_MD
        )
        
        if self.title:
            self.title_label = QLabel(self.title)
            self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {DesignTokens.FONT_SIZE_LG}px;
                font-weight: 600;
                color: {DesignTokens.TEXT_PRIMARY};
                margin-bottom: {DesignTokens.SPACE_XS}px;
            }}
            """)
            self.layout.addWidget(self.title_label)
        
        if self.subtitle:
            self.subtitle_label = QLabel(self.subtitle)
            self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                font-size: {DesignTokens.FONT_SIZE_SM}px;
                color: {DesignTokens.TEXT_SECONDARY};
            }}
            """)
            self.layout.addWidget(self.subtitle_label)
    
    def setup_style(self):
        """Apply card styling"""
        self.setStyleSheet(StyleSheetManager.card(self.elevated))
    
    def setup_shadow(self):
        """Add drop shadow effect"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def add_content(self, widget: QWidget):
        """Add content to card"""
        self.layout.addWidget(widget)

class ModernProgressBar(QProgressBar):
    """Modern progress bar with animations"""
    
    def __init__(self):
        super().__init__()
        self.setup_style()
        self.setup_animation()
    
    def setup_style(self):
        """Apply modern styling"""
        self.setStyleSheet(StyleSheetManager.progress_bar())
        self.setTextVisible(True)
    
    def setup_animation(self):
        """Setup smooth value animations"""
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(DesignTokens.ANIMATION_NORMAL)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def setValueAnimated(self, value: int):
        """Set value with smooth animation"""
        self.animation.setStartValue(self.value())
        self.animation.setEndValue(value)
        self.animation.start()

class LoadingIndicator(QWidget):
    """Modern loading indicator"""
    
    def __init__(self, message: str = "Loading...", size: int = 32):
        super().__init__()
        self.message = message
        self.size = size
        self.angle = 0
        
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        """Setup loading UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(DesignTokens.SPACE_MD)
        
        # Spinner placeholder (using label for now)
        self.spinner = QLabel("⟳")
        self.spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner.setStyleSheet(f"""
        QLabel {{
            font-size: {self.size}px;
            color: {DesignTokens.PRIMARY};
        }}
        """)
        layout.addWidget(self.spinner)
        
        # Message
        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet(f"""
        QLabel {{
            font-size: {DesignTokens.FONT_SIZE_MD}px;
            color: {DesignTokens.TEXT_SECONDARY};
        }}
        """)
        layout.addWidget(self.message_label)
    
    def setup_animation(self):
        """Setup rotation animation"""
        self.rotation_animation = QPropertyAnimation(self, b"rotation")
        self.rotation_animation.setDuration(1000)
        self.rotation_animation.setStartValue(0)
        self.rotation_animation.setEndValue(360)
        self.rotation_animation.setLoopCount(-1)  # Infinite loop
    
    def start_animation(self):
        """Start loading animation"""
        self.rotation_animation.start()
    
    def stop_animation(self):
        """Stop loading animation"""
        self.rotation_animation.stop()

class ModernSidebar(QWidget):
    """Modern responsive sidebar component"""
    
    tab_requested = pyqtSignal(int)
    width_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_collapsed = False
        self.current_width = DesignTokens.SIDEBAR_WIDTH_FULL
        self.current_tab = 0
        
        self.setup_ui()
        self.setup_style()
        self.setup_animations()
    
    def setup_ui(self):
        """Setup sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(DesignTokens.SPACE_XS)
        layout.setContentsMargins(
            DesignTokens.SPACE_SM, DesignTokens.SPACE_MD,
            DesignTokens.SPACE_SM, DesignTokens.SPACE_MD
        )
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        layout.addSpacing(DesignTokens.SPACE_LG)
        
        # Navigation items
        self.nav_items = self.create_navigation()
        for item in self.nav_items:
            layout.addWidget(item)
        
        layout.addStretch()
        
        # Footer
        footer = self.create_footer()
        layout.addWidget(footer)
    
    def create_header(self) -> QWidget:
        """Create sidebar header with logo and toggle"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(DesignTokens.SPACE_SM, 0, DesignTokens.SPACE_SM, 0)
        
        # Logo
        self.logo_label = QLabel("🎯 MuMu Manager")
        self.logo_label.setStyleSheet(f"""
        QLabel {{
            font-size: {DesignTokens.FONT_SIZE_LG}px;
            font-weight: 700;
            color: {DesignTokens.TEXT_PRIMARY};
        }}
        """)
        layout.addWidget(self.logo_label)
        
        layout.addStretch()
        
        # Toggle button
        self.toggle_btn = ModernButton("☰", variant="outline", size="sm")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        layout.addWidget(self.toggle_btn)
        
        return header
    
    def create_navigation(self) -> List[QWidget]:
        """Create navigation items"""
        nav_items = []
        
        items = [
            ("📊 Dashboard", 0),
            ("💻 Instances", 1), 
            ("🤖 Automation", 2),
            ("⚙️ Settings", 3),
        ]
        
        for text, index in items:
            item = self.create_nav_item(text, index)
            nav_items.append(item)
        
        return nav_items
    
    def create_nav_item(self, text: str, index: int) -> QWidget:
        """Create a single navigation item"""
        item = QFrame()
        item.setObjectName(f"nav_item_{index}")
        item.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(
            DesignTokens.SPACE_SM, DesignTokens.SPACE_SM,
            DesignTokens.SPACE_SM, DesignTokens.SPACE_SM
        )
        
        # Text with icon
        text_label = QLabel(text)
        text_label.setStyleSheet(f"""
        QLabel {{
            font-size: {DesignTokens.FONT_SIZE_MD}px;
            color: {DesignTokens.TEXT_SECONDARY};
            font-weight: 500;
        }}
        """)
        layout.addWidget(text_label)
        
        layout.addStretch()
        
        # Style
        item.setStyleSheet(StyleSheetManager.nav_item())
        
        # Click handler
        def on_click():
            self.set_active_tab(index)
            self.tab_requested.emit(index)
        
        item.mousePressEvent = lambda e: on_click()
        
        return item
    
    def create_footer(self) -> QWidget:
        """Create sidebar footer"""
        footer = QWidget()
        layout = QVBoxLayout(footer)
        layout.setSpacing(DesignTokens.SPACE_XS)
        layout.setContentsMargins(DesignTokens.SPACE_SM, 0, DesignTokens.SPACE_SM, 0)
        
        # Status indicator
        status = QLabel("🟢 Connected")
        status.setStyleSheet(f"""
        QLabel {{
            color: {DesignTokens.SUCCESS};
            font-size: {DesignTokens.FONT_SIZE_SM}px;
            font-weight: 500;
        }}
        """)
        layout.addWidget(status)
        
        return footer
    
    def setup_style(self):
        """Apply sidebar styling"""
        self.setStyleSheet(StyleSheetManager.sidebar())
        self.setFixedWidth(self.current_width)
    
    def setup_animations(self):
        """Setup width animations"""
        self.width_animation = QPropertyAnimation(self, b"fixedWidth")
        self.width_animation.setDuration(DesignTokens.ANIMATION_NORMAL)
        self.width_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def toggle_sidebar(self):
        """Toggle sidebar collapse state"""
        if self.is_collapsed:
            self.expand_sidebar()
        else:
            self.collapse_sidebar()
    
    def collapse_sidebar(self):
        """Collapse sidebar to icon-only mode"""
        self.is_collapsed = True
        target_width = DesignTokens.SIDEBAR_WIDTH_COLLAPSED
        self.animate_width(target_width)
        self.logo_label.hide()
    
    def expand_sidebar(self):
        """Expand sidebar to full mode"""
        self.is_collapsed = False
        target_width = DesignTokens.SIDEBAR_WIDTH_FULL
        self.animate_width(target_width)
        self.logo_label.show()
    
    def animate_width(self, target_width: int):
        """Animate sidebar width change"""
        self.width_animation.setStartValue(self.width())
        self.width_animation.setEndValue(target_width)
        self.width_animation.finished.connect(
            lambda: self.width_changed.emit(target_width)
        )
        self.width_animation.start()
    
    def set_active_tab(self, index: int):
        """Set active tab with visual feedback"""
        self.current_tab = index
        
        # Update visual state of nav items
        for i, item in enumerate(self.nav_items):
            if i == index:
                item.setStyleSheet(f"""
                QFrame {{
                    background-color: {DesignTokens.PRIMARY};
                    border-radius: {DesignTokens.BORDER_RADIUS}px;
                    padding: {DesignTokens.SPACE_SM}px;
                    margin: {DesignTokens.SPACE_XS}px 0px;
                }}
                QLabel {{
                    color: {DesignTokens.TEXT_WHITE};
                    font-weight: 600;
                }}
                """)
            else:
                item.setStyleSheet(StyleSheetManager.nav_item())

class ModernTable(QTableWidget):
    """Modern table with enhanced styling"""
    
    def __init__(self, rows: int = 0, columns: int = 0):
        super().__init__(rows, columns)
        self.setup_style()
        self.setup_behavior()
    
    def setup_style(self):
        """Apply modern table styling"""
        self.setStyleSheet(StyleSheetManager.table())
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
    
    def setup_behavior(self):
        """Setup modern table behavior"""
        self.setSortingEnabled(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
