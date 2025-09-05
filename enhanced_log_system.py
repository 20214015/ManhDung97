"""
Enhanced Log System for MumuManager Pro
Hệ thống log nâng cao với filtering, search, export, và real-time monitoring
"""

__all__ = [
    'LogLevel', 'LogEntry', 'LogStorage', 'EnhancedLogWidget',
    'log_debug', 'log_info', 'log_success', 'log_warning', 'log_error', 'log_critical'
]

import time
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
# from log_settings_dialog import LogSettingsDialog
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit,
    QComboBox, QCheckBox, QLabel, QSplitter, QFrame, QScrollArea,
    QGroupBox, QSpinBox, QFileDialog, QMessageBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings, QDateTime
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCharFormat, QIcon

class LogLevel(Enum):
    """Log levels with priorities"""
    DEBUG = (0, "🔍", "#6B7280")      # Gray
    INFO = (1, "ℹ️", "#3B82F6")       # Blue  
    SUCCESS = (2, "✅", "#10B981")    # Green
    WARNING = (3, "⚠️", "#F59E0B")    # Yellow
    ERROR = (4, "❌", "#EF4444")      # Red
    CRITICAL = (5, "🚨", "#DC2626")   # Dark Red

class LogEntry:
    """Enhanced log entry with metadata"""
    def __init__(self, message: str, level: LogLevel = LogLevel.INFO, 
                 category: str = "General", details: Optional[Dict] = None):
        self.timestamp = datetime.now()
        self.message = message
        self.level = level
        self.category = category
        self.details = details or {}
        self.id = int(time.time() * 1000000)  # Unique ID
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for export"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.name,
            'category': self.category,
            'message': self.message,
            'details': self.details
        }
        
    def formatted_time(self) -> str:
        """Get formatted timestamp"""
        return self.timestamp.strftime('%H:%M:%S')
        
    def formatted_message(self) -> str:
        """Get formatted message with icon"""
        icon = self.level.value[1]
        return f"[{self.formatted_time()}] {icon} {self.message}"

class LogStorage:
    """Enhanced log storage with search and filtering"""
    def __init__(self, max_entries: int = 5000):
        self.max_entries = max_entries
        self.entries: List[LogEntry] = []
        self._categories = set()
        
    def add_entry(self, entry: LogEntry):
        """Add log entry with automatic cleanup"""
        self.entries.append(entry)
        self._categories.add(entry.category)
        
        # Cleanup old entries
        if len(self.entries) > self.max_entries:
            # Remove oldest 20%
            remove_count = self.max_entries // 5
            self.entries = self.entries[remove_count:]
            
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return sorted(list(self._categories))
        
    def filter_entries(self, level_filter: Optional[LogLevel] = None,
                      category_filter: Optional[str] = None,
                      search_text: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[LogEntry]:
        """Filter entries based on criteria"""
        filtered = self.entries
        
        if level_filter:
            filtered = [e for e in filtered if e.level.value[0] >= level_filter.value[0]]
            
        if category_filter and category_filter != "All":
            filtered = [e for e in filtered if e.category == category_filter]
            
        if search_text:
            search_lower = search_text.lower()
            filtered = [e for e in filtered if search_lower in e.message.lower()]
            
        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]
            
        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]
            
        return filtered
        
    def get_stats(self) -> Dict:
        """Get log statistics"""
        stats = {level.name: 0 for level in LogLevel}
        categories = {}
        
        for entry in self.entries:
            stats[entry.level.name] += 1
            categories[entry.category] = categories.get(entry.category, 0) + 1
            
        return {
            'total_entries': len(self.entries),
            'by_level': stats,
            'by_category': categories,
            'oldest_entry': self.entries[0].timestamp if self.entries else None,
            'newest_entry': self.entries[-1].timestamp if self.entries else None
        }

