"""
Enhanced Search Filter Widget
============================

Tạo widget tìm kiếm và lọc nâng cao cho dashboard
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QFrame, QGroupBox, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon
from typing import Dict, Any, Optional, Tuple
import re


class SearchCriteria:
    """Criteria for advanced search"""

    def __init__(self):
        self.query = ""
        self.status_filter = "All"
        self.cpu_min = 0
        self.cpu_max = 100
        self.memory_min = 0
        self.memory_max = 100
        self.case_sensitive = False
        self.regex_mode = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'status_filter': self.status_filter,
            'cpu_min': self.cpu_min,
            'cpu_max': self.cpu_max,
            'memory_min': self.memory_min,
            'memory_max': self.memory_max,
            'case_sensitive': self.case_sensitive,
            'regex_mode': self.regex_mode
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchCriteria':
        criteria = cls()
        criteria.query = data.get('query', '')
        criteria.status_filter = data.get('status_filter', 'All')
        criteria.cpu_min = data.get('cpu_min', 0)
        criteria.cpu_max = data.get('cpu_max', 100)
        criteria.memory_min = data.get('memory_min', 0)
        criteria.memory_max = data.get('memory_max', 100)
        criteria.case_sensitive = data.get('case_sensitive', False)
        criteria.regex_mode = data.get('regex_mode', False)
        return criteria


class EnhancedSearchFilterWidget(QWidget):
    """Enhanced search and filter widget"""

    # Signals
    search_changed = pyqtSignal(SearchCriteria)
    filter_applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.criteria = SearchCriteria()
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._emit_search_changed)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Search input section
        search_group = QGroupBox("🔍 Tìm kiếm")
        search_layout = QVBoxLayout(search_group)

        # Search input
        search_input_layout = QHBoxLayout()
        search_label = QLabel("Tìm theo tên hoặc ID:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Nhập tên instance hoặc ID...")
        self.search_edit.setMinimumWidth(200)

        search_input_layout.addWidget(search_label)
        search_input_layout.addWidget(self.search_edit)
        search_layout.addLayout(search_input_layout)

        # Search options
        options_layout = QHBoxLayout()
        self.case_sensitive_cb = QCheckBox("Phân biệt hoa thường")
        self.regex_cb = QCheckBox("Regex mode")
        options_layout.addWidget(self.case_sensitive_cb)
        options_layout.addWidget(self.regex_cb)
        options_layout.addStretch()
        search_layout.addLayout(options_layout)

        layout.addWidget(search_group)

        # Filter section
        filter_group = QGroupBox("🎯 Bộ lọc")
        filter_layout = QVBoxLayout(filter_group)

        # Status filter
        status_layout = QHBoxLayout()
        status_label = QLabel("Trạng thái:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Running", "Stopped", "Error"])
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        filter_layout.addLayout(status_layout)

        # CPU filter
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU (%):")
        self.cpu_min_spin = QSpinBox()
        self.cpu_min_spin.setRange(0, 100)
        self.cpu_min_spin.setValue(0)
        cpu_separator = QLabel("-")
        self.cpu_max_spin = QSpinBox()
        self.cpu_max_spin.setRange(0, 100)
        self.cpu_max_spin.setValue(100)

        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_min_spin)
        cpu_layout.addWidget(cpu_separator)
        cpu_layout.addWidget(self.cpu_max_spin)
        cpu_layout.addStretch()
        filter_layout.addLayout(cpu_layout)

        # Memory filter
        memory_layout = QHBoxLayout()
        memory_label = QLabel("Memory (%):")
        self.memory_min_spin = QSpinBox()
        self.memory_min_spin.setRange(0, 100)
        self.memory_min_spin.setValue(0)
        memory_separator = QLabel("-")
        self.memory_max_spin = QSpinBox()
        self.memory_max_spin.setRange(0, 100)
        self.memory_max_spin.setValue(100)

        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self.memory_min_spin)
        memory_layout.addWidget(memory_separator)
        memory_layout.addWidget(self.memory_max_spin)
        memory_layout.addStretch()
        filter_layout.addLayout(memory_layout)

        layout.addWidget(filter_group)

        # Action buttons
        buttons_layout = QHBoxLayout()
        self.apply_btn = QPushButton("🔄 Áp dụng")
        self.reset_btn = QPushButton("🔄 Đặt lại")
        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def _connect_signals(self):
        """Connect widget signals"""
        self.search_edit.textChanged.connect(self._on_search_text_changed)
        self.status_combo.currentTextChanged.connect(self._on_filter_changed)
        self.cpu_min_spin.valueChanged.connect(self._on_filter_changed)
        self.cpu_max_spin.valueChanged.connect(self._on_filter_changed)
        self.memory_min_spin.valueChanged.connect(self._on_filter_changed)
        self.memory_max_spin.valueChanged.connect(self._on_filter_changed)
        self.case_sensitive_cb.toggled.connect(self._on_filter_changed)
        self.regex_cb.toggled.connect(self._on_filter_changed)

        self.apply_btn.clicked.connect(self._apply_filters)
        self.reset_btn.clicked.connect(self._reset_filters)

    def _on_search_text_changed(self, text: str):
        """Handle search text changes with debouncing"""
        self.criteria.query = text
        self.search_timer.start(300)  # 300ms debounce

    def _on_filter_changed(self):
        """Handle filter changes"""
        self._update_criteria_from_ui()
        self.search_timer.start(300)  # 300ms debounce

    def _emit_search_changed(self):
        """Emit search changed signal"""
        self.search_changed.emit(self.criteria)

    def _update_criteria_from_ui(self):
        """Update criteria from UI controls"""
        self.criteria.status_filter = self.status_combo.currentText()
        self.criteria.cpu_min = self.cpu_min_spin.value()
        self.criteria.cpu_max = self.cpu_max_spin.value()
        self.criteria.memory_min = self.memory_min_spin.value()
        self.criteria.memory_max = self.memory_max_spin.value()
        self.criteria.case_sensitive = self.case_sensitive_cb.isChecked()
        self.criteria.regex_mode = self.regex_cb.isChecked()

    def _apply_filters(self):
        """Apply current filters"""
        self._update_criteria_from_ui()
        self.filter_applied.emit()
        self.search_changed.emit(self.criteria)

    def _reset_filters(self):
        """Reset all filters to default"""
        self.search_edit.clear()
        self.status_combo.setCurrentText("All")
        self.cpu_min_spin.setValue(0)
        self.cpu_max_spin.setValue(100)
        self.memory_min_spin.setValue(0)
        self.memory_max_spin.setValue(100)
        self.case_sensitive_cb.setChecked(False)
        self.regex_cb.setChecked(False)

        self.criteria = SearchCriteria()
        self.filter_applied.emit()
        self.search_changed.emit(self.criteria)

    def get_search_criteria(self) -> SearchCriteria:
        """Get current search criteria"""
        return self.criteria

    def set_search_criteria(self, criteria: SearchCriteria):
        """Set search criteria"""
        self.criteria = criteria
        self._update_ui_from_criteria()

    def _update_ui_from_criteria(self):
        """Update UI from criteria"""
        self.search_edit.setText(self.criteria.query)
        self.status_combo.setCurrentText(self.criteria.status_filter)
        self.cpu_min_spin.setValue(self.criteria.cpu_min)
        self.cpu_max_spin.setValue(self.criteria.cpu_max)
        self.memory_min_spin.setValue(self.criteria.memory_min)
        self.memory_max_spin.setValue(self.criteria.memory_max)
        self.case_sensitive_cb.setChecked(self.criteria.case_sensitive)
        self.regex_cb.setChecked(self.criteria.regex_mode)


class EnhancedSearchProxy:
    """Enhanced proxy model for advanced filtering"""

    def __init__(self, source_model):
        self.source_model = source_model
        self.criteria = SearchCriteria()
        self.filtered_indices = []

    def set_criteria(self, criteria: SearchCriteria):
        """Set search criteria"""
        self.criteria = criteria
        self._apply_filter()

    def _apply_filter(self):
        """Apply current filter criteria"""
        self.filtered_indices = []

        for row in range(self.source_model.rowCount()):
            if self._matches_criteria(row):
                self.filtered_indices.append(row)

    def _matches_criteria(self, row: int) -> bool:
        """Check if row matches current criteria"""
        try:
            # Get instance data
            instance_data = self.source_model.get_instance_data(row)
            if not instance_data:
                return False

            # Status filter
            if self.criteria.status_filter != "All":
                if instance_data.get('status', '').lower() != self.criteria.status_filter.lower():
                    return False

            # CPU filter
            cpu_usage = instance_data.get('cpu_percent', 0)
            if not (self.criteria.cpu_min <= cpu_usage <= self.criteria.cpu_max):
                return False

            # Memory filter
            memory_usage = instance_data.get('memory_percent', 0)
            if not (self.criteria.memory_min <= memory_usage <= self.criteria.memory_max):
                return False

            # Text search
            if self.criteria.query:
                search_text = f"{instance_data.get('name', '')} {instance_data.get('id', '')}"
                if self.criteria.regex_mode:
                    try:
                        flags = 0 if self.criteria.case_sensitive else re.IGNORECASE
                        if not re.search(self.criteria.query, search_text, flags):
                            return False
                    except re.error:
                        # Invalid regex, treat as literal search
                        if self.criteria.case_sensitive:
                            if self.criteria.query not in search_text:
                                return False
                        else:
                            if self.criteria.query.lower() not in search_text.lower():
                                return False
                else:
                    # Literal search
                    if self.criteria.case_sensitive:
                        if self.criteria.query not in search_text:
                            return False
                    else:
                        if self.criteria.query.lower() not in search_text.lower():
                            return False

            return True

        except Exception as e:
            print(f"⚠️ Error filtering row {row}: {e}")
            return False

    def rowCount(self):
        """Get filtered row count"""
        return len(self.filtered_indices)

    def mapToSource(self, filtered_row: int):
        """Map filtered row to source row"""
        if 0 <= filtered_row < len(self.filtered_indices):
            return self.filtered_indices[filtered_row]
        return -1

    def mapFromSource(self, source_row: int):
        """Map source row to filtered row"""
        try:
            return self.filtered_indices.index(source_row)
        except ValueError:
            return -1


def create_enhanced_search_filter_widget(source_model) -> Tuple[EnhancedSearchFilterWidget, EnhancedSearchProxy]:
    """
    Create enhanced search filter widget and proxy

    Args:
        source_model: The source model to filter

    Returns:
        Tuple of (filter_widget, proxy_model)
    """
    try:
        # Create filter widget
        filter_widget = EnhancedSearchFilterWidget()

        # Create proxy model
        proxy = EnhancedSearchProxy(source_model)

        # Connect filter widget to proxy
        filter_widget.search_changed.connect(proxy.set_criteria)

        print("✅ Enhanced search filter widget created successfully")
        return filter_widget, proxy

    except Exception as e:
        print(f"⚠️ Failed to create enhanced search filter: {e}")
        # Return fallback components
        fallback_widget = QLineEdit()
        fallback_widget.setPlaceholderText("Tìm kiếm cơ bản...")

        class FallbackProxy:
            def __init__(self, source_model):
                self.source_model = source_model

            def rowCount(self):
                return self.source_model.rowCount()

            def mapToSource(self, row):
                return row

            def mapFromSource(self, row):
                return row

        fallback_proxy = FallbackProxy(source_model)
        return fallback_widget, fallback_proxy
