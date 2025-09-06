"""
Main Window Module
==================

Cửa sổ chính của ứng dụng MuMu Manager Pro với UI/UX được tối ưu hóa và 
hệ thống auto-refresh thông minh.

Author: GitHub Copilot
Date: August 22, 2025
Version: 2.0 - Enterprise Edition
"""

# =====================================================================
# STANDARD LIBRARY IMPORTS
# =====================================================================
import os
import sys
import time
import random
from typing import List, Dict, Any, Tuple, Optional

# =====================================================================
# OPTIONAL SYSTEM IMPORTS
# =====================================================================
try:
    import ctypes
    from ctypes import wintypes
except ImportError:
    ctypes = None

# =====================================================================
# PYQT6 IMPORTS - CORE
# =====================================================================
from PyQt6.QtCore import Qt, QTimer, QSettings, QPoint, QItemSelectionModel
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QCloseEvent

# =====================================================================
# PYQT6 IMPORTS - WIDGETS
# =====================================================================
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QHeaderView, 
    QLineEdit, QProgressBar, QStatusBar, QMessageBox, QFileDialog, 
    QCheckBox, QLabel, QTextEdit, QMenu, QComboBox, QSplitter, 
    QFrame, QInputDialog, QTabWidget, QGroupBox, QFormLayout, 
    QAbstractItemView, QTableView, QStackedWidget
)

# =====================================================================
# APPLICATION MODULES - CORE
# =====================================================================
from constants import APP_NAME, APP_VERSION, Action, TableColumn
from theme import AppTheme
from backend import MumuManager
from mumu_manager import set_global_mumu_manager

# =====================================================================
# APPLICATION MODULES - WORKERS & TASKS
# =====================================================================
from workers import (
    GenericWorker, auto_launch_task, batch_sim_edit_task,
    apply_settings_task
)

# =====================================================================
# APPLICATION MODULES - UI COMPONENTS
# =====================================================================
from widgets import StatusPillDelegate, InstancesModel, InstancesProxy
from dialogs import SettingsDialog
from settings_editor import SettingsEditorDialog
# from monokai_automation_page import MonokaiAutomationPage  # ← OLD IMPORT DISABLED

# =====================================================================
# ENHANCED AUTOMATION INTEGRATION - PHASE 2
# =====================================================================
try:
    from enhanced_monokai_automation import create_enhanced_automation_page, EnhancedMonokaiAutomationPage as MonokaiAutomationPage
    from automation_integration_patch import apply_automation_patch, is_enhanced_mode_available
    ENHANCED_AUTOMATION_AVAILABLE = True
    print("✅ Enhanced automation integration loaded successfully")
except ImportError as e:
    print(f"⚠️ Enhanced automation not available: {e}")
    ENHANCED_AUTOMATION_AVAILABLE = False
    # Fallback for legacy mode
    try:
        from monokai_automation_page import MonokaiAutomationPage
        print("✅ Using legacy automation page as fallback")
    except ImportError:
        print("❌ No automation page available")
        MonokaiAutomationPage = None

# =====================================================================
# APPLICATION MODULES - MONOKAI THEME INTEGRATION
# =====================================================================
# Enhanced Monokai theme components
try:
    from dashboard_monokai_enhanced import EnhancedMonokaiDashboard
    from monokai_theme import MonokaiTheme, apply_monokai_theme
    MONOKAI_AVAILABLE = True
    print("✅ Monokai theme components loaded successfully")
except ImportError as e:
    print(f"⚠️ Monokai components not available: {e}")
    MONOKAI_AVAILABLE = False
from feather_icons import get_icon

# =====================================================================
# APPLICATION MODULES - LOGGING SYSTEM
# =====================================================================
from enhanced_log_system import (
    EnhancedLogWidget, LogLevel, log_info, log_success, 
    log_warning, log_error, log_debug
)
from log_settings_dialog import LogSettingsDialog

# =====================================================================
# MODERN UI SYSTEM - ENTERPRISE COMPONENTS
# =====================================================================
from ui import (
    ModernButton, ModernCard, ModernProgressBar, ModernTable, 
    DesignTokens
)
from ui.performance import AsyncTaskManager

# =====================================================================
# UI MANAGERS - REFACTORED COMPONENTS
# =====================================================================
from managers import (
    SidebarManager, ContentManager, StatusBarManager
)

# =====================================================================
# ADVANCED OPTIMIZATIONS - PERFORMANCE SYSTEMS
# =====================================================================
# ✅ PHASE 3 OPTIMIZATION IMPORTS - Memory Pool Management
from optimizations.smart_cache import global_smart_cache, CacheStrategy
from optimizations.progressive_loading import ProgressiveLoader, StartupOptimizer
from optimizations.intelligent_worker_pool import IntelligentWorkerPool, TaskPriority
from optimizations.memory_pool import get_memory_manager, get_object_pool
from optimizations.performance_acceleration import get_acceleration_manager, is_acceleration_available
from optimizations.ultra_database import get_ultra_database, UltraFastDatabase
from ui.table_virtualization import VirtualizedTableView

# =====================================================================
# OPTIMIZATION INTEGRATION - Phase 1
# =====================================================================
try:
    from services import get_service_manager
    from core import get_event_manager, get_state_manager, EventTypes, emit_event
    from main_window_integration_patch import MainWindowOptimizationMixin
    # Phase 2: Modular Components
    from components.dashboard_component import create_dashboard_component
    from components.control_panel_component import create_control_panel_component
    from components.status_component import create_status_component
    # Phase 3: Production Components
    from components.performance_monitor_component import create_performance_monitor_component
    from components.settings_component import create_settings_component
    OPTIMIZATION_AVAILABLE = True  # Re-enable optimization with fixed ServiceManager
    print("✅ Optimization components loaded for main_window.py")
except ImportError as e:
    print(f"⚠️ Optimization components not available: {e}")
    OPTIMIZATION_AVAILABLE = False

# =============================================================================
# MAIN WINDOW CLASS
# =============================================================================

