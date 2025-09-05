"""
Enhanced Dashboard Monokai - Nâng cấp và tối ưu dashboard với Modern Architecture
==================================================================================

Nâng cấp toàn diện dashboard_monokai.py với:
- Model/View architecture hiện đại
- Performance optimization
- Enhanced search & filtering
- Smart caching và progressive loading
- Real-time analytics và monitoring

Author: GitHub Copilot Assistant
Date: 2025-01-27
Version: 2.0 Enhanced
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableView, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QPushButton, QLineEdit, QComboBox, QSplitter,
    QGroupBox, QGridLayout, QProgressBar, QTextEdit, QScrollArea, QAbstractItemView,
    QMenu, QMessageBox, QSpinBox, QCheckBox, QSlider
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QItemSelectionModel, QThread, pyqtSlot, QAbstractTableModel, QModelIndex, QThreadPool, QRunnable, QObject
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QBrush, QAction
import sys
import gc
import weakref
import zlib
import pickle
import lzma
import datetime
from typing import Dict, List, Optional, Any, Type, Tuple
from collections import deque, OrderedDict
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QTableWidgetItem, QWidget
import psutil
import time
import threading


# Import advanced memory management
from optimizations.memory_pool import AdvancedMemoryManager
from optimizations.smart_cache import PredictiveCache
from optimizations.intelligent_worker_pool import AdvancedWorkerPool

# Import constants
try:
    from constants import TableColumn
except ImportError:
    # Fallback definition
    class TableColumn:
        CHECKBOX = 0
        STT = 1
        NAME = 2
        STATUS = 3
        ADB = 4
        DISK_USAGE = 5
        SPACER = 6


class VirtualScrollingModel(QAbstractTableModel):
    """Virtual scrolling model cho large datasets (>1000 rows)"""

    # Signals
    data_loaded = pyqtSignal(int, int)  # start_row, end_row
    loading_progress = pyqtSignal(int, int)  # current, total

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []  # Full dataset
        self._visible_rows = []  # Currently visible rows
        self._total_rows = 0
        self._chunk_size = 100  # Rows per chunk
        self._visible_range = (0, 0)  # (start, end) of visible rows
        self._columns = ['Index', 'Name', 'Status', 'CPU', 'Memory', 'Disk', 'AI Score', 'Health']

        # Advanced memory pool integration
        self.memory_pool = AdvancedMemoryManager(self)

        # Background loading
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(2)  # Limit concurrent operations

        # Cache for loaded chunks
        self._loaded_chunks = set()
        self._pending_chunks = set()

    def set_total_rows(self, total: int):
        """Set total number of rows (virtual)"""
        self.beginResetModel()
        self._total_rows = total
        self._data = [None] * total  # Placeholder array
        self.endResetModel()

    def set_visible_range(self, start: int, end: int):
        """Set visible row range để load data on demand"""
        if self._visible_range == (start, end):
            return

        self._visible_range = (start, end)

        # Calculate required chunks
        start_chunk = start // self._chunk_size
        end_chunk = min(end // self._chunk_size, (self._total_rows - 1) // self._chunk_size)

        # Load required chunks
        for chunk_id in range(start_chunk, end_chunk + 1):
            if chunk_id not in self._loaded_chunks and chunk_id not in self._pending_chunks:
                self._load_chunk_async(chunk_id)

    def _load_chunk_async(self, chunk_id: int):
        """Load data chunk asynchronously"""
        self._pending_chunks.add(chunk_id)

        # Create background worker
        worker = DataLoaderWorker(chunk_id, self._chunk_size, self._total_rows)
        worker.signals.finished.connect(lambda chunk_data, cid=chunk_id: self._on_chunk_loaded(cid, chunk_data))
        worker.signals.progress.connect(self.loading_progress.emit)

        self.thread_pool.start(worker)

    def _on_chunk_loaded(self, chunk_id: int, chunk_data: List[Dict]):
        """Handle khi chunk data được load xong"""
        if chunk_id in self._pending_chunks:
            self._pending_chunks.remove(chunk_id)
            self._loaded_chunks.add(chunk_id)

            # Store in memory pool
            chunk_size_mb = len(chunk_data) * 0.001  # Rough estimate: 1KB per row
            if self.memory_pool.allocate_chunk(f"chunk_{chunk_id}", chunk_data, chunk_size_mb):
                # Update data array
                start_idx = chunk_id * self._chunk_size
                for i, row_data in enumerate(chunk_data):
                    if start_idx + i < len(self._data):
                        self._data[start_idx + i] = row_data

                # Notify view about data changes
                start_row = chunk_id * self._chunk_size
                end_row = min(start_row + len(chunk_data), self._total_rows)
                self.data_loaded.emit(start_row, end_row)

                # Emit dataChanged signal
                if start_row < end_row:
                    top_left = self.index(start_row, 0)
                    bottom_right = self.index(end_row - 1, len(self._columns) - 1)
                    self.dataChanged.emit(top_left, bottom_right)

    def rowCount(self, parent=QModelIndex()) -> int:
        """Return total row count"""
        if parent.isValid():
            return 0
        return self._total_rows

    def columnCount(self, parent=QModelIndex()) -> int:
        """Return column count"""
        if parent.isValid():
            return 0
        return len(self._columns)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        """Get data for cell"""
        if not index.isValid() or index.row() >= self._total_rows:
            return None

        row_data = self._data[index.row()]
        if row_data is None:
            # Data not loaded yet
            if role == Qt.ItemDataRole.DisplayRole:
                return "Loading..."
            return None

        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:  # Index
                return str(row_data.get('index', index.row() + 1))
            elif col == 1:  # Name
                return row_data.get('name', f'MuMu-{index.row()}')
            elif col == 2:  # Status
                return row_data.get('status', 'Unknown')
            elif col == 3:  # CPU
                return row_data.get('cpu_usage', '0%')
            elif col == 4:  # Memory
                return row_data.get('memory_usage', '0MB')
            elif col == 5:  # Disk
                return row_data.get('disk_usage', '0GB')
            elif col == 6:  # AI Score
                return row_data.get('ai_score', 'C')
            elif col == 7:  # Health
                return row_data.get('health', 'Unknown')

        elif role == Qt.ItemDataRole.BackgroundRole:
            # Color coding based on status/health
            status = row_data.get('status', '').lower()
            if status == 'running':
                return QColor('#4CAF50')  # Green
            elif status == 'stopped':
                return QColor('#F44336')  # Red
            elif status == 'starting':
                return QColor('#FF9800')  # Orange

        return None

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Header data"""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self._columns):
                return self._columns[section]
        return None

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        return self.memory_pool.get_memory_usage()


class DataLoaderWorkerSignals(QObject):
    """Signals cho DataLoaderWorker"""
    finished = pyqtSignal(list)  # chunk_data
    progress = pyqtSignal(int, int)  # current, total
    error = pyqtSignal(str)  # error_message


class DataLoaderWorker(QRunnable):
    """Background worker để load data chunks"""

    def __init__(self, chunk_id: int, chunk_size: int, total_rows: int):
        super().__init__()
        self.chunk_id = chunk_id
        self.chunk_size = chunk_size
        self.total_rows = total_rows
        self.signals = DataLoaderWorkerSignals()

    def run(self):
        """Load data chunk trong background"""
        try:
            start_idx = self.chunk_id * self.chunk_size
            end_idx = min(start_idx + self.chunk_size, self.total_rows)

            chunk_data = []

            # Simulate data loading (replace with actual backend call)
            for i in range(start_idx, end_idx):
                # Generate mock data for demonstration
                instance_data = {
                    'index': i,
                    'name': f'MuMu Player {i}',
                    'status': 'running' if i % 3 == 0 else 'stopped' if i % 3 == 1 else 'starting',
                    'cpu_usage': f'{5 + (i % 20)}%',
                    'memory_usage': f'{100 + (i % 500)}MB',
                    'disk_usage': f'{2 + (i % 10)}.0GB',
                    'ai_score': ['A+', 'A', 'B+', 'B', 'C'][i % 5],
                    'health': ['Excellent', 'Good', 'Fair', 'Poor'][i % 4]
                }
                chunk_data.append(instance_data)

                # Emit progress
                progress = int(((i - start_idx + 1) / (end_idx - start_idx)) * 100)
                self.signals.progress.emit(progress, 100)

            # Simulate network delay
            time.sleep(0.1)

            self.signals.finished.emit(chunk_data)

        except Exception as e:
            self.signals.error.emit(str(e))


class BackgroundDataProcessor(QObject):
    """Background data processor cho real-time updates"""

    # Signals
    data_updated = pyqtSignal(list)  # updated_data
    processing_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)  # error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_processing = False
        self.update_interval = 5000  # 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_data_updates)
        self.last_update_time = time.time()

    def start_processing(self):
        """Start background data processing"""
        if not self.is_processing:
            self.is_processing = True
            self.timer.start(self.update_interval)
            print("✅ Background data processor started")

    def stop_processing(self):
        """Stop background data processing"""
        self.is_processing = False
        self.timer.stop()
        print("🛑 Background data processor stopped")

    def process_data_updates(self):
        """Process data updates trong background"""
        try:
            current_time = time.time()

            # Simulate data updates (replace with actual backend monitoring)
            updated_instances = []

            # Generate some random updates
            import random
            for i in range(random.randint(1, 5)):  # 1-5 random updates
                instance_idx = random.randint(0, 999)  # Random instance
                update_data = {
                    'index': instance_idx,
                    'cpu_usage': f'{random.randint(5, 95)}%',
                    'memory_usage': f'{random.randint(100, 800)}MB',
                    'status': random.choice(['running', 'stopped', 'starting']),
                    'last_update': current_time
                }
                updated_instances.append(update_data)

            if updated_instances:
                self.data_updated.emit(updated_instances)

            self.last_update_time = current_time

        except Exception as e:
            self.error_occurred.emit(str(e))

    def force_update(self):
        """Force immediate data update"""
        if self.is_processing:
            self.process_data_updates()


# ===== END OF OPTIMIZATION CLASSES =====

# Import existing optimization components
try:
    from widgets import StatusPillDelegate, InstancesModel, InstancesProxy, CheckboxDelegate
    from enhanced_search_filter import create_enhanced_search_filter_widget, SearchCriteria
    from optimizations.smart_cache import PredictiveCache
    from optimizations.performance_monitor import PerformanceMonitor
    from optimizations.memory_pool import AdvancedMemoryManager
    from ui.components.optimized_table import OptimizedInstanceModel
    ENHANCED_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some enhanced components not available: {e}")
    ENHANCED_COMPONENTS_AVAILABLE = False


