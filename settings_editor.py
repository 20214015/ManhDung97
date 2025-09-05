"""
Simple Settings Editor - Sửa cấu hình đơn giản không crash
Version 2.0 - Simplified and stable
"""

import json
import os
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QLineEdit,
    QCheckBox, QComboBox, QScrollArea, QMessageBox, QLabel, QSpinBox,
    QDoubleSpinBox, QWidget, QGroupBox, QTextEdit, QSplitter, QTabWidget,
    QProgressBar, QFileDialog, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# Configuration templates based on real MuMu VM config structure
CONFIG_TEMPLATES = {
    'Gaming': {
        'name': '🎮 Gaming Performance',
        'description': 'Tối ưu cho gaming với hiệu năng cao',
        'settings': {
            'vm.cpu': '4',
            'vm.memory': '6.000000',
            'vm.phone.brand': 'Samsung',
            'vm.phone.model': 'Galaxy S22 Ultra',
            'vm.phone.manufacturer': 'Samsung',
            'vm.phone.miit': 'SM-G998B',
            'vm.root': 'true',
            'vm.system_vdi.sharable': 'Readonly'
        }
    },
    'Office': {
        'name': '💼 Office Work',
        'description': 'Cân bằng cho công việc văn phòng',
        'settings': {
            'vm.cpu': '2',
            'vm.memory': '3.000000',
            'vm.phone.brand': 'Google',
            'vm.phone.model': 'Pixel 6',
            'vm.phone.manufacturer': 'Google',
            'vm.phone.miit': 'GR1YH',
            'vm.root': 'false',
            'vm.system_vdi.sharable': 'Readonly'
        }
    },
    'Samsung_S20_FE': {
        'name': '📱 Samsung Galaxy S20 FE',
        'description': 'Template từ JSON mẫu thực tế',
        'settings': {
            'vm.cpu': '2',
            'vm.memory': '3.000000',
            'vm.phone.brand': 'Samsung',
            'vm.phone.model': 'Galaxy S20 FE',
            'vm.phone.manufacturer': 'Samsung',
            'vm.phone.miit': 'SM-G7810',
            'vm.root': 'false',
            'vm.system_vdi.sharable': 'Readonly'
        }
    },
    'High_Performance': {
        'name': '🚀 High Performance',
        'description': 'Cấu hình hiệu năng cao nhất',
        'settings': {
            'vm.cpu': '8',
            'vm.memory': '8.000000',
            'vm.phone.brand': 'OnePlus',
            'vm.phone.model': 'OnePlus 11',
            'vm.phone.manufacturer': 'OnePlus',
            'vm.phone.miit': 'CPH2449',
            'vm.root': 'true',
            'vm.system_vdi.sharable': 'Readonly'
        }
    },
    'Balanced': {
        'name': '⚖️ Balanced',
        'description': 'Cấu hình cân bằng tổng thể',
        'settings': {
            'vm.cpu': '3',
            'vm.memory': '4.000000',
            'vm.phone.brand': 'Xiaomi',
            'vm.phone.model': 'Mi 12',
            'vm.phone.manufacturer': 'Xiaomi',
            'vm.phone.miit': '2201123G',
            'vm.root': 'false',
            'vm.system_vdi.sharable': 'Readonly'
        }
    }
}

# Phone model presets based on real device specs
PHONE_MODELS = {
    'Samsung Galaxy S22 Ultra': {
        'brand': 'Samsung',
        'manufacturer': 'Samsung', 
        'miit': 'SM-G998B',
        'description': 'Flagship Samsung 2022'
    },
    'Samsung Galaxy S21': {
        'brand': 'Samsung',
        'manufacturer': 'Samsung',
        'miit': 'SM-G991B', 
        'description': 'Samsung flagship 2021'
    },
    'Samsung Galaxy S20 FE': {
        'brand': 'Samsung',
        'manufacturer': 'Samsung',
        'miit': 'SM-G7810',
        'description': 'Samsung Fan Edition'
    },
    'Google Pixel 6': {
        'brand': 'Google',
        'manufacturer': 'Google',
        'miit': 'GR1YH',
        'description': 'Google Pixel 6'
    },
    'Google Pixel 7': {
        'brand': 'Google', 
        'manufacturer': 'Google',
        'miit': 'GVU6C',
        'description': 'Google Pixel 7'
    },
    'OnePlus 11': {
        'brand': 'OnePlus',
        'manufacturer': 'OnePlus',
        'miit': 'CPH2449',
        'description': 'OnePlus flagship 2023'
    },
    'Xiaomi Mi 12': {
        'brand': 'Xiaomi',
        'manufacturer': 'Xiaomi', 
        'miit': '2201123G',
        'description': 'Xiaomi flagship'
    },
    'iPhone 14 Pro': {
        'brand': 'Apple',
        'manufacturer': 'Apple',
        'miit': 'iPhone15,3',
        'description': 'iPhone 14 Pro'
    }
}

