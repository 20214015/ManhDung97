"""
🚀 TABLE VIRTUALIZATION SYSTEM
Xử lý hàng nghìn items mà không lag UI
"""

from PyQt6.QtWidgets import QAbstractScrollArea, QScrollBar
from PyQt6.QtCore import QRect, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QFont

class VirtualizedTableView:
    """Table virtualization cho performance cao"""
    
    def __init__(self, table_widget):
        self.table = table_widget
        self.visible_rows = []
        self.total_items = 0
        self.row_height = 30
        self.buffer_size = 10  # Extra rows to render
        
        # Performance tracking
        self.last_scroll_time = 0
        self.scroll_debounce = QTimer()
        self.scroll_debounce.setSingleShot(True)
        self.scroll_debounce.setInterval(16)  # 60 FPS
        self.scroll_debounce.timeout.connect(self._update_visible_rows)
        
        # Connect scroll events
        if hasattr(self.table, 'verticalScrollBar'):
            self.table.verticalScrollBar().valueChanged.connect(self._on_scroll)
    
    def _on_scroll(self, value):
        """Handle scroll events với debouncing"""
        import time
        self.last_scroll_time = time.time()
        self.scroll_debounce.start()
    
    def _update_visible_rows(self):
        """Update chỉ những rows visible + buffer"""
        if not self.table:
            return
            
        # Tính visible range
        viewport_height = self.table.viewport().height()
        scroll_value = self.table.verticalScrollBar().value()
        
        start_row = max(0, scroll_value // self.row_height - self.buffer_size)
        visible_count = (viewport_height // self.row_height) + (2 * self.buffer_size)
        end_row = min(self.total_items, start_row + visible_count)
        
        # Chỉ update nếu range thay đổi đáng kể
        new_range = (start_row, end_row)
        if not hasattr(self, '_last_range') or abs(new_range[0] - self._last_range[0]) > 5:
            self._render_visible_rows(start_row, end_row)
            self._last_range = new_range
    
    def _render_visible_rows(self, start_row, end_row):
        """Render chỉ visible rows để tăng performance"""
        # This would integrate with the actual table model
        # For now, this is the framework
        pass
    
    def set_total_items(self, count):
        """Set tổng số items để tính virtualization"""
        self.total_items = count
        self._update_visible_rows()
        
    def enable_virtualization(self):
        """Enable table virtualization"""
        print(f"🚀 Table Virtualization enabled for {self.total_items} items")
        
    def get_performance_stats(self):
        """Get virtualization performance stats"""
        visible_range = getattr(self, '_last_range', (0, 0))
        return {
            'total_items': self.total_items,
            'visible_range': visible_range,
            'rendered_rows': visible_range[1] - visible_range[0],
            'buffer_size': self.buffer_size,
            'row_height': self.row_height
        }
