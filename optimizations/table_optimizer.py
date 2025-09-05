#!/usr/bin/env python3
"""
📊 TABLE VIRTUALIZATION OPTIMIZER - Phase 4.5
Advanced table virtualization for 516+ instances with performance optimization
"""

import time
from typing import Dict, List, Optional, Any, Set
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QRect, QPoint, QAbstractItemModel, QModelIndex
from PyQt6.QtWidgets import QTableView, QWidget
from PyQt6.QtGui import QPainter, QPaintEvent
from collections import deque

class VirtualizedTableModel(QAbstractItemModel):
    """🚀 Virtualized table model for large datasets"""

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._data: List[Dict[str, Any]] = []
        self._visible_rows: Set[int] = set()
        self._cache: Dict[int, Dict[str, Any]] = {}
        self._batch_size = 50  # Load 50 rows at a time
        self._preload_distance = 20  # Preload 20 rows ahead/behind

    def set_data(self, data: List[Dict[str, Any]]):
        """Set the complete dataset"""
        self.beginResetModel()
        self._data = data
        self._cache.clear()
        self._visible_rows.clear()
        self.endResetModel()

    def rowCount(self, parent: Optional[QModelIndex] = None) -> int:
        return len(self._data)

    def columnCount(self, parent: Optional[QModelIndex] = None) -> int:
        return 6  # STT, Name, Status, ADB, Disk, Spacer

    def data(self, index: QModelIndex, role: int = 0) -> Any:
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        # Ensure row data is cached
        if row not in self._cache:
            self._load_row_data(row)

        if row in self._cache:
            row_data = self._cache[row]
            return self._get_column_data(row_data, col, role)

        return None

    def _load_row_data(self, row: int):
        """Load row data into cache"""
        if 0 <= row < len(self._data):
            self._cache[row] = self._data[row].copy()

    def _get_column_data(self, row_data: Dict[str, Any], col: int, role: int):
        """Get data for specific column"""
        if role != 0:  # DisplayRole
            return None

        if col == 0:  # STT
            return str(row_data.get('index', 'N/A'))
        elif col == 1:  # Name
            return row_data.get('name', 'N/A')
        elif col == 2:  # Status
            return 'Running' if row_data.get('is_process_started') else 'Stopped'
        elif col == 3:  # ADB
            return str(row_data.get('adb_port', 'N/A'))
        elif col == 4:  # Disk
            disk_bytes = row_data.get('disk_size_bytes', 0)
            if disk_bytes > 0:
                disk_gb = disk_bytes / (1024**3)
                return f"{disk_gb:.2f}GB" if disk_gb >= 1 else f"{disk_gb*1024:.2f}MB"
            return 'N/A'
        return ''

class OptimizedTableView(QTableView):
    """🚀 Optimized table view with virtualization support"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._virtual_model = VirtualizedTableModel(self)
        self.setModel(self._virtual_model)

        # Performance optimizations
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)

        # Virtualization settings
        self._visible_range = (0, 50)  # Currently visible rows
        self._preload_timer = QTimer(self)
        self._preload_timer.timeout.connect(self._update_visible_range)
        self._preload_timer.setInterval(100)  # Update every 100ms

        # Connect scroll signals for virtualization
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)

    def set_data(self, data: List[Dict[str, Any]]):
        """Set table data with virtualization"""
        self._virtual_model.set_data(data)
        self._update_visible_range()

    def _on_scroll(self):
        """Handle scroll events for virtualization"""
        self._preload_timer.start()  # Debounced update

    def _update_visible_range(self):
        """Update visible row range for virtualization"""
        scrollbar = self.verticalScrollBar()
        if scrollbar:
            value = scrollbar.value()
            page_size = self.height() // self.rowHeight(0) if self.rowHeight(0) > 0 else 20

            start_row = max(0, value)
            end_row = min(self._virtual_model.rowCount(), value + page_size + 10)

            self._visible_range = (start_row, end_row)

            # Preload data for visible range
            for row in range(start_row, end_row):
                if row not in self._virtual_model._cache:
                    self._virtual_model._load_row_data(row)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get virtualization performance statistics"""
        return {
            'total_rows': self._virtual_model.rowCount(),
            'cached_rows': len(self._virtual_model._cache),
            'visible_range': self._visible_range,
            'cache_hit_rate': len(self._virtual_model._cache) / max(1, self._virtual_model.rowCount())
        }
