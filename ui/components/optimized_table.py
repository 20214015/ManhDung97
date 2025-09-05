"""
Optimized Table View Components
===============================

High-performance table view with Model/View pattern and rendering optimizations.
"""

from typing import Dict, List, Any, Optional
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, pyqtSignal, QSortFilterProxyModel
from PyQt6.QtWidgets import QTableView, QHeaderView, QAbstractItemView, QStyledItemDelegate
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

from constants import TableColumn
from services.cache_service import InstanceInfo, InstanceStatus


class OptimizedInstanceModel(QAbstractTableModel):
    """Optimized table model with uniform row heights and smart updates"""
    
    stats_updated = pyqtSignal(int, int)  # total, running
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._instances: Dict[int, InstanceInfo] = {}
        self._row_to_index: List[int] = []  # Maps row number to instance index
        self._index_to_row: Dict[int, int] = {}  # Maps instance index to row number
        
        # Performance optimization flags
        self._sorting_enabled = True
        self._uniform_row_heights = True
        
    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._instances)
        
    def columnCount(self, parent=QModelIndex()) -> int:
        return 7  # Checkbox, Index, Name, Status, ADB, Disk, Spacer
        
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return None
            
        headers = ["", "Index", "Name", "Status", "ADB", "Disk", ""]
        return headers[section] if 0 <= section < len(headers) else ""
        
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
            
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        
        # Checkbox column is user-checkable
        if index.column() == TableColumn.CHECKBOX:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
            
        return flags
        
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._row_to_index):
            return None
            
        instance_index = self._row_to_index[index.row()]
        instance_info = self._instances.get(instance_index)
        
        if not instance_info:
            return None
            
        column = index.column()
        
        # Display role
        if role == Qt.ItemDataRole.DisplayRole:
            if column == TableColumn.STT:
                return str(instance_info.index)
            elif column == TableColumn.NAME:
                return instance_info.name
            elif column == TableColumn.STATUS:
                return self._format_status(instance_info.status)
            elif column == TableColumn.ADB:
                return f":{instance_info.adb_port}" if instance_info.adb_port > 0 else "N/A"
            elif column == TableColumn.DISK_USAGE:
                return instance_info.disk_usage
            return None
            
        # CheckState role for checkbox
        elif role == Qt.ItemDataRole.CheckStateRole:
            if column == TableColumn.CHECKBOX:
                # You can store checkbox state in instance_info or separate dict
                return Qt.CheckState.Unchecked  # Default unchecked
            return None
            
        # Text alignment
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if column in [TableColumn.STT, TableColumn.ADB]:
                return int(Qt.AlignmentFlag.AlignCenter)
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
        # Foreground color for status
        elif role == Qt.ItemDataRole.ForegroundRole:
            if column == TableColumn.STATUS:
                return self._get_status_color(instance_info.status)
            return None
            
        # Tooltip
        elif role == Qt.ItemDataRole.ToolTipRole:
            if column == TableColumn.STATUS:
                return f"Status: {self._format_status(instance_info.status)}\nLast updated: {instance_info.last_updated:.1f}s ago"
            elif column == TableColumn.DISK_USAGE:
                if instance_info.disk_size_bytes > 0:
                    gb = instance_info.disk_size_bytes / (1024**3)
                    return f"Disk usage: {gb:.2f} GB ({instance_info.disk_size_bytes:,} bytes)"
            return None
            
        return None
        
    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid() or index.row() >= len(self._row_to_index):
            return False
            
        # Handle checkbox state changes
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == TableColumn.CHECKBOX:
            # You can implement checkbox state storage here
            self.dataChanged.emit(index, index, [role])
            return True
            
        return False
        
    def update_instances(self, instances: Dict[int, InstanceInfo]):
        """Smart update that minimizes model resets"""
        # Disable sorting during update for performance
        old_sorting = self._sorting_enabled
        self._sorting_enabled = False
        
        # Check if we need full reset or can do incremental update
        if self._needs_full_reset(instances):
            self._full_reset(instances)
        else:
            self._incremental_update(instances)
            
        # Re-enable sorting
        self._sorting_enabled = old_sorting
        
        # Update statistics
        running_count = sum(1 for info in instances.values() 
                          if info.status == InstanceStatus.RUNNING)
        self.stats_updated.emit(len(instances), running_count)
        
    def update_single_instance(self, instance_info: InstanceInfo):
        """Update single instance without model reset"""
        instance_index = instance_info.index
        
        if instance_index in self._index_to_row:
            # Update existing instance
            row = self._index_to_row[instance_index]
            self._instances[instance_index] = instance_info
            
            # Emit data changed for the entire row
            start_index = self.index(row, 0)
            end_index = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(start_index, end_index)
        else:
            # New instance - add to end
            self._add_instance(instance_info)
            
    def _needs_full_reset(self, new_instances: Dict[int, InstanceInfo]) -> bool:
        """Check if full model reset is needed"""
        # Full reset if instance count changed significantly
        if abs(len(new_instances) - len(self._instances)) > 5:
            return True
            
        # Full reset if many instances are new
        new_indices = set(new_instances.keys())
        old_indices = set(self._instances.keys())
        new_count = len(new_indices - old_indices)
        
        return new_count > len(self._instances) * 0.3  # More than 30% new
        
    def _full_reset(self, instances: Dict[int, InstanceInfo]):
        """Perform full model reset"""
        self.beginResetModel()
        
        self._instances = instances.copy()
        self._rebuild_index_maps()
        
        self.endResetModel()
        
    def _incremental_update(self, instances: Dict[int, InstanceInfo]):
        """Perform incremental update"""
        # Update existing instances
        for instance_index, instance_info in instances.items():
            if instance_index in self._instances:
                old_info = self._instances[instance_index]
                if old_info.has_changed(instance_info):
                    self.update_single_instance(instance_info)
                    
        # Add new instances
        for instance_index, instance_info in instances.items():
            if instance_index not in self._instances:
                self._add_instance(instance_info)
                
        # Remove deleted instances
        to_remove = []
        for instance_index in self._instances:
            if instance_index not in instances:
                to_remove.append(instance_index)
                
        for instance_index in to_remove:
            self._remove_instance(instance_index)
            
    def _add_instance(self, instance_info: InstanceInfo):
        """Add new instance to model"""
        row = len(self._instances)
        
        self.beginInsertRows(QModelIndex(), row, row)
        
        self._instances[instance_info.index] = instance_info
        self._row_to_index.append(instance_info.index)
        self._index_to_row[instance_info.index] = row
        
        self.endInsertRows()
        
    def _remove_instance(self, instance_index: int):
        """Remove instance from model"""
        if instance_index not in self._index_to_row:
            return
            
        row = self._index_to_row[instance_index]
        
        self.beginRemoveRows(QModelIndex(), row, row)
        
        del self._instances[instance_index]
        del self._index_to_row[instance_index]
        self._row_to_index.pop(row)
        
        # Update row mappings for shifted rows
        for i in range(row, len(self._row_to_index)):
            idx = self._row_to_index[i]
            self._index_to_row[idx] = i
            
        self.endRemoveRows()
        
    def _rebuild_index_maps(self):
        """Rebuild index mapping tables"""
        self._row_to_index = sorted(self._instances.keys())
        self._index_to_row = {idx: row for row, idx in enumerate(self._row_to_index)}
        
    def _format_status(self, status: InstanceStatus) -> str:
        """Format status for display"""
        status_map = {
            InstanceStatus.RUNNING: "🟢 Running",
            InstanceStatus.STOPPED: "🔴 Stopped", 
            InstanceStatus.STARTING: "🟡 Starting",
            InstanceStatus.STOPPING: "🟠 Stopping",
            InstanceStatus.ERROR: "❌ Error",
            InstanceStatus.UNKNOWN: "❓ Unknown"
        }
        return status_map.get(status, "❓ Unknown")
        
    def _get_status_color(self, status: InstanceStatus) -> QColor:
        """Get color for status display"""
        color_map = {
            InstanceStatus.RUNNING: QColor("#4CAF50"),   # Green
            InstanceStatus.STOPPED: QColor("#F44336"),   # Red
            InstanceStatus.STARTING: QColor("#FF9800"),  # Orange
            InstanceStatus.STOPPING: QColor("#FF5722"), # Deep Orange  
            InstanceStatus.ERROR: QColor("#FF1744"),     # Error Red
            InstanceStatus.UNKNOWN: QColor("#9E9E9E")    # Grey
        }
        return color_map.get(status, QColor("#000000"))