class EnhancedLogWidget(QWidget):
    """Enhanced log widget with advanced features"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.storage = LogStorage()
        self.auto_scroll = True
        self.paused = False
        self.pending_entries = []
        
        # Settings attributes
        self.max_lines = 1000
        self.auto_scroll_enabled = True
        self.batch_size = 100
        
        self.setup_ui()
        self.setup_timer()
        
    def showEvent(self, event):
        """Override showEvent để refresh khi widget được hiển thị"""
        super().showEvent(event)
        # Refresh để hiển thị logs có sẵn
        self.refresh_display()
        
    def setup_ui(self):
        """Setup enhanced UI components"""
        layout = QVBoxLayout(self)
        
        # Control panel
        self.create_control_panel()
        layout.addWidget(self.control_panel)
        
        # Main log area - tabbed interface
        self.tabs = QTabWidget()
        
        # Text view tab
        self.text_tab = QWidget()
        self.setup_text_view()
        self.tabs.addTab(self.text_tab, "📄 Text View")
        
        # Table view tab  
        self.table_tab = QWidget()
        self.setup_table_view()
        self.tabs.addTab(self.table_tab, "📊 Table View")
        
        # Stats tab
        self.stats_tab = QWidget()
        self.setup_stats_view()
        self.tabs.addTab(self.stats_tab, "📈 Statistics")
        
        layout.addWidget(self.tabs)
        
        # Status bar - hidden để giao diện sạch sẽ hơn
        # self.setup_status_bar()
        # layout.addWidget(self.status_frame)
        
    def create_control_panel(self):
        """Create simplified control panel with search and settings only"""
        self.control_panel = QFrame()
        self.control_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(self.control_panel)
        
        # Search box
        layout.addWidget(QLabel("� Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search in messages...")
        self.search_box.textChanged.connect(self.apply_filters)
        layout.addWidget(self.search_box)
        
        # Settings button
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.open_log_settings)
        layout.addWidget(self.settings_btn)
        
        # Initialize hidden filters with default values
        self.level_filter = QComboBox()
        self.level_filter.addItem("All Levels", None)
        for level in LogLevel:
            self.level_filter.addItem(f"{level.value[1]} {level.name}", level)
        self.level_filter.hide()  # Hidden but functional
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", "All")
        self.category_filter.hide()  # Hidden but functional
        
    def setup_text_view(self):
        """Setup simplified text view"""
        layout = QVBoxLayout(self.text_tab)
        
        # Text area - no controls needed, all moved to Settings
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setFont(QFont("Consolas", 10))
        layout.addWidget(self.text_output)
        
        # Store reference for compatibility
        self.text_view = self.text_output
        
    def setup_table_view(self):
        """Setup table view for structured logs"""
        layout = QVBoxLayout(self.table_tab)
        
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels([
            "Time", "Level", "Category", "Message", "Details"
        ])
        
        # Configure table
        header = self.log_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Time
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Level
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)          # Message
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Details
        
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.log_table.setSortingEnabled(True)
        
        layout.addWidget(self.log_table)
        
    def setup_stats_view(self):
        """Setup statistics view"""
        layout = QVBoxLayout(self.stats_tab)
        
        # Stats display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
        
        # Refresh stats button
        refresh_btn = QPushButton("🔄 Refresh Statistics")
        refresh_btn.clicked.connect(self.update_stats)
        layout.addWidget(refresh_btn)
        
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_frame = QFrame()
        self.status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(self.status_frame)
        
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        self.entry_count_label = QLabel("0 entries")
        layout.addWidget(self.entry_count_label)
        
        self.filtered_count_label = QLabel("")
        layout.addWidget(self.filtered_count_label)
        
    def setup_timer(self):
        """Setup update timer for batched updates"""
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.refresh_display)
        
    def log_message(self, message: str, level: LogLevel = LogLevel.INFO, 
                   category: str = "General", details: Optional[Dict] = None):
        """Add log message with enhanced metadata"""
        entry = LogEntry(message, level, category, details)
        
        if self.paused:
            self.pending_entries.append(entry)
        else:
            self.storage.add_entry(entry)
            self.update_category_filter()
            
            # Batch updates for performance
            if not self.update_timer.isActive():
                self.update_timer.start(100)  # 100ms debounce
                
    def process_pending_entries(self):
        """Process pending entries in batch"""
        if self.pending_entries and not self.paused:
            for entry in self.pending_entries:
                self.storage.add_entry(entry)
            self.pending_entries.clear()
            self.update_category_filter()
        
    def update_category_filter(self):
        """Update category filter dropdown"""
        current = self.category_filter.currentData()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", "All")
        
        for category in self.storage.get_categories():
            self.category_filter.addItem(f"📂 {category}", category)
            
        # Restore selection
        if current:
            index = self.category_filter.findData(current)
            if index >= 0:
                self.category_filter.setCurrentIndex(index)
                
    def apply_filters(self):
        """Apply current filters and refresh display"""
        if not self.update_timer.isActive():
            self.update_timer.start(200)
            
    def refresh_display(self):
        """Refresh all display views"""
        # Process any pending entries first
        self.process_pending_entries()
        
        # Get filtered entries
        level_filter = self.level_filter.currentData() if hasattr(self, 'level_filter') else None
        category_filter = self.category_filter.currentData() if hasattr(self, 'category_filter') else "All"
        search_text = self.search_box.text().strip() if hasattr(self, 'search_box') else ""
        
        filtered_entries = self.storage.filter_entries(
            level_filter=level_filter,
            category_filter=category_filter if category_filter != "All" else None,
            search_text=search_text if search_text else None
        )
        
        # Update text view
        self.update_text_view(filtered_entries)
        
        # Update table view
        self.update_table_view(filtered_entries)
        
        # Update status (chỉ nếu status bar được enabled)
        total = len(self.storage.entries)
        filtered = len(filtered_entries)
        
        if hasattr(self, 'entry_count_label') and self.entry_count_label:
            self.entry_count_label.setText(f"{total} total entries")
        
        if hasattr(self, 'filtered_count_label') and self.filtered_count_label:
            if filtered != total:
                self.filtered_count_label.setText(f"({filtered} shown)")
            else:
                self.filtered_count_label.setText("")
            
    def update_text_view(self, entries: List[LogEntry]):
        """Update text view with entries"""
        self.text_output.clear()
        
        for entry in entries[-1000:]:  # Show last 1000 entries
            formatted = entry.formatted_message()
            color = entry.level.value[2]
            
            # Apply color formatting
            cursor = self.text_output.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)
            cursor.insertText(formatted + "\n")
            
        # Auto-scroll if enabled
        if self.auto_scroll:
            scrollbar = self.text_output.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
    def update_table_view(self, entries: List[LogEntry]):
        """Update table view with entries"""
        if not hasattr(self, 'log_table') or not self.log_table:
            return
            
        self.log_table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Time
            self.log_table.setItem(row, 0, QTableWidgetItem(entry.formatted_time()))
            
            # Level with color
            level_item = QTableWidgetItem(f"{entry.level.value[1]} {entry.level.name}")
            level_item.setForeground(QColor(entry.level.value[2]))
            self.log_table.setItem(row, 1, level_item)
            
            # Category
            self.log_table.setItem(row, 2, QTableWidgetItem(entry.category))
            
            # Message
            self.log_table.setItem(row, 3, QTableWidgetItem(entry.message))
            
            # Details
            details_text = json.dumps(entry.details) if entry.details else ""
            self.log_table.setItem(row, 4, QTableWidgetItem(details_text))
            
    def update_stats(self):
        """Update statistics view"""
        stats = self.storage.get_stats()
        
        stats_html = f"""
        <h3>📈 Log Statistics</h3>
        <p><strong>Total Entries:</strong> {stats['total_entries']}</p>
        
        <h4>📊 By Level:</h4>
        <ul>
        """
        
        for level_name, count in stats['by_level'].items():
            if count > 0:
                level = LogLevel[level_name]
                color = level.value[2]
                icon = level.value[1]
                stats_html += f'<li style="color: {color}">{icon} {level_name}: {count}</li>'
        
        stats_html += """
        </ul>
        <h4>📂 By Category:</h4>
        <ul>
        """
        
        for category, count in stats['by_category'].items():
            stats_html += f"<li>📂 {category}: {count}</li>"
            
        stats_html += "</ul>"
        
        if stats['oldest_entry'] and stats['newest_entry']:
            stats_html += f"""
            <h4>⏰ Time Range:</h4>
            <p><strong>Oldest:</strong> {stats['oldest_entry'].strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Newest:</strong> {stats['newest_entry'].strftime('%Y-%m-%d %H:%M:%S')}</p>
            """
            
        self.stats_text.setHtml(stats_html)
        
    def toggle_pause(self, paused: bool):
        """Toggle log pausing"""
        self.paused = paused
        if paused:
            if hasattr(self, 'pause_btn') and self.pause_btn:
                self.pause_btn.setText("▶️ Resume")
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText("⏸️ Paused")
        else:
            if hasattr(self, 'pause_btn') and self.pause_btn:
                self.pause_btn.setText("⏸️ Pause")
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText("▶️ Active")
            # Process any pending entries
            self.process_pending_entries()
            
    def toggle_auto_scroll(self, enabled: bool):
        """Toggle auto-scroll"""
        self.auto_scroll = enabled
        
    def toggle_word_wrap(self, enabled: bool):
        """Toggle word wrap"""
        if enabled:
            self.text_output.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.text_output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            
    def change_font_size(self, size: int):
        """Change font size"""
        font = self.text_output.font()
        font.setPointSize(size)
        self.text_output.setFont(font)
        
    def clear_logs(self):
        """Clear all logs"""
        reply = QMessageBox.question(
            self, "Clear Logs", 
            "Are you sure you want to clear all log entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.entries.clear()
            self.storage._categories.clear()
            self.pending_entries.clear()
            self.refresh_display()
            self.update_category_filter()
            
    def export_logs(self):
        """Export logs to file"""
        # Get filtered entries
        level_filter = self.level_filter.currentData()
        category_filter = self.category_filter.currentData()
        search_text = self.search_box.text().strip()
        
        entries = self.storage.filter_entries(
            level_filter=level_filter,
            category_filter=category_filter if category_filter != "All" else None,
            search_text=search_text if search_text else None
        )
        
        if not entries:
            QMessageBox.information(self, "Export", "No entries to export.")
            return
            
        # Choose format
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Logs",
            f"mumu_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "JSON Files (*.json);;CSV Files (*.csv);;Text Files (*.txt)"
        )
        
        if not file_path:
            return
            
        try:
            if selected_filter.startswith("JSON"):
                self.export_json(file_path, entries)
            elif selected_filter.startswith("CSV"):
                self.export_csv(file_path, entries)
            else:
                self.export_text(file_path, entries)
                
            QMessageBox.information(self, "Export", f"Successfully exported {len(entries)} entries to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export logs:\n{e}")
            
    def export_json(self, file_path: str, entries: List[LogEntry]):
        """Export to JSON format"""
        data = {
            'export_time': datetime.now().isoformat(),
            'total_entries': len(entries),
            'entries': [entry.to_dict() for entry in entries]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def export_csv(self, file_path: str, entries: List[LogEntry]):
        """Export to CSV format"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Level', 'Category', 'Message', 'Details'])
            
            for entry in entries:
                writer.writerow([
                    entry.timestamp.isoformat(),
                    entry.level.name,
                    entry.category,
                    entry.message,
                    json.dumps(entry.details) if entry.details else ''
                ])
                
    def export_text(self, file_path: str, entries: List[LogEntry]):
        """Export to text format"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"MumuManager Pro Log Export\n")
            f.write(f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Entries: {len(entries)}\n")
            f.write("=" * 80 + "\n\n")
            
            for entry in entries:
                f.write(f"{entry.formatted_message()}\n")
                if entry.details:
                    f.write(f"  Details: {json.dumps(entry.details)}\n")
                f.write("\n")
    
    def open_log_settings(self):
        """Mở dialog cài đặt log"""
        try:
            from log_settings_dialog import LogSettingsDialog
            dialog = LogSettingsDialog(self)
            if dialog.exec():
                # Áp dụng các cài đặt mới
                self.apply_log_settings()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open log settings: {str(e)}")
    
    def apply_log_settings(self):
        """Áp dụng các cài đặt log từ QSettings"""
        settings = QSettings('MumuManager', 'LogSettings')
        
        # Áp dụng cài đặt font
        font_family = settings.value('display/font_family', 'Consolas')
        font_size = int(settings.value('display/font_size', 10))
        font = QFont(font_family, font_size)
        
        # Áp dụng cho text view
        self.log_display.setFont(font)
        
        # Áp dụng cài đặt hiển thị
        max_lines = int(settings.value('display/max_lines', 1000))
        auto_scroll = settings.value('display/auto_scroll', True, type=bool)
        
        self.max_lines = max_lines
        self.auto_scroll_enabled = auto_scroll
        
        # Áp dụng cài đặt performance
        batch_size = int(settings.value('performance/batch_size', 100))
        update_interval = int(settings.value('performance/update_interval', 100))
        
        self.batch_size = batch_size
        if hasattr(self, 'update_timer'):
            self.update_timer.setInterval(update_interval)
        
        # Refresh display
        self.apply_settings_refresh()
    
    def apply_settings_refresh(self):
        """Refresh log display với settings mới từ settings dialog"""
        # Check if UI components exist
        if not hasattr(self, 'text_view'):
            return
            
        # Clear và reload display
        self.text_view.clear()
        
        # Get current filter settings
        level_filter = self.level_filter.currentData() if hasattr(self, 'level_filter') else None
        category_filter = self.category_filter.currentData() if hasattr(self, 'category_filter') else "All"
        search_text = self.search_box.text().strip() if hasattr(self, 'search_box') else ""
        
        # Apply filters and update display
        entries = self.storage.filter_entries(
            level_filter=level_filter,
            category_filter=category_filter if category_filter != "All" else None,
            search_text=search_text if search_text else None
        )
        
        # Update display với entries mới
        for entry in entries[-self.max_lines:]:  # Limit to max_lines
            self.text_view.append(entry.formatted_message())
        
        # Auto scroll nếu enabled
        if hasattr(self, 'auto_scroll_enabled') and self.auto_scroll_enabled:
            cursor = self.text_view.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.text_view.setTextCursor(cursor)

# Convenience methods for common log levels
def log_debug(widget: EnhancedLogWidget, message: str, category: str = "Debug", details: Dict = None):
    widget.log_message(message, LogLevel.DEBUG, category, details)

def log_info(widget: EnhancedLogWidget, message: str, category: str = "General", details: Dict = None):
    widget.log_message(message, LogLevel.INFO, category, details)

def log_success(widget: EnhancedLogWidget, message: str, category: str = "General", details: Dict = None):
    widget.log_message(message, LogLevel.SUCCESS, category, details)

def log_warning(widget: EnhancedLogWidget, message: str, category: str = "General", details: Dict = None):
    widget.log_message(message, LogLevel.WARNING, category, details)

def log_error(widget: EnhancedLogWidget, message: str, category: str = "Error", details: Dict = None):
    widget.log_message(message, LogLevel.ERROR, category, details)

def log_critical(widget: EnhancedLogWidget, message: str, category: str = "Critical", details: Dict = None):
    widget.log_message(message, LogLevel.CRITICAL, category, details)
