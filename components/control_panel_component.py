"""
Control Panel Component Module
==============================

Extracted control panel logic from main_window.py để modularize UI controls.
"""

import time
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QGroupBox, QGridLayout)
from PyQt6.QtCore import pyqtSignal, QObject, Qt

# Optimization imports
try:
    from services import get_service_manager
    from core import get_event_manager, EventTypes, emit_event
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False

class ControlPanelComponent(QObject):
    """
    Modular Control Panel Component for instance management buttons.
    
    Features:
    - ServiceManager integration
    - EventManager communication
    - Modular button groups
    - State management
    """
    
    # Signals for button actions
    create_requested = pyqtSignal()
    clone_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    restart_requested = pyqtSignal()
    
    # Automation signals
    auto_start_requested = pyqtSignal()
    auto_pause_requested = pyqtSignal()
    auto_stop_requested = pyqtSignal()
    
    # Advanced operation signals
    multi_start_requested = pyqtSignal()
    multi_stop_requested = pyqtSignal()
    multi_restart_requested = pyqtSignal()
    
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.widget = None
        
        # Optimization components
        if OPTIMIZATION_AVAILABLE:
            self.service_manager = get_service_manager()
            self.event_manager = get_event_manager()
            
            # Subscribe to events
            self.event_manager.subscribe(EventTypes.UI_STATE_CHANGED, self._handle_state_change)
        
        # Button references
        self.buttons = {}
        self.button_groups = {}
        
    def create_control_panel(self) -> QWidget:
        """Create control panel widget with organized button groups"""
        
        control_panel = QWidget()
        layout = QVBoxLayout(control_panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create button groups
        instance_group = self._create_instance_management_group()
        operation_group = self._create_operation_group()
        automation_group = self._create_automation_group()
        advanced_group = self._create_advanced_operations_group()
        
        # Add groups to layout
        layout.addWidget(instance_group)
        layout.addWidget(operation_group)
        layout.addWidget(automation_group)
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        # Connect signals
        self._connect_button_signals()
        
        self.widget = control_panel
        return control_panel
    
    def _create_instance_management_group(self) -> QGroupBox:
        """Create instance management button group"""
        group = QGroupBox("Instance Management")
        layout = QGridLayout(group)
        
        # Create buttons
        self.buttons['create'] = QPushButton("➕ Tạo mới")
        self.buttons['clone'] = QPushButton("📋 Sao chép")
        self.buttons['delete'] = QPushButton("🗑️ Xóa")
        
        # Add to layout
        layout.addWidget(self.buttons['create'], 0, 0)
        layout.addWidget(self.buttons['clone'], 0, 1)
        layout.addWidget(self.buttons['delete'], 0, 2)
        
        # Style buttons
        self._apply_button_styles(self.buttons['create'], 'primary')
        self._apply_button_styles(self.buttons['clone'], 'secondary')
        self._apply_button_styles(self.buttons['delete'], 'danger')
        
        self.button_groups['instance'] = group
        return group
    
    def _create_operation_group(self) -> QGroupBox:
        """Create basic operation button group"""
        group = QGroupBox("Basic Operations")
        layout = QGridLayout(group)
        
        # Create buttons
        self.buttons['start'] = QPushButton("▶️ Khởi động")
        self.buttons['stop'] = QPushButton("⏹️ Dừng")
        self.buttons['restart'] = QPushButton("🔄 Khởi động lại")
        
        # Add to layout
        layout.addWidget(self.buttons['start'], 0, 0)
        layout.addWidget(self.buttons['stop'], 0, 1)
        layout.addWidget(self.buttons['restart'], 0, 2)
        
        # Style buttons
        self._apply_button_styles(self.buttons['start'], 'success')
        self._apply_button_styles(self.buttons['stop'], 'warning')
        self._apply_button_styles(self.buttons['restart'], 'info')
        
        self.button_groups['operation'] = group
        return group
    
    def _create_automation_group(self) -> QGroupBox:
        """Create automation control button group"""
        group = QGroupBox("Automation Control")
        layout = QGridLayout(group)
        
        # Create buttons
        self.buttons['auto_start'] = QPushButton("🚀 Tự động bắt đầu")
        self.buttons['auto_pause'] = QPushButton("⏸️ Tạm dừng")
        self.buttons['auto_stop'] = QPushButton("⏹️ Dừng tự động")
        
        # Add to layout
        layout.addWidget(self.buttons['auto_start'], 0, 0)
        layout.addWidget(self.buttons['auto_pause'], 0, 1)
        layout.addWidget(self.buttons['auto_stop'], 0, 2)
        
        # Style buttons
        self._apply_button_styles(self.buttons['auto_start'], 'success')
        self._apply_button_styles(self.buttons['auto_pause'], 'warning')
        self._apply_button_styles(self.buttons['auto_stop'], 'danger')
        
        self.button_groups['automation'] = group
        return group
    
    def _create_advanced_operations_group(self) -> QGroupBox:
        """Create advanced operations button group"""
        group = QGroupBox("Advanced Operations")
        layout = QGridLayout(group)
        
        # Create buttons
        self.buttons['multi_start'] = QPushButton("⚡ Khởi động nhiều")
        self.buttons['multi_stop'] = QPushButton("🛑 Dừng nhiều")
        self.buttons['multi_restart'] = QPushButton("🔄 Restart nhiều")
        
        # Add to layout
        layout.addWidget(self.buttons['multi_start'], 0, 0)
        layout.addWidget(self.buttons['multi_stop'], 0, 1)
        layout.addWidget(self.buttons['multi_restart'], 0, 2)
        
        # Style buttons
        self._apply_button_styles(self.buttons['multi_start'], 'success')
        self._apply_button_styles(self.buttons['multi_stop'], 'danger')
        self._apply_button_styles(self.buttons['multi_restart'], 'info')
        
        self.button_groups['advanced'] = group
        return group
    
    def _apply_button_styles(self, button: QPushButton, variant: str):
        """Apply themed styles to buttons"""
        base_style = """
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                border: 2px solid transparent;
                min-width: 120px;
            }
            QPushButton:hover {
                margin-top: -2px;
                padding: 8px 18px;
                border: 2px solid #66d9ef;
            }
            QPushButton:pressed {
                margin-top: 0px;
                padding: 8px 16px;
                border: 2px solid #f92672;
            }
        """
        
        variant_styles = {
            'primary': """
                QPushButton {
                    background-color: #007ACC;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #005A9E;
                }
            """,
            'secondary': """
                QPushButton {
                    background-color: #6C757D;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #545B62;
                }
            """,
            'success': """
                QPushButton {
                    background-color: #28A745;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #1E7E34;
                }
            """,
            'danger': """
                QPushButton {
                    background-color: #DC3545;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #C82333;
                }
            """,
            'warning': """
                QPushButton {
                    background-color: #FFC107;
                    color: #212529;
                }
                QPushButton:hover {
                    background-color: #E0A800;
                }
            """,
            'info': """
                QPushButton {
                    background-color: #17A2B8;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """
        }
        
        style = base_style + variant_styles.get(variant, '')
        button.setStyleSheet(style)
    
    def _connect_button_signals(self):
        """Connect button clicks to signals"""
        # Instance management
        if 'create' in self.buttons:
            self.buttons['create'].clicked.connect(self.create_requested.emit)
        if 'clone' in self.buttons:
            self.buttons['clone'].clicked.connect(self.clone_requested.emit)
        if 'delete' in self.buttons:
            self.buttons['delete'].clicked.connect(self.delete_requested.emit)
        
        # Basic operations
        if 'start' in self.buttons:
            self.buttons['start'].clicked.connect(self.start_requested.emit)
        if 'stop' in self.buttons:
            self.buttons['stop'].clicked.connect(self.stop_requested.emit)
        if 'restart' in self.buttons:
            self.buttons['restart'].clicked.connect(self.restart_requested.emit)
        
        # Automation
        if 'auto_start' in self.buttons:
            self.buttons['auto_start'].clicked.connect(self.auto_start_requested.emit)
        if 'auto_pause' in self.buttons:
            self.buttons['auto_pause'].clicked.connect(self.auto_pause_requested.emit)
        if 'auto_stop' in self.buttons:
            self.buttons['auto_stop'].clicked.connect(self.auto_stop_requested.emit)
        
        # Advanced operations
        if 'multi_start' in self.buttons:
            self.buttons['multi_start'].clicked.connect(self.multi_start_requested.emit)
        if 'multi_stop' in self.buttons:
            self.buttons['multi_stop'].clicked.connect(self.multi_stop_requested.emit)
        if 'multi_restart' in self.buttons:
            self.buttons['multi_restart'].clicked.connect(self.multi_restart_requested.emit)
    
    def _handle_state_change(self, event_data: Dict[str, Any]):
        """Handle UI state changes from EventManager"""
        state = event_data.get('state', {})
        
        # Update button states based on current state
        if 'is_busy' in state:
            self.set_buttons_enabled(not state['is_busy'])
        
        if 'has_selection' in state:
            self.set_operation_buttons_enabled(state['has_selection'])
    
    def set_buttons_enabled(self, enabled: bool):
        """Enable/disable all buttons"""
        for button in self.buttons.values():
            if button:
                button.setEnabled(enabled)
    
    def set_operation_buttons_enabled(self, enabled: bool):
        """Enable/disable operation buttons based on selection"""
        operation_buttons = ['start', 'stop', 'restart', 'delete', 'clone',
                           'multi_start', 'multi_stop', 'multi_restart']
        
        for button_name in operation_buttons:
            if button_name in self.buttons and self.buttons[button_name]:
                self.buttons[button_name].setEnabled(enabled)
    
    def set_button_text(self, button_name: str, text: str):
        """Update button text"""
        if button_name in self.buttons and self.buttons[button_name]:
            self.buttons[button_name].setText(text)
    
    def get_button(self, button_name: str) -> Optional[QPushButton]:
        """Get button by name"""
        return self.buttons.get(button_name)
    
    def get_button_group(self, group_name: str) -> Optional[QGroupBox]:
        """Get button group by name"""
        return self.button_groups.get(group_name)


# Factory function
def create_control_panel_component(parent_window) -> ControlPanelComponent:
    """Factory function để create control panel component"""
    return ControlPanelComponent(parent_window)