class OptimizedTableView(QTableView):
    """High-performance table view with optimizations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_optimizations()
        
    def _setup_optimizations(self):
        """Apply performance optimizations"""
        # Enable uniform row heights for better performance
        self.setUniformRowHeights(True)
        
        # Viewport optimizations
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_StaticContents, True)
        
        # Selection and interaction
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        
        # Header configuration
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Resize specific columns to content
        for col in [TableColumn.CHECKBOX, TableColumn.STT, TableColumn.ADB, TableColumn.DISK_USAGE]:
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
            
        # Hide vertical header
        self.verticalHeader().setVisible(False)
        
        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Initially disable sorting for better loading performance
        self.setSortingEnabled(False)
        
    def setModel(self, model):
        """Override setModel to apply optimizations after model is set"""
        super().setModel(model)
        
        # Re-enable sorting after model is set
        if model:
            self.setSortingEnabled(True)
            
    def enable_sorting(self, enabled: bool):
        """Enable/disable sorting for performance during data loading"""
        self.setSortingEnabled(enabled)
        
    def get_selected_indices(self) -> List[int]:
        """Get selected instance indices"""
        if not self.model():
            return []
            
        indices = []
        for index in self.selectionModel().selectedRows():
            row = index.row()
            if hasattr(self.model(), '_row_to_index') and row < len(self.model()._row_to_index):
                instance_index = self.model()._row_to_index[row]
                indices.append(instance_index)
                
        return indices


class StatusPillDelegate(QStyledItemDelegate):
    """Custom delegate for status column with pill-style rendering"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def paint(self, painter: QPainter, option, index):
        """Custom paint for status pills"""
        if index.column() != TableColumn.STATUS:
            super().paint(painter, option, index)
            return
            
        painter.save()
        
        # Get status data
        status_text = index.data(Qt.ItemDataRole.DisplayRole)
        status_color = index.data(Qt.ItemDataRole.ForegroundRole)
        
        if not status_text:
            painter.restore()
            return
            
        # Setup pill geometry
        rect = option.rect
        pill_rect = rect.adjusted(5, 2, -5, -2)
        
        # Draw pill background
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if status_color:
            bg_color = QColor(status_color)
            bg_color.setAlpha(30)  # Semi-transparent background
            painter.setBrush(QBrush(bg_color))
            
            border_color = QColor(status_color)
            painter.setPen(QPen(border_color, 1))
        else:
            painter.setBrush(QBrush(QColor(240, 240, 240)))
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            
        painter.drawRoundedRect(pill_rect, 8, 8)
        
        # Draw text
        if status_color:
            painter.setPen(QPen(QColor(status_color)))
        else:
            painter.setPen(QPen(QColor(0, 0, 0)))
            
        painter.drawText(pill_rect, Qt.AlignmentFlag.AlignCenter, status_text)
        
        painter.restore()


class OptimizedProxyModel(QSortFilterProxyModel):
    """Proxy model with filtering capabilities"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDynamicSortFilter(True)
        self._status_filter = None
        self._name_filter = ""
        
    def set_status_filter(self, status: Optional[InstanceStatus]):
        """Filter by instance status"""
        self._status_filter = status
        self.invalidateFilter()
        
    def set_name_filter(self, name_filter: str):
        """Filter by instance name"""
        self._name_filter = name_filter.lower()
        self.invalidateFilter()
        
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Custom filtering logic"""
        model = self.sourceModel()
        if not model or not hasattr(model, '_row_to_index'):
            return True
            
        if source_row >= len(model._row_to_index):
            return False
            
        instance_index = model._row_to_index[source_row]
        instance_info = model._instances.get(instance_index)
        
        if not instance_info:
            return False
            
        # Status filter
        if self._status_filter and instance_info.status != self._status_filter:
            return False
            
        # Name filter
        if self._name_filter and self._name_filter not in instance_info.name.lower():
            return False
            
        return True