class SettingsLoaderWorker(QThread):
    """Worker thread để load settings"""
    settings_loaded = pyqtSignal(dict)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, manager, indices):
        super().__init__()
        self.manager = manager
        self.indices = indices
        self._is_cancelled = False
        
    def run(self):
        """Load settings từ instances theo cấu trúc MuMu VM config"""
        try:
            settings = {}
            total = len(self.indices)
            
            for i, idx in enumerate(self.indices):
                if self._is_cancelled:
                    return
                    
                # Real VM config structure từ MuMu
                instance_settings = {
                    'vm.cpu': '2',
                    'vm.memory': '3.000000',
                    'vm.phone.brand': 'Samsung',
                    'vm.phone.model': 'Galaxy S20 FE',
                    'vm.phone.manufacturer': 'Samsung',
                    'vm.phone.miit': 'SM-G7810',
                    'vm.phone.imei': '',
                    'vm.phone.number': '',
                    'vm.phone.code': 'RESERVED',
                    'vm.phone.rom.reset': '0',
                    'vm.root': 'false',
                    'vm.system_vdi.sharable': 'Readonly',
                    'vm.gpu.model': 'Adreno (TM) 640',
                    'vm.nat.port_forward.adb.host_port': '16544',
                    'vm.nat.port_forward.api.host_port': '17590'
                }
                
                for key, value in instance_settings.items():
                    if key not in settings:
                        settings[key] = []
                    settings[key].append(value)
                
                progress = int((i + 1) / total * 100)
                self.progress_updated.emit(progress)
                
            self.settings_loaded.emit(settings)
            
        except Exception as e:
            print(f"Error loading VM settings: {e}")
            self.settings_loaded.emit({})
    
    def cancel(self):
        """Cancel loading"""
        self._is_cancelled = True

