"""
Performance Monitoring Component
===============================

Advanced performance monitoring and analytics cho production deployment.
"""

import time
import threading
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QGroupBox, QTableWidget, QTableWidgetItem,
                            QTabWidget, QPushButton, QTextEdit)
from PyQt6.QtCore import pyqtSignal, QObject, Qt, QTimer, QThread
from PyQt6.QtGui import QFont
import json
from datetime import datetime, timedelta

# Try importing psutil for system metrics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Try importing charts for advanced visualization
try:
    from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False

# Optimization imports
try:
    from services import get_service_manager
    from core import get_event_manager, EventTypes, emit_event
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: float = field(default_factory=time.time)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    gpu_percent: float = 0.0
    disk_io_read: float = 0.0
    disk_io_write: float = 0.0
    network_sent: float = 0.0
    network_recv: float = 0.0
    active_instances: int = 0
    ui_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    error_count: int = 0

@dataclass
class ComponentPerformance:
    """Individual component performance tracking"""
    component_name: str
    load_time: float = 0.0
    render_time: float = 0.0
    memory_usage: float = 0.0
    update_frequency: int = 0
    error_count: int = 0
    last_update: float = field(default_factory=time.time)

class PerformanceCollector(QThread):
    """Background thread for collecting performance metrics"""
    
    metrics_collected = pyqtSignal(object)  # PerformanceMetrics
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.collection_interval = 1.0  # seconds
        self.process = psutil.Process()
        
    def run(self):
        """Main collection loop"""
        while self.running:
            try:
                metrics = self._collect_metrics()
                self.metrics_collected.emit(metrics)
                time.sleep(self.collection_interval)
            except Exception as e:
                print(f"⚠️ Performance collection error: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        metrics = PerformanceMetrics()
        
        # System metrics
        metrics.cpu_percent = psutil.cpu_percent(interval=None)
        memory_info = psutil.virtual_memory()
        metrics.memory_percent = memory_info.percent
        
        # Process metrics
        try:
            process_memory = self.process.memory_info()
            metrics.memory_mb = process_memory.rss / (1024 * 1024)  # Convert to MB
        except:
            metrics.memory_mb = 0.0
        
        # Disk I/O
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics.disk_io_read = disk_io.read_bytes / (1024 * 1024)  # MB
                metrics.disk_io_write = disk_io.write_bytes / (1024 * 1024)  # MB
        except:
            pass
        
        # Network I/O
        try:
            network_io = psutil.net_io_counters()
            if network_io:
                metrics.network_sent = network_io.bytes_sent / (1024 * 1024)  # MB
                metrics.network_recv = network_io.bytes_recv / (1024 * 1024)  # MB
        except:
            pass
        
        return metrics
    
    def stop(self):
        """Stop collection"""
        self.running = False
        self.quit()
        self.wait()

class PerformanceMonitorComponent(QObject):
    """
    Advanced Performance Monitoring Component for production deployment.
    
    Features:
    - Real-time system metrics
    - Component-level performance tracking
    - Performance analytics và alerting
    - Historical data và reporting
    - Optimization recommendations
    """
    
    # Signals
    performance_alert = pyqtSignal(str, str, float)  # type, message, value
    optimization_suggested = pyqtSignal(str, str)  # component, suggestion
    
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.widget = None
        
        # Performance tracking
        self.metrics_history: List[PerformanceMetrics] = []
        self.component_performance: Dict[str, ComponentPerformance] = {}
        self.max_history_size = 3600  # 1 hour of data at 1-second intervals
        
        # Thresholds for alerts
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'memory_mb': 1000.0,  # 1GB
            'ui_response_time': 100.0,  # 100ms
            'error_rate': 5.0  # 5 errors per minute
        }
        
        # Performance collector
        self.collector = PerformanceCollector()
        self.collector.metrics_collected.connect(self._on_metrics_collected)
        
        # Optimization components
        if OPTIMIZATION_AVAILABLE:
            self.service_manager = get_service_manager()
            self.event_manager = get_event_manager()
            
            # Subscribe to events
            self.event_manager.subscribe(EventTypes.COMPONENT_LOADED, self._on_component_loaded)
            self.event_manager.subscribe(EventTypes.UI_RENDER_TIME, self._on_ui_render_time)
        
        # UI Components
        self.charts = {}
        self.metric_labels = {}
        self.tables = {}
        
    def create_performance_monitor(self) -> QWidget:
        """Create performance monitoring dashboard"""
        
        monitor_widget = QTabWidget()
        
        # Real-time metrics tab
        realtime_tab = self._create_realtime_tab()
        monitor_widget.addTab(realtime_tab, "📊 Real-time")
        
        # Component performance tab
        component_tab = self._create_component_tab()
        monitor_widget.addTab(component_tab, "🧩 Components")
        
        # Analytics tab
        analytics_tab = self._create_analytics_tab()
        monitor_widget.addTab(analytics_tab, "📈 Analytics")
        
        # Alerts tab
        alerts_tab = self._create_alerts_tab()
        monitor_widget.addTab(alerts_tab, "🚨 Alerts")
        
        self.widget = monitor_widget
        return monitor_widget
    
    def _create_realtime_tab(self) -> QWidget:
        """Create real-time metrics display"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Metrics overview
        overview_group = QGroupBox("System Overview")
        overview_layout = QHBoxLayout(overview_group)
        
        # CPU gauge
        cpu_frame = self._create_metric_frame("CPU", "🖥️", "%")
        self.metric_labels['cpu'] = cpu_frame['value']
        overview_layout.addWidget(cpu_frame['frame'])
        
        # Memory gauge
        memory_frame = self._create_metric_frame("Memory", "🧠", "MB")
        self.metric_labels['memory'] = memory_frame['value']
        overview_layout.addWidget(memory_frame['frame'])
        
        # Instances gauge
        instances_frame = self._create_metric_frame("Instances", "📱", "")
        self.metric_labels['instances'] = instances_frame['value']
        overview_layout.addWidget(instances_frame['frame'])
        
        # Response time gauge
        response_frame = self._create_metric_frame("Response", "⚡", "ms")
        self.metric_labels['response'] = response_frame['value']
        overview_layout.addWidget(response_frame['frame'])
        
        layout.addWidget(overview_group)
        
        # Performance charts
        charts_group = QGroupBox("Performance Charts")
        charts_layout = QVBoxLayout(charts_group)
        
        # CPU/Memory chart
        cpu_memory_chart = self._create_performance_chart("CPU & Memory Usage")
        self.charts['cpu_memory'] = cpu_memory_chart
        charts_layout.addWidget(cpu_memory_chart)
        
        # Network I/O chart
        network_chart = self._create_performance_chart("Network I/O")
        self.charts['network'] = network_chart
        charts_layout.addWidget(network_chart)
        
        layout.addWidget(charts_group)
        
        return tab
    
    def _create_component_tab(self) -> QWidget:
        """Create component performance tracking"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Component performance table
        table_group = QGroupBox("Component Performance")
        table_layout = QVBoxLayout(table_group)
        
        self.tables['components'] = QTableWidget()
        self.tables['components'].setColumnCount(6)
        self.tables['components'].setHorizontalHeaderLabels([
            "Component", "Load Time (ms)", "Render Time (ms)", 
            "Memory (MB)", "Updates/min", "Errors"
        ])
        table_layout.addWidget(self.tables['components'])
        
        # Component controls
        controls_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_component_table)
        optimize_btn = QPushButton("🚀 Optimize")
        optimize_btn.clicked.connect(self._suggest_optimizations)
        
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(optimize_btn)
        controls_layout.addStretch()
        
        table_layout.addLayout(controls_layout)
        layout.addWidget(table_group)
        
        return tab
    
    def _create_analytics_tab(self) -> QWidget:
        """Create performance analytics"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Analytics summary
        summary_group = QGroupBox("Performance Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.analytics_text = QTextEdit()
        self.analytics_text.setReadOnly(True)
        self.analytics_text.setMaximumHeight(200)
        summary_layout.addWidget(self.analytics_text)
        
        layout.addWidget(summary_group)
        
        # Historical trends chart
        trends_group = QGroupBox("Historical Trends")
        trends_layout = QVBoxLayout(trends_group)
        
        trends_chart = self._create_performance_chart("Performance Trends (Last Hour)")
        self.charts['trends'] = trends_chart
        trends_layout.addWidget(trends_chart)
        
        layout.addWidget(trends_group)
        
        return tab
    
    def _create_alerts_tab(self) -> QWidget:
        """Create alerts and notifications"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Alert settings
        settings_group = QGroupBox("Alert Thresholds")
        settings_layout = QVBoxLayout(settings_group)
        
        # Add threshold controls here
        settings_info = QLabel("Configure performance alert thresholds:")
        settings_layout.addWidget(settings_info)
        
        layout.addWidget(settings_group)
        
        # Recent alerts
        alerts_group = QGroupBox("Recent Alerts")
        alerts_layout = QVBoxLayout(alerts_group)
        
        self.alerts_text = QTextEdit()
        self.alerts_text.setReadOnly(True)
        alerts_layout.addWidget(self.alerts_text)
        
        layout.addWidget(alerts_group)
        
        return tab
    
    def _create_metric_frame(self, label_text: str, icon: str, unit: str) -> Dict[str, Any]:
        """Create a metric display frame"""
        frame = QGroupBox()
        layout = QVBoxLayout(frame)
        
        # Icon and label
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 16))
        name_label = QLabel(label_text)
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        # Value display
        value_label = QLabel("0.0")
        value_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #A6E22E;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Unit label
        unit_label = QLabel(unit)
        unit_label.setFont(QFont("Arial", 8))
        unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        layout.addWidget(unit_label)
        
        return {
            'frame': frame,
            'value': value_label,
            'unit': unit_label
        }
    
    def _create_performance_chart(self, title: str) -> QChartView:
        """Create performance chart"""
        chart = QChart()
        chart.setTitle(title)
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        
        # Create series
        cpu_series = QLineSeries()
        cpu_series.setName("CPU %")
        memory_series = QLineSeries()
        memory_series.setName("Memory %")
        
        chart.addSeries(cpu_series)
        chart.addSeries(memory_series)
        
        # Create axes
        axis_x = QValueAxis()
        axis_x.setTitleText("Time (seconds)")
        axis_y = QValueAxis()
        axis_y.setTitleText("Percentage")
        axis_y.setRange(0, 100)
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        cpu_series.attachAxis(axis_x)
        cpu_series.attachAxis(axis_y)
        memory_series.attachAxis(axis_x)
        memory_series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.RenderHint.Antialiasing)
        
        return chart_view
    
    def _on_metrics_collected(self, metrics: PerformanceMetrics):
        """Handle new metrics from collector"""
        # Add to history
        self.metrics_history.append(metrics)
        
        # Trim history if too large
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
        
        # Update UI
        self._update_realtime_display(metrics)
        
        # Check for alerts
        self._check_performance_alerts(metrics)
        
        # Update analytics
        self._update_analytics()
    
    def _update_realtime_display(self, metrics: PerformanceMetrics):
        """Update real-time display with new metrics"""
        if 'cpu' in self.metric_labels:
            self.metric_labels['cpu'].setText(f"{metrics.cpu_percent:.1f}")
            
        if 'memory' in self.metric_labels:
            self.metric_labels['memory'].setText(f"{metrics.memory_mb:.1f}")
            
        if 'instances' in self.metric_labels:
            self.metric_labels['instances'].setText(str(metrics.active_instances))
            
        if 'response' in self.metric_labels:
            self.metric_labels['response'].setText(f"{metrics.ui_response_time:.1f}")
    
    def _check_performance_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts"""
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            self.performance_alert.emit(
                "High CPU Usage", 
                f"CPU usage is {metrics.cpu_percent:.1f}%", 
                metrics.cpu_percent
            )
        
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            self.performance_alert.emit(
                "High Memory Usage", 
                f"Memory usage is {metrics.memory_percent:.1f}%", 
                metrics.memory_percent
            )
        
        if metrics.memory_mb > self.alert_thresholds['memory_mb']:
            self.performance_alert.emit(
                "High Memory Consumption", 
                f"Process memory is {metrics.memory_mb:.1f} MB", 
                metrics.memory_mb
            )
    
    def _update_analytics(self):
        """Update performance analytics"""
        if len(self.metrics_history) < 10:
            return
        
        recent_metrics = self.metrics_history[-60:]  # Last minute
        
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_mb for m in recent_metrics) / len(recent_metrics)
        max_cpu = max(m.cpu_percent for m in recent_metrics)
        max_memory = max(m.memory_mb for m in recent_metrics)
        
        analytics_text = f"""