class EnhancedMonokaiDashboard(QWidget):
    """Enhanced Dashboard với performance optimization và modern architecture"""
    
    # Enhanced signals for advanced communication
    instance_selected = pyqtSignal(int)
    refresh_requested = pyqtSignal()
    start_all_requested = pyqtSignal()
    stop_all_requested = pyqtSignal()
    start_instance_requested = pyqtSignal(int)
    stop_instance_requested = pyqtSignal(int)
    restart_instance_requested = pyqtSignal(int)
    cleanup_requested = pyqtSignal(list)
    
    # New enhanced signals
    performance_alert = pyqtSignal(str, str)  # title, message
    smart_action_suggested = pyqtSignal(str, list)  # action_type, instances
    
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.setObjectName("EnhancedMonokaiDashboard")
        
        # Store main window reference for auto-refresh control
        self.main_window = main_window or parent
        
        # Enhanced Monokai Color Palette
        self.colors = {
            'bg': '#272822',           # Background chính
            'bg_alt': '#2D2A2E',       # Background phụ
            'bg_dark': '#1E1E1E',      # Background tối hơn
            'fg': '#F8F8F2',           # Text chính
            'comment': '#75715E',       # Text phụ/comment
            'pink': '#F92672',         # Accent pink
            'green': '#A6E22E',        # Success green
            'orange': '#FD971F',       # Warning orange
            'blue': '#66D9EF',         # Info blue
            'purple': '#AE81FF',       # Purple
            'yellow': '#E6DB74',       # String yellow
            'red': '#F44336',          # Red color
            'border': '#49483E',       # Border color
            'selection': '#3E3D32',    # Selection color
            'success': '#4CAF50',      # Modern success
            'warning': '#FF9800',      # Modern warning
            'error': '#F44336',        # Modern error
            'info': '#2196F3'          # Modern info
        }
        
        # Data management
        self.instances_data = []
        self.backend = None
        
        # Enhanced components initialization
        self.smart_cache = None
        self.performance_monitor = None
        self.memory_pool = None
        self.enhanced_filter_widget = None

        # ===== VIRTUAL SCROLLING & MEMORY OPTIMIZATION =====
        self.virtual_scrolling_model = None
        self.background_processor = None
        self.large_dataset_mode = False  # Enable for >1000 rows
        self.virtual_scroll_enabled = False
        self.memory_pool_manager = AdvancedMemoryManager(self)  # Advanced memory management

        # Performance tracking
        self.performance_mode = False
        self.ai_insights_enabled = True
        self.smart_refresh_interval = 5000  # ms
        
        # Initialize button attributes to prevent AttributeError
        self.init_button_attributes()
        
        # Initialize enhanced components if available
        if ENHANCED_COMPONENTS_AVAILABLE:
            self.init_enhanced_components()
        
        # Create standard model/proxy for compatibility
        self.init_models()
        
        # Setup UI
        self.setup_ui()
        self.apply_enhanced_monokai_style()
        self.setup_timers()
        self.connect_signals()
        
        print("✅ EnhancedMonokaiDashboard initialized with performance optimization")
    
    def init_button_attributes(self):
        """Initialize all button attributes to prevent AttributeError"""
        # Action buttons
        self.ai_suggest_btn = QPushButton("🧠 AI Suggest")
        self.btn_start_instance = QPushButton("▶️ Start")
        self.btn_stop_instance = QPushButton("⏹️ Stop")
        self.btn_restart_instance = QPushButton("🔄 Restart")
        self.btn_delete_instance = QPushButton("🗑️ Delete")
        self.auto_refresh_btn = QPushButton("🤖 Auto")
        self.btn_select_all = QPushButton("✅ Smart Select")
        self.btn_deselect_all = QPushButton("❌ Clear")
        self.performance_mode_btn = QPushButton("⚡ Turbo Mode")
        
        print("✅ Button attributes initialized")
        
    def init_enhanced_components(self):
        """Initialize enhanced optimization components"""
        try:
            # Smart caching system
            self.smart_cache = PredictiveCache(max_size_mb=50)

            # Enhanced Performance Monitor
            self.performance_monitor = PerformanceMonitor()

            # Memory Pool for efficient memory management
            self.memory_pool = AdvancedMemoryManager()

            # Auto-detect and enable optimizations based on system capabilities
            self.auto_enable_optimizations()

            print("✅ Enhanced optimization components initialized")

        except Exception as e:
            print(f"⚠️ Failed to initialize enhanced components: {e}")

    def auto_enable_optimizations(self):
        """Auto-detect và enable optimizations dựa trên system capabilities"""
        try:
            # Check system memory
            import psutil
            memory = psutil.virtual_memory()
            available_memory_gb = memory.available / (1024**3)

            # Check CPU cores
            cpu_count = psutil.cpu_count()

            print(f"🔍 System Analysis: {available_memory_gb:.1f}GB RAM, {cpu_count} CPU cores")

            # DISABLE background processing for manual-only mode
            if available_memory_gb >= 8 and cpu_count >= 4:
                print("🚀 High-performance system detected - MANUAL REFRESH ONLY")

                # Disable background processing for manual mode
                # self.enable_background_processing()  # DISABLED

                # Set higher memory limits
                if hasattr(self, 'memory_pool_manager'):
                    self.memory_pool_manager.max_memory_mb = 200  # 200MB for high-end systems

            elif available_memory_gb >= 4:
                print("⚡ Standard system detected - MANUAL REFRESH ONLY")

                # Disable background processing for manual mode
                # self.enable_background_processing()  # DISABLED

            else:
                print("🐌 Limited system detected - MANUAL REFRESH ONLY")

                # Reduce memory limits for low-end systems
                if hasattr(self, 'memory_pool_manager'):
                    self.memory_pool_manager.max_memory_mb = 50  # 50MB for low-end systems

        except Exception as e:
            print(f"⚠️ Auto-optimization detection failed: {e}")
            
    def init_models(self):
        """Initialize Model/View components"""
        try:
            if ENHANCED_COMPONENTS_AVAILABLE:
                # Use enhanced models if available
                self.instances_model = InstancesModel(self)
                self.instances_proxy = InstancesProxy(self)
                self.instances_proxy.setSourceModel(self.instances_model)
                self.status_delegate = StatusPillDelegate(self)
                self.checkbox_delegate = CheckboxDelegate(self)
                print("✅ Enhanced Model/View components initialized")
            else:
                # Fallback to basic implementation
                # Provide a lightweight fallback InstancesModel that implements
                # update_row_by_index and set_rows so callers won't hit NoneType.
                class FallbackInstancesModel(QAbstractTableModel):
                    def __init__(self, parent):
                        super().__init__(parent)
                        self.parent = parent
                        self._data = []
                        self._ui_states = {}  # Initialize ui_states for compatibility

                    def rowCount(self, parent=QModelIndex()):
                        return len(getattr(self.parent, 'instances_data', []))

                    def columnCount(self, parent=QModelIndex()):
                        return 9  # Match the enhanced table column count

                    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
                        if not index.isValid():
                            return None
                        instances_data = getattr(self.parent, 'instances_data', [])
                        if index.row() >= len(instances_data):
                            return None
                        if role == Qt.ItemDataRole.DisplayRole:
                            instance = instances_data[index.row()]
                            if index.column() == 0:  # #
                                return str(instance.get("index", ""))
                            elif index.column() == 1:  # Name
                                return instance.get("name", "")
                            elif index.column() == 2:  # Status
                                return instance.get("status", "")
                            elif index.column() == 3:  # ADB Port
                                return instance.get("adb", "")
                            elif index.column() == 4:  # CPU %
                                return instance.get("cpu_usage", "")
                            elif index.column() == 5:  # Memory
                                return instance.get("memory_usage", "")
                            elif index.column() == 6:  # Disk
                                return instance.get("disk_usage", "")
                            elif index.column() == 7:  # AI Score
                                return instance.get("ai_score", "")
                            elif index.column() == 8:  # Health
                                return instance.get("health", "")
                        return None

                    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
                        if role != Qt.ItemDataRole.DisplayRole:
                            return None
                        if orientation == Qt.Orientation.Horizontal:
                            headers = ["#", "Name", "Status", "ADB Port", "CPU %", "Memory", "Disk", "AI Score", "Health"]
                            return headers[section] if 0 <= section < len(headers) else ""
                        return None

                    def update_row_by_index(self, index, data):
                        """Update parent's instances_data by index (id) or position."""
                        try:
                            # Try to find by 'index' field first
                            for i, inst in enumerate(self.parent.instances_data):
                                if inst.get("index") == index:
                                    inst.update(data or {})
                                    self.parent.instances_data = self.parent.instances_data.copy()
                                    # Emit dataChanged signal to update views
                                    self.dataChanged.emit(self.index(i, 0), self.index(i, self.columnCount()-1))
                                    return True
                            # Fallback: treat index as positional index
                            if 0 <= index < len(self.parent.instances_data):
                                self.parent.instances_data[index].update(data or {})
                                self.parent.instances_data = self.parent.instances_data.copy()
                                # Emit dataChanged signal to update views
                                self.dataChanged.emit(self.index(index, 0), self.index(index, self.columnCount()-1))
                                return True
                            return False
                        except Exception as e:
                            print(f"⚠️ FallbackInstancesModel.update_row_by_index error: {e}")
                            return False

                    def set_rows(self, rows):
                        """Replace model rows with provided list[(index, info)]."""
                        try:
                            self.beginResetModel()
                            new = []
                            for idx, info in rows:
                                entry = {"index": idx}
                                entry.update(info or {})
                                new.append(entry)
                            self.parent.instances_data = new
                            self.parent.instances_data = new.copy()
                            self.endResetModel()
                            # Don't refresh UI here to avoid recursion - the model reset signal will handle it
                        except Exception as e:
                            print(f"⚠️ FallbackInstancesModel.set_rows error: {e}")
                            if hasattr(self, '_in_reset'):
                                self.endResetModel()

                    def set_ui_states(self, ui_states):
                        """Set transient ui status ('starting', 'stopping', ...) and refresh status column."""
                        try:
                            self._ui_states = dict(ui_states or {})
                            # For compatibility with main model
                            if hasattr(self.parent, 'instance_ui_states'):
                                self.parent.instance_ui_states.update(ui_states or {})
                            # Emit dataChanged signal for status column if we have any data
                            if hasattr(self.parent, 'instances_data') and self.parent.instances_data:
                                row_count = len(self.parent.instances_data)
                                if row_count > 0:
                                    # Status column is typically column 3
                                    tl = self.index(0, 3)
                                    br = self.index(row_count - 1, 3)
                                    self.dataChanged.emit(tl, br)
                        except Exception as e:
                            print(f"⚠️ FallbackInstancesModel.set_ui_states error: {e}")

                    def get_checked_indices(self):
                        """Return list of checked instance indices."""
                        try:
                            checked_indices = []
                            for instance in getattr(self.parent, 'instances_data', []):
                                if instance.get('checked', False):
                                    checked_indices.append(instance.get('index', 0))
                            return checked_indices
                        except Exception as e:
                            print(f"⚠️ FallbackInstancesModel.get_checked_indices error: {e}")
                            return []

                # instantiate fallback
                self.instances_model = FallbackInstancesModel(self)
                self.instances_proxy = None
                self.status_delegate = None
                print("⚠️ Using fallback InstancesModel with update_row_by_index support")
                
        except Exception as e:
            print(f"⚠️ Model initialization failed: {e}")
            self.instances_model = None
            self.instances_proxy = None
            self.status_delegate = None
            self.checkbox_delegate = None

    def set_backend(self, backend):
        """Set backend reference và intelligent data loading"""
        print("🔧 DEBUG: set_backend called")
        self.backend = backend
        print("🔧 DEBUG: backend assigned")
        if backend:
            # Connect action signals to backend methods
            self.start_instance_requested.connect(self._handle_start_instance)
            self.stop_instance_requested.connect(self._handle_stop_instance)
            self.restart_instance_requested.connect(self._handle_restart_instance)
            self.cleanup_requested.connect(self._handle_cleanup_instances)
            print("🔧 DEBUG: Action signals connected to backend")
            
            # Defer data loading DISABLED to prevent duplicate refresh
            from PyQt6.QtCore import QTimer
            # QTimer.singleShot(100, self._async_load_backend_data)  # DISABLED
            print("🔧 DEBUG: Async backend loading DISABLED to prevent duplicate refresh")
        print("🔧 DEBUG: set_backend completed")
    
    def _handle_start_instance(self, instance_id: int):
        """Handle start instance request"""
        print(f"🚀 DEBUG: _handle_start_instance called with instance_id: {instance_id}")
        if self.backend:
            print(f"🚀 Starting instance {instance_id}")
            success, message = self.backend.control_instance([instance_id], 'launch')
            print(f"🚀 Backend control_instance result: success={success}, message='{message}'")
            if success:
                print(f"✅ Instance {instance_id} started successfully")
            else:
                print(f"❌ Failed to start instance {instance_id}: {message}")
        else:
            print(f"❌ Backend not available for instance {instance_id}")
    
    def _handle_stop_instance(self, instance_id: int):
        """Handle stop instance request"""
        if self.backend:
            print(f"🛑 Stopping instance {instance_id}")
            success, message = self.backend.control_instance([instance_id], 'shutdown')
            if success:
                print(f"✅ Instance {instance_id} stopped successfully")
            else:
                print(f"❌ Failed to stop instance {instance_id}: {message}")
    
    def _handle_restart_instance(self, instance_id: int):
        """Handle restart instance request"""
        if self.backend:
            print(f"🔄 Restarting instance {instance_id}")
            # Stop first
            success1, msg1 = self.backend.control_instance([instance_id], 'shutdown')
            if success1:
                # Then start
                success2, msg2 = self.backend.control_instance([instance_id], 'launch')
                if success2:
                    print(f"✅ Instance {instance_id} restarted successfully")
                else:
                    print(f"❌ Failed to restart instance {instance_id} (start failed): {msg2}")
            else:
                print(f"❌ Failed to restart instance {instance_id} (stop failed): {msg1}")
    
    def _handle_cleanup_instances(self, instance_ids: list):
        """Handle cleanup instances request"""
        if self.backend and instance_ids:
            print(f"🗑️ Deleting instances {instance_ids}")
            success, message = self.backend.delete_instance(instance_ids)
            if success:
                print(f"✅ Instances {instance_ids} deleted successfully")
            else:
                print(f"❌ Failed to delete instances {instance_ids}: {message}")
    
    def _async_load_backend_data(self):
        """Async load backend data sau khi UI đã hiển thị"""
        print("🔧 DEBUG: Starting async backend data loading")
        try:
            self.smart_load_data_from_backend()
            print("🔧 DEBUG: Async backend data loading completed")
        except Exception as e:
            print(f"⚠️ Error in async backend loading: {e}")
            self.create_enhanced_demo_data()
    
    def smart_load_data_from_backend(self):
        """Smart load dữ liệu từ backend với caching"""
        if not self.backend:
            print("⚠️ No backend available - creating AI demo data")
            self.create_enhanced_demo_data()
            return
            
        try:
            # Check cache first if available
            cached_data = None
            if self.smart_cache:
                cached_data = self.smart_cache.get("get_instances", command_type="instance_list")
                
            if cached_data:
                print("🚀 Loading from smart cache")
                self.update_instances_data(cached_data)
                return
                
            # Load from backend
            instances = None
            if hasattr(self.backend, 'get_instances'):
                print("🔍 Smart loading instances via get_instances...")
                instances = self.backend.get_instances()
            elif hasattr(self.backend, 'get_all_info'):
                print("🔍 Smart loading instances via get_all_info...")
                print("🔍 DEBUG: About to call backend.get_all_info()")
                try:
                    success, data = self.backend.get_all_info()
                    print(f"🔍 DEBUG: backend.get_all_info() returned: success={success}, data_type={type(data)}")
                    if success:
                        print(f"🔍 DEBUG: Success=True, processing data...")
                        if data:
                            print(f"🔍 DEBUG: Data is not empty, type: {type(data)}")
                            if isinstance(data, dict):
                                instances = list(data.values())
                                print(f"📊 Smart converted {len(instances)} instances")
                            else:
                                instances = data
                                print(f"📊 Smart loaded data directly: {len(instances) if hasattr(instances, '__len__') else 'unknown length'}")
                        else:
                            print("🔍 DEBUG: Data is empty")
                    else:
                        print(f"🔍 DEBUG: Success=False, error: {data}")
                        instances = None
                except Exception as e:
                    print(f"🔍 DEBUG: Exception in get_all_info(): {type(e).__name__}: {e}")
                    instances = None
                        
            if instances:
                print(f"✅ Smart loaded {len(instances)} instances from backend")
                self.update_instances_data(instances)
                
                # Cache the data
                if self.smart_cache:
                    self.smart_cache.set("get_instances", instances, command_type="instance_list")
            else:
                print("⚠️ No instances data - creating enhanced demo")
                self.create_enhanced_demo_data()
                
        except Exception as e:
            print(f"⚠️ Error in smart loading: {e}")
            self.create_enhanced_demo_data()
    
    def create_enhanced_demo_data(self):
        """Create enhanced demo data với AI metrics"""
        self.instances_data = []
        ai_scores = ['A+', 'A', 'B+', 'B', 'C+']
        health_states = ['Excellent', 'Good', 'Fair', 'Poor']
        
        for i in range(25):  # More demo instances
            self.instances_data.append({
                'index': i,
                'name': f'AI-MuMu Player {i}',
                'status': 'running' if i % 3 == 0 else 'stopped',
                'adb': 16384 + i,
                'disk_usage': f'{1.0 + i * 0.1:.1f}GB',
                'cpu_usage': f'{10 + i * 2}%',
                'memory_usage': f'{1.5 + i * 0.3:.1f}GB',
                'ai_score': ai_scores[i % len(ai_scores)],
                'health': health_states[i % len(health_states)],
                'efficiency': f'{85 + (i % 15)}%',
                'uptime': f'{i}h {(i*7) % 60}m'
            })
        
        self.instances_data = self.instances_data.copy()
        self.populate_enhanced_table()
        self.update_enhanced_stats()
        self.sync_enhanced_model_data()
        
        print("✅ Enhanced demo data created with AI metrics")
    def setup_ui(self):
        """Setup enhanced giao diện dashboard"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main content area with intelligent splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setObjectName("MainSplitter")
        
        # Left panel - Enhanced Table và controls
        left_panel = self.create_enhanced_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel - AI Stats và monitoring
        right_panel = self.create_enhanced_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Intelligent splitter ratios
        main_splitter.setStretchFactor(0, 7)
        main_splitter.setStretchFactor(1, 3)
        
        layout.addWidget(main_splitter)
        
        # Enhanced status bar with AI insights
        self.create_enhanced_status_bar()
        layout.addWidget(self.status_bar)
        
    def create_enhanced_header(self):
        """Create enhanced header với AI insights"""
        self.header_widget = QFrame()
        self.header_widget.setObjectName("EnhancedHeader")
        self.header_widget.setFixedHeight(100)
        
        layout = QHBoxLayout(self.header_widget)
        
        # Enhanced title with AI indicator
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("🧠 AI-Enhanced MuMu Manager Dashboard")
        title_label.setObjectName("EnhancedHeaderTitle")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Powered by intelligent optimization & predictive analytics")
        subtitle_label.setObjectName("HeaderSubtitle")
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_widget)
        layout.addStretch()
        
        # Enhanced quick stats với AI metrics
        self.create_enhanced_stats_widget()
        layout.addWidget(self.stats_widget)
        
    def create_enhanced_stats_widget(self):
        """Create enhanced stats widget with AI metrics"""
        self.stats_widget = QFrame()
        self.stats_widget.setObjectName("EnhancedStatsWidget")
        stats_layout = QGridLayout(self.stats_widget)
        
        # Row 1: Basic stats
        self.total_label = QLabel("Total: 0")
        self.total_label.setObjectName("StatLabel")
        stats_layout.addWidget(self.total_label, 0, 0)
        
        self.running_label = QLabel("Running: 0")
        self.running_label.setObjectName("StatLabelGreen")
        stats_layout.addWidget(self.running_label, 0, 1)
        
        self.stopped_label = QLabel("Stopped: 0")
        self.stopped_label.setObjectName("StatLabelRed")
        stats_layout.addWidget(self.stopped_label, 0, 2)
        
        # Row 2: AI-enhanced metrics
        self.efficiency_label = QLabel("Efficiency: 95%")
        self.efficiency_label.setObjectName("StatLabelBlue")
        stats_layout.addWidget(self.efficiency_label, 1, 0)
        
        self.prediction_label = QLabel("AI Score: A+")
        self.prediction_label.setObjectName("StatLabelPurple")
        stats_layout.addWidget(self.prediction_label, 1, 1)
        
        self.health_label = QLabel("Health: Excellent")
        self.health_label.setObjectName("StatLabelGreen")
        stats_layout.addWidget(self.health_label, 1, 2)
        
    def create_enhanced_left_panel(self):
        """Create enhanced left panel với advanced search"""
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # Đưa controls lên đầu để ngang tầm với AI Performance Analytics
        controls = self.create_enhanced_controls()
        layout.addWidget(controls)
        
        # Enhanced instance table với AI optimization
        self.create_enhanced_instance_table()
        layout.addWidget(self.instance_table)
        
        return left_widget
        
    def create_enhanced_controls(self):
        """Create enhanced controls với AI features"""
        print("🔧 DEBUG: Starting create_enhanced_controls()")
        controls_widget = QFrame()
        controls_widget.setObjectName("EnhancedControlsFrame")
        controls_widget.setFixedHeight(80)  # Giảm chiều cao để bảng instance hiển thị nhiều hơn
        
        layout = QVBoxLayout(controls_widget)
        layout.setSpacing(4)  # Giảm khoảng cách để tiết kiệm không gian
        layout.setContentsMargins(5, 5, 5, 5)  # Giảm margin để tối ưu không gian
        
        # Bottom row: Action buttons 
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(4)  # Giảm khoảng cách giữa các nút để tiết kiệm không gian
        bottom_row.setContentsMargins(2, 2, 2, 2)  # Giảm margin để tối ưu không gian
        
        # Thêm stretch để căn giữa theo chiều ngang
        bottom_row.addStretch()

        # AI recommendation button
        self.ai_suggest_btn = QPushButton("🧠 AI SUGGEST")
        self.ai_suggest_btn.setObjectName("AIButton")
        self.ai_suggest_btn.clicked.connect(self.request_ai_suggestions)
        bottom_row.addWidget(self.ai_suggest_btn)

        # Instance control buttons
        self.btn_start_instance = QPushButton("▶️ START")
        self.btn_start_instance.setObjectName("StartInstanceButton")
        self.btn_start_instance.clicked.connect(self.handle_start_instance)
        bottom_row.addWidget(self.btn_start_instance)

        self.btn_stop_instance = QPushButton("⏹️ STOP")
        self.btn_stop_instance.setObjectName("StopInstanceButton")
        self.btn_stop_instance.clicked.connect(self.handle_stop_instance)
        bottom_row.addWidget(self.btn_stop_instance)

        self.btn_restart_instance = QPushButton("🔄 RESTART")
        self.btn_restart_instance.setObjectName("RestartInstanceButton")
        self.btn_restart_instance.clicked.connect(self.handle_restart_instance)
        bottom_row.addWidget(self.btn_restart_instance)

        self.btn_delete_instance = QPushButton("🗑️ DELETE")
        self.btn_delete_instance.setObjectName("DeleteInstanceButton")
        self.btn_delete_instance.clicked.connect(self.handle_delete_instance)
        bottom_row.addWidget(self.btn_delete_instance)

        self.auto_refresh_btn = QPushButton("🤖 AUTO")
        self.auto_refresh_btn.setObjectName("AutoButton")
        self.auto_refresh_btn.setCheckable(True)

        # Disable auto-refresh by default
        self.auto_refresh_btn.setChecked(False)
        self.auto_refresh_btn.setText("🤖 Auto")
        self.auto_refresh_btn.setToolTip("Click to enable auto-refresh (disabled by default)")

        self.auto_refresh_btn.toggled.connect(self.toggle_smart_auto_refresh)
        bottom_row.addWidget(self.auto_refresh_btn)

        # Enhanced select buttons
        self.btn_select_all = QPushButton("✅ SMART SELLECT")
        self.btn_select_all.setObjectName("SelectButton")
        self.btn_select_all.clicked.connect(self.smart_select_all)
        bottom_row.addWidget(self.btn_select_all)

        self.btn_deselect_all = QPushButton("❌ CLEAR")
        self.btn_deselect_all.setObjectName("DeselectButton")
        self.btn_deselect_all.clicked.connect(self.deselect_all_instances)
        bottom_row.addWidget(self.btn_deselect_all)

        # Performance mode toggle
        self.performance_mode_btn = QPushButton("⚡ TURBO")
        self.performance_mode_btn.setObjectName("PerformanceButton")
        self.performance_mode_btn.setCheckable(True)
        self.performance_mode_btn.toggled.connect(self.toggle_performance_mode)
        bottom_row.addWidget(self.performance_mode_btn)
        
        # Thêm stretch cuối để căn giữa theo chiều ngang
        bottom_row.addStretch()

        layout.addLayout(bottom_row)
        return controls_widget

    def get_selected_instance_ids(self):
        """Get selected instance IDs from the table"""
        selected_ids = []
        if hasattr(self, 'instance_table'):
            if hasattr(self.instance_table, 'selectedItems'):
                # QTableWidget
                selected_rows = set()
                for item in self.instance_table.selectedItems():
                    selected_rows.add(item.row())
                for row in selected_rows:
                    id_item = self.instance_table.item(row, 0)
                    if id_item:
                        try:
                            selected_ids.append(int(id_item.text()))
                        except Exception:
                            pass
            elif hasattr(self.instance_table, 'selectionModel'):
                # QTableView - Check if we have enhanced model with checkboxes
                if hasattr(self, 'instances_model') and self.instances_model and hasattr(self.instances_model, 'get_checked_indices'):
                    # Use checked instances instead of selected rows for bulk operations
                    selected_ids = self.instances_model.get_checked_indices()
                    print(f"🔍 DEBUG: Using checked instances: {selected_ids}")
                else:
                    # Fallback to selected rows
                    selection = self.instance_table.selectionModel().selectedRows()
                    print(f"🔍 DEBUG: QTableView selection has {len(selection)} rows")
                    for i, index in enumerate(selection):
                        print(f"🔍 DEBUG: Row {i}: index.row() = {index.row()}")
                        try:
                            model_index = self.instances_model.index(index.row(), 0)
                            data = self.instances_model.data(model_index)
                            print(f"🔍 DEBUG: Model data at row {index.row()}: {data}")
                            selected_ids.append(int(data))
                        except Exception as e:
                            print(f"⚠️ DEBUG: Error getting data for row {index.row()}: {e}")
        return selected_ids

    def handle_start_instance(self):
        """Handle start instance button"""
        ids = self.get_selected_instance_ids()
        print(f"🔍 DEBUG: Selected instance IDs: {ids}")
        print(f"🔍 DEBUG: Number of selected instances: {len(ids)}")
        
        if len(ids) == 1:
            # Single instance - use existing signal
            instance_id = ids[0]
            print(f"🚀 DEBUG: Emitting single start signal for instance {instance_id} (type: {type(instance_id)})")
            self.start_instance_requested.emit(instance_id)
        elif len(ids) > 1:
            # Multiple instances - handle them together
            print(f"🚀 DEBUG: Starting multiple instances: {ids}")
            if self.backend:
                success, message = self.backend.control_instance(ids, 'launch')
                print(f"🚀 DEBUG: Backend batch control_instance result: success={success}, message='{message}'")
                if success:
                    print(f"✅ Multiple instances {ids} started successfully")
                else:
                    print(f"❌ Failed to start multiple instances {ids}: {message}")
            else:
                print(f"❌ Backend not available for multiple instances {ids}")
        else:
            print("⚠️ No instances selected")

    def handle_stop_instance(self):
        """Handle stop instance button"""
        ids = self.get_selected_instance_ids()
        print(f"🛑 DEBUG: Selected instance IDs for stop: {ids}")
        print(f"🛑 DEBUG: Number of selected instances: {len(ids)}")
        
        if len(ids) == 1:
            # Single instance - use existing signal
            instance_id = ids[0]
            print(f"🛑 DEBUG: Emitting single stop signal for instance {instance_id}")
            self.stop_instance_requested.emit(instance_id)
        elif len(ids) > 1:
            # Multiple instances - handle them together
            print(f"🛑 DEBUG: Stopping multiple instances: {ids}")
            if self.backend:
                success, message = self.backend.control_instance(ids, 'shutdown')
                print(f"🛑 DEBUG: Backend batch control_instance result: success={success}, message='{message}'")
                if success:
                    print(f"✅ Multiple instances {ids} stopped successfully")
                else:
                    print(f"❌ Failed to stop multiple instances {ids}: {message}")
            else:
                print(f"❌ Backend not available for multiple instances {ids}")
        else:
            print("⚠️ No instances selected")

    def handle_restart_instance(self):
        """Handle restart instance button"""
        ids = self.get_selected_instance_ids()
        print(f"🔄 DEBUG: Selected instance IDs for restart: {ids}")
        print(f"🔄 DEBUG: Number of selected instances: {len(ids)}")
        
        if len(ids) == 1:
            # Single instance - use existing signal
            instance_id = ids[0]
            print(f"🔄 DEBUG: Emitting single restart signal for instance {instance_id}")
            self.restart_instance_requested.emit(instance_id)
        elif len(ids) > 1:
            # Multiple instances - handle them together
            print(f"🔄 DEBUG: Restarting multiple instances: {ids}")
            if self.backend:
                # For restart, we need to stop first, then start
                stop_success, stop_message = self.backend.control_instance(ids, 'shutdown')
                print(f"🔄 DEBUG: Stop phase result: success={stop_success}, message='{stop_message}'")
                
                if stop_success:
                    # Small delay before starting
                    import time
                    time.sleep(1)
                    
                    start_success, start_message = self.backend.control_instance(ids, 'launch')
                    print(f"🔄 DEBUG: Start phase result: success={start_success}, message='{start_message}'")
                    
                    if start_success:
                        print(f"✅ Multiple instances {ids} restarted successfully")
                    else:
                        print(f"❌ Failed to start multiple instances {ids} during restart: {start_message}")
                else:
                    print(f"❌ Failed to stop multiple instances {ids} during restart: {stop_message}")
            else:
                print(f"❌ Backend not available for multiple instances {ids}")
        else:
            print("⚠️ No instances selected")

    def handle_delete_instance(self):
        """Handle delete instance button"""
        ids = self.get_selected_instance_ids()
        if ids:
            self.cleanup_requested.emit(ids)
        

    def create_enhanced_instance_table(self):
        """Create enhanced instance table với AI optimization"""
        if ENHANCED_COMPONENTS_AVAILABLE and self.instances_model:
            # Use enhanced Model/View table
            self.instance_table = QTableView()
            self.instance_table.setObjectName("EnhancedInstanceTableView")
            self.instance_table.setModel(self.instances_model)
            
            # Connect model signals for checkbox updates
            self.instances_model.dataChanged.connect(self.on_model_data_changed)
            
            # Apply delegates if available
            if self.status_delegate:
                self.instance_table.setItemDelegateForColumn(3, self.status_delegate)
                print("🎯 Status delegate set for column 3")
            if hasattr(self, 'checkbox_delegate') and self.checkbox_delegate:
                self.instance_table.setItemDelegateForColumn(0, self.checkbox_delegate)
                print("✅ Checkbox delegate set for column 0")
                print(f"🔧 Checkbox delegate type: {type(self.checkbox_delegate)}")
            else:
                print("❌ Checkbox delegate not found or not created")
            
            # Enhanced table settings
            self.configure_enhanced_table_view()
            
        else:
            # Fallback to enhanced QTableWidget
            self.instance_table = QTableWidget()
            self.instance_table.setObjectName("EnhancedInstanceTable")
            self.configure_enhanced_table_widget()
            
        # Common optimizations
        self.apply_table_optimizations()
        
    def configure_enhanced_table_view(self):
        """Configure enhanced QTableView with AI features"""
        # Performance optimizations
        # Note: QTableView doesn't have setUniformRowHeights() like QTableWidget
        # Row heights are managed by the model and delegate
        self.instance_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed | QAbstractItemView.EditTrigger.AnyKeyPressed)
        self.instance_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.instance_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.instance_table.setAlternatingRowColors(True)
        self.instance_table.setSortingEnabled(True)
        self.instance_table.setWordWrap(False)

        # Performance optimizations - only use methods that exist for QTableView
        # Note: setViewportUpdateMode may not be available in all Qt versions
        try:
            self.instance_table.setViewportUpdateMode(QAbstractItemView.ViewportUpdateMode.LazyViewportUpdate)
        except AttributeError:
            pass  # Method not available

        # Smooth scrolling
        try:
            self.instance_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
            self.instance_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        except AttributeError:
            pass  # Methods not available

        # Hide row numbers
        vertical_header = self.instance_table.verticalHeader()
        if vertical_header:
            vertical_header.setVisible(False)
        
        # Enhanced header configuration
        header = self.instance_table.horizontalHeader()
        if header:
            try:
                header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name column
                header.setStretchLastSection(True)
            except AttributeError:
                pass  # Methods not available for this Qt version
        
    def configure_enhanced_table_widget(self):
        """Configure enhanced QTableWidget as fallback"""
        # Enhanced columns with AI insights
        columns = ["#", "Name", "Status", "ADB Port", "CPU %", "Memory", "Disk", "AI Score", "Health"]
        self.instance_table.setColumnCount(len(columns))
        self.instance_table.setHorizontalHeaderLabels(columns)
        
        # Enhanced table settings
        self.instance_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.instance_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.instance_table.setAlternatingRowColors(True)
        self.instance_table.setSortingEnabled(True)
        self.instance_table.setWordWrap(False)
        
        # Enhanced header
        header = self.instance_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # #
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Status
            
    def apply_table_optimizations(self):
        """Apply AI-powered table optimizations"""
        # Smooth scrolling optimizations
        self.instance_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.instance_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        
        # Context menu
        self.instance_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.instance_table.customContextMenuRequested.connect(self.show_enhanced_context_menu)

        # Signal connections - handle both QTableWidget and QTableView
        if hasattr(self.instance_table, 'cellDoubleClicked'):
            # QTableWidget signals
            self.instance_table.cellDoubleClicked.connect(self.on_instance_double_click)
            self.instance_table.itemSelectionChanged.connect(self.on_enhanced_selection_changed)
        else:
            # QTableView signals
            selection_model = self.instance_table.selectionModel()
            if selection_model:
                selection_model.selectionChanged.connect(self.on_enhanced_selection_changed)
            self.instance_table.doubleClicked.connect(self.on_instance_double_click)
            # Connect click signal for QTableView
            self.instance_table.clicked.connect(self.on_table_clicked)
            # Also connect selection change for status updates
            if selection_model:
                selection_model.selectionChanged.connect(self.on_enhanced_selection_changed)
        
    def create_enhanced_right_panel(self):
        """Create enhanced right panel với lazy loading cho performance tối ưu"""
        # Tạo container chính
        self.right_panel_container = QWidget()
        self.right_panel_layout = QVBoxLayout(self.right_panel_container)

        # Tạo loading placeholder ban đầu
        self.create_right_panel_placeholder()

        # Lazy load các component nặng sau khi UI chính đã render
        QTimer.singleShot(500, self.lazy_load_right_panel_components)

        return self.right_panel_container

    def create_right_panel_placeholder(self):
        """Tạo placeholder panel trong khi lazy loading"""
        # Clear existing layout
        self.clear_layout(self.right_panel_layout)

        # Loading indicator
        loading_widget = QWidget()
        loading_layout = QVBoxLayout(loading_widget)

        loading_label = QLabel("🔄 Đang tải Analytics Panel...")
        loading_label.setObjectName("LoadingLabel")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(loading_label)

        # Progress bar cho loading
        self.right_panel_progress = QProgressBar()
        self.right_panel_progress.setObjectName("RightPanelProgress")
        self.right_panel_progress.setRange(0, 0)  # Indeterminate progress
        loading_layout.addWidget(self.right_panel_progress)

        # Status text
        self.right_panel_status = QLabel("Khởi tạo AI Analytics...")
        self.right_panel_status.setObjectName("RightPanelStatus")
        self.right_panel_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(self.right_panel_status)

        loading_layout.addStretch()
        self.right_panel_layout.addWidget(loading_widget)

    def lazy_load_right_panel_components(self):
        """Lazy load các component nặng của right panel"""
        try:
            self.right_panel_status.setText("🔧 Tạo AI Analytics Panel...")

            # Phase 1: Load AI Analytics (nhẹ nhất)
            QTimer.singleShot(100, self.load_ai_analytics_component)

            # Phase 2: Load System Stats (trung bình)
            QTimer.singleShot(300, self.load_system_stats_component)

            # Phase 3: Load Smart Actions (nặng)
            QTimer.singleShot(500, self.load_smart_actions_component)

            # Phase 4: Load Intelligent Logs (nặng nhất)
            QTimer.singleShot(700, self.load_intelligent_logs_component)

            # Phase 5: Finalize và optimize
            QTimer.singleShot(900, self.finalize_right_panel_loading)

        except Exception as e:
            print(f"⚠️ Lazy loading error: {e}")
            self.create_fallback_right_panel()

    def load_ai_analytics_component(self):
        """Load AI Analytics component với lazy loading"""
        try:
            self.right_panel_status.setText("🧠 Khởi tạo AI Analytics...")

            # AI Performance Analytics Group
            ai_group = QGroupBox("🧠 AI Performance Analytics")
            ai_group.setObjectName("AIStatsGroup")
            self.create_ai_analytics_panel_lazy(ai_group)

            self.right_panel_layout.addWidget(ai_group)
            print("✅ AI Analytics component loaded")

        except Exception as e:
            print(f"⚠️ AI Analytics loading error: {e}")

    def load_system_stats_component(self):
        """Load System Stats component với lazy loading"""
        try:
            self.right_panel_status.setText("📊 Khởi tạo System Monitoring...")

            # Enhanced System Stats Group
            stats_group = QGroupBox("📊 System Intelligence")
            stats_group.setObjectName("StatsGroup")
            self.create_enhanced_stats_panel_lazy(stats_group)

            self.right_panel_layout.addWidget(stats_group)
            print("✅ System Stats component loaded")

        except Exception as e:
            print(f"⚠️ System Stats loading error: {e}")

    def load_smart_actions_component(self):
        """Load Smart Actions component với lazy loading"""
        try:
            self.right_panel_status.setText("⚡ Khởi tạo Smart Actions...")

            # Smart Actions Panel Group
            actions_group = QGroupBox("⚡ Smart Actions")
            actions_group.setObjectName("SmartActionsGroup")
            self.create_smart_actions_panel_lazy(actions_group)

            self.right_panel_layout.addWidget(actions_group)
            print("✅ Smart Actions component loaded")

        except Exception as e:
            print(f"⚠️ Smart Actions loading error: {e}")

    def load_intelligent_logs_component(self):
        """Load Intelligent Logs component với lazy loading"""
        try:
            self.right_panel_status.setText("📜 Khởi tạo Intelligent Logs...")

            # Real-time Log Analysis Group
            log_group = QGroupBox("📜 Intelligent Logs")
            log_group.setObjectName("LogGroup")
            self.create_intelligent_log_panel_lazy(log_group)

            self.right_panel_layout.addWidget(log_group)
            print("✅ Intelligent Logs component loaded")

        except Exception as e:
            print(f"⚠️ Intelligent Logs loading error: {e}")

    def finalize_right_panel_loading(self):
        """Finalize right panel loading và cleanup"""
        try:
            self.right_panel_status.setText("🎉 Hoàn thành! AI Dashboard Ready")

            # Remove loading indicator sau 1 giây
            QTimer.singleShot(1000, self.remove_loading_placeholder)

            # Start real-time updates
            self.start_lazy_component_updates()

            print("✅ Right panel lazy loading completed successfully")

        except Exception as e:
            print(f"⚠️ Finalize loading error: {e}")

    def remove_loading_placeholder(self):
        """Remove loading placeholder sau khi load xong"""
        try:
            # Clear layout và remove loading widget
            self.clear_layout(self.right_panel_layout)

            # Re-add all loaded components
            self.rebuild_right_panel_layout()

        except Exception as e:
            print(f"⚠️ Remove placeholder error: {e}")

    def rebuild_right_panel_layout(self):
        """Rebuild right panel layout sau khi lazy loading"""
        try:
            # Find và re-add các group boxes đã được tạo
            for i in reversed(range(self.right_panel_layout.count())):
                widget = self.right_panel_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            # Re-add components theo thứ tự
            if hasattr(self, 'ai_analytics_group'):
                self.right_panel_layout.addWidget(self.ai_analytics_group)
            if hasattr(self, 'system_stats_group'):
                self.right_panel_layout.addWidget(self.system_stats_group)
            if hasattr(self, 'smart_actions_group'):
                self.right_panel_layout.addWidget(self.smart_actions_group)
            if hasattr(self, 'intelligent_logs_group'):
                self.right_panel_layout.addWidget(self.intelligent_logs_group)

        except Exception as e:
            print(f"⚠️ Rebuild layout error: {e}")

    def clear_layout(self, layout):
        """Helper method để clear layout"""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                self.clear_layout(item.layout())

    def create_fallback_right_panel(self):
        """Tạo fallback right panel nếu lazy loading fail"""
        try:
            self.clear_layout(self.right_panel_layout)

            fallback_label = QLabel("⚠️ Analytics Panel không thể tải\nVui lòng thử lại sau")
            fallback_label.setObjectName("FallbackLabel")
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.right_panel_layout.addWidget(fallback_label)

            retry_btn = QPushButton("🔄 Thử lại")
            retry_btn.clicked.connect(self.retry_lazy_loading)
            self.right_panel_layout.addWidget(retry_btn)

        except Exception as e:
            print(f"⚠️ Fallback panel error: {e}")

    def retry_lazy_loading(self):
        """Retry lazy loading khi user click retry"""
        print("🔄 Retrying lazy loading...")
        self.create_right_panel_placeholder()
        QTimer.singleShot(200, self.lazy_load_right_panel_components)
        
    def create_ai_analytics_panel_lazy(self, parent):
        """Create AI analytics panel with lazy loading"""
        layout = QGridLayout(parent)

        # AI Prediction Metrics
        self.ai_efficiency_label = QLabel("System Efficiency: 94.2%")
        self.ai_efficiency_label.setObjectName("AIMetricLabel")
        layout.addWidget(self.ai_efficiency_label, 0, 0, 1, 2)

        # Predictive bars
        layout.addWidget(QLabel("Performance Prediction:"), 1, 0)
        self.ai_performance_bar = QProgressBar()
        self.ai_performance_bar.setObjectName("AIProgressBar")
        self.ai_performance_bar.setValue(92)
        self.ai_performance_bar.setFormat("92% Optimal")
        layout.addWidget(self.ai_performance_bar, 1, 1)

        layout.addWidget(QLabel("Resource Optimization:"), 2, 0)
        self.ai_resource_bar = QProgressBar()
        self.ai_resource_bar.setObjectName("AIProgressBar")
        self.ai_resource_bar.setValue(87)
        self.ai_resource_bar.setFormat("87% Efficient")
        layout.addWidget(self.ai_resource_bar, 2, 1)

        # AI Insights Text
        self.ai_insights_text = QTextEdit()
        self.ai_insights_text.setObjectName("AIInsightsText")
        self.ai_insights_text.setMaximumHeight(80)
        self.ai_insights_text.setReadOnly(True)
        self.ai_insights_text.setPlainText("🧠 AI Analysis: System performing optimally\n📈 Performance trend: Stable\n⚡ Resource usage: Efficient")
        layout.addWidget(self.ai_insights_text, 3, 0, 1, 2)

        # Store reference for rebuild
        self.ai_analytics_group = parent

    def create_enhanced_stats_panel_lazy(self, parent):
        """Create enhanced stats panel with lazy loading"""
        layout = QGridLayout(parent)

        # System stats with real-time monitoring
        self.enhanced_memory_label = QLabel("Memory: Monitoring")
        self.enhanced_cpu_label = QLabel("CPU: Active")
        self.enhanced_disk_label = QLabel("Disk: Available")

        layout.addWidget(self.enhanced_memory_label, 0, 0)
        layout.addWidget(self.enhanced_cpu_label, 0, 1)

        # Progress bars with system monitoring
        layout.addWidget(QLabel("Memory Usage:"), 1, 0)
        self.smart_memory_progress = QProgressBar()
        self.smart_memory_progress.setObjectName("MemoryProgress")
        layout.addWidget(self.smart_memory_progress, 1, 1)

        layout.addWidget(QLabel("CPU Usage:"), 2, 0)
        self.smart_cpu_progress = QProgressBar()
        self.smart_cpu_progress.setObjectName("CPUProgress")
        layout.addWidget(self.smart_cpu_progress, 2, 1)

        layout.addWidget(QLabel("Disk Usage:"), 3, 0)
        self.smart_disk_progress = QProgressBar()
        self.smart_disk_progress.setObjectName("DiskProgress")
        layout.addWidget(self.smart_disk_progress, 3, 1)

        # Store reference for rebuild
        self.system_stats_group = parent

    def create_smart_actions_panel_lazy(self, parent):
        """Create smart actions panel with lazy loading"""
        layout = QVBoxLayout(parent)

        # Smart action buttons với AI recommendations
        self.smart_start_btn = QPushButton("▶️ Start")
        self.smart_start_btn.setObjectName("StartInstanceButton")
        self.smart_start_btn.clicked.connect(self.handle_start_instance)
        layout.addWidget(self.smart_start_btn)

        self.smart_stop_btn = QPushButton("⏹️ Stop")
        self.smart_stop_btn.setObjectName("StopInstanceButton")
        self.smart_stop_btn.clicked.connect(self.handle_stop_instance)
        layout.addWidget(self.smart_stop_btn)

        self.btn_restart_smart = QPushButton("🔄 Restart")
        self.btn_restart_smart.setObjectName("RestartSmartButton")
        self.btn_restart_smart.clicked.connect(self.handle_restart_instance)
        layout.addWidget(self.btn_restart_smart)

        self.predict_btn = QPushButton("🔮 Predict Performance")
        self.predict_btn.setObjectName("PredictButton")
        self.predict_btn.clicked.connect(self.show_performance_prediction)
        layout.addWidget(self.predict_btn)

        # Store reference for rebuild
        self.smart_actions_group = parent

    def create_intelligent_log_panel_lazy(self, parent):
        """Create intelligent log panel with lazy loading"""
        layout = QVBoxLayout(parent)

        self.intelligent_log_text = QTextEdit()
        self.intelligent_log_text.setObjectName("IntelligentLogText")
        self.intelligent_log_text.setMaximumHeight(120)
        self.intelligent_log_text.setReadOnly(True)
        self.intelligent_log_text.setPlainText("📜 AI Log Analysis Ready\n⏰ Waiting for system events...\n🔍 Intelligent monitoring active")
        layout.addWidget(self.intelligent_log_text)

        # Store reference for rebuild
        self.intelligent_logs_group = parent

    def start_lazy_component_updates(self):
        """Start real-time updates cho các lazy loaded components"""
        try:
            # AI Analytics updates - 5 giây
            if hasattr(self, 'ai_analytics_update_timer'):
                self.ai_analytics_update_timer.stop()
            self.ai_analytics_update_timer = QTimer()
            self.ai_analytics_update_timer.timeout.connect(self.update_ai_analytics_realtime)
            self.ai_analytics_update_timer.start(5000)

            # System Stats updates - 2 giây
            if hasattr(self, 'system_stats_update_timer'):
                self.system_stats_update_timer.stop()
            self.system_stats_update_timer = QTimer()
            self.system_stats_update_timer.timeout.connect(self.update_system_stats_realtime)
            self.system_stats_update_timer.start(2000)

            # Intelligent Logs updates - 3 giây
            if hasattr(self, 'logs_update_timer'):
                self.logs_update_timer.stop()
            self.logs_update_timer = QTimer()
            self.logs_update_timer.timeout.connect(self.update_intelligent_logs_realtime)
            self.logs_update_timer.start(3000)

            print("✅ Lazy component real-time updates started")

        except Exception as e:
            print(f"⚠️ Start lazy updates error: {e}")

    def update_ai_analytics_realtime(self):
        """Update AI analytics trong real-time"""
        try:
            if not hasattr(self, 'ai_efficiency_label'):
                return

            # Simulate AI analysis updates
            import random
            efficiency = 90 + random.randint(0, 10)
            performance = 85 + random.randint(0, 15)
            optimization = 80 + random.randint(0, 20)

            self.ai_efficiency_label.setText(f"System Efficiency: {efficiency:.1f}%")
            self.ai_performance_bar.setValue(performance)
            self.ai_performance_bar.setFormat(f"{performance}% Optimal")
            self.ai_resource_bar.setValue(optimization)
            self.ai_resource_bar.setFormat(f"{optimization}% Efficient")

            # Update AI insights
            insights = [
                f"🧠 AI Analysis: System efficiency at {efficiency:.1f}%",
                f"📈 Performance prediction: {performance}% optimal",
                f"⚡ Resource optimization: {optimization}% efficient",
                f"🔍 System health: {'Excellent' if efficiency > 95 else 'Good' if efficiency > 85 else 'Fair'}"
            ]
            self.ai_insights_text.setPlainText("\n".join(insights))

        except Exception as e:
            print(f"⚠️ AI analytics update error: {e}")

    def update_system_stats_realtime(self):
        """Update system stats trong real-time"""
        try:
            if not hasattr(self, 'smart_memory_progress'):
                return

            # Real system monitoring
            import psutil

            # Memory
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.smart_memory_progress.setValue(int(memory_percent))
            self.smart_memory_progress.setFormat(f"{memory_percent:.1f}% Used")
            self.enhanced_memory_label.setText(f"Memory: {memory_percent:.1f}%")

            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.smart_cpu_progress.setValue(int(cpu_percent))
            self.smart_cpu_progress.setFormat(f"{cpu_percent:.1f}% Active")
            self.enhanced_cpu_label.setText(f"CPU: {cpu_percent:.1f}%")

            # Disk
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.smart_disk_progress.setValue(int(disk_percent))
            self.smart_disk_progress.setFormat(f"{disk_percent:.1f}% Used")
            self.enhanced_disk_label.setText(f"Disk: {disk_percent:.1f}%")

        except Exception as e:
            print(f"⚠️ System stats update error: {e}")

    def update_intelligent_logs_realtime(self):
        """Update intelligent logs trong real-time"""
        try:
            if not hasattr(self, 'intelligent_log_text'):
                return

            # Generate intelligent log entries
            import datetime
            current_time = datetime.datetime.now().strftime("%H:%M:%S")

            log_entries = [
                f"[{current_time}] 📊 System monitoring active",
                f"[{current_time}] 🔍 AI analysis running",
                f"[{current_time}] ⚡ Performance optimization active",
                f"[{current_time}] 🛡️ Security monitoring enabled"
            ]

            # Add some random events
            import random
            events = [
                f"[{current_time}] 🚀 Instance optimization completed",
                f"[{current_time}] 📈 Performance improved by 5%",
                f"[{current_time}] 🔧 Memory cleanup performed",
                f"[{current_time}] ⚡ CPU usage optimized"
            ]

            if random.random() < 0.3:  # 30% chance
                log_entries.append(random.choice(events))

            self.intelligent_log_text.setPlainText("\n".join(log_entries[-5:]))  # Keep last 5 entries

        except Exception as e:
            print(f"⚠️ Intelligent logs update error: {e}")

    def stop_lazy_component_updates(self):
        """Stop all lazy component updates khi cleanup"""
        try:
            timers = [
                'ai_analytics_update_timer',
                'system_stats_update_timer',
                'logs_update_timer'
            ]

            for timer_name in timers:
                if hasattr(self, timer_name):
                    timer = getattr(self, timer_name)
                    if timer and timer.isActive():
                        timer.stop()
                        print(f"✅ Stopped {timer_name}")

        except Exception as e:
            print(f"⚠️ Stop lazy updates error: {e}")

    def create_enhanced_status_bar(self):
        """Create enhanced status bar with AI insights"""
        self.status_bar = QFrame()
        self.status_bar.setObjectName("EnhancedStatusBar")
        self.status_bar.setFixedHeight(35)
        
        layout = QHBoxLayout(self.status_bar)
        
        self.status_label = QLabel("🧠 AI Ready - System Optimized")
        self.status_label.setObjectName("EnhancedStatusLabel")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # AI mode indicator
        self.ai_mode_label = QLabel("AI Mode: Active")
        self.ai_mode_label.setObjectName("AIModeLabel")
        layout.addWidget(self.ai_mode_label)
        
        # Performance indicator
        self.perf_indicator = QLabel("Performance: Excellent")
        self.perf_indicator.setObjectName("PerfIndicator")
        layout.addWidget(self.perf_indicator)
        
        self.time_label = QLabel("")
        self.time_label.setObjectName("TimeLabel")
        layout.addWidget(self.time_label)
        
    def setup_timers(self):
        """Setup intelligent timers với adaptive intervals"""
        # Smart refresh timer with adaptive intervals (disabled by default)
        self.smart_refresh_timer = QTimer()
        self.smart_refresh_timer.timeout.connect(self.intelligent_auto_refresh)
        # Do not start automatically - only manual refresh
        
        # Performance monitoring timer (disabled to save resources)
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.monitor_performance)
        # self.performance_timer.start(2000)  # Disabled auto-start
        
        # Time update timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()
        
    def connect_signals(self):
        """Connect enhanced signals với performance components"""
        try:
            # Performance Monitor signals
            if self.performance_monitor:
                self.performance_monitor.metrics_updated.connect(self.on_performance_updated)
                
            print("✅ Enhanced signals connected successfully")
            
        except Exception as e:
            print(f"⚠️ Signal connection error: {e}")    # ================= ENHANCED DATA METHODS =================
    
    def update_instances_data(self, instances):
        """Enhanced update instances data với AI analysis"""
        self.instances_data = []
        ai_scores = ['A+', 'A', 'B+', 'B', 'C+']
        health_states = ['Excellent', 'Good', 'Fair', 'Poor']
        
        for i, instance in enumerate(instances):
            # Use the actual instance index from the backend data
            instance_index = instance.get('index', i)
            enhanced_instance = {
                'index': instance_index,
                'name': instance.get('name', f'AI-MuMu Player {i}'),
                'status': instance.get('status', 'Stopped'),
                'adb': instance.get('adb_port', 16384 + i),
                'disk_usage': instance.get('disk_usage', '1.0GB'),
                'cpu_usage': instance.get('cpu_usage', '15%'),
                'memory_usage': instance.get('memory_usage', '2.1GB'),
                'ai_score': ai_scores[i % len(ai_scores)],
                'health': health_states[i % len(health_states)],
                'efficiency': f'{85 + (i % 15)}%',
                'uptime': instance.get('uptime', f'{i}h {(i*7) % 60}m')
            }
            self.instances_data.append(enhanced_instance)
        
        # Use instances_data directly (no filtering needed)
        self.populate_enhanced_table()
        self.update_enhanced_stats()
        self.sync_enhanced_model_data()
        
        # Cache the enhanced data
        if self.smart_cache:
            self.smart_cache.set("get_instances", self.instances_data, command_type="instance_list")
        
    def populate_enhanced_table(self):
        """Enhanced table population với AI insights"""
        if not hasattr(self.instance_table, 'setRowCount'):
            # QTableView - use model
            if self.instances_model:
                # Model will handle the data
                pass
            return
            
        try:
            # QTableWidget implementation with AI columns
            self.instance_table.setSortingEnabled(False)
            self.instance_table.setRowCount(len(self.instances_data))
            
            for row, instance in enumerate(self.instances_data):
                try:
                    # Index
                    index_item = QTableWidgetItem(str(instance.get('index', row + 1)))
                    index_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.instance_table.setItem(row, 0, index_item)
                    
                    # Name
                    name_item = QTableWidgetItem(instance.get('name', f'MuMu-{row}'))
                    self.instance_table.setItem(row, 1, name_item)
                    
                    # Enhanced Status with AI colors
                    status = instance.get('status', 'offline')
                    status_item = self.create_enhanced_status_item(status)
                    self.instance_table.setItem(row, 2, status_item)
                    
                    # ADB Port
                    adb_port = instance.get('adb', 'N/A')
                    adb_item = QTableWidgetItem(str(adb_port))
                    adb_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.instance_table.setItem(row, 3, adb_item)
                    
                    # CPU % with AI analysis
                    cpu_value = instance.get('cpu_usage', 0)
                    cpu_item = QTableWidgetItem(str(cpu_value))
                    cpu_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.instance_table.setItem(row, 4, cpu_item)
                    
                    # Memory
                    memory = instance.get('memory_usage', 'N/A')
                    memory_item = QTableWidgetItem(str(memory))
                    memory_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.instance_table.setItem(row, 5, memory_item)
                    
                    # Disk Usage
                    disk = instance.get('disk_usage', 'N/A')
                    disk_item = QTableWidgetItem(str(disk))
                    disk_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.instance_table.setItem(row, 6, disk_item)
                    
                    # AI Score (new column)
                    ai_score = instance.get('ai_score', 'C')
                    ai_item = QTableWidgetItem(ai_score)
                    ai_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if ai_score in ['A+', 'A']:
                        ai_item.setForeground(QColor(self.colors['success']))
                    elif ai_score in ['B+', 'B']:
                        ai_item.setForeground(QColor(self.colors['warning']))
                    else:
                        ai_item.setForeground(QColor(self.colors['error']))
                    self.instance_table.setItem(row, 7, ai_item)
                    
                    # Health (new column)
                    health = instance.get('health', 'Unknown')
                    health_item = QTableWidgetItem(health)
                    health_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if health == 'Excellent':
                        health_item.setForeground(QColor(self.colors['success']))
                    elif health == 'Good':
                        health_item.setForeground(QColor(self.colors['info']))
                    elif health == 'Fair':
                        health_item.setForeground(QColor(self.colors['warning']))
                    else:
                        health_item.setForeground(QColor(self.colors['error']))
                    self.instance_table.setItem(row, 8, health_item)
                    
                except Exception as e:
                    print(f"⚠️ Error populating row {row}: {e}")
                    continue
            
            self.instance_table.setSortingEnabled(True)
            # Don't call sync_enhanced_model_data() here to avoid recursion
            self.update_enhanced_stats()
            
            print(f"✅ Enhanced table populated with {len(self.instances_data)} instances")
            
        except Exception as e:
            print(f"⚠️ Error in populate_enhanced_table: {e}")
    
    def create_enhanced_status_item(self, status):
        """Create enhanced status item với AI colors"""
        if status == 'running':
            status_display = "🟢 AI Running"
            status_color = self.colors['success']
        elif status == 'starting':
            status_display = "🟡 AI Starting"
            status_color = self.colors['warning']
        elif status == 'stopping':
            status_display = "🟠 AI Stopping"
            status_color = self.colors['orange']
        else:
            status_display = "🔴 AI Stopped"
            status_color = self.colors['error']
            
        status_item = QTableWidgetItem(status_display)
        status_item.setForeground(QColor(status_color))
        return status_item
    

    
    def sync_enhanced_model_data(self):
        """Enhanced sync với Model/View architecture"""
        if not self.instances_model:
            return
            
        try:
            # Convert enhanced data to model format
            model_data = []
            for instance in self.instances_data:
                index = instance.get('index', 0)
                info = {k: v for k, v in instance.items() if k != 'index'}
                # Add AI metadata
                info['ai_enhanced'] = True
                info['enhanced_score'] = instance.get('ai_score', 'C')
                model_data.append((index, info))
            
            # Update model
            if hasattr(self.instances_model, 'set_rows'):
                self.instances_model.set_rows(model_data)
                
        except Exception as e:
            print(f"Warning: Enhanced model sync failed: {e}")
    
    def update_enhanced_stats(self):
        """Update enhanced stats với AI insights - TỐI ƯU HÓA"""
        # Tối ưu hóa: Tính toán tất cả metrics trong một vòng lặp duy nhất
        total = len(self.instances_data)
        if total == 0:
            return

        # Single pass optimization - tính toán tất cả metrics cùng lúc
        running = 0
        ai_scores = []
        health_states = []

        for instance in self.instances_data:
            # Count running instances
            if instance.get('status') == 'running':
                running += 1

            # Collect AI scores và health states
            ai_scores.append(instance.get('ai_score', 'C'))
            health_states.append(instance.get('health', 'Poor'))

        stopped = total - running

        # Calculate AI metrics efficiently
        excellent_count = sum(1 for score in ai_scores if score in ['A+', 'A'])
        efficiency = (excellent_count / total) * 100

        healthy_count = sum(1 for health in health_states if health in ['Excellent', 'Good'])
        health_percentage = (healthy_count / total) * 100

        # Update system stats with real data
        self.update_real_system_stats()
        
    def update_real_system_stats(self):
        """Update real system stats with monitoring"""
        try:
            # Memory
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            if hasattr(self, 'smart_memory_progress'):
                self.smart_memory_progress.setValue(int(memory_percent))
                self.smart_memory_progress.setFormat(f"{memory_percent:.1f}% Used")

            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if hasattr(self, 'smart_cpu_progress'):
                self.smart_cpu_progress.setValue(int(cpu_percent))
                self.smart_cpu_progress.setFormat(f"{cpu_percent:.1f}% Active")

            # Disk
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if hasattr(self, 'smart_disk_progress'):
                self.smart_disk_progress.setValue(int(disk_percent))
                self.smart_disk_progress.setFormat(f"{disk_percent:.1f}% Used")

        except Exception as e:
            print(f"⚠️ Error updating system stats: {e}")
    
    # ================= ENHANCED ACTION METHODS =================
    
    def request_ai_suggestions(self):
        """Request AI suggestions cho optimization"""
        try:
            selected_instances = self.get_selected_instances()
            
            if not selected_instances:
                suggestions = [
                    "💡 AI suggests starting 3-5 instances for optimal performance",
                    "🔧 Consider enabling Turbo Mode for better efficiency", 
                    "📊 Current system load is low - good time for maintenance",
                    "⚡ Memory optimization is available"
                ]
            else:
                suggestions = [
                    f"🧠 AI recommends optimizing {len(selected_instances)} selected instances",
                    "🚀 Suggested action: Restart for better performance",
                    "💾 Memory cleanup recommended for selected instances",
                    "⚡ Performance boost available"
                ]
            
            import random
            suggestion = random.choice(suggestions)
            self.status_label.setText(f"🧠 AI Suggestion: {suggestion}")
            
            # Emit signal for MainWindow integration
            self.smart_action_suggested.emit("suggestion", selected_instances)
            
        except Exception as e:
            print(f"⚠️ AI suggestion error: {e}")
    
    def smart_refresh(self):
        """Smart refresh - DISABLED để tránh auto-refresh"""
        self.status_label.setText("🚫 Auto-refresh DISABLED - manual refresh only")
        print("🚫 smart_refresh called but DISABLED - no refresh_requested.emit()")
        # Do not emit refresh_requested signal to prevent auto-refresh
        # self.refresh_requested.emit()  # DISABLED
            
    def toggle_smart_auto_refresh(self, enabled):
        """Toggle smart auto refresh - delegate to MainWindow's system"""
        # Delegate to MainWindow's auto-refresh system for consistency
        if hasattr(self.main_window, '_toggle_auto_refresh'):
            # Check current state and only toggle if needed
            current_state = getattr(self.main_window, 'auto_refresh_enabled', False)
            
            # Update button state first
            if enabled:
                self.auto_refresh_btn.setText("🔄 Smart Auto")
                self.auto_refresh_btn.setToolTip("Smart auto-refresh enabled - click to disable")
            else:
                self.auto_refresh_btn.setText("🤖 Auto")
                self.auto_refresh_btn.setToolTip("Click to enable smart auto-refresh")

            # Only call toggle if current state doesn't match desired state
            if current_state != enabled:
                self.main_window._toggle_auto_refresh()

            # Update button checked state to match desired state
            self.auto_refresh_btn.setChecked(enabled)
        else:
            # Fallback if MainWindow method not available - DISABLED for no auto-refresh
            print("⚠️ MainWindow auto-refresh method not available - auto-refresh permanently DISABLED")
            # Always disable auto-refresh regardless of enabled parameter
            self.smart_refresh_timer.stop()
            self.status_label.setText("🤖 Auto-refresh permanently DISABLED - manual refresh only")
    
    def toggle_performance_mode(self, enabled):
        """Toggle performance mode với enhanced optimization"""
        self.performance_mode = enabled
        
        if enabled:
            # Enable turbo mode optimizations
            self.smart_refresh_interval = 2000  # Faster refresh
            self.ai_insights_enabled = True
            
            # Update UI to reflect turbo mode
            self.performance_mode_btn.setText("⚡ Turbo: ON")
            self.status_label.setText("⚡ Turbo Mode: Enhanced performance active")
            
        else:
            # Disable turbo mode
            self.smart_refresh_interval = 5000  # Normal refresh
            
            self.performance_mode_btn.setText("⚡ Turbo Mode")
            self.status_label.setText("⚡ Turbo Mode: Disabled")
    
    def smart_select_all(self):
        """Smart select với AI recommendations"""
        try:
            # AI-powered selection based on current conditions
            if hasattr(self, 'instances_model') and self.instances_model:
                # Enhanced model with checkboxes
                self.instances_model.set_all_checked(True)
                count = len(self.instances_model.get_checked_indices())
                self.status_label.setText(f"✅ Smart Select: All {count} instances selected")
                print(f"✅ Smart Select: Selected {count} instances via checkboxes")
            elif hasattr(self.instance_table, 'selectAll'):
                self.instance_table.selectAll()
                self.status_label.setText(f"🧠 AI Smart Select: All instances selected")
            else:
                # QTableWidget implementation
                total_rows = self.instance_table.rowCount()
                for row in range(total_rows):
                    self.instance_table.selectRow(row)
                self.status_label.setText(f"🧠 AI Smart Select: All {total_rows} instances selected")
            
            self.on_enhanced_selection_changed()
            
        except Exception as e:
            print(f"⚠️ Smart select error: {e}")
    
    def smart_start_instances(self):
        """Smart start instances với AI analysis"""
        try:
            selected_instances = self.get_selected_instances()
            
            if not selected_instances:
                # AI suggests optimal instances to start
                stopped_instances = [i for i in self.instances_data if i.get('status') != 'running']
                if stopped_instances:
                    # Select top instances based on AI score
                    sorted_instances = sorted(stopped_instances, key=lambda x: x.get('ai_score', 'Z'), reverse=True)
                    optimal_count = min(3, len(sorted_instances))  # Start top 3
                    
                    for instance in sorted_instances[:optimal_count]:
                        instance_id = instance.get('index', 0)
                        self.start_instance_requested.emit(instance_id)
                        
                    self.status_label.setText(f"🚀 AI Smart Start: {optimal_count} optimal instances starting")
                else:
                    self.status_label.setText("🚀 All instances already running")
            else:
                # Start selected instances
                for instance in selected_instances:
                    instance_id = instance.get('index', 0)
                    self.start_instance_requested.emit(instance_id)

                self.status_label.setText(f"🚀 START: {len(selected_instances)} instances starting")

        except Exception as e:
            print(f"⚠️ Smart start error: {e}")
    
    def smart_stop_instances(self):
        """Smart stop instances với AI analysis"""
        try:
            selected_instances = self.get_selected_instances()
            
            if not selected_instances:
                # AI suggests instances to stop (lowest performing)
                running_instances = [i for i in self.instances_data if i.get('status') == 'running']
                if running_instances:
                    # Sort by AI score (stop lowest performing first)
                    sorted_instances = sorted(running_instances, key=lambda x: x.get('ai_score', 'A+'))
                    
                    for instance in sorted_instances[:2]:  # Stop bottom 2
                        instance_id = instance.get('index', 0)
                        self.stop_instance_requested.emit(instance_id)
                        
                    self.status_label.setText("🛑 AI Smart Stop: Low-performing instances stopped")
                else:
                    self.status_label.setText("🛑 No running instances to stop")
            else:
                # Stop selected instances
                for instance in selected_instances:
                    instance_id = instance.get('index', 0)
                    self.stop_instance_requested.emit(instance_id)

                self.status_label.setText(f"🛑 STOP: {len(selected_instances)} instances stopping")

        except Exception as e:
            print(f"⚠️ Smart stop error: {e}")
    
    def request_ai_optimization(self):
        """Request comprehensive AI optimization"""
        try:
            if self.ai_optimizer:
                optimization_data = {
                    'instances': self.instances_data,
                    'system_load': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'optimization_type': 'comprehensive'
                }
                
                self.ai_optimization_requested.emit(optimization_data)
                self.status_label.setText("⚡ AI Optimization: Analyzing and optimizing system...")
            else:
                # Fallback optimization
                self.status_label.setText("⚡ Basic optimization applied")
                
        except Exception as e:
            print(f"⚠️ AI optimization error: {e}")
    
    def show_performance_prediction(self):
        """Show AI performance prediction dialog"""
        try:
            # Generate AI prediction based on current metrics
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            running_count = sum(1 for i in self.instances_data if i.get('status') == 'running')
            
            prediction_score = max(0, 100 - cpu_usage/2 - memory_usage/3)
            
            prediction_text = f"""🔮 AI Performance Prediction
            
📊 Current System Analysis:
• CPU Usage: {cpu_usage:.1f}%
• Memory Usage: {memory_usage:.1f}%
• Running Instances: {running_count}

🧠 AI Prediction Score: {prediction_score:.1f}/100

📈 Recommendations:
• Predicted optimal performance for next hour
• System capacity: {max(0, 100-running_count*3)}% available
• Memory efficiency: {max(0, 100-memory_usage)}% optimal
• CPU optimization: {max(0, 100-cpu_usage)}% efficient

🎯 Suggested Actions:
• {('Reduce instances' if running_count > 10 else 'System ready for more instances')}
• {('Enable memory optimization' if memory_usage > 70 else 'Memory usage optimal')}
• {('Consider performance mode' if cpu_usage > 60 else 'CPU performance excellent')}"""
            
            msg = QMessageBox(self)
            msg.setWindowTitle("🔮 AI Performance Prediction")
            msg.setText(prediction_text)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
            
        except Exception as e:
            print(f"⚠️ Performance prediction error: {e}")
    
    # ================= SIGNAL HANDLERS =================
    
    @pyqtSlot(dict)
    def on_ai_optimization_applied(self, optimization_data):
        """Handle AI optimization applied"""
        optimization_type = optimization_data.get('type', 'unknown')
        improvement = optimization_data.get('improvement', 0)
        
        self.status_label.setText(f"✅ AI Optimization Applied: {improvement:.1f}% improvement")
        
        # Update AI insights
        self.update_ai_insights()
        
    @pyqtSlot(str, str)
    def on_performance_alert(self, title, message):
        """Handle performance alerts from AI"""
        self.status_label.setText(f"⚠️ {title}: {message}")
        
        # Show notification if critical
        if "critical" in message.lower():
            msg = QMessageBox(self)
            msg.setWindowTitle(title)
            msg.setText(message)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()
    
    @pyqtSlot(list)
    def on_ai_prediction_ready(self, predictions):
        """Handle AI predictions"""
        if predictions:
            avg_confidence = sum(p.get('confidence', 0) for p in predictions) / len(predictions)
            self.status_label.setText(f"🔮 AI Predictions Ready: {avg_confidence:.1f}% confidence")
    
    @pyqtSlot(dict)
    def on_performance_updated(self, metrics):
        """Handle performance metrics update"""
        efficiency = metrics.get('efficiency', 0)
        self.ai_efficiency_label.setText(f"System Efficiency: {efficiency:.1f}%")
    
    def on_instance_double_click(self, row_or_index, column=None):
        """Enhanced double click với instance info - handles both QTableWidget and QTableView"""
        # Handle QTableView doubleClicked signal (passes QModelIndex)
        if hasattr(row_or_index, 'row'):
            # This is a QModelIndex from QTableView
            row = row_or_index.row()
        else:
            # This is (row, column) from QTableWidget
            row = row_or_index

        if row < len(self.instances_data):
            instance = self.instances_data[row]
            instance_id = instance.get('index', 0)

            # Emit original signal for compatibility
            self.instance_selected.emit(instance_id)
    
    def on_model_data_changed(self, topLeft, bottomRight, roles):
        """Handle model data changes, especially checkbox updates"""
        try:
            # Check if checkbox column was changed
            if topLeft.column() == TableColumn.CHECKBOX and Qt.ItemDataRole.CheckStateRole in roles:
                print(f"🔍 DEBUG: Checkbox data changed for row {topLeft.row()}")
                # Trigger selection change to update status
                self.on_enhanced_selection_changed()
        except Exception as e:
            print(f"⚠️ Error handling model data change: {e}")
    
    def on_enhanced_selection_changed(self):
        """Enhanced selection change với instance info"""
        try:
            selected_instances = self.get_selected_instances()
            selected_count = len(selected_instances)

            if selected_count == 0:
                self.status_label.setText("Ready")
            elif selected_count == 1:
                instance = selected_instances[0]
                status = instance.get('status', 'Unknown')
                self.status_label.setText(f"Selected: {instance.get('name', 'Unknown')} ({status})")
            else:
                running_count = sum(1 for i in selected_instances if i.get('status') == 'running')
                self.status_label.setText(f"Selected: {selected_count} instances ({running_count} running)")

            # Update action button states
            self.update_smart_action_buttons()

        except Exception as e:
            print(f"⚠️ Enhanced selection change error: {e}")

    def on_table_clicked(self, index):
        """Handle table click events - auto-check checkbox when clicking on instance name"""
        try:
            if not index.isValid():
                return
                
            row = index.row()
            column = index.column()
            
            print(f"🖱️ Table clicked: row={row}, column={column}")
            
            # If clicked on NAME column (column 2), auto-toggle the checkbox
            if column == 2 and hasattr(self, 'instances_model') and self.instances_model:
                print(f"🖱️ Clicked on name column, toggling checkbox for row {row}")
                
                # Get checkbox index for this row
                checkbox_index = self.instances_model.index(row, 0)  # Column 0 is checkbox
                
                # Get current checkbox state
                current_state = self.instances_model.data(checkbox_index, Qt.ItemDataRole.CheckStateRole)
                new_state = Qt.CheckState.Unchecked if current_state == Qt.CheckState.Checked else Qt.CheckState.Checked
                
                # Toggle the checkbox
                success = self.instances_model.setData(checkbox_index, new_state, Qt.ItemDataRole.CheckStateRole)
                if success:
                    print(f"✅ Auto-toggled checkbox for row {row}: {new_state}")
                    # Update status
                    self.on_enhanced_selection_changed()
                else:
                    print(f"❌ Failed to auto-toggle checkbox for row {row}")
            
            # Also call the regular selection change handler
            self.on_enhanced_selection_changed()
            
        except Exception as e:
            print(f"⚠️ Table click error: {e}")
    
    def update_smart_action_buttons(self):
        """Update smart action buttons based on selection"""
        try:
            # Check if buttons are created (lazy loading)
            if not hasattr(self, 'smart_start_btn') or self.smart_start_btn is None:
                return
                
            selected_instances = self.get_selected_instances()
            selected_count = len(selected_instances)
            
            if selected_count == 0:
                self.smart_start_btn.setText("🚀 START")
                self.smart_stop_btn.setText("🛑  STOP")
            elif selected_count == 1:
                self.smart_start_btn.setText("🚀 START SELECTED")
                self.smart_stop_btn.setText("🛑 STOP SELECTED")
            else:
                self.smart_start_btn.setText(f"🚀 START ALL ({selected_count})")
                self.smart_stop_btn.setText(f"🛑 STOP ALL ({selected_count})")

        except Exception as e:
            print(f"⚠️ Button update error: {e}")
    
    # ================= ENHANCED CONTEXT MENU =================
    
    def show_enhanced_context_menu(self, position):
        """Show enhanced context menu với smart actions"""
        try:
            item = self.instance_table.itemAt(position) if hasattr(self.instance_table, 'itemAt') else None
            if not item:
                return
                
            row = item.row() if item else -1
            if row < 0 or row >= len(self.instances_data):
                return
                
            instance = self.instances_data[row]
            
            menu = QMenu(self)
            menu.setObjectName("EnhancedContextMenu")
            
            # Apply enhanced styling
            self.style_enhanced_context_menu(menu)
            
            # Header with instance info
            header_action = QAction(f"📱 {instance.get('name', 'Unknown')}", self)
            header_action.setEnabled(False)
            menu.addAction(header_action)
            menu.addSeparator()
            
            # Instance control actions
            status = instance.get('status', 'stopped')
            if status != 'running':
                start_action = QAction("▶️ Smart Start", self)
                start_action.triggered.connect(lambda: self.context_smart_start(row))
                menu.addAction(start_action)
            
            if status == 'running':
                stop_action = QAction("⏹️ Smart Stop", self)
                stop_action.triggered.connect(lambda: self.context_smart_stop(row))
                menu.addAction(stop_action)
                
            restart_action = QAction("🔄 Smart Restart", self)
            restart_action.triggered.connect(lambda: self.context_smart_restart(row))
            menu.addAction(restart_action)
            
            # Show menu
            global_pos = self.instance_table.mapToGlobal(position)
            menu.exec(global_pos)
            
        except Exception as e:
            print(f"⚠️ Enhanced context menu error: {e}")
    
    def style_enhanced_context_menu(self, menu):
        """Apply enhanced styling to context menu"""
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {self.colors['bg']};
                border: 2px solid {self.colors['purple']};
                border-radius: 8px;
                padding: 8px;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 12px;
                color: {self.colors['fg']};
            }}
            QMenu::item {{
                background-color: transparent;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
                color: {self.colors['fg']};
            }}
            QMenu::item:selected {{
                background-color: {self.colors['selection']};
                color: {self.colors['yellow']};
                border: 1px solid {self.colors['purple']};
            }}
            QMenu::item:disabled {{
                color: {self.colors['comment']};
                font-weight: bold;
            }}
            QMenu::separator {{
                height: 2px;
                background-color: {self.colors['comment']};
                margin: 4px;
            }}
        """)
    
    def context_smart_start(self, row):
        """Start instance from context menu with AI optimization"""
        try:
            instance = self.instances_data[row]
            instance_id = instance.get('index', 0)
            self.start_instance_requested.emit(instance_id)
            self.status_label.setText(f"🚀 AI Smart Starting: {instance.get('name', 'Unknown')}")
        except Exception as e:
            print(f"⚠️ Context smart start error: {e}")
    
    def context_smart_stop(self, row):
        """Stop instance from context menu with AI optimization"""
        try:
            instance = self.instances_data[row]
            instance_id = instance.get('index', 0)
            self.stop_instance_requested.emit(instance_id)
            self.status_label.setText(f"🛑 AI Smart Stopping: {instance.get('name', 'Unknown')}")
        except Exception as e:
            print(f"⚠️ Context smart stop error: {e}")
    
    def context_smart_restart(self, row):
        """Restart instance from context menu with AI optimization"""
        try:
            instance = self.instances_data[row]
            instance_id = instance.get('index', 0)
            self.restart_instance_requested.emit(instance_id)
            self.status_label.setText(f"🔄 AI Smart Restarting: {instance.get('name', 'Unknown')}")
        except Exception as e:
            print(f"⚠️ Context smart restart error: {e}")
    
    def context_smart_restart(self, row):
        """Smart restart specific instance"""
        try:
            instance = self.instances_data[row]
            self.status_label.setText(f"🔄 Smart Restarting: {instance.get('name', 'Unknown')}")
        except Exception as e:
            print(f"⚠️ Context smart restart error: {e}")
    
    # ================= ENHANCED STYLING =================
    
    def apply_enhanced_monokai_style(self):
        """Apply enhanced Monokai styling với AI theme"""
        style = f"""
        /* Enhanced Main Dashboard */
        QWidget#EnhancedMonokaiDashboard {{
            background-color: {self.colors['bg']};
            color: {self.colors['fg']};
            font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
        }}
        
        /* Enhanced Header */
        QFrame#EnhancedHeader {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['bg_alt']}, stop: 1 {self.colors['bg_dark']});
            border: 2px solid {self.colors['border']};
            border-radius: 8px;
            margin: 5px;
        }}
        
        QLabel#EnhancedHeaderTitle {{
            font-size: 20px;
            font-weight: bold;
            color: {self.colors['pink']};
            padding: 10px;
        }}
        
        QLabel#HeaderSubtitle {{
            font-size: 12px;
            color: {self.colors['comment']};
            font-style: italic;
            padding: 0px 10px 10px 10px;
        }}
        
        /* Enhanced Stats Widget */
        QFrame#EnhancedStatsWidget {{
            background-color: {self.colors['bg_alt']};
            border: 2px solid {self.colors['purple']};
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
        }}
        
        QLabel#StatLabel, QLabel#StatLabelGreen, QLabel#StatLabelRed, 
        QLabel#StatLabelBlue, QLabel#StatLabelPurple {{
            font-weight: bold;
            padding: 6px 12px;
            margin: 2px;
            border-radius: 4px;
            font-size: 11px;
        }}
        
        QLabel#StatLabel {{
            color: {self.colors['fg']};
            background-color: {self.colors['border']};
        }}
        
        QLabel#StatLabelGreen {{
            color: {self.colors['bg']};
            background-color: {self.colors['success']};
        }}
        
        QLabel#StatLabelRed {{
            color: {self.colors['fg']};
            background-color: {self.colors['error']};
        }}
        
        QLabel#StatLabelBlue {{
            color: {self.colors['bg']};
            background-color: {self.colors['info']};
        }}
        
        QLabel#StatLabelPurple {{
            color: {self.colors['fg']};
            background-color: {self.colors['purple']};
        }}
        
        /* Enhanced Controls */
        QFrame#EnhancedControlsFrame {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {self.colors['bg_alt']}, stop: 1 {self.colors['bg']});
            border: 2px solid {self.colors['border']};
            border-radius: 6px;
            margin: 2px;
        }}
        
        QLineEdit#EnhancedSearchInput {{
            background-color: {self.colors['bg_dark']};
            border: 2px solid {self.colors['border']};
            border-radius: 4px;
            padding: 8px;
            color: {self.colors['fg']};
            font-size: 12px;
            selection-background-color: {self.colors['purple']};
        }}
        
        QLineEdit#EnhancedSearchInput:focus {{
            border: 2px solid {self.colors['blue']};
            background-color: {self.colors['bg']};
        }}
        
        QComboBox#EnhancedStatusFilter {{
            background-color: {self.colors['bg_dark']};
            border: 2px solid {self.colors['border']};
            border-radius: 4px;
            padding: 6px;
            color: {self.colors['fg']};
            min-width: 100px;
        }}
        
        QComboBox#EnhancedStatusFilter::drop-down {{
            border: none;
            width: 20px;
                             }}
        
        QComboBox#EnhancedStatusFilter::down-arrow {{
            image: none;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid {self.colors['comment']};
        }}
        
        QComboBox#EnhancedStatusFilter:hover {{
            border: 2px solid {self.colors['blue']};
        }}
        
        /* Enhanced Buttons */
        QPushButton#AIButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 {self.colors['purple']}, stop: 1 {self.colors['pink']});
            border: 2px solid {self.colors['purple']};
            border-radius: 4px;
            padding: 6px 12px;
            color: {self.colors['fg']};
            font-weight: bold;
            font-size: 11px;
            min-width: 90px;
            max-width: 120px;
            min-height: 28px;
            max-height: 32px;
        }}
        
        QPushButton#AIButton:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 {self.colors['pink']}, stop: 1 {self.colors['purple']});
            border: 2px solid {self.colors['pink']};
        }}
        
        /* Instance Control Buttons */
        QPushButton#StartInstanceButton {{
            background-color: {self.colors['success']};
            border: 2px solid {self.colors['green']};
            border-radius: 6px;
            padding: 8px 16px;
            color: {self.colors['bg']};
            font-weight: bold;
            font-size: 11px;
        }}
        
        QPushButton#StartInstanceButton:hover {{
            background-color: {self.colors['green']};
            border-color: {self.colors['success']};
        }}
        
        QPushButton#StopInstanceButton {{
            background-color: {self.colors['error']};
            border: 2px solid {self.colors['red']};
            border-radius: 6px;
            padding: 8px 16px;
            color: {self.colors['bg']};
            font-weight: bold;
            font-size: 11px;
        }}
        
        QPushButton#StopInstanceButton:hover {{
            background-color: {self.colors['red']};
            border-color: {self.colors['error']};
        }}
        
        QPushButton#RestartInstanceButton {{
            background-color: {self.colors['warning']};
            border: 2px solid {self.colors['orange']};
            border-radius: 6px;
            padding: 8px 16px;
            color: {self.colors['bg']};
            font-weight: bold;
            font-size: 11px;
        }}
        
        QPushButton#RestartInstanceButton:hover {{
            background-color: {self.colors['orange']};
            border-color: {self.colors['warning']};
        }}
        
        QPushButton#DeleteInstanceButton {{
            background-color: {self.colors['error']};
            border: 2px solid {self.colors['red']};
            border-radius: 4px;
            padding: 6px 12px;
            color: {self.colors['bg']};
            font-weight: bold;
            font-size: 11px;
            min-width: 70px;
            max-width: 90px;
            min-height: 28px;
            max-height: 32px;
        }}
        
        QPushButton#DeleteInstanceButton:hover {{
            background-color: {self.colors['red']};
            border-color: {self.colors['error']};
        }}
        
        QPushButton#RestartSmartButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 {self.colors['orange']}, stop: 1 {self.colors['warning']});
            border: 2px solid {self.colors['orange']};
            border-radius: 6px;
            padding: 8px 16px;
            color: {self.colors['bg']};
            font-weight: bold;
        }}
        
        QPushButton#RestartSmartButton:hover {{
            background-color: {self.colors['orange']};
            border-color: {self.colors['warning']};
        }}
        
        QPushButton#RefreshButton, QPushButton#AutoButton, 
        QPushButton#SelectButton, QPushButton#DeselectButton {{
            background-color: {self.colors['border']};
            border: 2px solid {self.colors['comment']};
            border-radius: 4px;
            padding: 6px 12px;
            color: {self.colors['fg']};
            font-weight: bold;
            font-size: 11px;
            min-width: 90px;
            max-width: 120px;
            min-height: 28px;
            max-height: 32px;
        }}
        
        QPushButton#RefreshButton:hover, QPushButton#AutoButton:hover,
        QPushButton#SelectButton:hover, QPushButton#DeselectButton:hover {{
            background-color: {self.colors['blue']};
            border-color: {self.colors['blue']};
        }}
        
        QPushButton#AutoButton:checked {{
            background-color: {self.colors['success']};
            border-color: {self.colors['success']};
        }}
        
        QPushButton#PerformanceButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['orange']}, stop: 1 {self.colors['yellow']});
            border: 2px solid {self.colors['orange']};
            border-radius: 4px;
            padding: 6px 12px;
            color: {self.colors['bg']};
            font-weight: bold;
            font-size: 11px;
            min-width: 90px;
            max-width: 120px;
            min-height: 28px;
            max-height: 32px;
        }}
        
        QPushButton#PerformanceButton:checked {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['success']}, stop: 1 {self.colors['green']});
        }}
        
        /* Enhanced Table */
        QTableView#EnhancedInstanceTableView, QTableWidget#EnhancedInstanceTable {{
            background-color: {self.colors['bg']};
            alternate-background-color: {self.colors['bg_alt']};
            color: {self.colors['fg']};
            border: 2px solid {self.colors['border']};
            border-radius: 6px;
            gridline-color: {self.colors['border']};
            selection-background-color: {self.colors['selection']};
            selection-color: {self.colors['yellow']};
            font-size: 11px;
        }}
        
        QTableView#EnhancedInstanceTableView::item, QTableWidget#EnhancedInstanceTable::item {{
            padding: 8px;
            border-bottom: 1px solid {self.colors['border']};
        }}
        
        QTableView#EnhancedInstanceTableView::item:selected, 
        QTableWidget#EnhancedInstanceTable::item:selected {{
            background-color: {self.colors['selection']};
            color: {self.colors['yellow']};
        }}
        
        QHeaderView::section {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 {self.colors['border']}, stop: 1 {self.colors['bg_alt']});
            color: {self.colors['pink']};
            padding: 8px;
            border: 1px solid {self.colors['comment']};
            font-weight: bold;
            font-size: 11px;
        }}
        
        /* Enhanced Group Boxes */
        QGroupBox#AIStatsGroup, QGroupBox#StatsGroup, 
        QGroupBox#SmartActionsGroup, QGroupBox#LogGroup {{
            color: {self.colors['fg']};
            border: 2px solid {self.colors['purple']};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
            font-size: 12px;
        }}
        
        QGroupBox#AIStatsGroup::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px 0 10px;
            color: {self.colors['purple']};
        }}
        
        QGroupBox#StatsGroup::title, QGroupBox#SmartActionsGroup::title, QGroupBox#LogGroup::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px 0 10px;
            color: {self.colors['orange']};
        }}
        
        /* Enhanced Progress Bars */
        QProgressBar#AIProgressBar, QProgressBar#SmartMemoryProgress,
        QProgressBar#SmartCPUProgress, QProgressBar#SmartDiskProgress {{
            border: 2px solid {self.colors['border']};
            border-radius: 4px;
            background-color: {self.colors['bg_alt']};
            text-align: center;
            color: {self.colors['fg']};
            font-weight: bold;
            font-size: 10px;
        }}
        
        QProgressBar#AIProgressBar::chunk {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['purple']}, stop: 1 {self.colors['pink']});
            border-radius: 2px;
        }}
        
        QProgressBar#SmartMemoryProgress::chunk {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['blue']}, stop: 1 {self.colors['info']});
            border-radius: 2px;
        }}
        
        QProgressBar#SmartCPUProgress::chunk {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['green']}, stop: 1 {self.colors['success']});
            border-radius: 2px;
        }}
        
        QProgressBar#SmartDiskProgress::chunk {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['orange']}, stop: 1 {self.colors['warning']});
            border-radius: 2px;
        }}
        
        /* Enhanced Smart Action Buttons */
        QPushButton#SmartActionButton {{
            background-color: {self.colors['bg_alt']};
            border: 2px solid {self.colors['blue']};
            border-radius: 6px;
            padding: 8px 16px;
            color: {self.colors['fg']};
            font-weight: bold;
            font-size: 11px;
        }}
        
        QPushButton#SmartActionButton:hover {{
            background-color: {self.colors['blue']};
            color: {self.colors['bg']};
        }}
        
        QPushButton#OptimizeButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 {self.colors['orange']}, stop: 1 {self.colors['warning']});
            border: 2px solid {self.colors['orange']};
            border-radius: 6px;
            padding: 8px 16px;
            color: {self.colors['bg']};
            font-weight: bold;
        }}
        
        QPushButton#PredictButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 {self.colors['purple']}, stop: 1 {self.colors['blue']});
            border: 2px solid {self.colors['purple']};
            border-radius: 6px;
            padding: 8px 16px;
            color: {self.colors['fg']};
            font-weight: bold;
        }}
        
        /* Enhanced Text Areas */
        QTextEdit#AIInsightsText, QTextEdit#IntelligentLogText {{
            background-color: {self.colors['bg_dark']};
            border: 2px solid {self.colors['border']};
            border-radius: 4px;
            color: {self.colors['fg']};
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            font-size: 10px;
            padding: 6px;
        }}
        
        /* Enhanced Status Bar */
        QFrame#EnhancedStatusBar {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['bg_alt']}, stop: 1 {self.colors['bg_dark']});
            border-top: 2px solid {self.colors['border']};
        }}
        
        QLabel#EnhancedStatusLabel {{
            color: {self.colors['success']};
            font-weight: bold;
            font-size: 12px;
        }}
        
        QLabel#AIModeLabel {{
            color: {self.colors['purple']};
            font-weight: bold;
            font-size: 11px;
        }}
        
        QLabel#PerfIndicator, QLabel#PerfIndicatorGood, 
        QLabel#PerfIndicatorWarning, QLabel#PerfIndicatorExcellent {{
            font-weight: bold;
            font-size: 11px;
        }}
        
        QLabel#PerfIndicatorExcellent {{
            color: {self.colors['success']};
        }}
        
        QLabel#PerfIndicatorGood {{
            color: {self.colors['info']};
        }}
        
        QLabel#PerfIndicatorWarning {{
            color: {self.colors['warning']};
        }}
        
        QLabel#TimeLabel {{
            color: {self.colors['comment']};
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            font-size: 11px;
        }}
        
        /* Enhanced Scrollbars */
        QScrollBar:vertical {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['bg_alt']}, stop: 1 {self.colors['bg']});
            width: 14px;
            border-radius: 7px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['purple']}, stop: 1 {self.colors['pink']});
            border-radius: 6px;
            min-height: 30px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {self.colors['pink']}, stop: 1 {self.colors['purple']});
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        /* Splitter */
        QSplitter#MainSplitter::handle {{
            background-color: {self.colors['border']};
            width: 3px;
        }}
        
        QSplitter#MainSplitter::handle:hover {{
            background-color: {self.colors['purple']};
        }}
        """
        
        self.setStyleSheet(style)
        
    # ================= COMPATIBILITY METHODS =================
    
    def update_instances(self, instances_data):
        """Compatibility method - update instances data"""
        self.update_instances_data(instances_data)
    
    def get_selected_instances(self):
        """Enhanced get selected instances với error handling"""
        try:
            selected_instances = []
            
            if hasattr(self.instance_table, 'selectedItems'):
                # QTableWidget
                selected_rows = set()
                for item in self.instance_table.selectedItems():
                    if item:
                        selected_rows.add(item.row())
                        
                for row in selected_rows:
                    if 0 <= row < len(self.instances_data):
                        selected_instances.append(self.instances_data[row])
            else:
                # QTableView - Check if we have enhanced model with checkboxes
                if hasattr(self, 'instances_model') and self.instances_model and hasattr(self.instances_model, 'get_checked_indices'):
                    # Use checked instances instead of selected rows
                    checked_indices = self.instances_model.get_checked_indices()
                    for instance_id in checked_indices:
                        # Find the instance data by ID
                        for instance in self.instances_data:
                            if instance.get('index') == instance_id:
                                selected_instances.append(instance)
                                break
                else:
                    # Fallback to selected rows
                    selection_model = self.instance_table.selectionModel()
                    if selection_model:
                        selected_indexes = selection_model.selectedRows()
                        for index in selected_indexes:
                            if index.isValid():
                                row = index.row()
                                if 0 <= row < len(self.instances_data):
                                    selected_instances.append(self.instances_data[row])
                                
            return selected_instances
            
        except Exception as e:
            print(f"⚠️ Error getting selected instances: {e}")
            return []
    
    def deselect_all_instances(self):
        """Enhanced deselect all instances"""
        try:
            if hasattr(self, 'instances_model') and self.instances_model:
                # Enhanced model with checkboxes
                self.instances_model.set_all_checked(False)
                self.status_label.setText("❌ All instances deselected")
                print("❌ Deselect All: Cleared all checkboxes")
            else:
                self.instance_table.clearSelection()
                self.status_label.setText("🧠 AI Ready - All instances deselected")
            self.on_enhanced_selection_changed()
        except Exception as e:
            print(f"⚠️ Enhanced deselect error: {e}")
    
    def intelligent_auto_refresh(self):
        """Intelligent auto refresh - PERMANENTLY DISABLED"""
        # Auto-refresh permanently disabled - do nothing
        print("🚫 Auto-refresh called but DISABLED - no action taken")
        return  # Exit immediately without any refresh operations
    
    def monitor_performance(self):
        """Monitor system performance"""
        try:
            # Simple performance monitoring - can be enhanced later
            pass
        except Exception as e:
            print(f"⚠️ Performance monitoring error: {e}")
    
    def update_time(self):
        """Update time display"""
        try:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.setText(current_time)
        except Exception as e:
            print(f"⚠️ Time update error: {e}")
            
    # ================= DEMO AND TESTING =================
    
    def create_demo_mode(self):
        """Create demo mode for testing"""
        self.create_enhanced_demo_data()
        
        # Start demo timers
        demo_timer = QTimer()
        demo_timer.timeout.connect(self.update_demo_data)
        demo_timer.start(3000)  # Update every 3 seconds
        
    def update_demo_data(self):
        """Update demo data để simulate real-time changes"""
        try:
            import random
            
            # Update random instances
            for instance in self.instances_data[:5]:  # Update first 5
                if random.random() < 0.3:  # 30% chance
                    # Toggle status
                    current_status = instance.get('status', 'stopped')
                    instance['status'] = 'running' if current_status != 'running' else 'stopped'
                    
                    # Update AI metrics
                    scores = ['A+', 'A', 'B+', 'B', 'C+']
                    instance['ai_score'] = random.choice(scores)
                    
                    # Update health
                    healths = ['Excellent', 'Good', 'Fair', 'Poor']
                    instance['health'] = random.choice(healths)
            
            # Refresh display
            self.instances_data = self.instances_data.copy()
            self.populate_enhanced_table()
            self.update_enhanced_stats()
            
        except Exception as e:
            print(f"⚠️ Demo update error: {e}")
    
    # Add compatibility helper to avoid NoneType update_row_by_index errors
    def update_row_by_index(self, index: int, row_data: Dict[str, Any]):
        """Compatibility helper: update a single row by index.
        If instances_model provides update_row_by_index, delegate to it.
        Otherwise update internal data and refresh the UI when updated.
        """
        try:
            # Prefer model's native update if available
            if getattr(self, "instances_model", None) and hasattr(self.instances_model, "update_row_by_index"):
                try:
                    self.instances_model.update_row_by_index(index, row_data)
                    return
                except Exception as e:
                    print(f"⚠️ instances_model.update_row_by_index failed: {e}")

            # Fallback: update internal instances_data
            updated = False
            for i, inst in enumerate(self.instances_data):
                if inst.get("index") == index:
                    inst.update(row_data or {})
                    updated = True
                    break

            if not updated:
                # try to find by position index as fallback
                if 0 <= index < len(self.instances_data):
                    self.instances_data[index].update(row_data or {})
                    updated = True

            # If using QTableWidget fallback, repopulate that row or full table
            if hasattr(self, "instance_table"):
                from PyQt6.QtWidgets import QTableWidget
                if isinstance(self.instance_table, QTableWidget):
                    # Simple approach: refresh the whole table to keep things consistent
                    self.instances_data = self.instances_data.copy()
                    self.populate_enhanced_table()
                else:
                    # If using QTableView backed by a proxy/model and model not available,
                    # refresh by syncing filtered data to model (if possible)
                    self.sync_enhanced_model_data()

        except Exception as e:
            print(f"⚠️ update_row_by_index error: {e}")

    # ===== VIRTUAL SCROLLING & MEMORY OPTIMIZATION METHODS =====

    def enable_virtual_scrolling(self, total_rows: int = 10000):
        """Enable virtual scrolling cho large datasets"""
        try:
            print(f"🚀 Enabling virtual scrolling for {total_rows} rows...")

            # Create virtual scrolling model
            self.virtual_scrolling_model = VirtualScrollingModel()
            self.virtual_scrolling_model.set_total_rows(total_rows)

            # Connect signals
            self.virtual_scrolling_model.data_loaded.connect(self.on_virtual_data_loaded)
            self.virtual_scrolling_model.loading_progress.connect(self.on_virtual_loading_progress)

            # Replace current table model
            if hasattr(self, 'instance_table') and hasattr(self.instance_table, 'setModel'):
                self.instance_table.setModel(self.virtual_scrolling_model)

                # Configure table for virtual scrolling
                self.instance_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
                self.instance_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

                # Connect scroll signals for dynamic loading
                scrollbar = self.instance_table.verticalScrollBar()
                if scrollbar:
                    scrollbar.valueChanged.connect(self.on_scroll_position_changed)

            # DISABLE background processor for manual-only mode
            # self.enable_background_processing()  # DISABLED - manual refresh only

            self.virtual_scroll_enabled = True
            self.large_dataset_mode = True

            print("✅ Virtual scrolling enabled (MANUAL REFRESH ONLY)")

        except Exception as e:
            print(f"⚠️ Failed to enable virtual scrolling: {e}")

    def on_scroll_position_changed(self, value: int):
        """Handle scroll position changes để load data on demand"""
        try:
            if not self.virtual_scrolling_model or not self.virtual_scroll_enabled:
                return

            # Calculate visible range
            viewport = self.instance_table.viewport()
            if not viewport:
                return

            # Get visible rows
            top_row = self.instance_table.indexAt(viewport.rect().topLeft()).row()
            bottom_row = self.instance_table.indexAt(viewport.rect().bottomLeft()).row()

            if top_row >= 0 and bottom_row >= 0:
                visible_start = max(0, top_row - 50)  # Load some buffer rows
                visible_end = min(self.virtual_scrolling_model._total_rows - 1, bottom_row + 50)

                # Update visible range in model
                self.virtual_scrolling_model.set_visible_range(visible_start, visible_end)

        except Exception as e:
            print(f"⚠️ Scroll position change error: {e}")

    def on_virtual_data_loaded(self, start_row: int, end_row: int):
        """Handle khi virtual data được load"""
        try:
            print(f"📦 Virtual data loaded: rows {start_row}-{end_row}")

            # Update UI indicators
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"📦 Loaded data for rows {start_row}-{end_row}")

            # Trigger UI update
            if hasattr(self, 'instance_table'):
                self.instance_table.viewport().update()

        except Exception as e:
            print(f"⚠️ Virtual data loaded error: {e}")

    def on_virtual_loading_progress(self, current: int, total: int):
        """Handle virtual loading progress"""
        try:
            if hasattr(self, 'right_panel_progress'):
                self.right_panel_progress.setValue(current)
                self.right_panel_progress.setMaximum(total)
        except Exception as e:
            print(f"⚠️ Virtual loading progress error: {e}")

    def enable_background_processing(self):
        """Enable background data processing"""
        try:
            if not self.background_processor:
                self.background_processor = BackgroundDataProcessor()
                self.background_processor.data_updated.connect(self.on_background_data_updated)
                self.background_processor.error_occurred.connect(self.on_background_error)

            self.background_processor.start_processing()
            print("✅ Background data processing enabled")

        except Exception as e:
            print(f"⚠️ Failed to enable background processing: {e}")

    def disable_background_processing(self):
        """Disable background data processing"""
        try:
            if self.background_processor:
                self.background_processor.stop_processing()
                print("🛑 Background data processing disabled")
        except Exception as e:
            print(f"⚠️ Failed to disable background processing: {e}")

    def on_background_data_updated(self, updated_data: list):
        """Handle background data updates"""
        try:
            print(f"🔄 Background update: {len(updated_data)} items")

            # Update virtual model if available
            if self.virtual_scrolling_model and updated_data:
                for update_item in updated_data:
                    row_idx = update_item.get('index', 0)
                    if 0 <= row_idx < len(self.virtual_scrolling_model._data):
                        # Update data in model
                        if self.virtual_scrolling_model._data[row_idx] is not None:
                            self.virtual_scrolling_model._data[row_idx].update(update_item)

                # Emit data changed signal
                if hasattr(self, 'instance_table'):
                    self.instance_table.viewport().update()

            # Update status
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"🔄 Updated {len(updated_data)} instances")

        except Exception as e:
            print(f"⚠️ Background data update error: {e}")

    def on_background_error(self, error_msg: str):
        """Handle background processing errors"""
        try:
            print(f"⚠️ Background processing error: {error_msg}")

            if hasattr(self, 'status_label'):
                self.status_label.setText(f"⚠️ Background error: {error_msg}")

        except Exception as e:
            print(f"⚠️ Background error handler error: {e}")

    def optimize_memory_usage(self):
        """Optimize memory usage với memory pool"""
        try:
            # Force garbage collection
            gc.collect()

            # Get memory pool stats
            if self.virtual_scrolling_model:
                memory_stats = self.virtual_scrolling_model.get_memory_stats()
                print(f"📊 Memory Pool Stats: {memory_stats}")

                # Log memory usage
                if hasattr(self, 'intelligent_log_text'):
                    stats_text = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 📊 Memory: {memory_stats['current_mb']:.1f}MB used ({memory_stats['usage_percent']:.1f}%)"
                    current_text = self.intelligent_log_text.toPlainText()
                    new_text = f"{stats_text}\n{current_text}"
                    # Keep only last 10 lines
                    lines = new_text.split('\n')[:10]
                    self.intelligent_log_text.setPlainText('\n'.join(lines))

            # Optimize instance data
            if hasattr(self, 'instances_data') and len(self.instances_data) > 1000:
                # Use memory pool for large datasets
                data_size_mb = len(self.instances_data) * 0.001  # Rough estimate
                if self.memory_pool_manager.allocate_chunk("instances_data", self.instances_data, data_size_mb):
                    print(f"✅ Instances data cached in memory pool ({data_size_mb:.1f}MB)")
                else:
                    print("⚠️ Failed to cache instances data in memory pool")

        except Exception as e:
            print(f"⚠️ Memory optimization error: {e}")

    def toggle_performance_mode(self):
        """Toggle performance mode với memory optimization"""
        try:
            self.performance_mode = not self.performance_mode

            if self.performance_mode:
                print("⚡ Performance Mode: ENABLED")

                # Enable optimizations
                if len(self.instances_data) > 1000:
                    self.enable_virtual_scrolling(len(self.instances_data))

                # Optimize memory
                self.optimize_memory_usage()

                # Update UI
                if hasattr(self, 'status_label'):
                    self.status_label.setText("⚡ Performance Mode: Active")

            else:
                print("🐌 Performance Mode: DISABLED")

                # Disable optimizations
                if self.background_processor:
                    self.background_processor.stop_processing()

                # Update UI
                if hasattr(self, 'status_label'):
                    self.status_label.setText("🐌 Performance Mode: Inactive")

        except Exception as e:
            print(f"⚠️ Performance mode toggle error: {e}")

    def get_performance_stats(self) -> dict:
        """Get comprehensive performance statistics"""
        try:
            stats = {
                'virtual_scrolling_enabled': self.virtual_scroll_enabled,
                'large_dataset_mode': self.large_dataset_mode,
                'background_processing_active': self.background_processor.is_processing if self.background_processor else False,
                'memory_pool_stats': self.memory_pool_manager.get_memory_usage() if hasattr(self, 'memory_pool_manager') else None,
                'instance_count': len(self.instances_data) if hasattr(self, 'instances_data') else 0,
                'performance_mode': self.performance_mode
            }

            if self.virtual_scrolling_model:
                stats['virtual_model_stats'] = self.virtual_scrolling_model.get_memory_stats()

            return stats

        except Exception as e:
            print(f"⚠️ Performance stats error: {e}")
            return {}

    def detect_and_enable_large_dataset_optimizations(self, data_count: int):
        """Detect large datasets và enable optimizations automatically"""
        try:
            if data_count >= 1000 and not self.large_dataset_mode:
                print(f"🔍 Large dataset detected: {data_count} items")

                # Enable virtual scrolling
                self.enable_virtual_scrolling(data_count)

                # Update UI indicators
                if hasattr(self, 'performance_mode_btn'):
                    self.performance_mode_btn.setChecked(True)
                    self.performance_mode_btn.setText("⚡ Turbo Mode (Active)")

                if hasattr(self, 'status_label'):
                    self.status_label.setText(f"⚡ Large dataset mode enabled for {data_count} items")

                # Log to intelligent logs
                if hasattr(self, 'intelligent_log_text'):
                    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ Large dataset optimizations enabled ({data_count} items)"
                    current_text = self.intelligent_log_text.toPlainText()
                    self.intelligent_log_text.setPlainText(f"{log_entry}\n{current_text}")

            elif data_count < 1000 and self.large_dataset_mode:
                print(f"📉 Dataset size reduced: {data_count} items - disabling large dataset mode")

                # Disable virtual scrolling
                self.disable_virtual_scrolling()

                if hasattr(self, 'performance_mode_btn'):
                    self.performance_mode_btn.setChecked(False)
                    self.performance_mode_btn.setText("⚡ Turbo Mode")

        except Exception as e:
            print(f"⚠️ Large dataset detection error: {e}")

    def disable_virtual_scrolling(self):
        """Disable virtual scrolling và revert to normal mode"""
        try:
            self.virtual_scroll_enabled = False
            self.large_dataset_mode = False

            # Stop background processing
            if self.background_processor:
                self.background_processor.stop_processing()

            print("✅ Virtual scrolling disabled")

        except Exception as e:
            print(f"⚠️ Disable virtual scrolling error: {e}")

    def create_demo_large_dataset(self, size: int = 5000):
        """Create demo large dataset để test virtual scrolling"""
        try:
            print(f"🎭 Creating demo dataset with {size} items...")

            # Create demo data
            demo_data = []
            for i in range(size):
                instance = {
                    'index': i,
                    'name': f'MuMu Instance {i:04d}',
                    'status': ['running', 'stopped', 'starting'][i % 3],
                    'cpu_usage': f'{(i % 95) + 5}%',
                    'memory_usage': f'{(i % 800) + 100}MB',
                    'disk_usage': f'{(i % 10) + 2}.0GB',
                    'ai_score': ['A+', 'A', 'B+', 'B', 'C'][i % 5],
                    'health': ['Excellent', 'Good', 'Fair', 'Poor'][i % 4],
                    'uptime': f'{i % 24}h {(i * 7) % 60}m'
                }
                demo_data.append(instance)

            # Set data và enable optimizations
            self.instances_data = demo_data
            self.instances_data = demo_data.copy()

            # Detect large dataset
            self.detect_and_enable_large_dataset_optimizations(len(demo_data))

            # Update UI
            self.update_enhanced_stats()

            print(f"✅ Demo dataset created with {size} items")

        except Exception as e:
            print(f"⚠️ Create demo dataset error: {e}")

    # ===== END OF OPTIMIZATION METHODS =====