class SimpleSettingsEditorDialog(QDialog):
    """Settings Editor đơn giản không crash"""
    
    def __init__(self, manager, indices, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.indices = indices
        self.settings_cache = {}
        self.widgets = {}
        self.initial_values = {}
        
        self.setWindowTitle("🔧 Sửa Cấu hình MuMu - MumuManager")
        self.setModal(True)
        self.resize(800, 600)
        
        # Apply custom title bar styling
        self._apply_custom_title_bar_style()
        
        self.setup_ui()
        self._start_loading()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Main content
        self.main_widget = QWidget()
        layout.addWidget(self.main_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.template_btn = QPushButton("📋 Templates")
        self.template_btn.clicked.connect(self.show_templates)
        button_layout.addWidget(self.template_btn)
        
        self.import_btn = QPushButton("📥 Import JSON")
        self.import_btn.clicked.connect(self.import_settings)
        button_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 Export JSON")
        self.export_btn.clicked.connect(self.export_settings)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        
        self.apply_btn = QPushButton("✅ Áp dụng")
        self.apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_btn)
        
        self.cancel_btn = QPushButton("❌ Hủy")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _start_loading(self):
        """Start loading settings"""
        self.progress_bar.setVisible(True)
        self.loader_worker = SettingsLoaderWorker(self.manager, self.indices)
        self.loader_worker.settings_loaded.connect(self._on_settings_loaded)
        self.loader_worker.progress_updated.connect(self.progress_bar.setValue)
        self.loader_worker.start()
    
    def _on_settings_loaded(self, settings):
        """Handle loaded settings"""
        self.progress_bar.setVisible(False)
        self.settings_cache = settings
        self._build_settings_ui()
    
    def _build_settings_ui(self):
        """Build settings UI with simple form layout"""
        # Clear existing content
        if hasattr(self, 'scroll_area'):
            self.scroll_area.deleteLater()
        
        # Create scrollable area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Content widget
        content_widget = QWidget()
        form_layout = QFormLayout(content_widget)
        
        # Add settings widgets
        for key, values in self.settings_cache.items():
            if not values:
                continue
                
            current_value = values[0] if values else ""
            widget = self._create_widget_for_setting(key, current_value)
            
            if widget:
                self.widgets[key] = widget
                self.initial_values[key] = self._get_widget_value(widget)
                
                # Nice label with Vietnamese names
                label = self._get_friendly_label(key)
                form_layout.addRow(f"{label}:", widget)
        
        self.scroll_area.setWidget(content_widget)
        
        # Add to main layout
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.addWidget(self.scroll_area)
    
    def _create_widget_for_setting(self, key: str, current_value: str) -> QWidget:
        """Create widget for VM config setting based on real structure"""
        
        # VM CPU configuration
        if key == 'vm.cpu':
            container = QWidget()
            layout = QHBoxLayout(container)
            
            spin = QSpinBox()
            spin.setRange(1, 16)
            spin.setSuffix(" cores")
            spin.setValue(int(current_value) if current_value.isdigit() else 2)
            layout.addWidget(spin)
            
            # Quick CPU presets
            for val in [1, 2, 4, 6, 8]:
                btn = QPushButton(str(val))
                btn.setMaximumWidth(30)
                btn.clicked.connect(lambda checked, v=val: spin.setValue(v))
                layout.addWidget(btn)
                
            return container
            
        # VM Memory configuration  
        elif key == 'vm.memory':
            container = QWidget()
            layout = QHBoxLayout(container)
            
            spin = QDoubleSpinBox()
            spin.setRange(1.0, 16.0)
            spin.setDecimals(6)
            spin.setSuffix(" GB")
            try:
                spin.setValue(float(current_value) if current_value else 3.0)
            except ValueError:
                spin.setValue(3.0)
            layout.addWidget(spin)
            
            # Memory presets
            for val in [2.0, 3.0, 4.0, 6.0, 8.0]:
                btn = QPushButton(f"{val:.0f}")
                btn.setMaximumWidth(30)
                btn.clicked.connect(lambda checked, v=val: spin.setValue(v))
                layout.addWidget(btn)
                
            return container
            
        # Phone brand selection
        elif key == 'vm.phone.brand':
            combo = QComboBox()
            brands = ['Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Apple', 'Huawei', 'Oppo', 'Vivo']
            combo.addItems(brands)
            if current_value in brands:
                combo.setCurrentText(current_value)
            return combo
            
        # Phone model selection with presets
        elif key == 'vm.phone.model':
            container = QWidget()
            layout = QHBoxLayout(container)
            
            combo = QComboBox()
            combo.setEditable(True)
            models = list(PHONE_MODELS.keys())
            combo.addItems(models)
            combo.setCurrentText(current_value)
            layout.addWidget(combo)
            
            # Preset button
            preset_btn = QPushButton("📱")
            preset_btn.setMaximumWidth(30)
            preset_btn.setToolTip("Chọn từ preset")
            preset_btn.clicked.connect(lambda: self._show_phone_presets(combo))
            layout.addWidget(preset_btn)
            
            return container
            
        # Phone manufacturer
        elif key == 'vm.phone.manufacturer':
            combo = QComboBox()
            combo.setEditable(True)
            manufacturers = ['Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Apple', 'Huawei']
            combo.addItems(manufacturers)
            combo.setCurrentText(current_value)
            return combo
            
        # MIIT model code
        elif key == 'vm.phone.miit':
            line_edit = QLineEdit()
            line_edit.setText(str(current_value))
            line_edit.setPlaceholderText("VD: SM-G7810, GVU6C, CPH2449...")
            return line_edit
            
        # IMEI with generator
        elif key == 'vm.phone.imei':
            container = QWidget()
            layout = QHBoxLayout(container)
            
            line_edit = QLineEdit()
            line_edit.setText(str(current_value))
            line_edit.setPlaceholderText("15-digit IMEI")
            layout.addWidget(line_edit)
            
            # IMEI generator button
            gen_btn = QPushButton("🎲")
            gen_btn.setMaximumWidth(30)
            gen_btn.setToolTip("Tạo IMEI ngẫu nhiên")
            gen_btn.clicked.connect(lambda: line_edit.setText(self._generate_imei()))
            layout.addWidget(gen_btn)
            
            return container
            
        # Root access
        elif key == 'vm.root':
            checkbox = QCheckBox()
            checkbox.setChecked(current_value.lower() == 'true')
            checkbox.setText("Enable root access")
            return checkbox
            
        # System VDI sharing
        elif key == 'vm.system_vdi.sharable':
            combo = QComboBox()
            combo.addItems(['Readonly', 'Writable', 'None'])
            if current_value in ['Readonly', 'Writable', 'None']:
                combo.setCurrentText(current_value)
            return combo
            
        # Port configurations
        elif 'port' in key:
            spin = QSpinBox()
            spin.setRange(1024, 65535)
            try:
                spin.setValue(int(current_value) if current_value.isdigit() else 8080)
            except ValueError:
                spin.setValue(8080)
            return spin
            
        # Boolean ROM reset
        elif key == 'vm.phone.rom.reset':
            checkbox = QCheckBox()
            checkbox.setChecked(current_value == '1')
            checkbox.setText("Reset ROM on restart")
            return checkbox
            
        else:
            # Default text input for other settings
            line_edit = QLineEdit()
            line_edit.setText(str(current_value))
            return line_edit
    
    def _show_phone_presets(self, combo_widget):
        """Show phone model presets dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("📱 Chọn Phone Model")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # List widget for phone models
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        list_widget = QListWidget()
        
        for model, info in PHONE_MODELS.items():
            item = QListWidgetItem(f"{model}")
            item.setData(Qt.ItemDataRole.UserRole, model)
            item.setToolTip(f"{info['description']}\nBrand: {info['brand']}\nMIIT: {info['miit']}")
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        # Buttons
        buttons = QHBoxLayout()
        apply_btn = QPushButton("✅ Chọn")
        cancel_btn = QPushButton("❌ Hủy")
        
        def apply_phone():
            current_item = list_widget.currentItem()
            if current_item:
                model = current_item.data(Qt.ItemDataRole.UserRole)
                combo_widget.setCurrentText(model)
                
                # Auto-update related fields
                if model in PHONE_MODELS:
                    info = PHONE_MODELS[model]
                    # Update brand và manufacturer nếu có widgets
                    for key, widget in self.widgets.items():
                        if key == 'vm.phone.brand' and isinstance(widget, QComboBox):
                            widget.setCurrentText(info['brand'])
                        elif key == 'vm.phone.manufacturer' and isinstance(widget, QComboBox):
                            widget.setCurrentText(info['manufacturer'])
                        elif key == 'vm.phone.miit' and isinstance(widget, QLineEdit):
                            widget.setText(info['miit'])
                
                dialog.accept()
        
        apply_btn.clicked.connect(apply_phone)
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons.addWidget(apply_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        dialog.exec()
    
    def _generate_imei(self) -> str:
        """Generate valid IMEI với Luhn algorithm"""
        import random
        
        # TAC (Type Allocation Code) - first 8 digits
        tac_list = [
            '35328508',  # Samsung
            '35404906',  # Google
            '86891304',  # OnePlus  
            '86071203',  # Xiaomi
            '35064805'   # Generic
        ]
        
        tac = random.choice(tac_list)
        
        # Serial number - next 6 digits
        serial = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Calculate check digit using Luhn algorithm
        digits = tac + serial
        total = 0
        
        for i, digit in enumerate(reversed(digits)):
            n = int(digit)
            if i % 2 == 1:  # Every second digit from right
                n *= 2
                if n > 9:
                    n = n // 10 + n % 10
            total += n
        
        check_digit = (10 - (total % 10)) % 10
        
        return digits + str(check_digit)
    
    def _flatten_vm_config(self, vm_config: dict, prefix: str = 'vm') -> dict:
        """Flatten nested VM config to dot notation"""
        flattened = {}
        
        for key, value in vm_config.items():
            new_key = f"{prefix}.{key}"
            
            if isinstance(value, dict):
                # Recursive flatten for nested objects
                nested = self._flatten_vm_config(value, new_key)
                flattened.update(nested)
            else:
                flattened[new_key] = value
                
        return flattened
    
    def _get_friendly_label(self, key: str) -> str:
        """Get user-friendly Vietnamese label for settings"""
        labels = {
            'vm.cpu': '⚡ CPU Cores',
            'vm.memory': '💾 Bộ nhớ RAM',
            'vm.phone.brand': '📱 Thương hiệu',
            'vm.phone.model': '📲 Model điện thoại',
            'vm.phone.manufacturer': '🏭 Nhà sản xuất',
            'vm.phone.miit': '🏷️ Mã MIIT',
            'vm.phone.imei': '🔢 IMEI',
            'vm.phone.number': '📞 Số điện thoại',
            'vm.phone.code': '🔐 Mã code',
            'vm.phone.rom.reset': '🔄 Reset ROM',
            'vm.root': '🔓 Root Access',
            'vm.system_vdi.sharable': '💿 Chia sẻ VDI',
            'vm.gpu.model': '🎮 GPU Model',
            'vm.nat.port_forward.adb.host_port': '🔌 ADB Port',
            'vm.nat.port_forward.api.host_port': '🌐 API Port'
        }
        
        return labels.get(key, key.replace('_', ' ').replace('.', ' › ').title())
    
    def _get_widget_value(self, widget) -> str:
        """Get value from widget, handling containers"""
        if isinstance(widget, QCheckBox):
            return 'true' if widget.isChecked() else 'false'
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return str(widget.value())
        elif isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QWidget):
            # Handle container widgets
            layout = widget.layout()
            if layout:
                for i in range(layout.count()):
                    child = layout.itemAt(i).widget()
                    if isinstance(child, (QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox)):
                        return self._get_widget_value(child)
        return ""
    
    def get_changed_values(self) -> Dict[str, str]:
        """Get changed settings"""
        changed = {}
        for key, widget in self.widgets.items():
            current_value = self._get_widget_value(widget)
            initial_value = str(self.initial_values.get(key, ""))
            
            if current_value != initial_value:
                changed[key] = current_value
                
        return changed
    
    def show_templates(self):
        """Show template selection dialog"""
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        
        dialog = QDialog(self)
        dialog.setWindowTitle("📋 Chọn Template")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        list_widget = QListWidget()
        for name, template in CONFIG_TEMPLATES.items():
            item = QListWidgetItem(f"{template.get('name', name)}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            item.setToolTip(template.get('description', ''))
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        buttons = QHBoxLayout()
        apply_btn = QPushButton("✅ Áp dụng")
        cancel_btn = QPushButton("❌ Hủy")
        
        def apply_template():
            current_item = list_widget.currentItem()
            if current_item:
                template_name = current_item.data(Qt.ItemDataRole.UserRole)
                self._apply_template(template_name)
                dialog.accept()
        
        apply_btn.clicked.connect(apply_template)
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons.addWidget(apply_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        dialog.exec()
    
    def _apply_template(self, template_name: str):
        """Apply template to current settings"""
        if template_name not in CONFIG_TEMPLATES:
            return
            
        template = CONFIG_TEMPLATES[template_name]
        settings = template.get('settings', {})
        
        for key, value in settings.items():
            if key in self.widgets:
                widget = self.widgets[key]
                self._set_widget_value(widget, value)
        
        QMessageBox.information(self, "✅ Template", f"Đã áp dụng template: {template.get('name', template_name)}")
    
    def _set_widget_value(self, widget, value: str):
        """Set value to widget, handling containers"""
        if isinstance(widget, QCheckBox):
            widget.setChecked(value.lower() == 'true')
        elif isinstance(widget, QComboBox):
            index = widget.findText(value)
            if index >= 0:
                widget.setCurrentIndex(index)
            else:
                widget.setCurrentText(value)
        elif isinstance(widget, QSpinBox):
            try:
                widget.setValue(int(float(value)))
            except (ValueError, TypeError):
                pass
        elif isinstance(widget, QDoubleSpinBox):
            try:
                widget.setValue(float(value))
            except (ValueError, TypeError):
                pass
        elif isinstance(widget, QLineEdit):
            widget.setText(value)
        elif isinstance(widget, QWidget):
            # Handle container widgets
            layout = widget.layout()
            if layout:
                for i in range(layout.count()):
                    child = layout.itemAt(i).widget()
                    if isinstance(child, (QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox)):
                        self._set_widget_value(child, value)
                        break
    
    def import_settings(self):
        """Import settings from JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Settings", "", "JSON Files (*.json);;All Files (*)")
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Support both flat settings và VM config structure
            if 'vm' in data and isinstance(data['vm'], dict):
                # VM config format từ JSON mẫu
                vm_config = data['vm']
                settings = self._flatten_vm_config(vm_config)
            else:
                settings = data.get('settings', data)
            
            for key, value in settings.items():
                if key in self.widgets:
                    self._set_widget_value(self.widgets[key], str(value))
            
            QMessageBox.information(self, "✅ Import", "VM settings imported successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Failed to import settings:\n{e}")
    
    def export_settings(self):
        """Export settings to JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Settings", "mumu_settings.json", "JSON Files (*.json);;All Files (*)")
        
        if not file_path:
            return
            
        try:
            # Get current values
            settings = {}
            for key, widget in self.widgets.items():
                settings[key] = self._get_widget_value(widget)
            
            # Create export data
            export_data = {
                'metadata': {
                    'export_time': '2024-01-01T12:00:00',
                    'version': '2.0',
                    'instances': len(self.indices)
                },
                'settings': settings
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "✅ Export", "Settings exported successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Failed to export settings:\n{e}")

    def _apply_custom_title_bar_style(self):
        """Apply custom styling to make title bar match main app"""
        # Set window flags for custom styling
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowTitleHint | 
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )
        
        # Apply custom stylesheet for title bar color matching main app
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
        """)

# For backward compatibility
SettingsEditorDialog = SimpleSettingsEditorDialog