Performance Analytics (Last Minute):
═══════════════════════════════════
📊 Average CPU: {avg_cpu:.1f}%
📊 Average Memory: {avg_memory:.1f} MB
🔝 Peak CPU: {max_cpu:.1f}%
🔝 Peak Memory: {max_memory:.1f} MB

📈 Total Samples: {len(self.metrics_history)}
⏱️ Monitoring Duration: {len(self.metrics_history)} seconds
        """
        
        if hasattr(self, 'analytics_text'):
            self.analytics_text.setText(analytics_text)
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.collector.start()
        print("🚀 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.collector.stop()
        print("⏹️ Performance monitoring stopped")
    
    def track_component_performance(self, component_name: str, operation: str, duration: float):
        """Track individual component performance"""
        if component_name not in self.component_performance:
            self.component_performance[component_name] = ComponentPerformance(component_name)
        
        comp_perf = self.component_performance[component_name]
        
        if operation == 'load':
            comp_perf.load_time = duration
        elif operation == 'render':
            comp_perf.render_time = duration
        elif operation == 'update':
            comp_perf.update_frequency += 1
        
        comp_perf.last_update = time.time()
    
    def _refresh_component_table(self):
        """Refresh component performance table"""
        table = self.tables.get('components')
        if not table:
            return
        
        table.setRowCount(len(self.component_performance))
        
        for row, (name, perf) in enumerate(self.component_performance.items()):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(f"{perf.load_time:.1f}"))
            table.setItem(row, 2, QTableWidgetItem(f"{perf.render_time:.1f}"))
            table.setItem(row, 3, QTableWidgetItem(f"{perf.memory_usage:.1f}"))
            table.setItem(row, 4, QTableWidgetItem(str(perf.update_frequency)))
            table.setItem(row, 5, QTableWidgetItem(str(perf.error_count)))
    
    def _suggest_optimizations(self):
        """Suggest performance optimizations"""
        suggestions = []
        
        for name, perf in self.component_performance.items():
            if perf.load_time > 100:  # > 100ms
                suggestions.append(f"{name}: Consider lazy loading")
            if perf.render_time > 50:  # > 50ms
                suggestions.append(f"{name}: Optimize rendering")
            if perf.update_frequency > 60:  # > 60 updates/min
                suggestions.append(f"{name}: Reduce update frequency")
        
        if suggestions:
            for suggestion in suggestions:
                self.optimization_suggested.emit(suggestion.split(':')[0], suggestion.split(':')[1])
    
    def _on_component_loaded(self, event_data: Dict[str, Any]):
        """Handle component loaded event"""
        component_name = event_data.get('component', '')
        load_time = event_data.get('duration', 0.0)
        self.track_component_performance(component_name, 'load', load_time)
    
    def _on_ui_render_time(self, event_data: Dict[str, Any]):
        """Handle UI render time event"""
        component_name = event_data.get('component', '')
        render_time = event_data.get('duration', 0.0)
        self.track_component_performance(component_name, 'render', render_time)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.metrics_history:
            return {}
        
        recent_hour = self.metrics_history[-3600:] if len(self.metrics_history) >= 3600 else self.metrics_history
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'avg_cpu': sum(m.cpu_percent for m in recent_hour) / len(recent_hour),
                'avg_memory_mb': sum(m.memory_mb for m in recent_hour) / len(recent_hour),
                'max_cpu': max(m.cpu_percent for m in recent_hour),
                'max_memory_mb': max(m.memory_mb for m in recent_hour),
                'total_samples': len(recent_hour)
            },
            'components': {name: {
                'load_time': perf.load_time,
                'render_time': perf.render_time,
                'memory_usage': perf.memory_usage,
                'update_frequency': perf.update_frequency,
                'error_count': perf.error_count
            } for name, perf in self.component_performance.items()}
        }


# Factory function
def create_performance_monitor_component(parent_window) -> PerformanceMonitorComponent:
    """Factory function để create performance monitor component"""
    return PerformanceMonitorComponent(parent_window)
