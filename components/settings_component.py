"""
Settings Management Component
============================

Advanced settings and user preferences management for production deployment.
"""

import json
import os
from typing import Optional, Dict, Any, List, Union, Callable
from dataclasses import dataclass, field, asdict
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
                            QComboBox, QGroupBox, QTabWidget, QPushButton,
                            QSlider, QColorDialog, QFontDialog, QFileDialog,
                            QTextEdit, QScrollArea, QGridLayout)
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QSettings
from PyQt6.QtGui import QFont, QColor

# Optimization imports
try:
    from services import get_service_manager
    from core import get_event_manager, EventTypes, emit_event
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False

@dataclass
class SettingDefinition:
    """Definition of a setting with metadata"""
    key: str
    name: str
    description: str
    setting_type: str  # 'bool', 'int', 'float', 'str', 'color', 'font', 'file', 'choice'
    default_value: Any
    category: str = "General"
    choices: Optional[List[str]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    validation: Optional[Callable] = None
    requires_restart: bool = False
    tooltip: str = ""

@dataclass
class SettingsCategory:
    """Settings category with organization"""
    name: str
    icon: str
    description: str
    settings: List[SettingDefinition] = field(default_factory=list)

class SettingsManager:
    """Advanced settings management with validation and persistence"""
    
    def __init__(self, app_name: str = "MuMuManagerPro"):
        self.app_name = app_name
        self.qsettings = QSettings(app_name, app_name)
        self.settings_file = os.path.join(os.path.expanduser("~"), f".{app_name.lower()}", "settings.json")
        self.categories: Dict[str, SettingsCategory] = {}
        self.settings_definitions: Dict[str, SettingDefinition] = {}
        self.change_callbacks: Dict[str, List[Callable]] = {}
        
        # Ensure settings directory exists
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        
        # Register default settings
        self._register_default_settings()
        
        # Load existing settings
        self.load_settings()
    
    def _register_default_settings(self):
        """Register default application settings"""
        
        # UI Settings Category
        ui_category = SettingsCategory(
            name="User Interface",
            icon="🎨",
            description="Appearance and user interface preferences"
        )
        
        ui_settings = [
            SettingDefinition(
                key="ui.theme",
                name="Theme",
                description="Application color theme",
                setting_type="choice",
                default_value="Dark",
                choices=["Light", "Dark", "Monokai", "Auto"],
                category="User Interface",
                tooltip="Choose the application color scheme"
            ),
            SettingDefinition(
                key="ui.font_size",
                name="Font Size",
                description="Base font size for the interface",
                setting_type="int",
                default_value=10,
                min_value=8,
                max_value=20,
                category="User Interface",
                tooltip="Adjust the size of text throughout the application"
            ),
            SettingDefinition(
                key="ui.font_family",
                name="Font Family",
                description="Font family for the interface",
                setting_type="font",
                default_value="Arial",
                category="User Interface",
                tooltip="Choose the font used throughout the application"
            ),
            SettingDefinition(
                key="ui.enable_animations",
                name="Enable Animations",
                description="Enable UI animations and transitions",
                setting_type="bool",
                default_value=True,
                category="User Interface",
                tooltip="Toggle smooth animations and transitions"
            ),
            SettingDefinition(
                key="ui.auto_refresh_interval",
                name="Auto Refresh Interval",
                description="Automatic refresh interval in seconds",
                setting_type="int",
                default_value=30,
                min_value=5,
                max_value=300,
                category="User Interface",
                tooltip="How often to automatically refresh instance data"
            )
        ]
        
        ui_category.settings = ui_settings
        self.register_category(ui_category)
        
        # Performance Settings Category
        perf_category = SettingsCategory(
            name="Performance",
            icon="🚀",
            description="Performance and optimization settings"
        )
        
        perf_settings = [
            SettingDefinition(
                key="performance.enable_caching",
                name="Enable Caching",
                description="Enable intelligent caching system",
                setting_type="bool",
                default_value=True,
                category="Performance",
                tooltip="Cache frequently accessed data for better performance"
            ),
            SettingDefinition(
                key="performance.max_worker_threads",
                name="Max Worker Threads",
                description="Maximum number of background worker threads",
                setting_type="int",
                default_value=4,
                min_value=1,
                max_value=16,
                category="Performance",
                requires_restart=True,
                tooltip="Number of threads for background operations"
            ),
            SettingDefinition(
                key="performance.memory_limit_mb",
                name="Memory Limit (MB)",
                description="Maximum memory usage limit in megabytes",
                setting_type="int",
                default_value=1024,
                min_value=256,
                max_value=4096,
                category="Performance",
                tooltip="Memory usage threshold for optimization"
            ),
            SettingDefinition(
                key="performance.enable_gpu_acceleration",
                name="GPU Acceleration",
                description="Enable GPU acceleration where available",
                setting_type="bool",
                default_value=False,
                category="Performance",
                requires_restart=True,
                tooltip="Use GPU for rendering and computations"
            )
        ]
        
        perf_category.settings = perf_settings
        self.register_category(perf_category)
        
        # Monitoring Settings Category
        monitor_category = SettingsCategory(
            name="Monitoring",
            icon="📊",
            description="Performance monitoring and logging settings"
        )
        
        monitor_settings = [
            SettingDefinition(
                key="monitoring.enable_performance_monitoring",
                name="Performance Monitoring",
                description="Enable real-time performance monitoring",
                setting_type="bool",
                default_value=True,
                category="Monitoring",
                tooltip="Monitor system and application performance"
            ),
            SettingDefinition(
                key="monitoring.log_level",
                name="Log Level",
                description="Logging detail level",
                setting_type="choice",
                default_value="INFO",
                choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                category="Monitoring",
                tooltip="Amount of detail in log messages"
            ),
            SettingDefinition(
                key="monitoring.max_log_files",
                name="Max Log Files",
                description="Maximum number of log files to keep",
                setting_type="int",
                default_value=10,
                min_value=1,
                max_value=100,
                category="Monitoring",
                tooltip="Number of historical log files to maintain"
            ),
            SettingDefinition(
                key="monitoring.performance_alert_threshold",
                name="Performance Alert Threshold",
                description="CPU usage threshold for performance alerts (%)",
                setting_type="float",
                default_value=80.0,
                min_value=50.0,
                max_value=95.0,
                category="Monitoring",
                tooltip="CPU usage percentage that triggers alerts"
            )
        ]
        
        monitor_category.settings = monitor_settings
        self.register_category(monitor_category)
    
    def register_category(self, category: SettingsCategory):
        """Register a settings category"""
        self.categories[category.name] = category
        
        for setting in category.settings:
            self.settings_definitions[setting.key] = setting
    
    def register_setting(self, setting: SettingDefinition):
        """Register a single setting"""
        self.settings_definitions[setting.key] = setting
        
        # Add to category if it exists
        if setting.category in self.categories:
            self.categories[setting.category].settings.append(setting)
    
    def get_value(self, key: str, default=None):
        """Get setting value with type conversion"""
        if key not in self.settings_definitions:
            return default
        
        setting_def = self.settings_definitions[key]
        stored_value = self.qsettings.value(key, setting_def.default_value)
        
        # Type conversion
        if setting_def.setting_type == "bool":
            return str(stored_value).lower() in ('true', '1', 'yes', 'on')
        elif setting_def.setting_type == "int":
            return int(stored_value)
        elif setting_def.setting_type == "float":
            return float(stored_value)
        else:
            return stored_value
    
    def set_value(self, key: str, value: Any, emit_change=True):
        """Set setting value with validation"""
        if key not in self.settings_definitions:
            raise KeyError(f"Unknown setting: {key}")
        
        setting_def = self.settings_definitions[key]
        
        # Validate value
        if not self._validate_value(setting_def, value):
            raise ValueError(f"Invalid value for {key}: {value}")
        
        # Store value
        self.qsettings.setValue(key, value)
        
        # Emit change signal if requested
        if emit_change and key in self.change_callbacks:
            for callback in self.change_callbacks[key]:
                try:
                    callback(key, value)
                except Exception as e:
                    print(f"⚠️ Settings callback error: {e}")
    
    def _validate_value(self, setting_def: SettingDefinition, value: Any) -> bool:
        """Validate setting value against definition"""
        try:
            # Type validation
            if setting_def.setting_type == "bool":
                bool(value)
            elif setting_def.setting_type == "int":
                int_val = int(value)
                if setting_def.min_value is not None and int_val < setting_def.min_value:
                    return False
                if setting_def.max_value is not None and int_val > setting_def.max_value:
                    return False
            elif setting_def.setting_type == "float":
                float_val = float(value)
                if setting_def.min_value is not None and float_val < setting_def.min_value:
                    return False
                if setting_def.max_value is not None and float_val > setting_def.max_value:
                    return False
            elif setting_def.setting_type == "choice":
                if setting_def.choices and value not in setting_def.choices:
                    return False
            
            # Custom validation
            if setting_def.validation:
                return setting_def.validation(value)
            
            return True
        except:
            return False
    
    def register_change_callback(self, key: str, callback: Callable):
        """Register callback for setting changes"""
        if key not in self.change_callbacks:
            self.change_callbacks[key] = []
        self.change_callbacks[key].append(callback)
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for key, value in data.items():
                    if key in self.settings_definitions:
                        self.qsettings.setValue(key, value)
        except Exception as e:
            print(f"⚠️ Failed to load settings: {e}")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            data = {}
            for key in self.settings_definitions:
                data[key] = self.get_value(key)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Failed to save settings: {e}")
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        for key, setting_def in self.settings_definitions.items():
            self.set_value(key, setting_def.default_value, emit_change=False)
        self.save_settings()
    
    def export_settings(self, file_path: str):
        """Export settings to file"""
        data = {
            'app_name': self.app_name,
            'export_timestamp': str(datetime.now()),
            'settings': {key: self.get_value(key) for key in self.settings_definitions}
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def import_settings(self, file_path: str):
        """Import settings from file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        settings_data = data.get('settings', {})
        for key, value in settings_data.items():
            if key in self.settings_definitions:
                try:
                    self.set_value(key, value, emit_change=False)
                except Exception as e:
                    print(f"⚠️ Failed to import setting {key}: {e}")
        
        self.save_settings()

class SettingsComponent(QObject):
    """
    Advanced Settings Management Component for user preferences.
    
    Features:
    - Organized settings categories
    - Real-time validation
    - Import/Export functionality
    - Change notifications
    - Professional UI
    """
    
    # Signals
    settings_changed = pyqtSignal(str, object)  # key, value
    settings_saved = pyqtSignal()
    settings_reset = pyqtSignal()
    
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.widget = None
        self.settings_manager = SettingsManager()
        
        # UI components
        self.category_tabs = {}
        self.setting_widgets = {}
        
        # Optimization components
        if OPTIMIZATION_AVAILABLE:
            self.service_manager = get_service_manager()
            self.event_manager = get_event_manager()
        
        # Connect settings manager callbacks
        self._register_callbacks()
    
    def create_settings_panel(self) -> QWidget:
        """Create settings management panel"""
        
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Settings tabs
        tabs = QTabWidget()
        
        for category_name, category in self.settings_manager.categories.items():
            tab = self._create_category_tab(category)
            tabs.addTab(tab, f"{category.icon} {category.name}")
            self.category_tabs[category_name] = tab
        
        layout.addWidget(tabs)
        
        # Footer with action buttons
        footer = self._create_footer()
        layout.addWidget(footer)
        
        self.widget = settings_widget
        return settings_widget
    
    def _create_header(self) -> QWidget:
        """Create settings header"""
        header = QGroupBox("Settings & Preferences")
        layout = QHBoxLayout(header)
        
        info_label = QLabel("Configure application behavior and appearance")
        info_label.setStyleSheet("color: #A6E22E; font-weight: bold;")
        
        layout.addWidget(info_label)
        layout.addStretch()
        
        return header
    
    def _create_category_tab(self, category: SettingsCategory) -> QWidget:
        """Create tab for settings category"""
        tab = QWidget()
        scroll_area = QScrollArea(tab)
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Category description
        desc_label = QLabel(category.description)
        desc_label.setStyleSheet("font-style: italic; color: #666666; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Settings grid
        grid_layout = QGridLayout()
        row = 0
        
        for setting in category.settings:
            self._add_setting_to_grid(grid_layout, setting, row)
            row += 1
        
        layout.addLayout(grid_layout)
        layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll_area)
        
        return tab
    
    def _add_setting_to_grid(self, grid_layout: QGridLayout, setting: SettingDefinition, row: int):
        """Add setting widget to grid layout"""
        # Label
        label = QLabel(setting.name)
        if setting.requires_restart:
            label.setText(f"{setting.name} *")
            label.setStyleSheet("color: #FFA500;")  # Orange for restart required
        
        if setting.tooltip:
            label.setToolTip(setting.tooltip)
        
        grid_layout.addWidget(label, row, 0)
        
        # Setting widget
        widget = self._create_setting_widget(setting)
        grid_layout.addWidget(widget, row, 1)
        
        # Description
        if setting.description:
            desc_label = QLabel(setting.description)
            desc_label.setStyleSheet("font-size: 8pt; color: #999999;")
            grid_layout.addWidget(desc_label, row, 2)
        
        self.setting_widgets[setting.key] = widget
    
    def _create_setting_widget(self, setting: SettingDefinition) -> QWidget:
        """Create appropriate widget for setting type"""
        current_value = self.settings_manager.get_value(setting.key)
        
        if setting.setting_type == "bool":
            widget = QCheckBox()
            widget.setChecked(current_value)
            widget.toggled.connect(lambda checked: self._on_setting_changed(setting.key, checked))
            
        elif setting.setting_type == "int":
            widget = QSpinBox()
            if setting.min_value is not None:
                widget.setMinimum(int(setting.min_value))
            if setting.max_value is not None:
                widget.setMaximum(int(setting.max_value))
            widget.setValue(current_value)
            widget.valueChanged.connect(lambda value: self._on_setting_changed(setting.key, value))
            
        elif setting.setting_type == "float":
            widget = QDoubleSpinBox()
            if setting.min_value is not None:
                widget.setMinimum(setting.min_value)
            if setting.max_value is not None:
                widget.setMaximum(setting.max_value)
            widget.setValue(current_value)
            widget.valueChanged.connect(lambda value: self._on_setting_changed(setting.key, value))
            
        elif setting.setting_type == "str":
            widget = QLineEdit()
            widget.setText(str(current_value))
            widget.textChanged.connect(lambda text: self._on_setting_changed(setting.key, text))
            
        elif setting.setting_type == "choice":
            widget = QComboBox()
            if setting.choices:
                widget.addItems(setting.choices)
                if current_value in setting.choices:
                    widget.setCurrentText(current_value)
            widget.currentTextChanged.connect(lambda text: self._on_setting_changed(setting.key, text))
            
        elif setting.setting_type == "color":
            widget = QPushButton()
            widget.setText("Choose Color")
            widget.setStyleSheet(f"background-color: {current_value};")
            widget.clicked.connect(lambda: self._choose_color(setting.key, widget))
            
        elif setting.setting_type == "font":
            widget = QPushButton()
            widget.setText(f"Font: {current_value}")
            widget.clicked.connect(lambda: self._choose_font(setting.key, widget))
            
        elif setting.setting_type == "file":
            widget_container = QWidget()
            layout = QHBoxLayout(widget_container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            line_edit = QLineEdit()
            line_edit.setText(str(current_value))
            line_edit.textChanged.connect(lambda text: self._on_setting_changed(setting.key, text))
            
            browse_btn = QPushButton("Browse...")
            browse_btn.clicked.connect(lambda: self._choose_file(setting.key, line_edit))
            
            layout.addWidget(line_edit)
            layout.addWidget(browse_btn)
            widget = widget_container
            
        else:
            # Fallback to text input
            widget = QLineEdit()
            widget.setText(str(current_value))
            widget.textChanged.connect(lambda text: self._on_setting_changed(setting.key, text))
        
        return widget
    
    def _create_footer(self) -> QWidget:
        """Create footer with action buttons"""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        
        # Restart required notice
        restart_label = QLabel("* Settings marked with * require restart")
        restart_label.setStyleSheet("color: #FFA500; font-style: italic;")
        
        layout.addWidget(restart_label)
        layout.addStretch()
        
        # Action buttons
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self._reset_settings)
        
        export_btn = QPushButton("📤 Export Settings")
        export_btn.clicked.connect(self._export_settings)
        
        import_btn = QPushButton("📥 Import Settings")
        import_btn.clicked.connect(self._import_settings)
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self._save_settings)
        save_btn.setStyleSheet("QPushButton { background-color: #28A745; color: white; font-weight: bold; }")
        
        layout.addWidget(reset_btn)
        layout.addWidget(export_btn)
        layout.addWidget(import_btn)
        layout.addWidget(save_btn)
        
        return footer
    
    def _on_setting_changed(self, key: str, value: Any):
        """Handle setting value change"""
        try:
            self.settings_manager.set_value(key, value)
            self.settings_changed.emit(key, value)
        except Exception as e:
            print(f"⚠️ Setting change error: {e}")
    
    def _choose_color(self, key: str, button: QPushButton):
        """Handle color chooser"""
        current_color = QColor(self.settings_manager.get_value(key))
        color = QColorDialog.getColor(current_color, self.parent_window)
        
        if color.isValid():
            color_name = color.name()
            button.setStyleSheet(f"background-color: {color_name};")
            self._on_setting_changed(key, color_name)
    
    def _choose_font(self, key: str, button: QPushButton):
        """Handle font chooser"""
        current_font = QFont(self.settings_manager.get_value(key))
        font, ok = QFontDialog.getFont(current_font, self.parent_window)
        
        if ok:
            font_name = font.family()
            button.setText(f"Font: {font_name}")
            self._on_setting_changed(key, font_name)
    
    def _choose_file(self, key: str, line_edit: QLineEdit):
        """Handle file chooser"""
        current_path = self.settings_manager.get_value(key)
        file_path, _ = QFileDialog.getOpenFileName(self.parent_window, "Choose File", current_path)
        
        if file_path:
            line_edit.setText(file_path)
            self._on_setting_changed(key, file_path)
    
    def _reset_settings(self):
        """Reset all settings to defaults"""
        self.settings_manager.reset_to_defaults()
        self._refresh_ui()
        self.settings_reset.emit()
    
    def _export_settings(self):
        """Export settings to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent_window, 
            "Export Settings", 
            f"mumumanager_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            self.settings_manager.export_settings(file_path)
    
    def _import_settings(self):
        """Import settings from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent_window, 
            "Import Settings", 
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            self.settings_manager.import_settings(file_path)
            self._refresh_ui()
    
    def _save_settings(self):
        """Save current settings"""
        self.settings_manager.save_settings()
        self.settings_saved.emit()
    
    def _refresh_ui(self):
        """Refresh UI with current setting values"""
        for key, widget in self.setting_widgets.items():
            current_value = self.settings_manager.get_value(key)
            setting_def = self.settings_manager.settings_definitions[key]
            
            if setting_def.setting_type == "bool" and isinstance(widget, QCheckBox):
                widget.setChecked(current_value)
            elif setting_def.setting_type == "int" and isinstance(widget, QSpinBox):
                widget.setValue(current_value)
            elif setting_def.setting_type == "float" and isinstance(widget, QDoubleSpinBox):
                widget.setValue(current_value)
            elif setting_def.setting_type == "str" and isinstance(widget, QLineEdit):
                widget.setText(str(current_value))
            elif setting_def.setting_type == "choice" and isinstance(widget, QComboBox):
                widget.setCurrentText(current_value)
    
    def _register_callbacks(self):
        """Register callbacks for setting changes"""
        # Register callbacks for important settings
        self.settings_manager.register_change_callback('ui.theme', self._on_theme_changed)
        self.settings_manager.register_change_callback('ui.font_size', self._on_font_size_changed)
        self.settings_manager.register_change_callback('performance.enable_caching', self._on_caching_changed)
    
    def _on_theme_changed(self, key: str, value: Any):
        """Handle theme change"""
        # Apply theme change immediately
        if hasattr(self.parent_window, 'apply_theme'):
            self.parent_window.apply_theme(value)
    
    def _on_font_size_changed(self, key: str, value: Any):
        """Handle font size change"""
        # Apply font size change immediately
        if hasattr(self.parent_window, 'set_font_size'):
            self.parent_window.set_font_size(value)
    
    def _on_caching_changed(self, key: str, value: Any):
        """Handle caching setting change"""
        # Toggle caching
        if OPTIMIZATION_AVAILABLE and hasattr(self.parent_window, 'smart_cache'):
            if value:
                self.parent_window.smart_cache.enable()
            else:
                self.parent_window.smart_cache.disable()


# Factory function
def create_settings_component(parent_window) -> SettingsComponent:
    """Factory function để create settings component"""
    return SettingsComponent(parent_window)