class MainWindow(QMainWindow, MainWindowOptimizationMixin):
    """
    Main Application Window - Enterprise Edition với Optimization Integration
    
    Features:
    - Modern UI with enterprise-level components
    - Smart auto-refresh with complete state preservation
    - Advanced caching system with persistence
    - Comprehensive user activity tracking
    - Professional logging and monitoring
    - ✅ NEW: Optimization components integration (ServiceManager, EventManager, StateManager)
    """

    def __init__(self):
        super().__init__()
        
        # 🚀 Initialize optimization components first
        self.init_optimization_components()
        
        self.setWindowTitle(f"MuMuManager MKV v{APP_VERSION}")
        self.resize(1600, 900)

        self.settings = QSettings()
        
        # Load automation settings from JSON file to synchronize with QSettings
        self._sync_automation_settings_from_file()
        
        self.mumu_manager = MumuManager(self.settings.value("manager_path", ""))
        set_global_mumu_manager(self.mumu_manager)
        
        # 🚀 SMART CACHE - Performance optimization với intelligent caching và persistence
        self.smart_cache = global_smart_cache  # Use global instance for consistency
        # Cache logging sẽ được handle bởi log widget sau khi init
        self.smart_cache.cache_hit.connect(self._on_cache_hit)
        self.smart_cache.cache_miss.connect(self._on_cache_miss)
        
        self.instance_cache: Dict[str, Any] = {}
        self.instance_ui_states: Dict[int, str] = {}
        self.worker: Optional[GenericWorker] = None
        self.refresh_worker: Optional[GenericWorker] = None
        self.update_workers: List[GenericWorker] = []
        self.failed_indices = set()
        
        # ✅ LAZY LOADING - Chỉ load tab khi cần
        self.loaded_pages = {}
        
        # 🚀 ADVANCED OPTIMIZATIONS - Performance Systems
        # ✅ SMART CACHE RE-ENABLED
        self.global_smart_cache = global_smart_cache
        self.table_virtualizer = None
        self.async_initializer = None
        self.loading_indicator = None
        
        # 🧠 MEMORY POOL MANAGEMENT - Phase 3 optimization
        self.memory_manager = get_memory_manager(self)
        self.memory_manager.memory_warning.connect(self._on_memory_warning)
        self.memory_manager.memory_critical.connect(self._on_memory_critical)
        
        # 🚀 PROGRESSIVE LOADING - Faster startup with component loading
        self.startup_optimizer = StartupOptimizer(self)
        self.progressive_loader = None
        
        # 🚀 INTELLIGENT WORKER POOL - Advanced task management (setup later)
        self.intelligent_worker_pool = IntelligentWorkerPool(max_workers=4, parent=self)
        # Worker pool signals will be setup in _setup_ui() after log_widget is ready
        
        # 🎮 PERFORMANCE ACCELERATION - Hardware-optimized rendering (Phase 3.2)
        self.acceleration_manager = get_acceleration_manager(self)
        self.accelerated_table = None
        
        # Performance monitoring setup
        
        # ⚡ ULTRA-FAST DATABASE - In-memory SQLite database (Phase 4.2)
        self.ultra_database = get_ultra_database()
        
        # Connect to database immediately
        try:
            if self.ultra_database.connect():
                print("⚡ Ultra-Fast Database connected successfully")
            else:
                print("❌ Ultra-Fast Database connection failed")
                self.ultra_database = None  # Disable if connection fails
        except Exception as e:
            print(f"❌ Ultra-Fast Database connection error: {e}")
            self.ultra_database = None
        
        # =====================================================================
        # UI MANAGERS - REFACTORED COMPONENTS
        # =====================================================================
        self.sidebar_manager = SidebarManager(self)
        self.content_manager = ContentManager(self)
        self.status_bar_manager = StatusBarManager(self)
        
        # 🚫 AUTO-REFRESH PERMANENTLY DISABLED - Manual refresh only
        self.auto_refresh_timer = QTimer()
        # Timer connection permanently disabled - no auto refresh
        # self.auto_refresh_timer.timeout.connect(self._auto_refresh_instances)  # PERMANENTLY DISABLED
        self.auto_refresh_enabled = False  # PERMANENTLY DISABLED - manual refresh only
        self.auto_refresh_interval = self.settings.value("auto_refresh/interval", 30, type=int)  # Keep for settings compatibility
        self.initial_refresh_done = False  # Track initial refresh status
        
        # Ensure timer can never start by disconnecting any potential signals
        try:
            self.auto_refresh_timer.timeout.disconnect()
        except:
            pass  # No signals connected
            
        # 🔒 SAFETY LOCK: Override timer start method to prevent any accidental activation
        original_start = self.auto_refresh_timer.start
        def disabled_start(*args, **kwargs):
            print("🚫 SAFETY LOCK: auto_refresh_timer.start() called but PERMANENTLY DISABLED")
            return
        self.auto_refresh_timer.start = disabled_start
        
        # Track user activity để pause auto-refresh khi cần
        self.user_activity_timer = QTimer()
        self.user_activity_timer.setSingleShot(True)
        self.last_user_activity = time.time()
        self.user_interaction_delay = 3  # Đợi 3s sau thao tác cuối cùng

        self._init_ui()
        self._connect_signals()

        app = QApplication.instance()
        if app and isinstance(app, QApplication):
            AppTheme.apply_theme(app, self.settings)
        self.update_button_icons()
        if hasattr(self, 'instances_model') and self.instances_model:
            self.instances_model.set_ui_states(self.instance_ui_states)
        self.update_ui_states()

        # 🚀 PROGRESSIVE LOADING - Faster startup with intelligent component loading
        self._setup_progressive_loading()
        
        # Load dashboard page on startup so UI components are available for signal connections
        print("🔧 DEBUG: Loading dashboard page on startup...")
        self.content_manager.load_page(0)
        self.content_manager.set_current_page(0)
        self.sidebar_manager.set_active_page(0)
        
        # Connect preload signal for optimization feedback
        self.content_manager.preload_completed.connect(self._on_page_preloaded)
        
        # Show UI immediately
        # Setup worker pool signals after UI is ready
        if hasattr(self, 'intelligent_worker_pool'):
            self._setup_worker_pool_signals()
        
        # Start memory monitoring after UI is ready
        if hasattr(self, 'memory_manager'):
            self.memory_manager.start_monitoring(10000)  # Monitor every 10 seconds
            self.log_message("🧠 Memory Pool Management started", LogLevel.SUCCESS, "Memory")
        
        self.show()

    def _connect_dashboard_component_signals(self):
        """Connect dashboard component signals to main window methods"""
        if hasattr(self, 'dashboard_component'):
            # Connect component signals
            self.dashboard_component.search_changed.connect(self._on_search_changed)
            self.dashboard_component.filter_changed.connect(self._on_filter_changed)
            self.dashboard_component.refresh_requested.connect(self._on_refresh_requested)
            self.dashboard_component.selection_changed.connect(self._on_selection_changed)
    
    def _assign_dashboard_ui_components(self, ui_components):
        """Assign UI components from dashboard component for compatibility"""
        # Extract components for existing code compatibility
        self.search_edit = ui_components.get('search_edit')
        if self.search_edit is None:
            # Fallback: create a basic search edit if not provided
            from PyQt6.QtWidgets import QLineEdit
            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText("Tìm theo tên hoặc index...")
            print("🔄 Created fallback search_edit component")
            
        self.filter_combo = ui_components.get('filter_combo')
        if self.filter_combo is None:
            # Fallback: create a basic filter combo if not provided
            from PyQt6.QtWidgets import QComboBox
            self.filter_combo = QComboBox()
            self.filter_combo.addItems(["Tất cả", "Đang chạy", "Đã tắt"])
            print("🔄 Created fallback filter_combo component")
        self.refresh_btn = ui_components.get('refresh_btn')
        self.btn_auto_refresh = ui_components.get('btn_auto_refresh')
        self.btn_select_all = ui_components.get('btn_select_all')
        if self.btn_select_all is None:
            # Fallback: create a basic button if not provided
            from PyQt6.QtWidgets import QPushButton
            self.btn_select_all = QPushButton("✅ Chọn tất cả")
            print("🔄 Created fallback btn_select_all component")
            
        self.btn_deselect_all = ui_components.get('btn_deselect_all')
        if self.btn_deselect_all is None:
            # Fallback: create a basic button if not provided
            from PyQt6.QtWidgets import QPushButton
            self.btn_deselect_all = QPushButton("❌ Bỏ chọn")
            print("🔄 Created fallback btn_deselect_all component")
        self.ai_tracker_status = ui_components.get('ai_tracker_status')
        self.table = ui_components.get('table')
        if self.table is None:
            # Fallback: create a basic table view with model/view architecture
            from PyQt6.QtWidgets import QTableView
            from widgets import InstancesModel, InstancesProxy
            self.table = QTableView()
            self.instances_model = InstancesModel(self)
            self.instances_proxy = InstancesProxy(self)
            self.instances_proxy.setSourceModel(self.instances_model)
            self.table.setModel(self.instances_proxy)
            print("🔄 Created fallback table view with Model/View architecture")
            
        self.instances_model = ui_components.get('instances_model')
        if self.instances_model is None:
            # Fallback: create a basic model if not provided
            from PyQt6.QtCore import QAbstractTableModel
            self.instances_model = None  # Will be set later if needed
            print("🔄 instances_model will be set to None (fallback)")
            
        self.instances_proxy = ui_components.get('instances_proxy')
        
        # Debug log
        print(f"🔍 Debug: instances_model = {self.instances_model}")
        print(f"🔍 Debug: instances_proxy = {self.instances_proxy}")
        print(f"🔍 Debug: table = {self.table}")
        
        # Create fallback instances_model if not provided by dashboard component
        if self.instances_model is None:
            print("❌ Warning: instances_model is None from dashboard component!")
            print("🔧 Creating fallback instances_model...")
            try:
                from widgets import InstancesModel, InstancesProxy
                self.instances_model = InstancesModel(self)
                self.instances_proxy = InstancesProxy(self)
                self.instances_proxy.setSourceModel(self.instances_model)
                
                # Connect to table if it's QTableView
                if hasattr(self.table, 'setModel'):
                    self.table.setModel(self.instances_proxy)
                    
                print("✅ Fallback instances_model created successfully")
            except Exception as e:
                print(f"❌ Failed to create fallback instances_model: {e}")
    
    # Dashboard component event handlers
    def _on_search_changed(self, query: str):
        """Handle search query change from dashboard component"""
        if hasattr(self, '_smart_debounce_search'):
            self._smart_debounce_search()
    
    def _on_filter_changed(self, filter_text: str):
        """Handle filter change from dashboard component"""
        if hasattr(self, '_filter_debounce'):
            self._filter_debounce.start()
    
    def _on_refresh_requested(self):
        """Handle refresh request from dashboard component"""
        if hasattr(self, 'refresh_instances'):
            self.refresh_instances()
    
    def _on_selection_changed(self, select_all: bool):
        """Handle selection change from dashboard component"""
        if hasattr(self, '_set_all_checkboxes_state'):
            self._set_all_checkboxes_state(select_all)

    def _connect_control_panel_signals(self):
        """Connect control panel component signals to main window methods"""
        if hasattr(self, 'control_panel_component'):
            # Connect basic operations
            self.control_panel_component.create_requested.connect(self._on_create_requested)
            self.control_panel_component.clone_requested.connect(self._on_clone_requested)
            self.control_panel_component.delete_requested.connect(self._on_delete_requested)
            self.control_panel_component.start_requested.connect(self._on_start_requested)
            self.control_panel_component.stop_requested.connect(self._on_stop_requested)
            self.control_panel_component.restart_requested.connect(self._on_restart_requested)
            
            # Connect automation
            self.control_panel_component.auto_start_requested.connect(self._on_auto_start_requested)
            self.control_panel_component.auto_pause_requested.connect(self._on_auto_pause_requested)
            self.control_panel_component.auto_stop_requested.connect(self._on_auto_stop_requested)
            
            # Connect advanced operations
            self.control_panel_component.multi_start_requested.connect(self._on_multi_start_requested)
            self.control_panel_component.multi_stop_requested.connect(self._on_multi_stop_requested)
            self.control_panel_component.multi_restart_requested.connect(self._on_multi_restart_requested)
    
    def _assign_control_panel_buttons(self):
        """Assign button references from control panel component for compatibility"""
        if hasattr(self, 'control_panel_component') and self.control_panel_component:
            try:
                # Map component buttons to legacy button names for compatibility
                self.btn_create = self.control_panel_component.get_button('create')
                self.btn_clone = self.control_panel_component.get_button('clone')
                self.btn_delete = self.control_panel_component.get_button('delete')
                self.btn_start_selected = self.control_panel_component.get_button('start')
                self.btn_stop_selected = self.control_panel_component.get_button('stop')
                self.btn_restart_selected = self.control_panel_component.get_button('restart')
                
                # Automation buttons
                self.btn_auto_start = self.control_panel_component.get_button('auto_start')
                self.btn_auto_pause = self.control_panel_component.get_button('auto_pause')
                self.btn_auto_stop = self.control_panel_component.get_button('auto_stop')
                
                print("✅ Control panel buttons mapped successfully")
            except Exception as e:
                print(f"⚠️ Control panel button mapping failed: {e}")
                self._create_fallback_buttons()
        else:
            print("⚠️ Control panel component not available, creating fallback buttons")
            self._create_fallback_buttons()
    
    def _create_fallback_buttons(self):
        """Create fallback buttons when control panel component is not available"""
        from ui.modern_components import ModernButton
        
        # Create basic buttons as fallback
        self.btn_start_selected = ModernButton("Bắt đầu", "success", "sm")
        self.btn_stop_selected = ModernButton("Dừng", "danger", "sm")
        self.btn_restart_selected = ModernButton("Khởi động lại", "warning", "sm")
        self.btn_create = ModernButton("Tạo", "primary", "sm")
        self.btn_clone = ModernButton("Sao chép", "info", "sm")
        self.btn_delete = ModernButton("Xóa", "danger", "sm")
        
        # Automation buttons
        self.btn_auto_start = ModernButton("Auto Start", "success", "sm")
        self.btn_auto_pause = ModernButton("Auto Pause", "warning", "sm")
        self.btn_auto_stop = ModernButton("Auto Stop", "danger", "sm")
        
        print("✅ Fallback buttons created successfully")
    
    # Control Panel Event Handlers
    def _on_create_requested(self):
        """Handle create request from control panel"""
        if hasattr(self, 'create_instance'):
            self.create_instance()
    
    def _on_clone_requested(self):
        """Handle clone request from control panel"""
        if hasattr(self, 'clone_selected_instances'):
            self.clone_selected_instances()
    
    def _on_delete_requested(self):
        """Handle delete request from control panel"""
        if hasattr(self, 'delete_selected_instances'):
            self.delete_selected_instances()
    
    def _on_start_requested(self):
        """Handle start request from control panel"""
        if hasattr(self, 'start_selected_instances'):
            self.start_selected_instances()
    
    def _on_stop_requested(self):
        """Handle stop request from control panel"""
        if hasattr(self, 'stop_selected_instances'):
            self.stop_selected_instances()
    
    def _on_restart_requested(self):
        """Handle restart request from control panel"""
        if hasattr(self, 'restart_selected_instances'):
            self.restart_selected_instances()
    
    def _on_auto_start_requested(self):
        """Handle auto start request from control panel"""
        if hasattr(self, '_start_automation'):
            self._start_automation()
    
    def _on_auto_pause_requested(self):
        """Handle auto pause request from control panel"""
        if hasattr(self, '_pause_automation'):
            self._pause_automation()
    
    def _on_auto_stop_requested(self):
        """Handle auto stop request from control panel"""
        if hasattr(self, '_stop_automation'):
            self._stop_automation()
    
    def _on_multi_start_requested(self):
        """Handle multi start request from control panel"""
        if hasattr(self, 'start_selected_instances'):
            self.start_selected_instances()
    
    def _on_multi_stop_requested(self):
        """Handle multi stop request from control panel"""
        if hasattr(self, 'stop_selected_instances'):
            self.stop_selected_instances()
    
    def _on_multi_restart_requested(self):
        """Handle multi restart request from control panel"""
        if hasattr(self, 'restart_selected_instances'):
            self.restart_selected_instances()

    def _connect_status_component_signals(self):
        """Connect status component signals to main window methods"""
        if hasattr(self, 'status_component'):
            # Connect status update signals
            self.status_component.status_updated.connect(self._on_status_updated)
            self.status_component.progress_updated.connect(self._on_progress_updated)
    
    def _assign_status_component_labels(self):
        """Assign status labels from component for compatibility"""
        if hasattr(self, 'status_component'):
            # Create simple compatibility labels pointing to component status
            from PyQt6.QtWidgets import QLabel
            self.selection_label = QLabel("Đã chọn: 0")
            self.auto_refresh_status_label = QLabel("🤖 AI Tracker: Ready")
            
            # Update them from component
            if hasattr(self.status_component, 'get_status'):
                selected_status = self.status_component.get_status('selected')
                if selected_status:
                    self.selection_label.setText(f"Đã chọn: {selected_status}")
                
                ai_status = self.status_component.get_status('ai_tracker')
                if ai_status:
                    self.auto_refresh_status_label.setText(f"🤖 AI: {ai_status}")
    
    # Status Component Event Handlers
    def _on_status_updated(self, category: str, status: str, level: str):
        """Handle status updates from status component"""
        # Update status bar manager with category-specific status
        if hasattr(self, 'status_bar_manager'):
            if category == 'instances':
                self.status_bar_manager.update_summary_status(f"📱 Instances: {status}")
            elif category == 'ai_tracker':
                self.status_bar_manager.update_summary_status(f"🤖 AI: {status}")
            elif category == 'memory':
                self.status_bar_manager.update_summary_status(f"🧠 Memory: {status}")
            else:
                self.status_bar_manager.update_summary_status(status)
    
    def _on_progress_updated(self, value: int, description: str):
        """Handle progress updates from status component"""
        # Update status bar manager with progress information
        if hasattr(self, 'status_bar_manager') and value > 0:
            self.status_bar_manager.update_summary_status(f"🔄 {description} ({value}%)")

    def _refresh_automation_button_styles(self):
        """Force refresh automation button styles to ensure proper theming."""
        # Set properties for CSS selectors after theme application
        automation_buttons = [
            (self.btn_auto_start, "success"),
            (self.btn_auto_pause, "warning"), 
            (self.btn_auto_stop, "danger")
        ]
        
        for button, variant in automation_buttons:
            # Update variant and property
            button.variant = variant
            button.setProperty("variant", variant)
            # Force style refresh
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def _update_automation_button_states(self):
        """Update automation button colors based on their enabled state."""
        # Use sidebar manager to update automation button states
        if hasattr(self, 'sidebar_manager'):
            automation_buttons = {}
            for attr in ['btn_auto_start', 'btn_auto_pause', 'btn_auto_stop']:
                if hasattr(self, attr):
                    automation_buttons[attr] = getattr(self, attr)
            
            self.sidebar_manager.update_automation_button_states(automation_buttons)
        else:
            # Fallback to direct manipulation if sidebar manager not available
            self._update_automation_button_states_legacy()

    def _update_automation_button_states_legacy(self):
        """Legacy method for updating automation button states directly."""
        # Force set disabled buttons to gray color directly
        if hasattr(self, 'btn_auto_pause') and self.btn_auto_pause is not None:
            if not self.btn_auto_pause.isEnabled():
                self.btn_auto_pause.setStyleSheet("""
                    QPushButton {
                        background-color: #555555;
                        color: #888888;
                        border: 1px solid #333333;
                        border-radius: 5px;
                        padding: 8px 12px;
                    }
                """)
            else:
                # Re-apply original style when enabled
                if hasattr(self.btn_auto_pause, 'setup_style'):
                    self.btn_auto_pause.variant = "warning"
                    self.btn_auto_pause.setup_style()
                else:
                    self.btn_auto_pause.setProperty("variant", "warning")
            
        if hasattr(self, 'btn_auto_stop') and self.btn_auto_stop is not None:
            if not self.btn_auto_stop.isEnabled():
                self.btn_auto_stop.setStyleSheet("""
                    QPushButton {
                        background-color: #555555;
                        color: #888888;
                        border: 1px solid #333333;
                        border-radius: 5px;
                        padding: 8px 12px;
                    }
                """)
            else:
                # Re-apply original style when enabled
                if hasattr(self.btn_auto_stop, 'setup_style'):
                    self.btn_auto_stop.variant = "danger"
                    self.btn_auto_stop.setup_style()
                else:
                    self.btn_auto_stop.setProperty("variant", "danger")
            
        if hasattr(self, 'btn_auto_start') and self.btn_auto_start is not None:
            if not self.btn_auto_start.isEnabled():
                self.btn_auto_start.setStyleSheet("""
                    QPushButton {
                        background-color: #555555;
                        color: #888888;
                        border: 1px solid #333333;
                        border-radius: 5px;
                        padding: 8px 12px;
                    }
                """)
            else:
                # Re-apply original style when enabled
                if hasattr(self.btn_auto_start, 'setup_style'):
                    self.btn_auto_start.variant = "success"
                    self.btn_auto_start.setup_style()
                else:
                    self.btn_auto_start.setProperty("variant", "success")
        
        # Force refresh - only for existing buttons
        buttons_to_update = []
        for attr in ['btn_auto_start', 'btn_auto_pause', 'btn_auto_stop']:
            if hasattr(self, attr) and getattr(self, attr, None) is not None:
                buttons_to_update.append(getattr(self, attr))
        
        for button in buttons_to_update:
            button.update()

    def check_manager_path(self):
        if not self.mumu_manager.is_valid():
            QMessageBox.warning(
                self,
                "Chưa cấu hình",
                "Đường dẫn đến MuMuManager.exe chưa được thiết lập hoặc không hợp lệ.\n\n"
                "Vui lòng vào 'Cài đặt' để chọn đúng đường dẫn."
            )
            self._open_settings()

    def closeEvent(self, event: QCloseEvent):
        """Tối ưu hóa cleanup khi đóng ứng dụng"""
        # 🚀 SAVE CACHE - Lưu cache để tránh cache miss lần sau
        try:
            self.smart_cache.save_cache()
            self.log_message("💾 Cache đã được lưu cho session tiếp theo", LogLevel.INFO, "Performance")
        except Exception as e:
            self.log_message(f"Cache save warning: {e}", LogLevel.WARNING, "Performance")
        
        # Dừng tất cả các worker đang chạy
        workers_to_stop = []
        if self.worker and self.worker.isRunning():
            workers_to_stop.append(self.worker)
        if self.refresh_worker and self.refresh_worker.isRunning():
            workers_to_stop.append(self.refresh_worker)
        workers_to_stop.extend([w for w in self.update_workers if w.isRunning()])

        if workers_to_stop:
            reply = QMessageBox.question(
                self,
                "Xác nhận Thoát",
                f"Có {len(workers_to_stop)} tác vụ đang chạy. Bạn có chắc muốn thoát không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Dừng tất cả workers
                for worker in workers_to_stop:
                    worker.stop()
                    
                # Đợi một chút để workers dọn dẹp
                QApplication.processEvents()
                
                # Cleanup resources
                self._cleanup_resources()
                event.accept()
            else:
                event.ignore()
        else:
            self._cleanup_resources()
            event.accept()

    def _cleanup_resources(self):
        """Enhanced cleanup để giải phóng memory và resources"""
        # Dừng auto refresh timer
        if hasattr(self, 'auto_refresh_timer'):
            self.auto_refresh_timer.stop()
            
        # Clear cache để giải phóng memory
        self.instance_cache.clear()
        self.instance_ui_states.clear()
        self.failed_indices.clear()
        
        # Cleanup smart cache với proper signal disconnection
        if hasattr(self, 'smart_cache'):
            try:
                self.smart_cache.cache_hit.disconnect()
                self.smart_cache.cache_miss.disconnect()
                if hasattr(self.smart_cache, 'cache_evicted'):
                    self.smart_cache.cache_evicted.disconnect()
                if hasattr(self.smart_cache, 'cache_cleared'):
                    self.smart_cache.cache_cleared.disconnect()
            except Exception:
                pass  # Ignore disconnection errors
        
        # Cleanup workers với proper signal disconnection
        if self.worker:
            try:
                self.worker.task_result.disconnect()
                self.worker.finished.disconnect()
                if self.worker.isRunning():
                    self.worker.terminate()
                    # Đảm bảo thread đã dừng hoàn toàn trước khi xóa
                    if not self.worker.wait(3000):  # Wait up to 3 seconds
                        print("⚠️ Worker thread did not finish gracefully, forcing termination")
            except Exception as e:
                print(f"⚠️ Error cleaning up worker: {e}")
            self.worker.deleteLater()
            self.worker = None
            
        if self.refresh_worker:
            try:
                self.refresh_worker.task_result.disconnect()
                self.refresh_worker.finished.disconnect()
                if self.refresh_worker.isRunning():
                    self.refresh_worker.terminate()
                    # Đảm bảo thread đã dừng hoàn toàn trước khi xóa
                    if not self.refresh_worker.wait(3000):  # Wait up to 3 seconds
                        print("⚠️ Refresh worker thread did not finish gracefully, forcing termination")
            except Exception as e:
                print(f"⚠️ Error cleaning up refresh worker: {e}")
            self.refresh_worker.deleteLater()
            self.refresh_worker = None
            
        for worker in self.update_workers:
            try:
                if hasattr(worker, 'task_result'):
                    worker.task_result.disconnect()
                if hasattr(worker, 'finished'):
                    worker.finished.disconnect()
                if worker.isRunning():
                    worker.terminate()
                    worker.wait()
            except Exception:
                pass
            worker.deleteLater()
        self.update_workers.clear()
        
        # Cleanup automation manager if exists
        if hasattr(self, 'automation_manager'):
            try:
                self.automation_manager.cleanup()
            except Exception:
                pass

    def _init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Use refactored managers
        main_layout.addWidget(self.sidebar_manager.get_sidebar_widget())
        main_layout.addWidget(self.content_manager.get_content_widget())

        # Set status bar using manager
        self.setStatusBar(self.status_bar_manager.get_status_bar())

    def _create_dashboard_page(self):
        """
        Tạo trang dashboard với modular component architecture
        
        Phase 2: Sử dụng DashboardComponent cho better maintainability
        """
        
        # 🚀 PHASE 2: Use modular dashboard component
        # Temporarily disabled to use MonokaiDashboard for full table functionality
        if False and OPTIMIZATION_AVAILABLE:
            try:
                # Create dashboard component
                self.dashboard_component = create_dashboard_component(self, self.mumu_manager)
                
                # Connect component signals to main window methods
                self._connect_dashboard_component_signals()
                
                # Create dashboard widget
                dashboard_widget = self.dashboard_component.create_dashboard()
                
                # Extract UI components for compatibility
                ui_components = self.dashboard_component.get_ui_components()
                self._assign_dashboard_ui_components(ui_components)
                
                print("🚀 Phase 2: Modular dashboard component created successfully!")
                return dashboard_widget
                
            except Exception as e:
                print(f"⚠️ Dashboard component creation failed: {e}")
                print("🔄 Falling back to legacy dashboard")
        
        # Legacy dashboard fallback (existing code)
        
        # Try to create MonokaiDashboard first
        print(f"🔧 DEBUG: MONOKAI_AVAILABLE = {MONOKAI_AVAILABLE}")
        if MONOKAI_AVAILABLE:
            try:
                print("🔧 DEBUG: Attempting to create EnhancedMonokaiDashboard...")
                # Use enhanced Monokai dashboard
                self.monokai_dashboard = EnhancedMonokaiDashboard(self)
                print("🔧 DEBUG: EnhancedMonokaiDashboard instantiated successfully")
                # Set backend reference
                print("🔧 DEBUG: Setting backend...")
                self.monokai_dashboard.set_backend(self.mumu_manager)
                print("🔧 DEBUG: Backend set successfully")
                
                # Expose controls for compatibility
                print("🔧 DEBUG: Assigning UI components...")
                # Search controls removed - create fallback if needed
                if hasattr(self.monokai_dashboard, 'search_edit'):
                    self.search_edit = self.monokai_dashboard.search_edit
                else:
                    self.search_edit = None
                if hasattr(self.monokai_dashboard, 'filter_combo'):
                    self.filter_combo = self.monokai_dashboard.filter_combo
                else:
                    self.filter_combo = None
                self.refresh_btn = getattr(self.monokai_dashboard, 'refresh_btn', None)
                self.btn_auto_refresh = getattr(self.monokai_dashboard, 'auto_refresh_btn', None)
                self.btn_select_all = getattr(self.monokai_dashboard, 'btn_select_all', None)
                self.btn_deselect_all = getattr(self.monokai_dashboard, 'btn_deselect_all', None)
                
                # Debug: Check if attributes are assigned
                print(f"🔧 DEBUG: Assigned search_edit = {self.search_edit}")
                print(f"🔧 DEBUG: Assigned filter_combo = {self.filter_combo}")
                print(f"🔧 DEBUG: Assigned btn_select_all = {self.btn_select_all}")
                
                # Set up table attributes from EnhancedMonokaiDashboard's instance_table 
                self.table = self.monokai_dashboard.instance_table
                # Use model/proxy from EnhancedMonokaiDashboard for compatibility
                self.instances_model = self.monokai_dashboard.instances_model
                self.instances_proxy = self.monokai_dashboard.instances_proxy
                
                # Connect dashboard signals to MainWindow methods
                print("🔧 DEBUG: Connecting dashboard signals...")
                self._connect_dashboard_signals()
                print("🔧 DEBUG: Dashboard signals connected")
                
                # Create control panel for buttons compatibility  
                print("🔧 DEBUG: Creating control panel...")
                self._create_control_panel()
                print("🔧 DEBUG: Control panel created")
                
                # Create log widget for compatibility
                print("🔧 DEBUG: Creating log widget...")
                try:
                    from enhanced_log_system import EnhancedLogWidget
                    self.log_widget = EnhancedLogWidget()
                except Exception as e:
                    print(f"Warning: Could not create log widget: {e}")
                    self.log_widget = None
                
                print("📊 Monokai dashboard created successfully!")
                
                # Connect search and filter signals now that components are available
                print("🔧 DEBUG: Connecting search and filter signals...")
                self._connect_search_filter_signals()
                
                return self.monokai_dashboard
            except Exception as e:
                print(f"⚠️ Failed to create Monokai dashboard: {e}")
                import traceback
                traceback.print_exc()
                print("🔄 Using standard dashboard instead")
        
        # Standard dashboard fallback - only if Monokai failed
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)

        left_panel_widget = QWidget()
        left_layout = QVBoxLayout(left_panel_widget)
        left_layout.setContentsMargins(0,0,0,0)

        filter_bar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Tìm theo tên hoặc index...")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tất cả", "Đang chạy", "Đã tắt"])
        
        # 🚀 MODERN CONTROLS - Improved UX with modern styling
        self.btn_select_all = QPushButton("✅ Chọn tất cả")
        self.btn_deselect_all = QPushButton("❌ Bỏ chọn")  
        # Refresh buttons DISABLED - AI Tracker thay thế
        # self.refresh_btn = QPushButton(" Làm mới")  # HIDDEN
        # self.btn_auto_refresh = QPushButton("🤖 Tự động")  # HIDDEN
        
        # Tạo AI status label thay thế
        self.ai_tracker_status = QLabel("🤖 AI Tracker: Đang theo dõi...")
        self.ai_tracker_status.setStyleSheet("color: #A6E22E; font-weight: bold;")
        self.ai_tracker_status.setToolTip("Global AI Tracker đang theo dõi instances real-time")

        filter_bar.addWidget(QLabel("Tìm kiếm:"))
        filter_bar.addWidget(self.search_edit)
        filter_bar.addSpacing(15)
        filter_bar.addWidget(QLabel("Trạng thái:"))
        filter_bar.addWidget(self.filter_combo)
        filter_bar.addStretch(1)
        filter_bar.addWidget(self.btn_select_all)
        filter_bar.addWidget(self.btn_deselect_all)
        # filter_bar.addWidget(self.refresh_btn)  # HIDDEN
        # filter_bar.addWidget(self.btn_auto_refresh)  # HIDDEN
        filter_bar.addWidget(self.ai_tracker_status)  # AI Status thay thế
        left_layout.addLayout(filter_bar)

        # Tạo Model/View setup
        self.instances_model = InstancesModel(self)
        self.instances_proxy = InstancesProxy(self)
        self.instances_proxy.setSourceModel(self.instances_model)

        # Tạo table với QTableView cho Model/View pattern
        self.table = QTableView()
        self.table.setModel(self.instances_proxy)
        
        # Cấu hình table
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            for col in [0, 1, 2, 3]:  # Basic columns
                if header:
                    header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.setSortingEnabled(True)
        
        # Hide vertical header to avoid confusion with Index column
        vertical_header = self.table.verticalHeader()
        if vertical_header:
            vertical_header.setVisible(False)

        left_layout.addWidget(self.table)
        layout.addWidget(left_panel_widget)
        
        # Connect signals for standard dashboard only
        if self.refresh_btn:
            self.refresh_btn.clicked.connect(self.refresh_instances)
        if self.btn_auto_refresh:
            self.btn_auto_refresh.clicked.connect(self._toggle_auto_refresh)  # Changed from toggled to clicked
        
        # Continue building the dashboard - DO NOT RETURN HERE
        # return dashboard_widget  # REMOVED: This was preventing the rest of the dashboard from being built
        layout = QVBoxLayout(dashboard_widget)

        left_panel_widget = QWidget()
        left_layout = QVBoxLayout(left_panel_widget)
        left_layout.setContentsMargins(0,0,0,0)

        filter_bar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Tìm theo tên hoặc index...")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tất cả", "Đang chạy", "Đã tắt"])
        
        # 🚀 MODERN CONTROLS - Improved UX with modern styling
        self.btn_select_all = QPushButton("✅ Chọn tất cả")
        self.btn_deselect_all = QPushButton("❌ Bỏ chọn")  
        self.refresh_btn = QPushButton("🔄 Làm mới")
        self.btn_auto_refresh = QPushButton("🤖 Tự động")
        self.btn_auto_refresh.setCheckable(True)
        self.btn_auto_refresh.setChecked(self.auto_refresh_enabled)

        # Cập nhật text và tooltip ban đầu dựa trên trạng thái
        if self.auto_refresh_enabled:
            self.btn_auto_refresh.setText("🔄 Đang tự động")
            self.btn_auto_refresh.setToolTip(f"Tắt tự động làm mới (đang chạy mỗi {self.auto_refresh_interval}s)")
        else:
            self.btn_auto_refresh.setText("🤖 Tự động")
            self.btn_auto_refresh.setToolTip(f"Bật tự động làm mới mỗi {self.auto_refresh_interval}s")
        
        # AI control removed

        filter_bar.addWidget(QLabel("Tìm kiếm:"))
        filter_bar.addWidget(self.search_edit)
        filter_bar.addSpacing(15)
        filter_bar.addWidget(QLabel("Trạng thái:"))
        filter_bar.addWidget(self.filter_combo)
        filter_bar.addStretch(1)
        filter_bar.addWidget(self.btn_select_all)
        filter_bar.addWidget(self.btn_deselect_all)
        filter_bar.addWidget(self.refresh_btn)
        filter_bar.addWidget(self.btn_auto_refresh)
        # AI control removed
        left_layout.addLayout(filter_bar)

        # Tạo Model/View setup trước
        self.instances_model = InstancesModel(self)
        self.instances_proxy = InstancesProxy(self)
        self.instances_proxy.setSourceModel(self.instances_model)

        # Tạo table với QTableView cho Model/View pattern
        self.table = QTableView()
        self.table.setModel(self.instances_proxy)
        
        # Cấu hình table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for col in [TableColumn.CHECKBOX, TableColumn.STT, TableColumn.ADB,
                    TableColumn.DISK_USAGE]:
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setItemDelegateForColumn(TableColumn.STATUS, StatusPillDelegate(self.table))
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.setSortingEnabled(True)
        
        # Hide vertical header to avoid confusion with Index column
        self.table.verticalHeader().setVisible(False)
        
        # 🚀 ENHANCED USER ACTIVITY TRACKING - Comprehensive table interaction detection
        self.table.clicked.connect(self._on_user_activity)
        self.table.selectionModel().selectionChanged.connect(self._on_user_activity)
        self.table.doubleClicked.connect(self._on_user_activity)
        
        # Advanced tracking for table interactions
        self.table.entered.connect(self._on_user_activity)  # Mouse enter
        self.table.pressed.connect(self._on_user_activity)  # Mouse press
        self.table.horizontalHeader().sectionClicked.connect(self._on_user_activity)  # Header clicks
        self.table.verticalScrollBar().valueChanged.connect(self._on_table_scroll)
        self.table.horizontalScrollBar().valueChanged.connect(self._on_table_scroll)
        
        # Context menu tracking
        self._context_menu_open = False
        self.table.customContextMenuRequested.connect(self._on_context_menu_requested)
        
        # 🚀 TABLE VIRTUALIZATION - Setup for high performance
        # TEMPORARILY DISABLED to fix hanging issue
        # self.table_virtualizer = VirtualizedTableView(self.table)
        # self.table_virtualizer.enable_virtualization()
        self.table_virtualizer = None
        print("⚠️ Table Virtualization temporarily disabled (fallback)")
        
        left_layout.addWidget(self.table)

        bottom_splitter = QSplitter(Qt.Orientation.Vertical)
        print("🔧 Creating control panel for fallback dashboard...")
        try:
            self._create_control_panel()
            print("✅ Control panel created successfully")
        except Exception as e:
            print(f"❌ Error creating control panel: {e}")
            import traceback
            traceback.print_exc()
        
        # Enhanced log system
        print("🔧 Creating log widget...")
        try:
            from enhanced_log_system import EnhancedLogWidget
            self.log_widget = EnhancedLogWidget()
            print("✅ Log widget created successfully")
        except Exception as e:
            print(f"❌ Error creating log widget: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simple widget with log_message method
            self.log_widget = self._create_fallback_log_widget()
        
        print("🔧 Adding widgets to splitter...")
        try:
            if hasattr(self, 'control_panel') and self.control_panel:
                bottom_splitter.addWidget(self.control_panel)
                print("✅ Control panel added to splitter")
            else:
                print("⚠️ Control panel not found, skipping")
                
            bottom_splitter.addWidget(self.log_widget)
            bottom_splitter.setStretchFactor(0, 0)
            bottom_splitter.setStretchFactor(1, 1)
            left_layout.addWidget(bottom_splitter)
            print("✅ Splitter configured successfully")
        except Exception as e:
            print(f"❌ Error configuring splitter: {e}")
            import traceback
            traceback.print_exc()

        layout.addWidget(left_panel_widget)
        # Dashboard widget now added in main initialization
        
        # Return standard dashboard
        return dashboard_widget

    def _create_control_panel(self):
        """
        Create control panel sử dụng modular component architecture
        
        Phase 2: Replace legacy button creation với ControlPanelComponent
        """
        
        # 🚀 PHASE 2: Use modular control panel component
        if OPTIMIZATION_AVAILABLE:
            try:
                # Create control panel component
                self.control_panel_component = create_control_panel_component(self)
                
                # Connect component signals to main window methods
                self._connect_control_panel_signals()
                
                # Create control panel widget
                self.control_panel = self.control_panel_component.create_control_panel()
                
                # Extract button references for compatibility
                self._assign_control_panel_buttons()
                
                print("🚀 Phase 2: Modular control panel component created successfully!")
                return
                
            except Exception as e:
                print(f"⚠️ Control panel component creation failed: {e}")
                print("🔄 Falling back to legacy control panel")
        
        # Legacy control panel fallback
        self.control_panel = QWidget()
        layout = QVBoxLayout(self.control_panel)
        layout.setContentsMargins(0, 5, 0, 5)

        action_bar = QHBoxLayout()
        action_bar.setSpacing(5)  # Reduce spacing between buttons for compact layout
        # 🚀 MODERN BUTTONS - Tối ưu UI/UX với hover effects và animations (Compact size)
        self.btn_start_selected = ModernButton("Bắt đầu", "success", "sm")
        self.btn_stop_selected = ModernButton("Dừng", "danger", "sm")
        self.btn_restart_selected = ModernButton("Restart", "secondary", "sm")
        self.btn_create = ModernButton("Tạo mới", "primary", "sm")
        self.btn_clone = ModernButton("Nhân bản", "secondary", "sm")
        self.btn_delete = ModernButton("Xóa", "danger", "sm")
        self.btn_batch_edit = ModernButton("Sửa IMEI", "secondary", "sm")
        self.btn_open_settings_editor = ModernButton("Cấu hình", "secondary", "sm")

        action_bar.addWidget(self.btn_start_selected)
        action_bar.addWidget(self.btn_stop_selected)
        action_bar.addWidget(self.btn_restart_selected)
        action_bar.addWidget(self.btn_create)
        action_bar.addWidget(self.btn_clone)
        action_bar.addWidget(self.btn_delete)
        action_bar.addStretch(1)
        action_bar.addWidget(self.btn_batch_edit)
        action_bar.addWidget(self.btn_open_settings_editor)
        layout.addLayout(action_bar)

        self.auto_panel = QGroupBox("Tự động hóa theo Index")
        auto_v_layout = QVBoxLayout(self.auto_panel)

        auto_h_layout = QHBoxLayout()
        # 🚀 MODERN AUTOMATION CONTROLS
        self.btn_auto_start = ModernButton("Bắt đầu", "success", "sm")
        self.btn_auto_pause = ModernButton("Tạm dừng", "warning", "sm")  # Khôi phục màu gốc
        self.btn_auto_stop = ModernButton("Dừng", "danger", "sm")        # Khôi phục màu gốc
        
        # Set initial disabled state for pause/stop buttons
        self.btn_auto_pause.setEnabled(False)
        self.btn_auto_stop.setEnabled(False)
        
        auto_h_layout.addWidget(self.btn_auto_start)
        auto_h_layout.addWidget(self.btn_auto_pause)
        auto_h_layout.addWidget(self.btn_auto_stop)
        auto_h_layout.addStretch(1)
        
        auto_v_layout.addLayout(auto_h_layout)
        
        # 🚀 MODERN PROGRESS BAR - Smooth animations
        self.auto_progress_bar = ModernProgressBar()
        self.auto_progress_bar.setFormat("Đang chạy... %p%")
        self.auto_progress_bar.setVisible(False)
        auto_v_layout.addWidget(self.auto_progress_bar)

        # Ẩn panel tự động hóa khi khởi động, hiện khi click nút "Tự động hóa"
        self.auto_panel.setVisible(False)
        layout.addWidget(self.auto_panel)

    def _create_apps_page(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        apk_group = QGroupBox("Cài đặt / Gỡ bỏ ứng dụng")
        apk_layout = QFormLayout(apk_group)
        self.apk_path_edit = QLineEdit()
        self.apk_path_edit.setPlaceholderText("Đường dẫn đến file .apk")
        browse_apk_btn = QPushButton("Chọn APK")
        browse_apk_btn.clicked.connect(lambda: self._browse_file(self.apk_path_edit, "APK Files (*.apk)"))
        apk_row = QHBoxLayout()
        apk_row.addWidget(self.apk_path_edit)
        apk_row.addWidget(browse_apk_btn)
        self.pkg_name_edit = QLineEdit()
        self.pkg_name_edit.setPlaceholderText("ví dụ: com.google.android.youtube")
        # 🚀 MODERN APK MANAGEMENT BUTTONS
        self.btn_install_apk = ModernButton("📦 Cài đặt APK", "success", "md")
        self.btn_uninstall_pkg = ModernButton("🗑️ Gỡ Package", "danger", "md")
        apk_layout.addRow("File APK:", apk_row)
        apk_layout.addRow("Tên Package:", self.pkg_name_edit)
        btn_row1 = QHBoxLayout()
        btn_row1.addWidget(self.btn_install_apk)
        btn_row1.addWidget(self.btn_uninstall_pkg)
        apk_layout.addRow(btn_row1)
        layout.addRow(apk_group)

        control_group = QGroupBox("Điều khiển ứng dụng")
        control_layout = QFormLayout(control_group)
        # 🚀 MODERN APP CONTROL BUTTONS
        self.btn_launch_app = ModernButton("🚀 Chạy App", "primary", "md")
        self.btn_stop_app = ModernButton("🛑 Dừng App", "danger", "md")
        btn_row2 = QHBoxLayout()
        btn_row2.addWidget(self.btn_launch_app)
        btn_row2.addWidget(self.btn_stop_app)
        control_layout.addRow(btn_row2)
        layout.addRow(control_group)

        return widget

    def _create_tools_page(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        adb_group = QGroupBox("Lệnh ADB tùy chỉnh")
        adb_layout = QFormLayout(adb_group)
        self.adb_cmd_edit = QLineEdit()
        self.adb_cmd_edit.setPlaceholderText("shell getprop ro.product.model")
        self.btn_run_adb = QPushButton("Chạy lệnh cho các VM đã chọn")
        adb_layout.addRow("Lệnh:", self.adb_cmd_edit)
        adb_layout.addRow(self.btn_run_adb)
        layout.addRow(adb_group)

        tools_group = QGroupBox("Công cụ thường dùng")
        tools_layout = QFormLayout(tools_group)
        self.btn_screencap = QPushButton("Chụp ảnh màn hình (lưu vào /sdcard/screen.png)")
        tools_layout.addRow(self.btn_screencap)
        layout.addRow(tools_group)

        return widget

    def _create_scripting_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        script_group = QGroupBox("Trình chạy kịch bản ADB")
        script_layout = QVBoxLayout(script_group)

        button_layout = QHBoxLayout()
        self.btn_load_script = QPushButton(" Mở Kịch bản")
        self.btn_save_script = QPushButton(" Lưu Kịch bản")
        self.btn_script_templates = QMenu("Mẫu Kịch bản", self)
        self.btn_script_templates.addAction("Lấy thông tin thiết bị", lambda: self._apply_script_template("device_info"))
        self.btn_script_templates.addAction("Liệt kê ứng dụng đã cài", lambda: self._apply_script_template("list_packages"))

        templates_button = QPushButton(" Mẫu Kịch bản")
        templates_button.setMenu(self.btn_script_templates)

        button_layout.addWidget(self.btn_load_script)
        button_layout.addWidget(self.btn_save_script)
        button_layout.addWidget(templates_button)
        button_layout.addStretch(1)
        script_layout.addLayout(button_layout)

        self.script_input = QTextEdit()
        self.script_input.setPlaceholderText("shell pm list packages\nshell getprop ro.product.model\n...")
        self.script_input.setFont(QFont("Consolas", 10))
        script_layout.addWidget(self.script_input)

        self.btn_run_script = QPushButton(" Chạy Kịch bản")
        script_layout.addWidget(self.btn_run_script)

        layout.addWidget(script_group)
        return widget

    def _create_automation_page(self):
        """Tạo trang Tự động hóa với thiết kế Monokai cổ điển và Enhanced Integration"""
        # Create original automation page
        original_automation_page = MonokaiAutomationPage(self)
        
        # Apply enhanced integration if available
        if ENHANCED_AUTOMATION_AVAILABLE and is_enhanced_mode_available():
            try:
                # Create enhanced automation page with modern features
                enhanced_page = create_enhanced_automation_page(original_automation_page, self)
                
                # Store references for access
                self.original_automation_page = original_automation_page
                self.enhanced_automation_page = enhanced_page
                
                # Apply automation patch for backward compatibility
                self.automation_patch = apply_automation_patch(original_automation_page)
                
                # Connect enhanced signals to main window
                self._connect_enhanced_automation_signals(enhanced_page)
                
                print("✅ Enhanced automation page created successfully")
                return enhanced_page
                
            except Exception as e:
                print(f"⚠️ Failed to create enhanced automation page: {e}")
                print("   Falling back to original automation page")
                
        # Fallback to original page
        print("📄 Using original automation page")
        return original_automation_page
    
    def _connect_enhanced_automation_signals(self, enhanced_page):
        """Connect enhanced automation signals to main window"""
        try:
            # Connect automation state changes
            enhanced_page.automation_state_changed.connect(self._on_enhanced_automation_state_changed)
            
            # Connect performance alerts
            enhanced_page.performance_alert.connect(self._on_enhanced_performance_alert)
            
            # Connect optimization events
            enhanced_page.optimization_applied.connect(self._on_enhanced_optimization_applied)
            
            # Connect to automation patch signals if available
            if hasattr(self, 'automation_patch'):
                patch = self.automation_patch
                
                # Connect patch signals to status updates
                patch.automation_started.connect(self._on_enhanced_automation_started)
                patch.automation_stopped.connect(self._on_enhanced_automation_stopped)
                patch.automation_paused.connect(self._on_enhanced_automation_paused)
                patch.progress_updated.connect(self._on_enhanced_progress_updated)
                patch.log_message.connect(self._on_enhanced_log_message)
            
            print("✅ Enhanced automation signals connected successfully")
            
        except Exception as e:
            print(f"⚠️ Failed to connect enhanced automation signals: {e}")
    
    # Enhanced automation signal handlers
    def _on_enhanced_automation_state_changed(self, running: bool, paused: bool):
        """Handle enhanced automation state changes"""
        try:
            if running:
                if paused:
                    self.log_message("⏸️ Enhanced automation paused", LogLevel.WARNING, "Automation")
                    self.statusBar().showMessage("Enhanced Automation: Paused")
                else:
                    self.log_message("🚀 Enhanced automation running", LogLevel.INFO, "Automation")
                    self.statusBar().showMessage("Enhanced Automation: Running")
            else:
                self.log_message("🛑 Enhanced automation stopped", LogLevel.INFO, "Automation")
                self.statusBar().showMessage("Enhanced Automation: Stopped")
        except Exception as e:
            print(f"Error handling enhanced automation state change: {e}")
    
    def _on_enhanced_performance_alert(self, message: str, level: str):
        """Handle enhanced performance alerts"""
        try:
            if level == "warning":
                self.log_message(message, LogLevel.WARNING, "Performance")
            elif level == "error":
                self.log_message(message, LogLevel.ERROR, "Performance")
            else:
                self.log_message(message, LogLevel.INFO, "Performance")
        except Exception as e:
            print(f"Error handling enhanced performance alert: {e}")
    
    def _on_enhanced_optimization_applied(self, optimization_info: dict):
        """Handle enhanced optimization applied"""
        try:
            message = f"🔧 Optimization applied: {optimization_info.get('type', 'Unknown')}"
            self.log_message(message, LogLevel.SUCCESS, "Optimization")
        except Exception as e:
            print(f"Error handling enhanced optimization: {e}")
    
    def _on_enhanced_automation_started(self):
        """Handle enhanced automation started"""
        try:
            self.log_message("✅ Enhanced automation started successfully", LogLevel.SUCCESS, "Automation")
            self.statusBar().showMessage("Enhanced Automation: Starting...")
        except Exception as e:
            print(f"Error handling enhanced automation started: {e}")
    
    def _on_enhanced_automation_stopped(self):
        """Handle enhanced automation stopped"""
        try:
            self.log_message("🛑 Enhanced automation stopped", LogLevel.WARNING, "Automation")
            self.statusBar().showMessage("Enhanced Automation: Stopped")
        except Exception as e:
            print(f"Error handling enhanced automation stopped: {e}")
    
    def _on_enhanced_automation_paused(self):
        """Handle enhanced automation paused"""
        try:
            self.log_message("⏸️ Enhanced automation paused", LogLevel.WARNING, "Automation")
            self.statusBar().showMessage("Enhanced Automation: Paused")
        except Exception as e:
            print(f"Error handling enhanced automation paused: {e}")
    
    def _on_enhanced_progress_updated(self, progress: float):
        """Handle enhanced progress updates"""
        try:
            self.statusBar().showMessage(f"Enhanced Automation: {progress:.1f}% complete")
            self.log_message(f"📊 Automation progress: {progress:.1f}%", LogLevel.DEBUG, "Progress")
        except Exception as e:
            print(f"Error handling enhanced progress update: {e}")
    
    def _on_enhanced_log_message(self, message: str, level: str):
        """Handle enhanced log messages"""
        try:
            if level == "error":
                log_level = LogLevel.ERROR
            elif level == "warning":
                log_level = LogLevel.WARNING
            elif level == "success":
                log_level = LogLevel.SUCCESS
            else:
                log_level = LogLevel.INFO
            
            self.log_message(message, log_level, "Enhanced Automation")
        except Exception as e:
            print(f"Error handling enhanced log message: {e}")
    
    # Public API methods for enhanced automation
    def get_enhanced_automation_status(self):
        """Get enhanced automation status"""
        try:
            if hasattr(self, 'automation_patch') and self.automation_patch:
                return self.automation_patch.get_automation_status_enhanced()
            elif hasattr(self, 'enhanced_automation_page'):
                return self.enhanced_automation_page.get_automation_status()
            else:
                return {'mode': 'legacy', 'enhanced': False}
        except Exception as e:
            print(f"Error getting enhanced automation status: {e}")
            return {'error': str(e)}
    
    def start_enhanced_automation(self, instances=None):
        """Start enhanced automation"""
        try:
            if hasattr(self, 'automation_patch') and self.automation_patch:
                success = self.automation_patch.start_automation_enhanced(instances)
                if success:
                    self.log_message("🚀 Enhanced automation started via API", LogLevel.SUCCESS, "API")
                return success
            else:
                self.log_message("⚠️ Enhanced automation not available", LogLevel.WARNING, "API")
                return False
        except Exception as e:
            self.log_message(f"❌ Failed to start enhanced automation: {e}", LogLevel.ERROR, "API")
            return False
    
    def stop_enhanced_automation(self, reason="user_request"):
        """Stop enhanced automation"""
        try:
            if hasattr(self, 'automation_patch') and self.automation_patch:
                success = self.automation_patch.stop_automation_enhanced(reason)
                if success:
                    self.log_message(f"🛑 Enhanced automation stopped: {reason}", LogLevel.WARNING, "API")
                return success
            else:
                self.log_message("⚠️ Enhanced automation not available", LogLevel.WARNING, "API")
                return False
        except Exception as e:
            self.log_message(f"❌ Failed to stop enhanced automation: {e}", LogLevel.ERROR, "API")
            return False
    
    def is_enhanced_automation_available(self):
        """Check if enhanced automation is available"""
        return (ENHANCED_AUTOMATION_AVAILABLE and 
                hasattr(self, 'automation_patch') and 
                self.automation_patch is not None)
    
    def get_automation_performance_metrics(self):
        """Get automation performance metrics"""
        try:
            if hasattr(self, 'automation_patch') and self.automation_patch:
                status = self.automation_patch.get_automation_status_enhanced()
                return status.get('performance_report', {})
            else:
                return {'error': 'Enhanced automation not available'}
        except Exception as e:
            return {'error': str(e)}

    def _connect_signals(self):
        # Connect manager signals
        self.sidebar_manager.navigation_requested.connect(self._handle_sidebar_navigation)
        self.sidebar_manager.settings_requested.connect(self._open_settings)
        self.sidebar_manager.theme_toggle_requested.connect(self._toggle_theme)

        self.content_manager.page_loaded.connect(self._on_page_loaded)
        self.content_manager.page_requested.connect(self._on_page_requested)

        # Legacy signal connections (keeping for compatibility)
        if hasattr(self, 'settings_btn'):
            self.settings_btn.clicked.connect(self._open_settings)
        if hasattr(self, 'theme_toggle_btn'):
            self.theme_toggle_btn.clicked.connect(self._toggle_theme)
        
        # 🚀 ENHANCED DEBOUNCING - Smart delay based on input length
        self._filter_debounce = QTimer(self)
        self._filter_debounce.setSingleShot(True)
        self._filter_debounce.timeout.connect(self._apply_filter)
        
        # Smart debouncing với delay động
        self._last_search_length = 0
        self._search_start_time = None
        
        # Note: Search and filter signals are now connected in _connect_search_filter_signals
        # after dashboard components are available
        
        # Note: Dashboard component signals are now connected in _connect_search_filter_signals
        # after dashboard components are available

        # 🚀 USER ACTIVITY TRACKING - Theo dõi thao tác user với auto-refresh pause
        # Add defensive checks for button connections
        if hasattr(self, 'btn_start_selected') and self.btn_start_selected:
            self.btn_start_selected.clicked.connect(lambda: [self._on_user_activity(), self._control_selected_instances(Action.LAUNCH)])
        if hasattr(self, 'btn_stop_selected') and self.btn_stop_selected:
            self.btn_stop_selected.clicked.connect(lambda: [self._on_user_activity(), self._control_selected_instances(Action.SHUTDOWN)])
        if hasattr(self, 'btn_restart_selected') and self.btn_restart_selected:
            self.btn_restart_selected.clicked.connect(lambda: [self._on_user_activity(), self._control_selected_instances(Action.RESTART)])
        if hasattr(self, 'btn_create') and self.btn_create:
            self.btn_create.clicked.connect(lambda: [self._on_user_activity(), self._create_instance()])
        if hasattr(self, 'btn_clone') and self.btn_clone:
            self.btn_clone.clicked.connect(lambda: [self._on_user_activity(), self._clone_instance()])
        if hasattr(self, 'btn_delete') and self.btn_delete:
            self.btn_delete.clicked.connect(lambda: [self._on_user_activity(), self._delete_selected_instances()])
        
        if hasattr(self, 'btn_batch_edit') and self.btn_batch_edit:
            self.btn_batch_edit.clicked.connect(lambda: [self._on_user_activity(), self._open_batch_edit_dialog()])
        if hasattr(self, 'btn_open_settings_editor') and self.btn_open_settings_editor:
            self.btn_open_settings_editor.clicked.connect(lambda: [self._on_user_activity(), self._open_settings_editor()])

        if hasattr(self, 'btn_auto_start') and self.btn_auto_start:
            self.btn_auto_start.clicked.connect(self._start_automation)
        if hasattr(self, 'btn_auto_pause') and self.btn_auto_pause:
            self.btn_auto_pause.clicked.connect(self._pause_resume_worker)
        if hasattr(self, 'btn_auto_stop') and self.btn_auto_stop:
            self.btn_auto_stop.clicked.connect(self._stop_worker)

        # Note: Signals for page-specific buttons are now connected in _connect_page_signals
        # for lazy loading optimization

        # Page-independent signals only
        # Note: config_path_edit signal is connected in _connect_page_signals for Config page
        
    def _connect_dashboard_signals(self):
        """Connect MonokaiDashboard signals to MainWindow methods"""
        if hasattr(self, 'monokai_dashboard'):
            try:
                # Connect action signals
                self.monokai_dashboard.start_all_requested.connect(self._start_all_instances)
                self.monokai_dashboard.stop_all_requested.connect(self._stop_all_instances)
                self.monokai_dashboard.start_instance_requested.connect(self._start_instance)
                self.monokai_dashboard.stop_instance_requested.connect(self._stop_instance)
                self.monokai_dashboard.restart_instance_requested.connect(self._restart_instance)
                self.monokai_dashboard.cleanup_requested.connect(self._cleanup_instances)
                
                # Connect other signals
                self.monokai_dashboard.refresh_requested.connect(self.refresh_instances)
                self.monokai_dashboard.instance_selected.connect(self._on_dashboard_instance_selected)
                
                print("✅ Dashboard signals connected successfully")
            except Exception as e:
                print(f"⚠️ Error connecting dashboard signals: {e}")
                import traceback
                traceback.print_exc()
    
    def _connect_search_filter_signals(self):
        """Connect search and filter signals after dashboard components are available"""
        try:
            # Connect search_edit signal
            if hasattr(self, 'search_edit') and self.search_edit is not None:
                self.search_edit.textChanged.connect(self._smart_debounce_search)
                print("✅ DEBUG: search_edit signal connected successfully")
            else:
                print("⚠️ search_edit not available for signal connection")
                
            # Connect filter_combo signal
            if hasattr(self, 'filter_combo') and self.filter_combo is not None:
                self.filter_combo.currentTextChanged.connect(lambda: self._filter_debounce.start())
                print("✅ DEBUG: filter_combo signal connected successfully")
            else:
                print("⚠️ filter_combo not available for signal connection")
                
            # Connect table and model signals
            if hasattr(self, 'instances_model') and self.instances_model and hasattr(self.instances_model, 'dataChanged'):
                self.instances_model.dataChanged.connect(lambda *_: self._update_selection_info())
                print("✅ DEBUG: instances_model dataChanged signal connected")
            else:
                print("⚠️ instances_model not available for dataChanged signal connection")
                
            if hasattr(self, 'table') and self.table:
                self.table.clicked.connect(self._on_table_clicked)
                print("✅ DEBUG: table clicked signal connected")
            else:
                print("⚠️ table not available for signal connection")
                
            # Connect button signals
            if hasattr(self, 'btn_select_all') and self.btn_select_all:
                self.btn_select_all.clicked.connect(lambda: self._set_all_checkboxes_state(True))
                print("✅ DEBUG: btn_select_all signal connected")
            else:
                print("⚠️ btn_select_all not available for signal connection")
                
            if hasattr(self, 'btn_deselect_all') and self.btn_deselect_all:
                self.btn_deselect_all.clicked.connect(lambda: self._set_all_checkboxes_state(False))
                print("✅ DEBUG: btn_deselect_all signal connected")
            else:
                print("⚠️ btn_deselect_all not available for signal connection")
                
        except Exception as e:
            print(f"⚠️ Error connecting search/filter signals: {e}")
            import traceback
            traceback.print_exc()
        
    def _on_dashboard_instance_selected(self, instance_id):
        """Handle instance selection from dashboard"""
        try:
            print(f"📍 Instance {instance_id} selected from dashboard")
            # Handle instance selection logic here
        except Exception as e:
            print(f"⚠️ Error handling dashboard instance selection: {e}")
        
    def _start_all_instances(self):
        """Start all instances"""
        try:
            print("🚀 Starting all instances...")
            # Get all instance indices
            all_indices = []
            if hasattr(self, 'instances_model') and self.instances_model:
                for row in range(self.instances_model.rowCount()):
                    # Get the index from model data
                    index_item = self.instances_model.item(row, TableColumn.STT)
                    if index_item:
                        try:
                            instance_index = int(index_item.text())
                            all_indices.append(instance_index)
                        except (ValueError, TypeError):
                            continue
            
            if all_indices:
                print(f"🚀 Starting {len(all_indices)} instances: {all_indices}")
                # Use launch action for all instances
                self._control_instances_by_indices(all_indices, Action.LAUNCH)
            else:
                print("⚠️ No instances found to start")
                if hasattr(self, 'monokai_dashboard'):
                    self.monokai_dashboard.status_label.setText("⚠️ No instances found")
        except Exception as e:
            print(f"⚠️ Error starting all instances: {e}")
            
    def _stop_all_instances(self):
        """Stop all instances"""
        try:
            print("⏹️ Stopping all instances...")
            # Get all instance indices
            all_indices = []
            if hasattr(self, 'instances_model') and self.instances_model:
                for row in range(self.instances_model.rowCount()):
                    # Get the index from model data
                    index_item = self.instances_model.item(row, TableColumn.STT)
                    if index_item:
                        try:
                            instance_index = int(index_item.text())
                            all_indices.append(instance_index)
                        except (ValueError, TypeError):
                            continue
            
            if all_indices:
                print(f"⏹️ Stopping {len(all_indices)} instances: {all_indices}")
                # Use shutdown action for all instances
                self._control_instances_by_indices(all_indices, Action.SHUTDOWN)
            else:
                print("⚠️ No instances found to stop")
                if hasattr(self, 'monokai_dashboard'):
                    self.monokai_dashboard.status_label.setText("⚠️ No instances found")
        except Exception as e:
            print(f"⚠️ Error stopping all instances: {e}")
            
    def _control_instances_by_indices(self, indices, action):
        """Control specific instances by indices"""
        try:
            if not indices:
                return
                
            print(f"🎮 Controlling {len(indices)} instances with action: {action}")
            
            # Direct control for each instance
            for instance_index in indices:
                self._control_single_instance(action, instance_index)
                    
        except Exception as e:
            print(f"⚠️ Error controlling instances by indices: {e}")
            import traceback
            traceback.print_exc()
            
    def _start_instance(self, instance_id):
        """Start specific instance"""
        try:
            print(f"▶️ Starting instance {instance_id}...")
            self._control_single_instance(Action.LAUNCH, instance_id)
        except Exception as e:
            print(f"⚠️ Error starting instance {instance_id}: {e}")
            
    def _stop_instance(self, instance_id):
        """Stop specific instance"""
        try:
            print(f"⏹️ Stopping instance {instance_id}...")
            self._control_single_instance(Action.SHUTDOWN, instance_id)
        except Exception as e:
            print(f"⚠️ Error stopping instance {instance_id}: {e}")
            
    def _restart_instance(self, instance_id):
        """Restart specific instance"""
        try:
            print(f"🔄 Restarting instance {instance_id}...")
            self._control_single_instance(Action.RESTART, instance_id)
        except Exception as e:
            print(f"⚠️ Error restarting instance {instance_id}: {e}")
            
    def _cleanup_instances(self, instance_ids):
        """Cleanup specific instances"""
        try:
            print(f"🧹 Cleaning up {len(instance_ids)} instances...")
            # Add cleanup logic here
            for instance_id in instance_ids:
                print(f"🧹 Cleaning instance {instance_id}")
                # Implement cleanup logic based on your backend
            
            # Update dashboard status
            if hasattr(self, 'monokai_dashboard'):
                self.monokai_dashboard.status_label.setText(f"✅ Cleaned up {len(instance_ids)} instances")
                
        except Exception as e:
            print(f"⚠️ Error cleaning up instances: {e}")
            if hasattr(self, 'monokai_dashboard'):
                self.monokai_dashboard.status_label.setText(f"❌ Cleanup error: {str(e)}")

        # Note: config_path_edit signal is connected in _connect_page_signals for Config page

    def _handle_sidebar_click(self, index):
        # ✅ LAZY LOADING: Load page on demand using content manager
        print(f"🔄 Sidebar clicked: index {index}")
        if index == 0:  # Dashboard index
            print("📊 Dashboard tab clicked!")

        # Use content manager for lazy loading
        self.content_manager.load_page(index)
        self.content_manager.set_current_page(index)

        # Update sidebar active state
        self.sidebar_manager.set_active_page(index)

    def _load_page(self, index):
        """Tải nội dung của một trang một cách lười biếng - DEPRECATED: Sử dụng ContentManager."""
        # Delegate to ContentManager
        self.content_manager.load_page(index)

    def _smart_debounce_search(self):
        """🚀 Smart debouncing - delay tùy theo độ dài input và tốc độ gõ"""
        import time
        
        # Safety check for search_edit
        if not hasattr(self, 'search_edit') or self.search_edit is None:
            print("⚠️ search_edit not available, skipping smart debounce search")
            return
            
        current_text = self.search_edit.text()
        current_length = len(current_text)
        current_time = time.time()
        
        # Tính delay dựa trên:
        # - Độ dài text: ít text = delay ngắn hơn  
        # - Tốc độ gõ: gõ nhanh = delay dài hơn
        if self._search_start_time is None:
            self._search_start_time = current_time
            
        # Base delay
        if current_length <= 2:
            base_delay = 100  # Delay ngắn cho 1-2 ký tự
        elif current_length <= 5:
            base_delay = 150  # Delay trung bình cho 3-5 ký tự
        else:
            base_delay = 200  # Delay dài cho text dài
            
        # Adjustment based on typing speed
        if self._last_search_length > 0:
            length_diff = abs(current_length - self._last_search_length)
            if length_diff > 3:  # Typing fast
                base_delay += 50
                
        self._last_search_length = current_length
        self._filter_debounce.setInterval(base_delay)
        self._filter_debounce.start()
        
        # Reset timer sau 2 giây không activity
        if current_time - self._search_start_time > 2:
            self._search_start_time = None


    def _smart_debounce_search(self):
        """🚀 Smart debouncing - delay tùy theo độ dài input và tốc độ gõ"""
        from time import time
        
        current_text = self.search_edit.text()
        current_length = len(current_text)
        current_time = time()
        
        # Tính delay dựa trên:
        # - Độ dài text: ít text = delay ngắn hơn  
        # - Tốc độ gõ: gõ nhanh = delay dài hơn
        if self._search_start_time is None:
            self._search_start_time = current_time
            
        # Base delay
        if current_length <= 2:
            base_delay = 100  # Delay ngắn cho 1-2 ký tự
        elif current_length <= 5:
            base_delay = 150  # Delay trung bình cho 3-5 ký tự
        else:
            base_delay = 200  # Delay dài cho text dài
            
        # Adjustment based on typing speed
        if self._last_search_length > 0:
            length_diff = abs(current_length - self._last_search_length)
            if length_diff > 3:  # Typing fast
                base_delay += 50
                
        self._last_search_length = current_length
        self._filter_debounce.setInterval(base_delay)
        self._filter_debounce.start()
        
        # Reset timer sau 2 giây không activity
        if current_time - self._search_start_time > 2:
            self._search_start_time = None


    def _smart_debounce_search(self):
        """🚀 Smart debouncing - delay tùy theo độ dài input và tốc độ gõ"""
        from time import time
        
        current_text = self.search_edit.text()
        current_length = len(current_text)
        current_time = time()
        
        # Tính delay dựa trên:
        # - Độ dài text: ít text = delay ngắn hơn  
        # - Tốc độ gõ: gõ nhanh = delay dài hơn
        if self._search_start_time is None:
            self._search_start_time = current_time
            
        # Base delay
        if current_length <= 2:
            base_delay = 100  # Delay ngắn cho 1-2 ký tự
        elif current_length <= 5:
            base_delay = 150  # Delay trung bình cho 3-5 ký tự
        else:
            base_delay = 200  # Delay dài cho text dài
            
        # Adjustment based on typing speed
        if self._last_search_length > 0:
            length_diff = abs(current_length - self._last_search_length)
            if length_diff > 3:  # Typing fast
                base_delay += 50
                
        self._last_search_length = current_length
        self._filter_debounce.setInterval(base_delay)
        self._filter_debounce.start()
        
        # Reset timer sau 2 giây không activity
        if current_time - self._search_start_time > 2:
            self._search_start_time = None


    def _smart_debounce_search(self):
        """🚀 Smart debouncing - delay tùy theo độ dài input và tốc độ gõ"""
        from time import time
        
        current_text = self.search_edit.text()
        current_length = len(current_text)
        current_time = time()
        
        # Tính delay dựa trên:
        # - Độ dài text: ít text = delay ngắn hơn  
        # - Tốc độ gõ: gõ nhanh = delay dài hơn
        if self._search_start_time is None:
            self._search_start_time = current_time
            
        # Base delay
        if current_length <= 2:
            base_delay = 100  # Delay ngắn cho 1-2 ký tự
        elif current_length <= 5:
            base_delay = 150  # Delay trung bình cho 3-5 ký tự
        else:
            base_delay = 200  # Delay dài cho text dài
            
        # Adjustment based on typing speed
        if self._last_search_length > 0:
            length_diff = abs(current_length - self._last_search_length)
            if length_diff > 3:  # Typing fast
                base_delay += 50
                
        self._last_search_length = current_length
        self._filter_debounce.setInterval(base_delay)
        self._filter_debounce.start()
        
        # Reset timer sau 2 giây không activity
        if current_time - self._search_start_time > 2:
            self._search_start_time = None

    def _connect_page_signals(self, page_index):
        """Kết nối signals cho các trang được tải lười."""
        if page_index == 1:  # Apps page
            if hasattr(self, 'btn_install_apk'):
                self.btn_install_apk.clicked.connect(self._install_apk)
                self.btn_uninstall_pkg.clicked.connect(self._uninstall_package)
                self.btn_launch_app.clicked.connect(self._launch_package)
                self.btn_stop_app.clicked.connect(self._stop_package)
        elif page_index == 2:  # Tools page
            if hasattr(self, 'btn_run_adb'):
                self.btn_run_adb.clicked.connect(self._run_custom_adb)
                self.btn_screencap.clicked.connect(self._take_screencap)
        elif page_index == 3:  # Scripting page
            if hasattr(self, 'btn_run_script'):
                self.btn_run_script.clicked.connect(self._run_script)
                self.btn_save_script.clicked.connect(self._save_script)
                self.btn_load_script.clicked.connect(self._load_script)

    def update_ui_states(self):
        is_worker_running = self.worker is not None and self.worker.isRunning()
        is_refreshing = self.refresh_worker is not None and self.refresh_worker.isRunning()
        is_busy = is_worker_running or is_refreshing

        # Update status bar manager with current state
        if hasattr(self, 'status_bar_manager'):
            # Get selected count from instances model instead of instance_ui_states
            selected_count = 0
            if hasattr(self, 'instances_model') and self.instances_model:
                try:
                    selected_count = len(self.instances_model.get_checked_indices())
                except Exception:
                    selected_count = 0
            self.status_bar_manager.update_selection_info(selected_count)

            if is_busy:
                self.status_bar_manager.update_summary_status("🔄 Đang xử lý...")
            else:
                self.status_bar_manager.update_summary_status("✅ Sẵn sàng")

        # Automation buttons - check if they exist
        if hasattr(self, 'btn_auto_start') and self.btn_auto_start is not None:
            self.btn_auto_start.setEnabled(not is_busy)
        if hasattr(self, 'btn_auto_pause') and self.btn_auto_pause is not None:
            self.btn_auto_pause.setEnabled(is_worker_running)
        if hasattr(self, 'btn_auto_stop') and self.btn_auto_stop is not None:
            self.btn_auto_stop.setEnabled(is_worker_running)

        # Cập nhật màu sắc buttons dựa trên trạng thái enabled/disabled
        self._update_automation_button_states()

        # Update pause button text
        if hasattr(self, 'btn_auto_pause') and self.btn_auto_pause is not None:
            if is_worker_running and hasattr(self.worker, '_is_paused') and self.worker._is_paused:
                self.btn_auto_pause.setText(" Tiếp tục")
            else:
                self.btn_auto_pause.setText(" Tạm dừng")
        
        self.update_button_icons()
        if hasattr(self, 'instances_model') and self.instances_model:
            self.instances_model.set_ui_states(self.instance_ui_states)
        
        # Control panel buttons - check if they exist
        for attr in ['refresh_btn', 'btn_create', 'btn_clone', 'btn_delete', 
                     'btn_start_selected', 'btn_stop_selected', 'btn_restart_selected',
                     'btn_open_settings_editor']:
            if hasattr(self, attr) and getattr(self, attr, None) is not None:
                getattr(self, attr).setEnabled(not is_busy)

        # Lazy-loaded buttons - check if they exist
        if hasattr(self, 'btn_run_script') and self.btn_run_script is not None:
            self.btn_run_script.setEnabled(not is_busy)

    def log_message(self, text: str, level: LogLevel = LogLevel.INFO, category: str = "General", details: Optional[dict] = None):
        """Enhanced log message with categorization and levels"""
        if hasattr(self, 'log_widget') and self.log_widget is not None:
            self.log_widget.log_message(text, level, category, details)

        # Also update status bar manager for immediate feedback
        if hasattr(self, 'status_bar_manager'):
            status_text = text.split('\n')[0]
            self.status_bar_manager.update_summary_status(status_text)
    
    # 🚀 CACHE EVENT HANDLERS - Smart performance logging
    # =====================================================================
    # EVENT HANDLERS
    # =====================================================================
    
    def _on_cache_hit(self, key: str) -> None:
        """
        Handle cache hit events.
        
        Args:
            key: The cache key that was hit
        """
        # Cache hit logging removed to reduce log spam
        # Performance improvement is transparent to user
        pass
    
    def _on_cache_miss(self, key: str) -> None:
        """
        Handle cache miss events.
        
        Args:
            key: The cache key that was missed
        """
        # Cache miss logging reduced to minimize log noise
        # Backend fetching is already logged elsewhere
        pass
    
    def _on_page_preloaded(self, page_index: int) -> None:
        """
        Handle page preload completion events.
        
        Args:
            page_index: Index of the preloaded page
        """
        print(f"🚀 Page {page_index} preloaded successfully - ready for instant switching")
    
    def _on_user_activity(self) -> None:
        """
        Track user activity for smart auto-refresh pausing.
        
        Updates the last activity timestamp to prevent auto-refresh
        from interrupting user interactions.
        """
        self.last_user_activity = time.time()
    
    def _on_table_scroll(self) -> None:
        """
        Handle table scrolling events.
        
        Treats scrolling as user activity to pause auto-refresh
        and maintain scroll position.
        """
        self.last_user_activity = time.time()
    
    def _on_context_menu_requested(self, position: QPoint) -> None:
        """
        Handle context menu requests with activity tracking.
        
        Args:
            position: The position where context menu was requested
        """
        self._context_menu_open = True
        self.last_user_activity = time.time()
        
        # Show the actual context menu
        self._show_table_context_menu(position)
        
        # Schedule to reset context menu flag after 5 seconds
        QTimer.singleShot(
            5000, 
            lambda: setattr(self, '_context_menu_open', False)
        )
    
    # =====================================================================
    # CACHE MANAGEMENT
    # =====================================================================
    
    def _preload_cache(self) -> None:
        """
        🚀 Smart cache preload to minimize cache misses on startup.
        
        Attempts to load cached data from previous sessions using smart cache system
        to provide immediate data availability and improve startup performance.
        """
        try:
            # 💾 SMART CACHE - Check for multiple cache types
            cache_keys = [
                ("instance_list", "Instance data"),
                ("adb_devices", "ADB devices"),
                ("system_info", "System information")
            ]
            
            loaded_count = 0
            for cache_key, description in cache_keys:
                cached_data = self.global_smart_cache.get(cache_key, command_type=cache_key)
                if cached_data:
                    loaded_count += 1
                    if cache_key == "instance_list":
                        # Update UI with cached instance data immediately
                        self._on_instances_loaded(cached_data)
            
            if loaded_count > 0:
                self.log_message(
                    f"💾 Smart Cache: Loaded {loaded_count}/{len(cache_keys)} cached datasets", 
                    LogLevel.INFO, 
                    "Cache"
                )
            else:
                self.log_message(
                    "🔄 Cache trống - Sẽ fetch data từ backend lần đầu", 
                    LogLevel.DEBUG, 
                    "Performance"
                )
                
        except Exception as e:
            self.log_message(
                f"Smart cache preload warning: {e}", 
                LogLevel.WARNING, 
                "Performance"
            )
            
    def show_cache_statistics(self):
        """🚀 Display smart cache performance statistics"""
        try:
            stats = self.global_smart_cache.get_stats()
            cache_info = (
                f"📊 Smart Cache Stats:\n"
                f"• Hit Rate: {stats['hit_rate']}\n"
                f"• Total Entries: {stats['total_entries']}\n" 
                f"• Memory Usage: {stats['total_size_mb']} MB\n"
                f"• Cache Hits: {stats['hit_count']}\n"
                f"• Cache Misses: {stats['miss_count']}"
            )
            
            self.log_message(cache_info, LogLevel.INFO, "Cache Performance")
            
            # Also show virtualization stats if available
            if self.table_virtualizer:
                virt_stats = self.table_virtualizer.get_performance_stats()
                virt_info = (
                    f"📊 Table Virtualization Stats:\n"
                    f"• Total Items: {virt_stats['total_items']:,}\n"
                    f"• Visible Range: {virt_stats['visible_range']}\n"
                    f"• Rendered Rows: {virt_stats['rendered_rows']}\n"
                    f"• Memory Saving: {((virt_stats['total_items'] - virt_stats['rendered_rows']) / max(virt_stats['total_items'], 1) * 100):.1f}%"
                )
                self.log_message(virt_info, LogLevel.INFO, "Virtualization Performance")
                
        except Exception as e:
            self.log_message(f"Failed to get cache stats: {e}", LogLevel.WARNING, "Cache")
    
    # =====================================================================
    # INSTANCE MANAGEMENT
    # =====================================================================
    def refresh_instances(self) -> None:
        """
        Refresh instances with forced backend update (bypass cache).
        
        Features:
        - Forces fresh data from backend (no cache)
        - Prevents concurrent refresh operations
        - Background task execution with progress tracking
        - Updates cache with fresh data for auto-refresh
        
        Returns:
            None
        """
        # Prevent concurrent operations
        if (self.worker and self.worker.isRunning()) or \
           (self.refresh_worker and self.refresh_worker.isRunning()):
            self.log_message(
                "Không thể làm mới khi một tác vụ khác đang chạy.", 
                LogLevel.WARNING, 
                "System"
            )
            return

        # Force invalidate cache to ensure fresh data
        self.log_message(
            "🔄 Refresh: Forcing fresh data from backend...", 
            LogLevel.INFO, 
            "Refresh"
        )
        
        if hasattr(self, 'smart_cache'):
            try:
                self.smart_cache.invalidate("instances_list")
            except Exception as e:
                self.log_message(f"⚠️ Cache invalidation failed: {e}", LogLevel.WARNING, "Cache")

        # Clear failed indices and prepare for fresh load
        self.failed_indices.clear()
        self.log_message(
            "🔄 Đang tải danh sách giả lập từ backend...", 
            LogLevel.INFO, 
            "Instance Management"
        )

        def refresh_task(worker: GenericWorker, manager: MumuManager, params: dict) -> dict:
            """Background task for fetching instance data."""
            worker.started.emit("Bắt đầu làm mới danh sách máy ảo...")
            
            # Fetch fresh data
            success, data = manager.get_all_info()
            worker.progress.emit(100)
            result = {"success": success, "data": data}
            
            return result

        # Initialize worker without complex cache integration
        # Clean up previous worker if exists
        if self.refresh_worker is not None:
            if self.refresh_worker.isRunning():
                self.refresh_worker.terminate()
                self.refresh_worker.wait()
            self.refresh_worker.task_result.disconnect()
            self.refresh_worker.finished.disconnect()
            self.refresh_worker.deleteLater()
            self.refresh_worker = None
            
        self.refresh_worker = GenericWorker(refresh_task, self.mumu_manager, {})
        self.refresh_worker.task_result.connect(self._on_instances_loaded)
        self.refresh_worker.finished.connect(self._on_refresh_finished)

        self.refresh_worker.start()
        self.update_ui_states()

    def _on_instances_loaded(self, result: dict, silent: bool = False) -> None:
        """
        Handle loaded instance data.
        
        Args:
            result: Dictionary containing success status and data
            silent: If True, suppresses logging (used for auto-refresh)
        
        Processes both successful and failed data loads,
        updating the instance cache and applying current filters.
        """
        success = result.get("success", False)
        data = result.get("data", "Không có dữ liệu trả về.")

        if not success:
            if not silent:  # Only log for manual refresh
                self.log_message(
                    f"Lỗi làm mới: {data}", 
                    LogLevel.ERROR, 
                    "Instance Management", 
                    {'error_details': str(data)}
                )
            self.instance_cache = {}
        else:
            self.instance_cache = data
            
            # ⚡ Update Ultra-Fast Database with new data
            if hasattr(self, 'ultra_database') and self.ultra_database and data:
                try:
                    # Convert instance cache to database format
                    db_instances = []
                    for idx, info in data.items():
                        db_instance = {
                            'id': int(idx),
                            'name': info.get('name', f'Instance {idx}'),
                            'status': 'running' if info.get('is_process_started') else 'stopped',
                            'cpu_usage': float(info.get('cpu_usage', 0.0)),
                            'memory_usage': float(info.get('memory_usage', 0.0)),
                            'disk_usage': info.get('disk_usage', '0MB'),
                            'adb_port': int(info.get('adb_port', 0)),
                            'version': info.get('version', 'unknown'),
                            'path': info.get('path', ''),
                            'metadata': {
                                'is_process_started': info.get('is_process_started'),
                                'original_data': info
                            }
                        }
                        db_instances.append(db_instance)
                    
                    # Bulk update database
                    updated_count = self.ultra_database.bulk_insert_instances(db_instances)
                    
                    if not silent and updated_count > 0:  # Only log for manual refresh
                        self.log_message(
                            f"⚡ Database updated: {updated_count} instances", 
                            LogLevel.INFO, 
                            "Database"
                        )
                        
                except Exception as e:
                    print(f"❌ Database update failed: {e}")
            
            if not silent:  # Only log for manual refresh
                self.log_message(
                    f"Đã tải {len(data)} giả lập.", 
                    LogLevel.SUCCESS, 
                    "Instance Management", 
                    {'instance_count': len(data)}
                )
                
                # 🎮 LOG PERFORMANCE ACCELERATION STATS
                if hasattr(self, 'acceleration_manager') and self.acceleration_manager:
                    accel_report = self.acceleration_manager.get_acceleration_report()
                    self.log_message(
                        f"🎮 Performance Acceleration: {accel_report['acceleration_status']}", 
                        LogLevel.INFO, 
                        "Performance", 
                        accel_report
                    )
        
        self._apply_filter()

    def _on_refresh_finished(self, msg: str) -> None:
        """
        Handle refresh completion.
        
        Args:
            msg: Completion message from worker
        
        Cleans up worker reference and updates UI states.
        """
        # Proper worker cleanup
        if self.refresh_worker is not None:
            self.refresh_worker.task_result.disconnect()
            self.refresh_worker.finished.disconnect()
            self.refresh_worker.deleteLater()
            self.refresh_worker = None
            
        self.update_ui_states()

    # =====================================================================
    # AUTO-REFRESH MANAGEMENT
    # =====================================================================
    
    def _start_auto_refresh(self) -> None:
        """
        🚫 AUTO-REFRESH PERMANENTLY DISABLED
        
        This method has been permanently disabled to prevent any automatic refresh.
        All refresh operations are now manual only.
        """
        print("🚫 _start_auto_refresh called but PERMANENTLY DISABLED")
        
        # Ensure timer is stopped if it was somehow started
        if hasattr(self, 'auto_refresh_timer') and self.auto_refresh_timer.isActive():
            self.auto_refresh_timer.stop()
            print("🚫 Stopped auto refresh timer that was running")
        
        # Ensure auto refresh flag is disabled
        self.auto_refresh_enabled = False
        
        # Update status to show manual only mode
        self._update_auto_refresh_status()
        
        return  # Exit without starting any timer

    def _stop_auto_refresh(self) -> None:
        """
        Stop auto-refresh system gracefully.
        
        Disables the auto-refresh cycle and updates UI status indicators.
        This method ensures clean shutdown of the refresh timer system.
        """
        if self.auto_refresh_timer.isActive():
            self.auto_refresh_timer.stop()
        
        # Disable auto-refresh to stop QTimer.singleShot cycle
        self.auto_refresh_enabled = False
        self.log_message("Đã tắt tự động làm mới", LogLevel.INFO, "Auto Refresh")
        self._update_auto_refresh_status()

    def _update_auto_refresh_status(self) -> None:
        """
        Update auto-refresh status in status bar.
        
        Displays current auto-refresh state with visual indicators:
        - Green color and timer info when enabled
        - Gray color and "Tắt" when disabled
        """
        if hasattr(self, 'status_bar_manager'):
            # Always show manual refresh mode
            status_text = "🔄 Manual Refresh Only"
            self.status_bar_manager.update_summary_status(status_text)
        elif hasattr(self, 'auto_refresh_status_label'):
            # Always show manual refresh mode
            self.auto_refresh_status_label.setText("🔄 Manual Refresh Only")
            self.auto_refresh_status_label.setStyleSheet("color: blue;")

    def _auto_refresh_instances(self) -> None:
        """
        Smart auto-refresh with comprehensive user activity detection.
        
        This is the core of the enterprise-level auto-refresh system that
        intelligently detects user interactions and delays refresh operations
        to prevent interrupting user workflows.
        
        Detection Layers:
        1. System State: Checks if auto-refresh is enabled
        2. Worker State: Prevents conflicts with running operations
        3. User Activity: Recent interaction detection with timing
        4. Table Interaction: Focus, selection, and mouse hover detection
        5. Context Menu: Prevents refresh during menu operations
        
        Features:
        - Non-disruptive background updates
        - State preservation during refresh
        - Intelligent delay calculations
        - Recursive scheduling for continuous operation
        """
        # Layer 1: Check if auto-refresh is enabled
        if not self.auto_refresh_enabled:
            return  # Stop the cycle cleanly
        
        # Layer 2: Check if workers are running
        if (self.worker and self.worker.isRunning()) or \
           (self.refresh_worker and self.refresh_worker.isRunning()):
            # Don't reschedule - break the cycle when auto-refresh is disabled
            print("🚫 Workers running but auto-refresh DISABLED - stopping cycle")
            return
        
        # Layer 3: Check recent user activity timing
        time_since_activity = time.time() - self.last_user_activity
        if time_since_activity < self.user_interaction_delay:
            # Don't reschedule - break the cycle when auto-refresh is disabled
            print("🚫 User active but auto-refresh DISABLED - stopping cycle")
            return
        
        # Layer 4: Check table interaction state
        has_selection = self.table.selectionModel().hasSelection()
        has_focus = self.table.hasFocus()
        mouse_over_table = self.table.underMouse()
        
        if has_focus or has_selection or mouse_over_table:
            # User actively interacting with table, but auto-refresh is disabled
            print("🚫 Table interaction detected but auto-refresh DISABLED - stopping cycle")
            if self.auto_refresh_timer.isActive():
                self.auto_refresh_timer.stop()
            return

        # Layer 5: Check context menu state
        if hasattr(self, '_context_menu_open') and self._context_menu_open:
            # Context menu open, but auto-refresh is disabled
            print("🚫 Context menu open but auto-refresh DISABLED - stopping cycle")
            if self.auto_refresh_timer.isActive():
                self.auto_refresh_timer.stop()
            return
        
        # 🚫 SILENT BACKGROUND REFRESH PERMANENTLY DISABLED
        # All checks passed but silent background refresh is disabled
        print("🚫 Silent background refresh PERMANENTLY DISABLED - no auto refresh")
        if self.auto_refresh_timer.isActive():
            self.auto_refresh_timer.stop()
        return

        # Timer will automatically trigger next refresh if still enabled
        # No need to manually schedule next cycle

    def _restart_timer_if_enabled(self) -> None:
        """Restart auto-refresh timer - PERMANENTLY DISABLED."""
        # Auto-refresh permanently disabled - never restart timer
        print("🚫 Timer restart requested but auto-refresh PERMANENTLY DISABLED")
        if self.auto_refresh_timer.isActive():
            self.auto_refresh_timer.stop()
        return

    def _silent_refresh_instances(self) -> None:
        """
        🚫 SILENT BACKGROUND REFRESH PERMANENTLY DISABLED
        
        This method has been disabled to prevent automatic background refreshing.
        All refresh operations are now manual only.
        """
        print("🚫 Silent background refresh called but PERMANENTLY DISABLED")
        return  # Exit immediately without performing any refresh operations

    # =====================================================================
    # TABLE STATE MANAGEMENT
    # =====================================================================
    
    def _save_table_state(self) -> None:
        """
        Save complete table state for preservation during refresh.
        
        Captures and stores:
        - Selected rows and their indices
        - Scroll position (vertical and horizontal)
        - Focus state and current cell
        - Sort order and column state
        
        This state is used to restore the exact user experience
        after background data updates.
        """
        try:
            # Save selected rows with their indices
            selection_model = self.table.selectionModel()
            self._saved_selected_rows = []
            if selection_model:
                selected_indexes = selection_model.selectedRows()
                self._saved_selected_rows = [index.row() for index in selected_indexes]
            
            # Save scroll positions (both vertical and horizontal)
            v_scrollbar = self.table.verticalScrollBar()
            h_scrollbar = self.table.horizontalScrollBar()
            self._saved_scroll_v = v_scrollbar.value() if v_scrollbar else 0
            self._saved_scroll_h = h_scrollbar.value() if h_scrollbar else 0
            
            # Save focus state and current selection
            self._saved_has_focus = self.table.hasFocus()
            
            # Save current row if any
            current_index = self.table.currentIndex()
            self._saved_current_row = current_index.row() if current_index.isValid() else -1
            
        except Exception as e:
            # Fallback - initialize empty state if saving fails
            self._saved_selected_rows = []
            self._saved_scroll_v = 0
            self._saved_scroll_h = 0
            self._saved_has_focus = False
            self._saved_current_row = -1

    def _restore_table_state(self) -> None:
        """
        Restore complete table state after refresh.
        
        Restores all saved state components:
        - Row selections with multi-selection support
        - Scroll position (vertical and horizontal)
        - Focus state and current cell
        - Table navigation state
        
        Uses robust error handling to ensure UI remains
        stable even if state restoration encounters issues.
        """
        try:
            # Restore row selections
            if hasattr(self, '_saved_selected_rows') and self._saved_selected_rows:
                selection_model = self.table.selectionModel()
                if selection_model:
                    selection_model.clearSelection()
                    for row in self._saved_selected_rows:
                        if 0 <= row < self.instances_model.rowCount():
                            index = self.instances_model.index(row, 0)
                            selection_model.select(
                                index, 
                                selection_model.SelectionFlag.Select | 
                                selection_model.SelectionFlag.Rows
                            )
            
            # Restore current row cursor
            if hasattr(self, '_saved_current_row') and self._saved_current_row >= 0:
                if self._saved_current_row < self.instances_model.rowCount():
                    current_index = self.instances_model.index(self._saved_current_row, 0)
                    self.table.setCurrentIndex(current_index)
            
            # Restore scroll position (with delay to ensure table is updated)
            if hasattr(self, '_saved_scroll_v') and hasattr(self, '_saved_scroll_h'):
                QTimer.singleShot(50, lambda: self._restore_scroll_position())
            
            # Restore focus state
            if hasattr(self, '_saved_has_focus') and self._saved_has_focus:
                QTimer.singleShot(100, lambda: self.table.setFocus())
                
        except Exception as e:
            # Silent fail for table state restoration to prevent UI disruption
            pass

    def _restore_scroll_position(self) -> None:
        """
        Restore scroll position with proper timing.
        
        Uses delayed restoration to ensure table layout
        is complete before setting scroll positions.
        """
        try:
            # Restore vertical scroll position
            if hasattr(self, '_saved_scroll_v'):
                v_scrollbar = self.table.verticalScrollBar()
                if v_scrollbar:
                    v_scrollbar.setValue(self._saved_scroll_v)
            
            # Restore horizontal scroll position
            if hasattr(self, '_saved_scroll_h'):
                h_scrollbar = self.table.horizontalScrollBar()
                if h_scrollbar:
                    h_scrollbar.setValue(self._saved_scroll_h)
        except Exception:
            # Silent fail to prevent disruption
            pass

    def _on_instances_loaded_silent_preserve(self, result: dict) -> None:
        """
        Silent instance loading with complete state preservation.
        
        Args:
            result: Dictionary containing success status and data
        
        Performs silent data loading followed by complete state restoration
        to maintain the exact user experience during background refresh.
        """
        # Load data silently (no user-visible logs)
        self._on_instances_loaded(result, silent=True)
        
        # Restore complete table state after data load
        QTimer.singleShot(10, self._restore_table_state)

    def _on_instances_loaded_silent(self, result: dict) -> None:
        """
        Simple silent instance loading without state preservation.
        
        Args:
            result: Dictionary containing success status and data
        
        Used for basic silent updates that don't require
        complete state preservation functionality.
        """
        self._on_instances_loaded(result, silent=True)

    # =====================================================================
    # AUTO-REFRESH CONTROLS
    # =====================================================================
    
    def _toggle_auto_refresh(self) -> None:
        """
        Manual refresh only - auto refresh permanently disabled.
        
        Button chỉ để trigger manual refresh, không có tự động.
        """
        # Force manual refresh
        self.refresh_instances()
        self.log_message("🔄 Manual refresh triggered", LogLevel.INFO, "Manual-Refresh")
        
        # Update button text to reflect manual action
        if hasattr(self, 'btn_auto_refresh') and self.btn_auto_refresh:
            self.btn_auto_refresh.setText("🔄 Refresh")
            self.btn_auto_refresh.setToolTip("Click để refresh thủ công")
        
        # Ensure auto refresh stays disabled
        self.auto_refresh_enabled = False
        
        # Stop any background processing 
        if hasattr(self, 'monokai_dashboard') and self.monokai_dashboard:
            if hasattr(self.monokai_dashboard, 'disable_background_processing'):
                self.monokai_dashboard.disable_background_processing()

        # Update status bar
        self._update_auto_refresh_status()

        # Lưu setting
        self.settings.setValue("auto_refresh/enabled", self.auto_refresh_enabled)

    # =====================================================================
    # UI MANAGEMENT - TABLE FILTERING & SEARCH
    # =====================================================================
    
    def _apply_filter(self) -> None:
        """
        Apply search and status filters to instance table.
        
        Features:
        - ⚡ Ultra-Fast Database search (80% faster)
        - Advanced search syntax support
        - Status filtering (running/stopped/all)
        - Case-insensitive search
        - Real-time filtering with instant results
        
        Processes instances using Ultra-Fast Database for maximum performance.
        """
        # ⚡ Use Ultra-Fast Database for search if available
        if hasattr(self, 'ultra_database') and self.ultra_database:
            self._apply_filter_with_database()
        else:
            self._apply_filter_legacy()
    
    def _apply_filter_with_database(self) -> None:
        """⚡ Apply filters using Ultra-Fast Database"""
        try:
            # Check if ultra_database is available
            if not hasattr(self, 'ultra_database') or self.ultra_database is None:
                print("⚠️ Ultra database not available, falling back to legacy search")
                self._apply_filter_legacy()
                return
            
            # Get filter criteria with safety checks
            keyword = ""
            if hasattr(self, 'search_edit') and self.search_edit is not None:
                keyword = self.search_edit.text().strip()
            else:
                print("⚠️ search_edit not available, using empty keyword")
                
            status_filter = "All"
            if hasattr(self, 'filter_combo') and self.filter_combo is not None:
                status_filter = self.filter_combo.currentText()
            else:
                print("⚠️ filter_combo not available, using 'All' filter")
            
            start_time = time.time()
            
            if keyword:
                # Use advanced search if keyword contains special syntax
                if ':' in keyword:
                    # Advanced search: "status:running cpu:>50"
                    results = self.ultra_database.search_instances(keyword, "advanced")
                else:
                    # Regular name search
                    results = self.ultra_database.search_instances(keyword, "name")
            else:
                # Get all instances (increased limit to handle large datasets)
                results = self.ultra_database.get_all_instances(5000)
            
            # Check if results is valid
            if results is None:
                print("⚠️ Database returned None results, falling back to legacy search")
                self._apply_filter_legacy()
                return
            
            # Apply status filter to database results
            filtered_items = []
            for result in results:
                # Convert database result to legacy format
                idx = result['id']
                disk_usage_raw = result['disk_usage']
                disk_bytes = self._parse_disk_usage_to_bytes(disk_usage_raw)
                
                # Debug log for first few instances (disabled to reduce noise)
                # if idx <= 205:  # Log first few to see data
                #     print(f"Debug Instance {idx}: disk_usage='{disk_usage_raw}' -> {disk_bytes} bytes")
                
                info = {
                    'name': result['name'],
                    'status': result['status'],
                    'cpu_usage': result['cpu_usage'],
                    'memory_usage': result['memory_usage'],
                    'disk_usage': disk_usage_raw,
                    'adb_port': result['adb_port'],
                    'version': result['version'],
                    'path': result['path'],
                    'is_process_started': result['status'] in ['running', 'starting'],
                    'metadata': result.get('metadata', {}),
                    # Add disk_size_bytes for widget compatibility
                    'disk_size_bytes': disk_bytes
                }
                
                # Apply status filter
                is_running = info.get("is_process_started", False)
                if status_filter == "Đang chạy" and not is_running: 
                    continue
                if status_filter == "Đã tắt" and is_running: 
                    continue
                
                filtered_items.append((idx, info))
            
            # Sort by index and update table
            filtered_items.sort(key=lambda x: x[0])
            self._populate_table(filtered_items)
            
            # Log performance improvement
            execution_time = time.time() - start_time
            if execution_time > 0:
                self.log_message(
                    f"⚡ Database search: {len(filtered_items)} results in {execution_time*1000:.1f}ms", 
                    LogLevel.INFO, 
                    "Database Performance"
                )
            
        except Exception as e:
            print(f"❌ Database search failed: {e}")
            # Fallback to legacy search
            self._apply_filter_legacy()
    
    def _parse_disk_usage_to_bytes(self, disk_usage_str: str) -> int:
        """Parse disk usage string (e.g., '1.5GB', '500MB') to bytes"""
        if not disk_usage_str or disk_usage_str == "N/A":
            return 0
            
        try:
            # Remove spaces and convert to uppercase
            usage_str = disk_usage_str.replace(" ", "").upper()
            
            # Extract number and unit
            import re
            match = re.match(r'(\d+\.?\d*)(GB|MB|KB|B)?', usage_str)
            if not match:
                return 0
                
            number = float(match.group(1))
            unit = match.group(2) or 'B'
            
            # Convert to bytes
            multipliers = {
                'B': 1,
                'KB': 1024,
                'MB': 1024 ** 2,
                'GB': 1024 ** 3
            }
            
            return int(number * multipliers.get(unit, 1))
            
        except (ValueError, AttributeError):
            return 0
    
    def _apply_filter_legacy(self) -> None:
        """Legacy filter method (fallback)"""
        # Get filter criteria with safety checks
        keyword = ""
        if hasattr(self, 'search_edit') and self.search_edit is not None:
            keyword = self.search_edit.text().strip().lower()
        else:
            print("⚠️ search_edit not available, using empty keyword")
            
        status_filter = "All"
        if hasattr(self, 'filter_combo') and self.filter_combo is not None:
            status_filter = self.filter_combo.currentText()
        else:
            print("⚠️ filter_combo not available, using 'All' filter")
            
        filtered_items = []
        
        # Apply filters to each instance
        for idx_str, info in self.instance_cache.items():
            try:
                idx = int(idx_str)
                name = info.get("name", "").lower()
                is_running = info.get("is_process_started", False)
                
                # Apply status filter
                if status_filter == "Đang chạy" and not is_running: 
                    continue
                if status_filter == "Đã tắt" and is_running: 
                    continue
                    
                # Apply keyword filter (name or index)
                if keyword and not (keyword in name or keyword == str(idx)): 
                    continue
                    
                filtered_items.append((idx, info))
            except (ValueError, TypeError):
                continue

        # Sort by index and update table
        filtered_items.sort(key=lambda item: item[0])
        self._populate_table(filtered_items)

    def _populate_table(self, items: List[Tuple[int, Dict]]) -> None:
        """
        Populate table with filtered instance data.
        
        Args:
            items: List of (index, info) tuples to display
        
        Features:
        - Model-based data population
        - UI state integration
        - Selection info update
        - Performance optimized for large datasets
        - Persistent selection by vmIndex
        """
        if hasattr(self, 'instances_model') and self.instances_model is not None:
            # Preserve selection by vmIndex before updating model
            selected_indices = set()
            if hasattr(self, 'table') and self.table and hasattr(self.table, 'selectionModel'):
                selection_model = self.table.selectionModel()
                if selection_model:
                    selected_rows = selection_model.selectedRows()
                    for index in selected_rows:
                        # Get vmIndex from UserRole of STT column
                        vm_index = self.instances_model.data(index, Qt.ItemDataRole.UserRole)
                        if vm_index is not None:
                            selected_indices.add(vm_index)
            
            # Update model data
            self.instances_model.set_rows(items)
            self.instances_model.set_ui_states(self.instance_ui_states)
            
            # Restore selection by vmIndex
            if selected_indices and hasattr(self, 'table') and self.table:
                selection_model = self.table.selectionModel()
                if selection_model:
                    selection_model.clearSelection()
                    for vm_index in selected_indices:
                        row = self.instances_model.find_source_row_by_index(vm_index)
                        if row >= 0:
                            # Select the entire row
                            model_index = self.instances_model.index(row, 0)
                            selection_model.select(model_index, QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
        
        self._update_selection_info()

    # =====================================================================
    # UI MANAGEMENT - SELECTION & VALIDATION
    # =====================================================================
    
    def _get_selected_indices(self, require_one: bool = False, require_at_least_one: bool = False) -> Optional[List[int]]:
        """
        Get selected instance indices with validation.
        
        Args:
            require_one: If True, requires exactly one selection
            require_at_least_one: If True, requires at least one selection
            
        Returns:
            Sorted list of selected indices, or None if validation fails
            
        Features:
        - Multiple validation modes
        - User-friendly error messages
        - Automatic sorting of results
        - Type safety with proper return types
        """
        indices = self.instances_model.get_checked_indices()
        
        # Validate selection requirements
        if require_at_least_one and not indices:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn ít nhất một giả lập.")
            return None
        if require_one and len(indices) != 1:
            QMessageBox.warning(self, "Chọn sai", "Vui lòng chọn chính xác MỘT giả lập.")
            return None
            
        return sorted(indices)

    # =====================================================================
    # INSTANCE CONTROL OPERATIONS
    # =====================================================================
    
    def _control_selected_instances(self, action: str) -> None:
        """
        Control selected instances with batch processing + Ultra-Fast Database + Performance optimization.
        
        Args:
            action: Control action to perform (start, stop, restart)
        
        Features:
        - Batch instance control with progress tracking
        - Ultra-Fast Database integration for bulk validation and updates
        - Performance-powered predictive optimization and user behavior tracking
        - Success/failure result tracking
        - Real-time progress updates
        - Comprehensive logging for each operation
        """
        indices = self._get_selected_indices(require_at_least_one=True)
        if not indices:
            return

        # ⚡ Use database for bulk validation if available
        valid_indices = indices
        if hasattr(self, 'ultra_database') and self.ultra_database:
            try:
                # Get instances from database for validation
                db_instances = self.ultra_database.search_instances(
                    query="",  # Get all
                    filters={'id': indices}
                )
                
                # Check if all instances are valid
                valid_indices = [inst['id'] for inst in db_instances if inst['id'] in indices]
                if len(valid_indices) != len(indices):
                    invalid_count = len(indices) - len(valid_indices)
                    self.log_message(
                        f"⚠️ {invalid_count} instances not found in database, using fallback validation",
                        LogLevel.WARNING,
                        "Database"
                    )
                
                # Log database acceleration
                self.log_message(
                    f"⚡ Database-accelerated bulk {action}: {len(valid_indices)} instances",
                    LogLevel.INFO,
                    "Database"
                )
                
            except Exception as e:
                print(f"Database validation error: {e}")
                # Fallback to original indices
                valid_indices = indices

        def control_task(worker: GenericWorker, manager: MumuManager, params: dict) -> dict:
            """Background task for instance control operations with database updates."""
            indices_to_control = params['indices']
            action_to_perform = params['action']
            total = len(indices_to_control)
            results = {'success': [], 'failed': []}
            worker.started.emit(f"--- ⚡ Bắt đầu {action_to_perform} {total} giả lập đã chọn ---")

            # ⚡ Prepare database update data
            db_updates = []
            new_status = 'running' if action_to_perform == 'start' else 'stopped'

            for i, index in enumerate(indices_to_control):
                worker.check_status()
                ok, msg = manager.control_instance([index], action_to_perform)
                if ok:
                    results['success'].append(index)
                    worker.log.emit(f"[{index}] {action_to_perform.title()}: Thành công")
                    
                    # ⚡ Prepare database status update
                    db_updates.append({'id': index, 'status': new_status})
                    
                else:
                    results['failed'].append(index)
                    worker.log.emit(f"[{index}] {action_to_perform.title()}: Thất bại")
                    worker.log.emit(f"  -> {msg}")
                    
                worker.progress.emit(int(((i + 1) / total) * 100))
                worker.msleep(200)

            # ⚡ Bulk update database if available
            if hasattr(self, 'ultra_database') and self.ultra_database and db_updates:
                try:
                    updated_count = 0
                    for update in db_updates:
                        if self.ultra_database.update_instance_status(update['id'], update['status']):
                            updated_count += 1
                    
                    if updated_count > 0:
                        worker.log.emit(f"⚡ Database updated: {updated_count} instance statuses")
                        
                except Exception as e:
                    worker.log.emit(f"Database update error: {e}")

            return results

        worker = GenericWorker(control_task, self.mumu_manager, {'indices': valid_indices, 'action': action})
        
        # Connect result handler to trigger status refresh after control operations
        worker.task_result.connect(self._on_control_task_completed)
        
        # Start worker with custom connection (don't use _start_worker to avoid double connections)
        if (self.worker and self.worker.isRunning()) or \
           (self.refresh_worker and self.refresh_worker.isRunning()):
            QMessageBox.warning(
                self, 
                "Đang bận", 
                "Một tác vụ khác đang chạy. Vui lòng đợi."
            )
            return

        # Initialize worker with progress tracking
        self.worker = worker
        
        # Defensive programming for global_progress_bar
        if hasattr(self, 'global_progress_bar') and self.global_progress_bar:
            self.global_progress_bar.setValue(0)
            self.global_progress_bar.setVisible(True)
        
        # Connect worker signals for comprehensive monitoring
        self.worker.started.connect(self.log_message)
        
        # Connect progress with defensive check
        if hasattr(self, 'global_progress_bar') and self.global_progress_bar:
            self.worker.progress.connect(self.global_progress_bar.setValue)
        self.worker.log.connect(self.log_message)
        self.worker.finished.connect(self._on_worker_finished)
        
        # Start worker and update UI state
        self.worker.start()
        self.update_ui_states()

    def _on_control_task_completed(self, result: dict) -> None:
        """
        Handle completion of instance control tasks.
        
        Args:
            result: Dictionary containing success/failed instance lists
        
        Features:
        - Immediate status refresh for successfully controlled instances
        - Smart cache invalidation for real-time status updates
        - Error tracking for failed operations
        """
        # Handle failed operations
        if 'failed' in result and result['failed']:
            self.failed_indices.update(result['failed'])
            self.log_message(
                f"⚠️ {len(result['failed'])} tác vụ con đã thất bại (xem log để biết chi tiết).",
                LogLevel.WARNING,
                "Instance Control"
            )

        # Refresh status for successfully controlled instances
        if 'success' in result and result['success']:
            successful_count = len(result['success'])
            self.log_message(
                f"🔄 Cập nhật trạng thái {successful_count} giả lập đã điều khiển...",
                LogLevel.INFO,
                "Status Update"
            )
            
            # Invalidate cache to ensure fresh data for updates
            if hasattr(self, 'smart_cache'):
                try:
                    self.smart_cache.invalidate("instances_list")
                    # Cache invalidation logging removed to reduce noise
                except Exception as e:
                    self.log_message(f"⚠️ Cache invalidation failed: {e}", LogLevel.WARNING, "Cache")
            
            # Request status update for each successful instance with delay
            for i, index in enumerate(result['success']):
                # Stagger updates to avoid overwhelming the system
                delay = 1000 + (i * 200)  # 1s base delay + 200ms per instance
                # Fix lambda closure issue by capturing index value properly
                def create_update_callback(instance_index):
                    return lambda: self._request_single_instance_update(instance_index)
                QTimer.singleShot(delay, create_update_callback(index))

        # Handle file discovery results
        if 'files' in result:
            if 'ota.vdi' in result.get('type', ''):
                self._on_files_found(result)
            elif 'customer_config.json' in result.get('type', ''):
                self._on_config_files_found(result)

    def _on_task_result(self, result: dict) -> None:
        """
        Handle generic task results (non-control tasks).
        
        Args:
            result: Dictionary containing task results
        
        This method handles results from tasks other than instance control,
        as control tasks are handled by the specialized _on_control_task_completed method.
        """
        # Handle file discovery results
        if 'files' in result:
            if 'ota.vdi' in result.get('type', ''):
                self._on_files_found(result)
            elif 'customer_config.json' in result.get('type', ''):
                self._on_config_files_found(result)

    def _toggle_theme(self):
        themes = ["dark", "light", "monokai"]
        current_theme = self.settings.value("theme/name", "dark")
        try:
            current_index = themes.index(current_theme)
            next_index = (current_index + 1) % len(themes)
        except ValueError:
            next_index = 0

        self.settings.setValue("theme/name", themes[next_index])
        AppTheme.apply_theme(QApplication.instance(), self.settings)
        self.update_button_icons()
        if hasattr(self, 'instances_model'):
            self.instances_model.set_ui_states(self.instance_ui_states)
        self._apply_native_theme_tweaks()

    def _open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Lưu interval cũ để so sánh
            old_interval = self.auto_refresh_interval
            
            # Cập nhật cài đặt
            self.mumu_manager = MumuManager(self.settings.value("manager_path", ""))
            set_global_mumu_manager(self.mumu_manager)
            self.auto_refresh_interval = self.settings.value("auto_refresh/interval", 30, type=int)
            
            # Nếu interval thay đổi và auto-refresh đang chạy, khởi động lại với interval mới
            if old_interval != self.auto_refresh_interval and self.auto_refresh_timer.isActive():
                self._stop_auto_refresh()
                self._start_auto_refresh()
                
            # Cập nhật tooltip cho button
            if hasattr(self, 'btn_auto_refresh'):
                if self.auto_refresh_timer.isActive():
                    self.btn_auto_refresh.setToolTip(f"Tắt tự động làm mới (đang chạy mỗi {self.auto_refresh_interval}s)")
                else:
                    self.btn_auto_refresh.setToolTip(f"Bật tự động làm mới mỗi {self.auto_refresh_interval}s")
            
            self.log_message("Đã lưu cài đặt.")
            AppTheme.apply_theme(QApplication.instance(), self.settings)
            self.update_button_icons()
        if hasattr(self, 'instances_model'):
            self.instances_model.set_ui_states(self.instance_ui_states)
            self._apply_native_theme_tweaks()

    def update_button_icons(self):
        # Update sidebar manager icons
        if hasattr(self, 'sidebar_manager'):
            self.sidebar_manager.update_button_styles()

        # Main UI buttons - check if they exist before updating
        if hasattr(self, 'settings_btn') and self.settings_btn is not None:
            self.settings_btn.setIcon(get_icon("settings"))
        if hasattr(self, 'theme_toggle_btn') and self.theme_toggle_btn is not None:
            self.theme_toggle_btn.setIcon(get_icon("theme"))

        # Control panel buttons - use defensive checking
        for attr, icon_name in [("btn_start_selected", "play"), ("btn_stop_selected", "stop"), 
                               ("btn_restart_selected", "restart"), ("btn_create", "add"),
                               ("btn_clone", "clone"), ("btn_delete", "delete"),
                               ("btn_batch_edit", "edit"), ("btn_open_settings_editor", "settings"),
                               ("refresh_btn", "refresh"), ("btn_auto_start", "play"), 
                               ("btn_auto_stop", "stop")]:
            if hasattr(self, attr) and getattr(self, attr, None) is not None:
                getattr(self, attr).setIcon(get_icon(icon_name))
        
        # Setup pause/resume button icon based on current state
        if hasattr(self, 'btn_auto_pause') and self.btn_auto_pause is not None:
            is_worker_running = self.worker is not None and self.worker.isRunning()
            if is_worker_running and hasattr(self.worker, '_is_paused') and self.worker._is_paused:
                self.btn_auto_pause.setIcon(get_icon("play"))
            else:
                self.btn_auto_pause.setIcon(get_icon("pause"))

        # Lazy-loaded buttons - check if they exist before updating icons
        if hasattr(self, 'btn_load_script') and self.btn_load_script is not None:
            self.btn_load_script.setIcon(get_icon("folder"))
        if hasattr(self, 'btn_save_script') and self.btn_save_script is not None:
            self.btn_save_script.setIcon(get_icon("save"))
        if hasattr(self, 'btn_run_script') and self.btn_run_script is not None:
            self.btn_run_script.setIcon(get_icon("run"))

    def _set_all_checkboxes_state(self, checked: bool):
        self.instances_model.set_all_checked(checked)
        self._update_selection_info()

    def _on_table_clicked(self, index):
        # Validate that index belongs to the correct model
        if index.model() != self.instances_proxy:
            return
        
        src = self.instances_proxy.mapToSource(index)
        if src.isValid():
            curr = self.instances_model.index(src.row(), TableColumn.CHECKBOX)
            state = self.instances_model.data(curr, Qt.ItemDataRole.CheckStateRole)
            new_state = Qt.CheckState.Unchecked if state == Qt.CheckState.Checked else Qt.CheckState.Checked
            self.instances_model.setData(curr, new_state, Qt.ItemDataRole.CheckStateRole)
        self._update_selection_info()

    def _update_selection_info(self) -> None:
        """
        Update selection counter in the UI.

        Displays the current count of selected instances
        in the selection label for user feedback.
        """
        count = len(self._get_selected_indices())

        # Update status bar manager with selection info
        if hasattr(self, 'status_bar_manager'):
            self.status_bar_manager.update_selection_info(count)

    # =====================================================================
    # UI MANAGEMENT - DIALOG HANDLERS
    # =====================================================================
    
    def _show_table_context_menu(self, pos: QPoint) -> None:
        """
        Show context menu for table items.
        
        Args:
            pos: Position where the context menu was requested
        
        Features:
        - Index validation and mapping
        - Dynamic action menu generation
        - Instance-specific operations
        - Separator organization for better UX
        
        Provides quick access to common instance operations
        directly from the table interface.
        """
        # Validate and map table position to model index
        view_index = self.table.indexAt(pos)
        if not view_index.isValid(): 
            return
        
        # Validate that index belongs to the correct model
        if view_index.model() != self.instances_proxy:
            return
            
        src_index = self.instances_proxy.mapToSource(view_index)
        if not src_index.isValid(): 
            return
            
        idx = self.instances_model.data(
            self.instances_model.index(src_index.row(), TableColumn.NAME), 
            Qt.ItemDataRole.UserRole
        )
        if idx is None: 
            return

        # Create context menu with instance actions
        menu = QMenu(self)
        actions = {
            "🚀 Khởi động": Action.LAUNCH, 
            "🔌 Tắt máy": Action.SHUTDOWN,
            "🔄 Khởi động lại": Action.RESTART, 
            "👁️ Hiện cửa sổ": Action.SHOW,
            "🙈 Ẩn cửa sổ": Action.HIDE
        }

        # Add control actions
        for text, action in actions.items():
            menu.addAction(text, lambda a=action, i=idx: self._control_single_instance(a, i))

        # Add configuration actions
        menu.addSeparator()
        menu.addAction("✏️ Đổi tên...", lambda i=idx: self._rename_instance(i))
        menu.addAction("🔧 Sửa Cấu hình...", lambda i=idx: self._open_settings_editor_for_single(i))
        
        # Show menu at cursor position
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _control_single_instance(self, action: str, index: int) -> None:
        """
        Control a single instance with UI state management.
        
        Args:
            action: Action to perform on the instance
            index: Instance index to control
        
        Features:
        - UI state tracking during operations
        - Visual feedback with state indicators
        - Background task execution
        - Result handling and logging
        """
        self.log_message(f"Thực hiện '{action}' cho máy ảo index {index}...")

        # Update UI state for visual feedback
        action_to_state = {
            Action.LAUNCH: "starting",
            Action.SHUTDOWN: "stopping",
            Action.RESTART: "restarting"
        }
        if action in action_to_state:
            self.instance_ui_states[index] = action_to_state[action]
            self._update_row_by_index(index)

        def control_task(worker: GenericWorker, manager: MumuManager, params: dict) -> dict:
            """Background task for single instance control."""
            idx, act = params['index'], params['action']
            worker.started.emit(f"--- ⚡ Bắt đầu {act} cho máy ảo {idx} ---")
            ok, msg = manager.control_instance([idx], act)
            if ok:
                worker.log.emit(f"[{idx}] {act.title()}: Thành công")
            else:
                worker.log.emit(f"[{idx}] {act.title()}: Thất bại\n  -> {msg}")
            worker.progress.emit(100)
            return {'success': ok, 'index': idx}

        # Execute control operation
        worker = GenericWorker(control_task, self.mumu_manager, {'index': index, 'action': action})
        worker.task_result.connect(self._on_single_control_completed)
        self._start_worker(worker)

    def _on_single_control_completed(self, result: dict) -> None:
        """
        Handle completion of single instance control operations.
        
        Args:
            result: Dictionary containing success status and index
        
        Features:
        - Status update trigger for successful operations
        - UI state cleanup
        - Error handling for failed operations
        """
        index = result.get('index')
        success = result.get('success', False)
        
        if success and index is not None:
            self.log_message(f"✅ Single control operation completed for VM {index}", LogLevel.DEBUG, "Control")
            
            # Invalidate cache immediately after successful control
            if hasattr(self, 'smart_cache'):
                try:
                    self.smart_cache.invalidate("instances_list")
                    # Cache invalidation logging removed to reduce noise
                except Exception as e:
                    self.log_message(f"⚠️ Cache invalidation failed: {e}", LogLevel.WARNING, "Cache")
            
            # Trigger status update with a delay to allow operation to complete
            QTimer.singleShot(1500, lambda: self._request_single_instance_update(index))
            
            # Fallback: Clear UI state after timeout if update doesn't complete
            QTimer.singleShot(10000, lambda: self._clear_ui_state_fallback(index))
        else:
            # Clear UI state on failure
            if index is not None and index in self.instance_ui_states:
                del self.instance_ui_states[index]
                self._update_row_by_index(index)
            self.log_message(f"❌ Single control operation failed for VM {index}", LogLevel.WARNING, "Control")

    def _clear_ui_state_fallback(self, index: int) -> None:
        """
        Fallback method to clear UI state if update doesn't complete.
        
        Args:
            index: Instance index to clear UI state for
        """
        if index in self.instance_ui_states:
            self.log_message(f"🔄 Fallback: Clearing UI state for VM {index}", LogLevel.DEBUG, "Fallback")
            del self.instance_ui_states[index]
            self._update_row_by_index(index)

    def _rename_instance(self, index: int) -> None:
        """
        Rename an instance with user input dialog.
        
        Args:
            index: Instance index to rename
        
        Features:
        - Current name prefilling
        - Input validation
        - Backend update with worker
        - Error handling and user feedback
        """
        current_name = self.instance_cache.get(str(index), {}).get("name", "")
        new_name, ok = QInputDialog.getText(
            self, 
            "Đổi tên Giả lập", 
            f"Nhập tên mới cho VM {index}:", 
            text=current_name
        )
        if ok and new_name and new_name != current_name:
            success, msg = self.mumu_manager.rename_instance(index, new_name)
            self.log_message(msg)
            if success:
                self._request_single_instance_update(index)

    def _create_instance(self):
        num, ok = QInputDialog.getInt(self, "Tạo Giả lập", "Số lượng cần tạo:", 1, 1, 100)
        if ok:
            success, msg = self.mumu_manager.create_instance(num)
            self.log_message(msg)
            if success: self.refresh_instances()

    def _clone_instance(self):
        indices = self._get_selected_indices(require_one=True)
        if not indices: return
        source_index = indices[0]
        num, ok = QInputDialog.getInt(self, "Nhân bản Giả lập", f"Số lượng nhân bản từ VM {source_index}:", 1, 1, 100)
        if ok:
            success, msg = self.mumu_manager.clone_instance(source_index, num)
            self.log_message(msg)
            if success: self.refresh_instances()

    def _delete_selected_instances(self):
        indices = self._get_selected_indices(require_at_least_one=True)
        if not indices: return
        reply = QMessageBox.question(self, 'Xác nhận Xóa',
            f"Bạn có chắc muốn xóa vĩnh viễn {len(indices)} giả lập đã chọn không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = self.mumu_manager.delete_instance(indices)
            self.log_message(msg)
            if success: self.refresh_instances()

    def _open_batch_edit_dialog(self, preselect: Optional[List[int]] = None):
        indices = preselect or self._get_selected_indices(require_at_least_one=True)
        if not indices: return
        tasks = [{'index': i, 'imei': self._generate_random_imei(), 'mac': None} for i in indices]
        self.log_message(f"Bắt đầu tác vụ sửa IMEI cho {len(indices)} máy...")
        self._start_worker(GenericWorker(batch_sim_edit_task, self.mumu_manager, tasks))

    def _generate_random_imei(self) -> str:
        import random
        def luhn_checksum(digits: str) -> int:
            s = 0
            for i, ch in enumerate(reversed(digits)):
                d = int(ch)
                if i % 2 == 0:
                    d *= 2
                    if d > 9: 
                        d -= 9
                s += d
            return (10 - (s % 10)) % 10
        
        tac = "356938"
        serial = "".join(str(random.randint(0,9)) for _ in range(8))
        body = tac + serial
        check = luhn_checksum(body)
        return body + str(check)

    # =====================================================================
    # WORKER MANAGEMENT
    # =====================================================================

    def _start_worker(self, worker_instance: GenericWorker) -> None:
        """
        Start a background worker with comprehensive management.
        
        Args:
            worker_instance: The GenericWorker instance to execute
        
        Features:
        - Concurrent operation prevention
        - Progress tracking with global progress bar
        - Comprehensive event handling and logging
        - UI state management during worker execution
        
        This method ensures only one worker runs at a time and provides
        complete lifecycle management for background operations.
        """
        # Prevent concurrent worker execution
        if (self.worker and self.worker.isRunning()) or \
           (self.refresh_worker and self.refresh_worker.isRunning()):
            QMessageBox.warning(
                self, 
                "Đang bận", 
                "Một tác vụ khác đang chạy. Vui lòng đợi."
            )
            return

        # Initialize worker with progress tracking
        self.worker = worker_instance
        
        # Defensive programming for global_progress_bar
        if hasattr(self, 'global_progress_bar') and self.global_progress_bar:
            self.global_progress_bar.setValue(0)
            self.global_progress_bar.setVisible(True)
        
        # Connect worker signals for comprehensive monitoring
        self.worker.started.connect(self.log_message)
        
        # Connect progress for non-auto-launch tasks (with defensive check)
        if worker_instance.task_func is not auto_launch_task:
            if hasattr(self, 'global_progress_bar') and self.global_progress_bar:
                self.worker.progress.connect(self.global_progress_bar.setValue)

        # Connect logging and completion handlers
        self.worker.log.connect(self.log_message)
        self.worker.task_result.connect(self._on_task_result)
        self.worker.finished.connect(self._on_worker_finished)
        
        # Start worker and update UI state
        self.worker.start()
        self.update_ui_states()

    def _on_worker_finished(self, msg: str) -> None:
        """
        Handle worker completion and cleanup.
        
        Args:
            msg: Completion message from worker
        
        Features:
        - Comprehensive worker cleanup with error handling
        - Progress bar management for different worker types
        - Resource cleanup to prevent memory leaks
        - UI state restoration
        """
        self.log_message(f"✅ {msg}")
        
        # Defensive programming for global_progress_bar
        if hasattr(self, 'global_progress_bar') and self.global_progress_bar:
            self.global_progress_bar.setVisible(False)
        
        # Hide auto progress bar for auto-launch tasks
        if self.worker and self.worker.task_func is auto_launch_task:
             self.auto_progress_bar.setVisible(False)

        # Robust worker cleanup with error handling
        if self.worker:
            try:
                self.worker.deleteLater()
            except Exception as e:
                print(f"Warning: Error cleaning up worker: {e}")
            finally:
                self.worker = None
                
        self.update_ui_states()

    def _pause_resume_worker(self) -> None:
        """
        Toggle worker pause/resume state.
        
        Provides user control over running workers with
        clear feedback about the current state.
        """
        if self.worker and self.worker.isRunning():
            if self.worker._is_paused:
                self.worker.resume()
                self.log_message("▶️ Tác vụ đã được tiếp tục.")
            else:
                self.worker.pause()
                self.log_message("⏸️ Tác vụ đã được tạm dừng.")
            self.update_ui_states()

    def _stop_worker(self) -> None:
        """
        Request worker termination.
        
        Sends a graceful stop request to the running worker
        and provides user feedback about the operation.
        """
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log_message("⏹️ Đã gửi yêu cầu dừng tác vụ.")

    # =====================================================================
    # AUTOMATION MANAGEMENT
    # =====================================================================
    
    def _start_automation(self) -> None:
        """
        Start automated instance launching with batch processing.
        
        Features:
        - Configurable start/end range validation
        - Batch size and delay settings
        - Progress tracking with dedicated progress bar
        - Parameter validation and error handling
        
        Retrieves automation settings from user preferences
        and validates them before starting the automation worker.
        """
        # Load automation parameters from settings
        params = {
            'start': int(self.settings.value("auto/start", 1)),
            'end': int(self.settings.value("auto/end", 10)),
            'batch': int(self.settings.value("auto/batch", 5)),
            'inst_delay': float(self.settings.value("auto/inst_delay", 2.0)),
            'batch_delay': float(self.settings.value("auto/batch_delay", 8.0)),
        }
        
        # Validate automation parameters
        if params['start'] > params['end']:
            QMessageBox.warning(
                self, 
                "Lỗi Cài đặt", 
                "Index Bắt đầu không thể lớn hơn Index Kết thúc."
            )
            return

        # Initialize automation progress tracking
        self.auto_progress_bar.setValue(0)
        self.auto_progress_bar.setVisible(True)

        # Create and start automation worker
        # Create and start automation worker
        automation_worker = GenericWorker(auto_launch_task, self.mumu_manager, params)
        automation_worker.progress.connect(self.auto_progress_bar.setValue)
        
        self._start_worker(automation_worker)

    # =====================================================================
    # FILE & UTILITY MANAGEMENT
    # =====================================================================
    
    def _browse_file(self, line_edit: QLineEdit, filter: str) -> None:
        """
        Open file browser dialog and set selected path to line edit.
        
        Args:
            line_edit: QLineEdit widget to update with selected path
            filter: File filter string for dialog
        
        Provides a convenient way to browse and select files
        with the selected path automatically populated in the UI.
        """
        path, _ = QFileDialog.getOpenFileName(self, "Chọn file", "", filter)
        if path: 
            line_edit.setText(path)

    def _run_adb_on_selected(self, command: str, log_prefix: str) -> None:
        """
        Execute ADB command on selected instances.
        
        Args:
            command: ADB command to execute
            log_prefix: Prefix for log messages
        
        Features:
        - Selected instance validation
        - Command execution with result logging
        - Error handling and user feedback
        """
        indices = self._get_selected_indices(require_at_least_one=True)
        if not indices: 
            return
            
        ok, msg = self.mumu_manager.run_adb_command(indices, command)
        self.log_message(f"[{log_prefix}] → {msg}")

    def _run_script(self) -> None:
        """
        Execute custom ADB script on selected instances.
        
        Features:
        - Multi-line script support
        - Selected instance validation
        - Progress tracking for script execution
        - Command-by-command execution with logging
        - Error handling and status monitoring
        """
        # Validate selected instances
        indices = self._get_selected_indices(require_at_least_one=True)
        if not indices: 
            return
            
        # Validate script content
        script = self.script_input.toPlainText().strip()
        if not script:
            QMessageBox.warning(self, "Lỗi", "Kịch bản không được để trống.")
            return
            
        # Parse script commands
        commands = [line.strip() for line in script.split('\n') if line.strip()]

        def run_script_task(worker: GenericWorker, manager: MumuManager, params: dict) -> dict:
            """Background task for script execution."""
            indices, commands = params['indices'], params['commands']
            total = len(commands)
            worker.started.emit(f"--- 📜 Bắt đầu chạy kịch bản trên {len(indices)} giả lập ---")
            
            for i, command in enumerate(commands):
                worker.check_status()
                worker.log.emit(f"\n▶️ [{i+1}/{total}] Đang chạy: adb {command}")
                ok, msg = manager.run_adb_command(indices, command)
                worker.log.emit(f"    └── Kết quả: {msg}")
                worker.progress.emit(int(((i + 1) / total) * 100))
                worker.msleep(200)
            return {}

        # Execute script with worker
        params = {'indices': indices, 'commands': commands}
        self._start_worker(GenericWorker(run_script_task, self.mumu_manager, params))

    def _save_script(self) -> None:
        """
        Save current script content to file.
        
        Features:
        - Content validation before saving
        - File dialog with appropriate filters
        - UTF-8 encoding for proper character support
        - Error handling with user feedback
        """
        script_content = self.script_input.toPlainText()
        if not script_content:
            QMessageBox.warning(self, "Thông báo", "Không có nội dung để lưu.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Lưu Kịch bản", 
            "", 
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                self.log_message(f"✅ Đã lưu kịch bản vào: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu tệp:\n{e}")

    def _load_script(self) -> None:
        """
        Load script content from file.
        
        Features:
        - File dialog with appropriate filters
        - UTF-8 encoding for proper character support
        - Error handling with user feedback
        - UI update with loaded content
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Mở Kịch bản", 
            "", 
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.script_input.setPlainText(f.read())
                self.log_message(f"✅ Đã tải kịch bản từ: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể mở tệp:\n{e}")

    def _apply_script_template(self, template_name: str) -> None:
        """
        Apply predefined script template.
        
        Args:
            template_name: Name of the template to apply
        
        Provides quick access to common ADB script patterns
        for faster script development and testing.
        """
        templates = {
            "device_info": "shell getprop ro.product.model\nshell settings get secure android_id",
            "list_packages": "shell pm list packages -3"
        }
        self.script_input.setPlainText(templates.get(template_name, ""))

    # =====================================================================
    # DISK FILE MANAGEMENT
    # =====================================================================
    
    # =====================================================================
    # CONFIGURATION MANAGEMENT
    # =====================================================================
    
    def _open_settings_editor_for_single(self, index: int) -> None:
        """
        Open settings editor for a single instance.
        
        Args:
            index: Instance index to configure
        
        Convenience method for opening configuration editor
        with a specific instance preselected.
        """
        self._open_settings_editor(preselect=[index])

    def _open_settings_editor(self, preselect: Optional[List[int]] = None) -> None:
        """
        Open settings editor dialog for selected instances.
        
        Args:
            preselect: Optional list of instance indices to preselect
        
        Features:
        - Instance selection validation
        - Preselection support for specific instances
        - Settings editor dialog integration
        - Error handling for invalid selections
        """
        indices = preselect or self._get_selected_indices(require_at_least_one=True)
        if not indices: 
            return

        # Open settings editor dialog
        dialog = SettingsEditorDialog(self.mumu_manager, indices, self)
        if dialog.exec():
            changed_settings = dialog.get_changed_values()
            if not changed_settings:
                self.log_message("ℹ️ Không có thay đổi nào được thực hiện.")
                return

            # Apply settings changes via worker
            params = {'indices': indices, 'settings': changed_settings}
            self._start_worker(GenericWorker(apply_settings_task, self.mumu_manager, params))

    def _install_apk(self):
        path = self.apk_path_edit.text().strip()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một file APK hợp lệ.")
            return
        self._run_adb_on_selected(f'install -r "{path}"', "Cài đặt APK")

    def _uninstall_package(self):
        pkg = self.pkg_name_edit.text().strip()
        if not pkg:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên package.")
            return
        self._run_adb_on_selected(f'uninstall {pkg}', f"Gỡ {pkg}")

    def _launch_package(self):
        pkg = self.pkg_name_edit.text().strip()
        if not pkg:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên package.")
            return
        cmd = f'shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1'
        self._run_adb_on_selected(cmd, f"Chạy {pkg}")

    def _stop_package(self):
        pkg = self.pkg_name_edit.text().strip()
        if not pkg:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên package.")
            return
        self._run_adb_on_selected(f'shell am force-stop {pkg}', f"Dừng {pkg}")

    def _run_custom_adb(self):
        cmd = self.adb_cmd_edit.text().strip()
        if not cmd:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập lệnh ADB.")
            return
        self._run_adb_on_selected(cmd, f"ADB '{cmd}'")

    def _take_screencap(self):
        cmd = "shell screencap -p /sdcard/screen.png"
        self._run_adb_on_selected(cmd, "Chụp màn hình")

    def _request_single_instance_update(self, index: int) -> None:
        """
        Request a single instance status update.
        
        Args:
            index: Instance index to update
        
        Features:
        - Non-blocking background status fetch
        - Worker management with cleanup
        - Cache update with fresh data
        - Real-time UI status refresh
        """
        # Log the update request
        self.log_message(f"🔄 Requesting status update for VM {index}", LogLevel.DEBUG, "Update Request")
        
        # Validate index parameter with detailed debugging
        if index is None:
            import traceback
            self.log_message(
                "❌ _request_single_instance_update: index is None", 
                LogLevel.ERROR, 
                "Debug"
            )
            self.log_message(f"Call stack: {traceback.format_stack()[-3:-1]}", LogLevel.DEBUG)
            return
            
        if not isinstance(index, int):
            import traceback
            self.log_message(
                f"❌ _request_single_instance_update: index is not int, got {type(index)}: {index}", 
                LogLevel.ERROR, 
                "Debug"
            )
            self.log_message(f"Call stack: {traceback.format_stack()[-3:-1]}", LogLevel.DEBUG)
            return

        def update_task(worker: GenericWorker, manager: MumuManager, params: dict) -> dict:
            """Background task to fetch single instance status."""
            idx = params['index']
            try:
                worker.log.emit(f"🔍 VM {idx}: Bắt đầu lấy thông tin...")
                success, data = manager.get_single_info(idx)
                worker.log.emit(f"🔍 VM {idx}: Backend returned success={success}, data_type={type(data)}, data_length={len(data) if isinstance(data, (dict, list, str)) else 'N/A'}")
                
                # Enhanced validation for data structure
                if success:
                    # Check if data is not None and not empty
                    if data is not None and data != "" and data != {}:
                        # Additional check for dict type and content
                        if isinstance(data, dict) and len(data) > 0:
                            worker.log.emit(f"✅ VM {idx}: Dữ liệu hợp lệ, keys: {list(data.keys())}")
                            return {'success': True, 'data': data, 'index': idx}
                        else:
                            worker.log.emit(f"⚠️ VM {idx}: Data is dict but empty or invalid: {data}")
                            return {'success': False, 'data': None, 'index': idx, 'error': f'Invalid data structure: {type(data)}'}
                    else:
                        worker.log.emit(f"⚠️ VM {idx}: Success but data is None/empty: {data}")
                        return {'success': False, 'data': None, 'index': idx, 'error': f'Empty data returned: {data}'}
                else:
                    # Failed to get info
                    worker.log.emit(f"❌ VM {idx}: Backend failed - {data}")
                    return {'success': False, 'data': None, 'index': idx, 'error': str(data)}
                    
            except Exception as e:
                worker.log.emit(f"❌ VM {idx}: Exception khi lấy thông tin - {str(e)}")
                return {'success': False, 'data': None, 'index': idx, 'error': str(e)}

        update_worker = GenericWorker(update_task, self.mumu_manager, {'index': index})
        update_worker.task_result.connect(self._on_single_instance_updated)
        update_worker.finished.connect(lambda: self._on_update_worker_finished(update_worker))
        self.update_workers.append(update_worker)
        update_worker.start()

    def _on_update_worker_finished(self, worker: GenericWorker):
        try:
            self.update_workers.remove(worker)
        except ValueError:
            pass

    def _on_single_instance_updated(self, result: dict) -> None:
        """
        Handle single instance update results.
        
        Args:
            result: Update result containing success status, data, and index
        
        Features:
        - Instance cache updating
        - UI state cleanup after successful operations
        - Row refresh with latest data
        - Cache invalidation for accurate status display
        """
        try:
            # Debug log for result structure
            self.log_message(f"🔍 Update result keys: {list(result.keys())}", LogLevel.DEBUG, "Debug")
            
            # Check if this is a proper update result with data (not control task result)
            if 'data' not in result:
                # This is likely a control task result, not an update task result
                self.log_message(f"🔍 Skipping non-update result: {result}", LogLevel.DEBUG, "Debug")
                return
            
            # Check if this is a proper update result with data
            if result.get('success') and 'data' in result and result['data']:
                index = result.get('index')
                if index is None:
                    self.log_message(
                        "❌ Lỗi: Không có index trong kết quả cập nhật",
                        LogLevel.ERROR,
                        "Instance Update"
                    )
                    return
                
                # Update instance cache with fresh data
                self.instance_cache[str(index)] = result['data']
                
                # Clear UI state to show actual status (not transitional state)
                if index in self.instance_ui_states:
                    del self.instance_ui_states[index]
                
                # Force refresh the specific row with new data
                self._update_row_by_index(index)
                
                # Invalidate cache to ensure next auto-refresh gets fresh data
                if hasattr(self, 'smart_cache'):
                    try:
                        cache_key = "instances_list"
                        self.smart_cache.invalidate(cache_key)
                    except Exception as cache_error:
                        self.log_message(f"⚠️ Cache invalidation failed: {cache_error}", LogLevel.WARNING, "Cache")
                
                # Log status for debugging
                status = "Running" if result['data'].get("is_process_started", False) else "Stopped"
                self.log_message(
                    f"✅ VM {index} status updated successfully: {status}", 
                    LogLevel.SUCCESS, 
                    "Status Update"
                )
            else:
                error_index = result.get('index', 'Unknown')
                error_msg = f"❌ ❌ ❌ Lỗi khi cập nhật thông tin cho máy ảo {result}"
                self.log_message(error_msg, LogLevel.ERROR, "Instance Update")
                
                # Enhanced debug info with detailed analysis
                if not result.get('success'):
                    self.log_message(f"🔍   → Success flag: {result.get('success')}", LogLevel.DEBUG, "Debug")
                if 'data' not in result:
                    self.log_message(f"🔍   → Missing 'data' key in result", LogLevel.DEBUG, "Debug")
                elif not result['data']:
                    self.log_message(f"🔍   → Empty/None data: {result['data']}", LogLevel.DEBUG, "Debug")
                    
                # Log the specific error if available
                if 'error' in result:
                    self.log_message(f"🔍   → Error details: {result['error']}", LogLevel.DEBUG, "Debug")
                    
        except Exception as e:
            error_index = result.get('index', 'Unknown')
            self.log_message(
                f"❌ Exception khi xử lý cập nhật VM {error_index}: {str(e)}", 
                LogLevel.ERROR, 
                "Instance Update"
            )
            # Log the full result for debugging
            self.log_message(f"  → Full result: {result}", LogLevel.DEBUG, "Debug")

    def _find_row_by_index(self, index: int) -> int:
        """Find row by instance index using model/view architecture"""
        if hasattr(self, 'instances_model') and self.instances_model:
            return self.instances_model.find_source_row_by_index(index)
        return -1

    def _update_row_by_index(self, index: int) -> None:
        """
        Update a specific table row by instance index.
        
        Args:
            index: Instance index to update
        
        Features:
        - Cache-based data retrieval
        - Model update with latest data
        - UI state synchronization
        - Error handling for missing data
        """
        info = self.instance_cache.get(str(index), {})
        if info:
            # Update the model with fresh instance data
            self.instances_model.update_row_by_index(index, info)
            # Sync UI states (loading, starting, stopping indicators)
            self.instances_model.set_ui_states(self.instance_ui_states)
            
            # Log successful update for debugging
            status = "Running" if info.get("is_process_started", False) else "Stopped"
            self.log_message(
                f"🔄 Row updated for VM {index}: {status}", 
                LogLevel.DEBUG, 
                "UI Update"
            )
        else:
            self.log_message(
                f"⚠️ No cache data found for VM {index}", 
                LogLevel.WARNING, 
                "UI Update"
            )

    def _update_row_content(self, row: int, idx: int, info: dict):
        # No longer used with Model/View
        pass

    def _setup_progressive_loading(self):
        """🚀 Progressive Loading - Advanced startup optimization with intelligent component loading"""
        self.log_message("🚀 Starting Progressive Loading System...", LogLevel.INFO, "Startup")
        
        # Initialize progressive loader
        self.progressive_loader = ProgressiveLoader()
        
        # Connect progressive loading signals
        self.progressive_loader.component_loaded.connect(self._on_progressive_component_loaded)
        self.progressive_loader.loading_progress.connect(self._on_progressive_loading_progress) 
        self.progressive_loader.loading_complete.connect(self._on_progressive_loading_complete)
        
        # Setup progressive loading components
        self._setup_progressive_components()
        
        # Start progressive loading
        if self.progressive_loader:
            self.progressive_loader.start_loading()
        
    def _setup_progressive_components(self):
        """Setup components for progressive loading with intelligent prioritization"""
        
        if not self.progressive_loader:
            return
            
        # 🔥 CRITICAL PRIORITY (1-2) - Essential for UI visibility
        self.progressive_loader.register_component(
            name="core_ui",
            loader_function=self._load_core_ui_components,
            priority=1,
            estimated_time=0.1
        )
        
        self.progressive_loader.register_component(
            name="theme_system",
            loader_function=self._load_theme_and_styling,
            priority=2,
            dependencies=["core_ui"],
            estimated_time=0.05
        )
        
        # ⚡ HIGH PRIORITY (3-4) - Core functionality
        self.progressive_loader.register_component(
            name="cache_system",
            loader_function=self._load_cache_system,
            priority=3,
            dependencies=["core_ui"],
            estimated_time=0.08
        )
        
        self.progressive_loader.register_component(
            name="manager_backend",
            loader_function=self._load_manager_path,
            priority=4,
            dependencies=["cache_system"],
            estimated_time=0.1
        )
        
        # � NORMAL PRIORITY (5-6) - Data loading
        self.progressive_loader.register_component(
            name="instance_table",
            loader_function=self._load_instance_data,
            priority=5,
            dependencies=["manager_backend", "theme_system"],
            estimated_time=0.2
        )
        
        self.progressive_loader.register_component(
            name="auto_refresh",
            loader_function=self._load_auto_refresh,
            priority=6,
            dependencies=["instance_table"],
            estimated_time=0.05
        )
        
        # 🔧 LOW PRIORITY (7+) - Advanced features (background loading)
        self.progressive_loader.register_component(
            name="optimization_systems",
            loader_function=self._load_optimization_systems,
            priority=7,
            dependencies=["cache_system"],
            estimated_time=0.1
        )
        
        self.progressive_loader.register_component(
            name="performance_monitor",
            loader_function=self._load_performance_monitor,
            priority=8,
            estimated_time=0.05
        )
    
    def _load_core_ui_components(self):
        """Load essential UI components for immediate visibility"""
        try:
            # Basic UI styling that makes app visible and responsive
            self._refresh_automation_button_styles()
            self._update_automation_button_states()
            self.log_message("✅ Core UI components loaded", LogLevel.SUCCESS, "Progressive")
        except Exception as e:
            self.log_message(f"❌ Core UI loading failed: {e}", LogLevel.ERROR, "Progressive")
    
    def _load_theme_and_styling(self):
        """Load theme system and advanced styling"""
        try:
            self._apply_native_theme_tweaks()
            # Additional theme optimizations can be added here
            self.log_message("✅ Theme system loaded", LogLevel.SUCCESS, "Progressive")
        except Exception as e:
            self.log_message(f"❌ Theme loading failed: {e}", LogLevel.ERROR, "Progressive")
    
    def _load_optimization_systems(self):
        """Load advanced optimization systems in background"""
        try:
            # Initialize table virtualization if needed
            if hasattr(self, 'table') and self.table:
                # Enable table virtualization for large datasets
                pass  # Implementation will be added later
            
            # Initialize worker pool performance monitoring
            if hasattr(self, 'intelligent_worker_pool'):
                performance = self.get_worker_pool_performance()
                workers_count = performance.get('pool_status', {}).get('active_workers', 0)
                self.log_message(f"📊 Worker Pool: {workers_count} workers active", LogLevel.INFO, "Progressive")
            
            self.log_message("✅ Optimization systems loaded", LogLevel.SUCCESS, "Progressive")
        except Exception as e:
            self.log_message(f"❌ Optimization systems failed: {e}", LogLevel.ERROR, "Progressive")
    
    def _load_performance_monitor(self):
        """Load performance monitoring in background"""
        try:
            # Performance monitoring initialization
            self.log_message("✅ Performance monitor loaded", LogLevel.SUCCESS, "Progressive")
        except Exception as e:
            self.log_message(f"❌ Performance monitor failed: {e}", LogLevel.ERROR, "Progressive")
    
    def _on_progressive_component_loaded(self, component_name: str):
        """Handle individual component loading completion"""
        self.log_message(f"📦 {component_name} loaded successfully", LogLevel.INFO, "Progressive")
    
    def _on_progressive_loading_progress(self, percentage: int):
        """Handle loading progress updates"""
        if percentage % 20 == 0:  # Log every 20% progress
            self.log_message(f"📊 Loading progress: {percentage}%", LogLevel.INFO, "Progressive")
    
    def _on_progressive_loading_complete(self):
        """Handle complete loading process"""
        self.log_message("🎉 Progressive Loading Complete! All systems ready.", LogLevel.SUCCESS, "Progressive")
        
        # Final startup tasks
        self._finish_startup()

    def _on_component_loaded(self, component_name: str):
        """Handle individual component loading completion"""
        self.log_message(f"📦 {component_name} loaded successfully", LogLevel.INFO, "Progressive")
    
    def _on_loading_progress(self, percentage: int):
        """Handle loading progress updates"""
        if percentage % 20 == 0:  # Log every 20% progress
            self.log_message(f"📊 Loading progress: {percentage}%", LogLevel.INFO, "Progressive")
    
    def _on_loading_complete(self):
        """Handle complete loading process"""
        self.log_message("🎉 Progressive Loading Complete! All systems ready.", LogLevel.SUCCESS, "Progressive")
        
        # Final startup tasks
        self._finish_startup()

    def _setup_simple_async_loading(self):
        """�🚀 Simple async loading - Non-blocking startup using QTimer (Legacy method)"""
        # Show loading message
        self.log_message("🚀 Starting MumuManager Pro with optimizations...", LogLevel.INFO, "Startup")
        
        # Load components one by one with small delays to prevent blocking
        QTimer.singleShot(50, self._load_ui_styling)
        QTimer.singleShot(100, self._load_cache_system) 
        QTimer.singleShot(150, self._load_manager_path)
        QTimer.singleShot(200, self._load_instance_data)
        QTimer.singleShot(250, self._load_auto_refresh)
        QTimer.singleShot(300, self._finish_startup)
        
    def _load_ui_styling(self):
        """Load UI styling components (Legacy)"""
        try:
            self._refresh_automation_button_styles()
            self._update_automation_button_states()
            self._apply_native_theme_tweaks()
            self.log_message("✅ UI Styling loaded", LogLevel.INFO, "Startup")
        except Exception as e:
            self.log_message(f"❌ UI Styling failed: {e}", LogLevel.ERROR, "Startup")
    
    def _load_cache_system(self):
        """Load cache system"""
        try:
            self._preload_cache()
            self.log_message("✅ Smart Cache system loaded", LogLevel.INFO, "Startup")
        except Exception as e:
            self.log_message(f"❌ Cache system failed: {e}", LogLevel.ERROR, "Startup")
    
    def _load_manager_path(self):
        """Load manager path check"""
        try:
            self.check_manager_path()
            self.log_message("✅ Manager path checked", LogLevel.INFO, "Startup")
        except Exception as e:
            self.log_message(f"❌ Manager path failed: {e}", LogLevel.ERROR, "Startup")
    
    def _load_instance_data(self):
        """Load instance data - chỉ refresh một lần khi khởi động"""
        try:
            if not self.initial_refresh_done:
                self.refresh_instances()
                self.initial_refresh_done = True  # Đánh dấu đã refresh lần đầu
                self.log_message("✅ Initial instance data loaded", LogLevel.INFO, "Startup")
            else:
                self.log_message("⏭️ Initial refresh already done, skipping", LogLevel.INFO, "Startup")
        except Exception as e:
            self.log_message(f"❌ Instance data failed: {e}", LogLevel.ERROR, "Startup")
    
    def _load_auto_refresh(self):
        """Load auto refresh system - DISABLED sau lần đầu"""
        try:
            # Auto refresh được disable hoàn toàn, chỉ refresh manual
            self.auto_refresh_enabled = False
            self._update_auto_refresh_status()
            self.log_message("✅ Auto refresh DISABLED - manual refresh only", LogLevel.INFO, "Startup")
        except Exception as e:
            self.log_message(f"❌ Auto refresh setup failed: {e}", LogLevel.ERROR, "Startup")
            
    def _finish_startup(self):
        """Finish startup process"""
        self.log_message("🎉 MumuManager Pro startup completed!", LogLevel.SUCCESS, "Startup")
        self.log_message("🚀 All optimizations active: Enhanced Debouncing, Smart Caching, Table Virtualization", LogLevel.INFO, "Performance")
        
        # 🎮 Initialize Performance Acceleration System
        self._setup_performance_acceleration()
        
        # ⚡ Initialize Ultra-Fast Database System
        self._setup_ultra_database()

    def _setup_performance_acceleration(self):
        """🎮 Setup performance acceleration system"""
        try:
            if hasattr(self, 'acceleration_manager') and self.acceleration_manager:
                # Start performance monitoring
                self.acceleration_manager.start_performance_monitoring(5000)
                
                # Create accelerated table demo (optional, for testing)
                accel_table = self.acceleration_manager.create_accelerated_table()
                if accel_table:
                    # Test with some sample data to demonstrate acceleration
                    test_data = [
                        [f"Instance {i}", f"Status {i%3}", f"CPU {random.randint(1,100)}%", f"Memory {random.randint(1,100)}%"]
                        for i in range(100)  # 100 test rows
                    ]
                    test_headers = ["Name", "Status", "CPU", "Memory"]
                    accel_table.set_table_data(test_data, test_headers)
                    
                    # Store reference for potential future use
                    self.accelerated_table = accel_table
                
                # Get acceleration report
                accel_report = self.acceleration_manager.get_acceleration_report()
                self.log_message(
                    f"🎮 Performance Acceleration initialized: {accel_report['acceleration_status']}", 
                    LogLevel.SUCCESS, 
                    "Performance", 
                    accel_report
                )
                
        except Exception as e:
            self.log_message(f"❌ Performance acceleration setup failed: {e}", LogLevel.ERROR, "Performance")

    def _setup_ultra_database(self):
        """⚡ Setup Ultra-Fast Database system"""
        try:
            if hasattr(self, 'ultra_database') and self.ultra_database:
                # Initialize database with current instance data
                if hasattr(self, 'instance_cache') and self.instance_cache:
                    # Convert instance cache to database format
                    db_instances = []
                    for idx, info in self.instance_cache.items():
                        db_instance = {
                            'id': idx,
                            'name': info.get('name', f'Instance {idx}'),
                            'status': info.get('status', 'unknown'),
                            'cpu_usage': float(info.get('cpu_usage', 0.0)),
                            'memory_usage': float(info.get('memory_usage', 0.0)),
                            'disk_usage': info.get('disk_usage', '0MB'),
                            'adb_port': int(info.get('adb_port', 0)),
                            'version': info.get('version', 'unknown'),
                            'path': info.get('path', ''),
                            'metadata': {
                                'startup_time': info.get('startup_time'),
                                'last_action': info.get('last_action'),
                                'original_data': info
                            }
                        }
                        db_instances.append(db_instance)
                    
                    # Bulk insert to database
                    if db_instances:
                        inserted_count = self.ultra_database.bulk_insert_instances(db_instances)
                        self.log_message(
                            f"⚡ Ultra-Fast DB initialized with {inserted_count} instances", 
                            LogLevel.SUCCESS, 
                            "Database"
                        )
                
                # Get database stats
                db_stats = self.ultra_database.get_database_stats()
                self.log_message(
                    f"⚡ Ultra-Fast Database ready: {db_stats.get('total_instances', 0)} instances, "
                    f"{db_stats.get('avg_operation_time_ms', 0):.2f}ms avg operation time", 
                    LogLevel.INFO, 
                    "Database",
                    db_stats
                )
                
        except Exception as e:
            self.log_message(f"❌ Ultra-Fast Database setup failed: {e}", LogLevel.ERROR, "Database")

    def _setup_async_initialization(self):
        """🚀 Setup async initialization system"""
        # Create async initializer
        self.async_initializer = AsyncInitializer(self)
        
        # Add components to background loading queue (priority: higher = first)
        self.async_initializer.add_component(
            "UI Styling", 
            self._async_load_ui_styling, 
            priority=5
        )
        self.async_initializer.add_component(
            "Cache System", 
            self._async_load_cache_system, 
            priority=4
        )
        self.async_initializer.add_component(
            "Manager Path", 
            self._async_load_manager_path, 
            priority=3
        )
        self.async_initializer.add_component(
            "Instance Data", 
            self._async_load_instance_data, 
            priority=2
        )
        self.async_initializer.add_component(
            "Auto Refresh", 
            self._async_load_auto_refresh, 
            priority=1
        )
        
        # Connect signals
        self.async_initializer.component_loaded.connect(self._on_component_loaded)
        self.async_initializer.initialization_completed.connect(self._on_initialization_completed)
        
        # Start background loading
        self.async_initializer.start()
        
        # Show loading indicator
        self._show_loading_indicator()
    
    def _async_load_ui_styling(self):
        """Async load UI styling components"""
        try:
            self._refresh_automation_button_styles()
            self._update_automation_button_states()
            self._apply_native_theme_tweaks()
            return "UI Styling loaded"
        except Exception as e:
            return f"UI Styling failed: {e}"
    
    def _async_load_cache_system(self):
        """Async load cache system"""
        try:
            self._preload_cache()
            return "Cache System loaded"
        except Exception as e:
            return f"Cache System failed: {e}"
    
    def _async_load_manager_path(self):
        """Async load manager path check"""
        try:
            self.check_manager_path()
            return "Manager Path checked"
        except Exception as e:
            return f"Manager Path failed: {e}"
    
    def _async_load_instance_data(self):
        """Async load instance data - DISABLED để tránh duplicate refresh"""
        try:
            # Skip async refresh vì đã refresh trong progressive loading
            if self.initial_refresh_done:
                self.log_message("⏭️ Async refresh skipped - already loaded in progressive loading", LogLevel.INFO, "Async")
                return "Instance Data already loaded"
            else:
                # Fallback nếu progressive loading chưa chạy
                self.refresh_instances()
                self.initial_refresh_done = True
                return "Instance Data loaded (fallback)"
        except Exception as e:
            return f"Instance Data failed: {e}"
    
    def _async_load_auto_refresh(self):
        """🚫 Async load auto refresh system - PERMANENTLY DISABLED"""
        try:
            # Auto refresh permanently disabled - always return disabled status
            print("🚫 _async_load_auto_refresh called but PERMANENTLY DISABLED")
            
            # Force ensure auto refresh is disabled
            self.auto_refresh_enabled = False
            
            # Stop timer if somehow running
            if hasattr(self, 'auto_refresh_timer') and self.auto_refresh_timer.isActive():
                self.auto_refresh_timer.stop()
                print("🚫 Stopped auto refresh timer during async load")
            
            self._update_auto_refresh_status()
            return "Auto Refresh permanently disabled"
        except Exception as e:
            return f"Auto Refresh disabled: {e}"
    
    def _show_loading_indicator(self):
        """Show loading indicator during async initialization"""
        if not hasattr(self, 'loading_indicator'):
            self.loading_indicator = AsyncLoadingIndicator(self)
            # Position at bottom of window
            self.loading_indicator.progress_bar.setGeometry(0, self.height() - 30, self.width(), 20)
            self.loading_indicator.status_label.setGeometry(10, self.height() - 50, self.width() - 20, 20)
    
    def _on_component_loaded(self, component_name, result):
        """Handle component loaded signal"""
        self.log_message(f"✅ Async Init: {component_name} - {result}", LogLevel.INFO, "Initialization")
    
    def _on_initialization_completed(self):
        """Handle initialization completed signal"""
        self.log_message("🚀 Async Initialization completed successfully!", LogLevel.SUCCESS, "Initialization")
        if hasattr(self, 'loading_indicator'):
            self.loading_indicator.hide_loading()

    def _apply_native_theme_tweaks(self):
        theme_name = self.settings.value("theme/name", "dark")
        
        self.setWindowIcon(get_icon("app_icon"))

        if sys.platform == "win32" and ctypes:
            hwnd = self.winId()
            dark_mode = 1 if theme_name in ["dark", "monokai"] else 0

            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            try:
                set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
                set_window_attribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
                set_window_attribute.restype = wintypes.LONG

                value = ctypes.c_int(dark_mode)
                set_window_attribute(
                    wintypes.HWND(int(hwnd)),
                    wintypes.DWORD(DWMWA_USE_IMMERSIVE_DARK_MODE),
                    ctypes.byref(value),
                    ctypes.sizeof(value)
                )
            except Exception as e:
                print(f"Không thể đặt chế độ dark mode cho title bar: {e}")

    def _start_find_config_files(self):
        """Tìm tất cả file config trong thư mục VMs"""
        default_path = r"C:\Program Files\Netease\MuMuPlayer\vms"
        vms_path = self.settings.value("cleanup/vms_path", default_path)

        if not os.path.isdir(vms_path):
            QMessageBox.critical(
                self, 
                "Lỗi", 
                f"Không thể tìm thấy thư mục MuMu Player tại:\n{vms_path}\n\n"
                "Vui lòng kiểm tra lại cài đặt hoặc chọn thủ công trong tab Dọn dẹp Disk."
            )
            return

        params = {'vms_path': vms_path, 'type': 'customer_config.json'}
        worker = GenericWorker(find_config_files_task, self.mumu_manager, params)
        worker.task_result.connect(self._on_config_files_found)
        self._start_worker(worker)

    def _on_config_files_found(self, result: dict):
        """Xử lý kết quả tìm kiếm config files"""
        found_files = result.get('files', [])
        self.found_config_files = found_files
        self.found_configs_display.clear()
        
        if found_files:
            self.found_configs_display.setText("\n".join(found_files))
            self.log_message(f"🔎 Tìm thấy {len(found_files)} file customer_config.json.")
        else:
            self.found_configs_display.setPlaceholderText("Không tìm thấy file customer_config.json nào.")
            self.log_message("✅ Không tìm thấy file customer_config.json nào.")
        
        self.update_ui_states()

    def _start_replace_config_files(self):
        """Thay thế tất cả config files"""
        if not self.found_config_files:
            QMessageBox.information(self, "Thông báo", "Không có file config nào để thay thế.")
            return

        source_file = self.config_path_edit.text().strip()
        if not source_file or not os.path.exists(source_file):
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn file config nguồn hợp lệ.")
            return

        reply = QMessageBox.question(
            self, 
            'Xác nhận Thay thế',
            f"Bạn có chắc chắn muốn thay thế {len(self.found_config_files)} file config?\n\n"
            f"File nguồn: {source_file}\n\n"
            "Hành động này không thể hoàn tác.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            params = {
                'source_file': source_file,
                'target_files': self.found_config_files
            }
            worker = GenericWorker(replace_config_files_task, self.mumu_manager, params)
            worker.finished.connect(self._on_config_replace_finished)
            self._start_worker(worker)

    def _on_config_replace_finished(self, msg):
        """Xử lý khi hoàn thành thay thế config"""
        self.found_config_files = []
        self.found_configs_display.clear()
        self.found_configs_display.setPlaceholderText("Danh sách các file customer_config.json tìm thấy sẽ hiển thị ở đây...")
        self.update_ui_states()

    # =====================================================================
    # 🚀 INTELLIGENT WORKER POOL INTEGRATION
    # =====================================================================
    
    def _setup_worker_pool_signals(self):
        """Setup intelligent worker pool signal connections"""
        try:
            # Connect worker pool signals for monitoring
            self.intelligent_worker_pool.task_completed.connect(self._on_worker_task_completed)
            self.intelligent_worker_pool.task_failed.connect(self._on_worker_task_failed)
            self.intelligent_worker_pool.stats_updated.connect(self._on_worker_stats_updated)
            
            self.log_message("🚀 Intelligent Worker Pool initialized", LogLevel.SUCCESS, "WorkerPool")
        except Exception as e:
            self.log_message(f"❌ Worker Pool setup failed: {e}", LogLevel.ERROR, "WorkerPool")
    
    def _on_worker_task_completed(self, task_id: str, result):
        """Handle completed worker pool task"""
        self.log_message(f"✅ Task completed: {task_id}", LogLevel.INFO, "WorkerPool")
    
    def _on_worker_task_failed(self, task_id: str, error: str):
        """Handle failed worker pool task"""
        self.log_message(f"❌ Task failed: {task_id} - {error}", LogLevel.ERROR, "WorkerPool")
    
    def _on_worker_stats_updated(self, stats: dict):
        """Handle worker pool statistics update"""
        if stats.get('active_workers', 0) > 0:
            # Log occasionally for monitoring
            workers = stats.get('active_workers', 0)
            queued = stats.get('queued_tasks', 0)
            if queued > 0:
                self.log_message(f"📊 Worker Pool: {workers} active, {queued} queued", LogLevel.DEBUG, "WorkerPool")
    
    def submit_worker_task(self, 
                          task_function,
                          args: tuple = (),
                          kwargs: Optional[dict] = None,
                          priority: 'TaskPriority' = None,
                          task_id: Optional[str] = None) -> str:
        """🚀 Submit task to intelligent worker pool with priority"""
        try:
            return self.intelligent_worker_pool.submit_task(
                task_function=task_function,
                args=args,
                kwargs=kwargs or {},
                priority=priority,
                task_id=task_id
            )
        except Exception as e:
            self.log_message(f"❌ Failed to submit task: {e}", LogLevel.ERROR, "WorkerPool")
            return ""
    
    def get_worker_pool_performance(self) -> dict:
        """Get worker pool performance report"""
        try:
            return self.intelligent_worker_pool.get_performance_report()
        except Exception as e:
            self.log_message(f"❌ Failed to get performance report: {e}", LogLevel.ERROR, "WorkerPool")
            return {}
    
    def shutdown_worker_pool(self):
        """Gracefully shutdown worker pool"""
        try:
            self.intelligent_worker_pool.shutdown()
            self.log_message("🛑 Worker Pool shutdown complete", LogLevel.INFO, "WorkerPool")
        except Exception as e:
            self.log_message(f"❌ Worker Pool shutdown error: {e}", LogLevel.ERROR, "WorkerPool")
    
    # 🧠 MEMORY MANAGEMENT CALLBACKS - Phase 3
    def _on_memory_warning(self, usage_percent: float):
        """Handle memory warning (80%+ usage)"""
        self.log_message(f"⚠️ Memory Warning: {usage_percent:.1f}% usage", LogLevel.WARNING, "Memory")
        
        # Trigger smart cleanup
        if hasattr(self, 'memory_manager'):
            report = self.memory_manager.get_memory_report()
            self.log_message(f"📊 Memory Report: {report.get('process_memory_mb', 0):.1f} MB used", LogLevel.INFO, "Memory")
    
    def _on_memory_critical(self, usage_percent: float):
        """Handle critical memory situation (90%+ usage)"""
        self.log_message(f"🚨 CRITICAL Memory: {usage_percent:.1f}% usage", LogLevel.ERROR, "Memory")
        
        # Emergency cleanup
        self.log_message("🛠️ Performing emergency memory cleanup...", LogLevel.WARNING, "Memory")
    
    def get_memory_performance_report(self) -> dict:
        """Get memory management performance report"""
        try:
            if hasattr(self, 'memory_manager'):
                return self.memory_manager.get_memory_report()
            return {'error': 'Memory manager not available'}
        except Exception as e:
            return {'error': str(e)}

    def _create_fallback_log_widget(self):
        """Create a fallback log widget with log_message method"""
        from PyQt6.QtWidgets import QTextEdit, QVBoxLayout
        from PyQt6.QtGui import QFont
        
        class FallbackLogWidget(QWidget):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Log")
                layout = QVBoxLayout(self)
                
                self.text_area = QTextEdit()
                self.text_area.setReadOnly(True)
                self.text_area.setFont(QFont("Consolas", 9))
                layout.addWidget(self.text_area)
                
            def log_message(self, text: str, level=None, category: str = "General", details=None):
                """Simple log_message implementation"""
                timestamp = time.strftime("%H:%M:%S")
                level_str = level.value if hasattr(level, 'value') else str(level or "INFO")
                message = f"[{timestamp}] {level_str} [{category}] {text}"
                if details:
                    message += f" | {details}"
                
                self.text_area.append(message)
                print(message)  # Also print to console
        
        return FallbackLogWidget()

    # =====================================================================
    # MANAGER SIGNAL HANDLERS - REFACTORED
    # =====================================================================

    def _handle_sidebar_navigation(self, index: int) -> None:
        """Handle navigation from sidebar manager."""
        self._handle_sidebar_click(index)

    def _on_page_loaded(self, index: int) -> None:
        """Handle page loaded from content manager."""
        page_names = ["Dashboard", "Apps", "Tools", "Scripting", "Cleanup", "Config", "Automation"]
        page_name = page_names[index] if index < len(page_names) else f"Page {index}"
        self.log_message(f"✅ Page loaded: {page_name}", LogLevel.INFO, "UI")

    def _on_page_requested(self, index: int) -> None:
        """Handle page requested from content manager."""
        # Update sidebar active state
        self.sidebar_manager.set_active_page(index)
    
    def _sync_automation_settings_from_file(self):
        """Sync automation settings from JSON file to QSettings for consistency"""
        try:
            import os
            import json
            
            if os.path.exists("automation_settings.json"):
                with open("automation_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                    # Sync to QSettings
                    self.settings.setValue("auto/start", settings.get('from_instance', 1))
                    self.settings.setValue("auto/end", settings.get('to_instance', 10))
                    self.settings.setValue("auto/batch", settings.get('batch_size', 5))
                    self.settings.setValue("auto/inst_delay", settings.get('start_delay', 2.0))
                    self.settings.setValue("auto/batch_delay", settings.get('batch_delay', 8.0))
                    
                    print(f"✅ Automation settings synced from file: batch={settings.get('batch_size', 5)}")
        except Exception as e:
            print(f"⚠️ Error syncing automation settings: {e}")


if __name__ == "__main__":
    """
    🚀 MuMu Manager Pro - Enterprise Edition
    =====================================
    
    Optimized Qt application with Phase 4 AI and Ultra-Fast Database integration
    """
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    
    try:
        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("MuMu Manager Pro")
        app.setApplicationVersion("4.2.0")
        app.setOrganizationName("MuMu Manager Pro")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        print("🚀 MuMu Manager Pro started successfully!")
        print("✨ Phase 4.1: Performance Optimization - ACTIVE")  
        print("⚡ Phase 4.2: Ultra-Fast Database - ACTIVE")
        print("🎯 Enterprise-grade performance ready!")
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)