"""
🚀 ASYNC INITIALIZATION SYSTEM
Background loading để UI hiển thị ngay lập tức
"""

import asyncio
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QProgressBar, QLabel

class AsyncInitializer(QThread):
    """Background initialization thread"""
    
    progress_updated = pyqtSignal(int, str)
    initialization_completed = pyqtSignal()
    component_loaded = pyqtSignal(str, object)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.components = []
        
    def add_component(self, name, loader_func, priority=0):
        """Add component to background loading queue"""
        self.components.append({
            'name': name,
            'loader': loader_func,
            'priority': priority,
            'loaded': False
        })
        
    def run(self):
        """Background loading process"""
        # Sort by priority
        self.components.sort(key=lambda x: x['priority'], reverse=True)
        
        total = len(self.components)
        for i, component in enumerate(self.components):
            try:
                self.progress_updated.emit(
                    int((i / total) * 100), 
                    f"Loading {component['name']}..."
                )
                
                # Load component
                result = component['loader']()
                component['loaded'] = True
                
                # Emit loaded signal
                self.component_loaded.emit(component['name'], result)
                
                # Small delay to prevent UI freezing
                self.msleep(10)
                
            except Exception as e:
                print(f"❌ Failed to load {component['name']}: {e}")
                
        self.progress_updated.emit(100, "Initialization complete!")
        self.initialization_completed.emit()

class AsyncLoadingIndicator:
    """Loading indicator cho async initialization"""
    
    def __init__(self, parent):
        self.parent = parent
        self.progress_bar = QProgressBar(parent)
        self.status_label = QLabel("Initializing...", parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup loading UI"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        
    def update_progress(self, value, message):
        """Update loading progress"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        
    def hide_loading(self):
        """Hide loading indicator"""
        self.progress_bar.hide()
        self.status_label.hide()
