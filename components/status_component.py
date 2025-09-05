"""
Status Component Module
=======================

Extracted status display logic from main_window.py để modularize status management.
"""

import time
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QGroupBox, QFrame)
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QTimer
from PyQt6.QtGui import QFont

# Optimization imports
try:
    from services import get_service_manager
    from core import get_event_manager, EventTypes, emit_event
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False

class StatusComponent(QObject):
    """
    Modular Status Component for displaying application status.
    
    Features:
    - Real-time status updates
    - Progress tracking
    - Multi-category status display
    - Event-driven updates
    """
    
    # Signals
    status_updated = pyqtSignal(str, str, str)  # category, status, level
    progress_updated = pyqtSignal(int, str)  # value, description
    
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.widget = None
        
        # Status tracking
        self.status_labels = {}
        self.status_values = {}
        self.progress_bars = {}
        
        # Optimization components
        if OPTIMIZATION_AVAILABLE:
            self.service_manager = get_service_manager()
            self.event_manager = get_event_manager()
            
            # Subscribe to events
            self.event_manager.subscribe(EventTypes.STATUS_UPDATE, self._handle_status_update)
            self.event_manager.subscribe(EventTypes.PROGRESS_UPDATE, self._handle_progress_update)
        
        # Auto-update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_dynamic_status)
        self.update_timer.start(1000)  # Update every second
        
    def create_status_panel(self) -> QWidget:
        """Create status panel with organized status groups"""
        
        status_panel = QWidget()
        layout = QVBoxLayout(status_panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create status groups
        system_status = self._create_system_status_group()
        operation_status = self._create_operation_status_group()
        progress_status = self._create_progress_status_group()
        
        # Add groups to layout
        layout.addWidget(system_status)
        layout.addWidget(operation_status)
        layout.addWidget(progress_status)
        layout.addStretch()
        
        # Initialize status values
        self._initialize_status_values()
        
        self.widget = status_panel
        return status_panel
    
    def _create_system_status_group(self) -> QGroupBox:
        """Create system status display group"""
        group = QGroupBox("System Status")
        layout = QVBoxLayout(group)
        
        # AI Tracker Status
        ai_frame = self._create_status_frame("AI Tracker", "🤖")
        self.status_labels['ai_tracker'] = ai_frame['value']
        layout.addWidget(ai_frame['frame'])
        
        # Memory Status
        memory_frame = self._create_status_frame("Memory", "🧠")
        self.status_labels['memory'] = memory_frame['value']
        layout.addWidget(memory_frame['frame'])
        
        # Cache Status
        cache_frame = self._create_status_frame("Cache", "💾")
        self.status_labels['cache'] = cache_frame['value']
        layout.addWidget(cache_frame['frame'])
        
        return group
    
    def _create_operation_status_group(self) -> QGroupBox:
        """Create operation status display group"""
        group = QGroupBox("Operation Status")
        layout = QVBoxLayout(group)
        
        # Instance Count
        instance_frame = self._create_status_frame("Instances", "📱")
        self.status_labels['instances'] = instance_frame['value']
        layout.addWidget(instance_frame['frame'])
        
        # Running Count
        running_frame = self._create_status_frame("Running", "▶️")
        self.status_labels['running'] = running_frame['value']
        layout.addWidget(running_frame['frame'])
        
        # Selection Count
        selection_frame = self._create_status_frame("Selected", "✅")
        self.status_labels['selected'] = selection_frame['value']
        layout.addWidget(selection_frame['frame'])
        
        return group
    
    def _create_progress_status_group(self) -> QGroupBox:
        """Create progress status display group"""
        group = QGroupBox("Progress Status")
        layout = QVBoxLayout(group)
        
        # Main progress bar
        main_progress_frame = QFrame()
        main_layout = QHBoxLayout(main_progress_frame)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        progress_label = QLabel("🔄 Operation:")
        self.progress_bars['main'] = QProgressBar()
        self.progress_bars['main'].setVisible(False)
        self.status_labels['progress'] = QLabel("Ready")
        
        main_layout.addWidget(progress_label)
        main_layout.addWidget(self.progress_bars['main'])
        main_layout.addWidget(self.status_labels['progress'])
        
        layout.addWidget(main_progress_frame)
        
        # Worker pool status
        worker_frame = self._create_status_frame("Workers", "⚙️")
        self.status_labels['workers'] = worker_frame['value']
        layout.addWidget(worker_frame['frame'])
        
        return group
    
    def _create_status_frame(self, label_text: str, icon: str) -> Dict[str, Any]:
        """Create a status display frame"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Icon and label
        icon_label = QLabel(icon)
        icon_label.setFixedWidth(30)
        
        text_label = QLabel(label_text + ":")
        text_label.setMinimumWidth(80)
        
        # Value label
        value_label = QLabel("Loading...")
        value_label.setStyleSheet("font-weight: bold; color: #A6E22E;")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        return {
            'frame': frame,
            'icon': icon_label,
            'label': text_label,
            'value': value_label
        }
    
    def _initialize_status_values(self):
        """Initialize default status values"""
        self.status_values = {
            'ai_tracker': 'Initializing...',
            'memory': 'Normal',
            'cache': 'Active',
            'instances': '0',
            'running': '0',
            'selected': '0',
            'workers': '0 active',
            'progress': 'Ready'
        }
        
        # Update display
        self._update_status_display()
    
    def _update_status_display(self):
        """Update all status displays"""
        for key, value in self.status_values.items():
            if key in self.status_labels and self.status_labels[key]:
                self.status_labels[key].setText(str(value))
    
    def _update_dynamic_status(self):
        """Update dynamic status values"""
        try:
            # Update AI tracker status
            if hasattr(self.parent_window, 'global_ai_tracker'):
                tracker = self.parent_window.global_ai_tracker
                if tracker:
                    active_count = len(getattr(tracker, 'tracked_instances', {}))
                    self.update_status('ai_tracker', f'{active_count} tracked', 'success')
            
            # Update memory status
            if OPTIMIZATION_AVAILABLE and hasattr(self.parent_window, 'memory_manager'):
                memory_manager = self.parent_window.memory_manager
                if memory_manager:
                    usage = getattr(memory_manager, 'get_memory_usage', lambda: 0)()
                    if usage > 80:
                        self.update_status('memory', f'{usage:.1f}% (High)', 'warning')
                    elif usage > 60:
                        self.update_status('memory', f'{usage:.1f}% (Normal)', 'info')
                    else:
                        self.update_status('memory', f'{usage:.1f}% (Good)', 'success')
            
            # Update cache status
            if hasattr(self.parent_window, 'smart_cache'):
                cache = self.parent_window.smart_cache
                if cache:
                    hit_rate = getattr(cache, 'get_hit_rate', lambda: 0)()
                    self.update_status('cache', f'{hit_rate:.1f}% hit rate', 'success')
            
            # Update instance counts
            if hasattr(self.parent_window, 'instances_model'):
                model = self.parent_window.instances_model
                if model:
                    total = getattr(model, 'rowCount', lambda: 0)()
                    self.update_status('instances', str(total), 'info')
            
        except Exception as e:
            pass  # Silent fail để không ảnh hưởng UI
    
    def _handle_status_update(self, event_data: Dict[str, Any]):
        """Handle status update events from EventManager"""
        category = event_data.get('category', '')
        status = event_data.get('status', '')
        level = event_data.get('level', 'info')
        
        self.update_status(category, status, level)
    
    def _handle_progress_update(self, event_data: Dict[str, Any]):
        """Handle progress update events from EventManager"""
        value = event_data.get('value', 0)
        description = event_data.get('description', '')
        
        self.update_progress(value, description)
    
    def update_status(self, category: str, status: str, level: str = 'info'):
        """Update specific status category"""
        if category in self.status_values:
            self.status_values[category] = status
            
            if category in self.status_labels and self.status_labels[category]:
                label = self.status_labels[category]
                label.setText(status)
                
                # Apply color based on level
                colors = {
                    'success': '#A6E22E',
                    'warning': '#FFC107',
                    'error': '#DC3545',
                    'info': '#17A2B8',
                    'primary': '#007ACC'
                }
                
                color = colors.get(level, '#A6E22E')
                label.setStyleSheet(f"font-weight: bold; color: {color};")
            
            # Emit signal
            self.status_updated.emit(category, status, level)
    
    def update_progress(self, value: int, description: str = ''):
        """Update progress bar"""
        if 'main' in self.progress_bars:
            progress_bar = self.progress_bars['main']
            progress_bar.setValue(value)
            progress_bar.setVisible(value > 0 and value < 100)
        
        if description and 'progress' in self.status_labels:
            self.status_labels['progress'].setText(description)
        
        # Emit signal
        self.progress_updated.emit(value, description)
    
    def show_progress(self, show: bool = True):
        """Show/hide progress bar"""
        if 'main' in self.progress_bars:
            self.progress_bars['main'].setVisible(show)
    
    def get_status(self, category: str) -> str:
        """Get current status for category"""
        return self.status_values.get(category, '')
    
    def reset_progress(self):
        """Reset progress bar"""
        self.update_progress(0, 'Ready')
        self.show_progress(False)


# Factory function
def create_status_component(parent_window) -> StatusComponent:
    """Factory function để create status component"""
    return StatusComponent(parent_window)
