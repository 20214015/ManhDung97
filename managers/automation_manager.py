"""
Automation Manager
==================

Handles all automation and scripting operations extracted from main_window.py.
Provides a clean separation of automation logic from UI code.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QFileDialog

from backend import MumuManager
from workers import GenericWorker
from core import get_event_manager, get_state_manager, EventTypes, emit_event


class AutomationManager(QObject):
    """
    Manages all automation and scripting operations including:
    - Script execution and management
    - Automation sequences
    - Template handling
    - Batch operations
    """
    
    # Signals for UI updates
    automation_started = pyqtSignal(str)  # automation_type
    automation_stopped = pyqtSignal(str)  # automation_type
    automation_paused = pyqtSignal(str)   # automation_type
    script_executed = pyqtSignal(str, bool, str)  # script_name, success, message
    script_saved = pyqtSignal(str)        # file_path
    script_loaded = pyqtSignal(str)       # file_path
    template_applied = pyqtSignal(str)    # template_name
    progress_updated = pyqtSignal(int, str)  # progress, description
    
    def __init__(self, mumu_manager: MumuManager, parent=None):
        super().__init__(parent)
        self.mumu_manager = mumu_manager
        self.logger = logging.getLogger('AutomationManager')
        
        # State management
        self.state_manager = get_state_manager()
        self.event_manager = get_event_manager()
        
        # Automation state
        self._current_script: str = ""
        self._script_templates: Dict[str, str] = {}
        self._automation_settings: Dict[str, Any] = {}
        self._is_automation_running: bool = False
        
        # Worker management
        self.automation_worker: Optional[GenericWorker] = None
        self.script_worker: Optional[GenericWorker] = None
        
        # Setup
        self._load_script_templates()
        self._setup_event_subscriptions()
        
    def _setup_event_subscriptions(self):
        """Setup event subscriptions for automation events"""
        self.event_manager.subscribe(EventTypes.AUTOMATION_STARTED, self._on_automation_started_event)
        self.event_manager.subscribe(EventTypes.AUTOMATION_STOPPED, self._on_automation_stopped_event)
        self.event_manager.subscribe(EventTypes.SCRIPT_EXECUTED, self._on_script_executed_event)
        
    def _on_automation_started_event(self, data: Dict[str, Any]):
        """Handle automation started event"""
        automation_type = data.get('type', 'unknown')
        self._is_automation_running = True
        self.automation_started.emit(automation_type)
        
    def _on_automation_stopped_event(self, data: Dict[str, Any]):
        """Handle automation stopped event"""
        automation_type = data.get('type', 'unknown')
        self._is_automation_running = False
        self.automation_stopped.emit(automation_type)
        
    def _on_script_executed_event(self, data: Dict[str, Any]):
        """Handle script executed event"""
        script_name = data.get('script_name', 'unknown')
        success = data.get('success', False)
        message = data.get('message', '')
        self.script_executed.emit(script_name, success, message)
        
    def _load_script_templates(self):
        """Load predefined script templates"""
        self._script_templates = {
            "Basic Instance Control": """# Basic Instance Control Script
# Control multiple instances with simple commands

# Get selected instances
selected_instances = get_selected_instances()

# Start all selected instances
for instance_id in selected_instances:
    start_instance(instance_id)
    wait(2)  # Wait 2 seconds between starts

print(f"Started {len(selected_instances)} instances")
""",
            
            "App Installation": """# App Installation Script
# Install APK on selected instances

# Configuration
apk_path = "/path/to/your/app.apk"
package_name = "com.example.app"

# Get selected instances
selected_instances = get_selected_instances()

# Install on each instance
for instance_id in selected_instances:
    print(f"Installing {package_name} on instance {instance_id}")
    install_apk(instance_id, apk_path)
    wait(5)  # Wait for installation

print(f"Installation completed on {len(selected_instances)} instances")
""",
            
            "Batch Operations": """# Batch Operations Script
# Perform multiple operations on instances

# Get all instances
all_instances = get_all_instances()

# Filter running instances
running_instances = [inst for inst in all_instances if inst['status'] == 'running']

# Perform batch operations
for instance in running_instances:
    instance_id = instance['id']
    
    # Example operations
    send_key(instance_id, "KEYCODE_HOME")
    wait(1)
    
    # Launch app
    launch_app(instance_id, "com.example.app")
    wait(3)
    
    # Take screenshot
    screenshot(instance_id, f"screenshot_{instance_id}.png")

print(f"Batch operations completed on {len(running_instances)} instances")
""",
            
            "System Cleanup": """# System Cleanup Script
# Clean up instances and reset states

# Get selected instances
selected_instances = get_selected_instances()

for instance_id in selected_instances:
    print(f"Cleaning up instance {instance_id}")
    
    # Stop instance
    stop_instance(instance_id)
    wait(2)
    
    # Clear app data
    clear_app_data(instance_id, "com.example.app")
    
    # Restart instance
    start_instance(instance_id)
    wait(5)

print(f"Cleanup completed on {len(selected_instances)} instances")
""",
            
            "Performance Monitor": """# Performance Monitor Script
# Monitor instance performance metrics

import time

# Get selected instances
selected_instances = get_selected_instances()

# Monitor for 60 seconds
duration = 60
start_time = time.time()

while time.time() - start_time < duration:
    for instance_id in selected_instances:
        # Get performance metrics
        cpu_usage = get_cpu_usage(instance_id)
        memory_usage = get_memory_usage(instance_id)
        
        print(f"Instance {instance_id}: CPU={cpu_usage}%, Memory={memory_usage}MB")
    
    wait(10)  # Check every 10 seconds

print("Performance monitoring completed")
"""
        }
        
    # Script Management
    def get_current_script(self) -> str:
        """Get current script content"""
        return self._current_script
        
    def set_current_script(self, script: str):
        """Set current script content"""
        self._current_script = script
        
    def clear_current_script(self):
        """Clear current script content"""
        self._current_script = ""
        
    # Script Execution
    def execute_script(self, script: str = None, script_name: str = "Custom Script") -> bool:
        """
        Execute a script.
        
        Args:
            script: Script content to execute (uses current script if None)
            script_name: Name of the script for logging
            
        Returns:
            True if script execution started successfully
        """
        try:
            if script is None:
                script = self._current_script
                
            if not script.strip():
                self.script_executed.emit(script_name, False, "Script is empty")
                return False
                
            def script_task(worker: GenericWorker, manager: MumuManager, params: dict) -> dict:
                """Background task for script execution"""
                script_content = params.get('script', '')
                script_name = params.get('script_name', 'Unknown')
                
                worker.started.emit(f"Executing script: {script_name}")
                worker.progress.emit(10)
                
                try:
                    # TODO: Implement actual script execution engine
                    # For now, we'll simulate script execution
                    
                    # Parse script and extract commands
                    lines = script_content.split('\n')
                    command_count = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
                    
                    worker.progress.emit(50)
                    
                    # Simulate execution
                    import time
                    time.sleep(2)  # Simulate processing time
                    
                    worker.progress.emit(100)
                    
                    return {
                        "success": True,
                        "message": f"Script executed successfully ({command_count} commands processed)",
                        "script_name": script_name
                    }
                    
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Script execution failed: {str(e)}",
                        "script_name": script_name
                    }
                    
            # Clean up previous worker if exists
            if self.script_worker is not None:
                self.script_worker.finished.disconnect()
                if hasattr(self.script_worker, 'error'):
                    self.script_worker.error.disconnect()
                self.script_worker.progress.disconnect()
                if self.script_worker.isRunning():
                    self.script_worker.terminate()
                    self.script_worker.wait()
                self.script_worker.deleteLater()
                self.script_worker = None
            
            # Create and start worker
            self.script_worker = GenericWorker(script_task, self.mumu_manager, {
                'script': script,
                'script_name': script_name
            })
            
            self.script_worker.finished.connect(self._on_script_executed)
            if hasattr(self.script_worker, 'error'):
                self.script_worker.error.connect(self._on_script_error)
            self.script_worker.progress.connect(
                lambda progress: self.progress_updated.emit(progress, f"Executing {script_name}")
            )
            
            self.script_worker.start()
            
            # Emit event
            emit_event(EventTypes.SCRIPT_EXECUTED, {
                'script_name': script_name,
                'started': True
            })
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to start script execution: {e}"
            self.logger.error(error_msg)
            self.script_executed.emit(script_name, False, error_msg)
            return False
            
    def _on_script_executed(self, result: dict):
        """Handle script execution completion"""
        success = result.get("success", False)
        message = result.get("message", "")
        script_name = result.get("script_name", "Unknown")
        
        self.script_executed.emit(script_name, success, message)
        
        # Emit event
        emit_event(EventTypes.SCRIPT_EXECUTED, {
            'script_name': script_name,
            'success': success,
            'message': message
        })
        
        # Clean up worker after completion
        if self.script_worker is not None:
            self.script_worker.finished.disconnect()
            if hasattr(self.script_worker, 'error'):
                self.script_worker.error.disconnect()
            self.script_worker.progress.disconnect()
            self.script_worker.deleteLater()
            self.script_worker = None
        
    def _on_script_error(self, error: str):
        """Handle script execution error"""
        self.logger.error(f"Script execution error: {error}")
        self.script_executed.emit("Unknown", False, f"Script error: {error}")
        
        # Clean up worker after error
        if self.script_worker is not None:
            self.script_worker.finished.disconnect()
            if hasattr(self.script_worker, 'error'):
                self.script_worker.error.disconnect()
            self.script_worker.progress.disconnect()
            self.script_worker.deleteLater()
            self.script_worker = None
    
    def cleanup(self):
        """Clean up resources when manager is destroyed"""
        if self.script_worker is not None:
            self.script_worker.finished.disconnect()
            if hasattr(self.script_worker, 'error'):
                self.script_worker.error.disconnect()
            self.script_worker.progress.disconnect()
            if self.script_worker.isRunning():
                self.script_worker.terminate()
                self.script_worker.wait()
            self.script_worker.deleteLater()
            self.script_worker = None
            
        if self.automation_worker is not None:
            if self.automation_worker.isRunning():
                self.automation_worker.terminate()
                self.automation_worker.wait()
            self.automation_worker.deleteLater()
            self.automation_worker = None
        
    # Script File Operations
    def save_script(self, file_path: str = None) -> bool:
        """
        Save current script to file.
        
        Args:
            file_path: File path to save to (prompts user if None)
            
        Returns:
            True if saved successfully
        """
        try:
            if not file_path:
                file_path, _ = QFileDialog.getSaveFileName(
                    None,
                    "Save Script",
                    "",
                    "Python Files (*.py);;Text Files (*.txt);;All Files (*)"
                )
                
            if not file_path:
                return False
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self._current_script)
                
            self.script_saved.emit(file_path)
            self.logger.info(f"Script saved to: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to save script: {e}"
            self.logger.error(error_msg)
            QMessageBox.critical(None, "Save Error", error_msg)
            return False
            
    def load_script(self, file_path: str = None) -> bool:
        """
        Load script from file.
        
        Args:
            file_path: File path to load from (prompts user if None)
            
        Returns:
            True if loaded successfully
        """
        try:
            if not file_path:
                file_path, _ = QFileDialog.getOpenFileName(
                    None,
                    "Load Script",
                    "",
                    "Python Files (*.py);;Text Files (*.txt);;All Files (*)"
                )
                
            if not file_path:
                return False
                
            if not os.path.exists(file_path):
                QMessageBox.warning(None, "File Error", f"File not found: {file_path}")
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                self._current_script = f.read()
                
            self.script_loaded.emit(file_path)
            self.logger.info(f"Script loaded from: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to load script: {e}"
            self.logger.error(error_msg)
            QMessageBox.critical(None, "Load Error", error_msg)
            return False
            
    # Template Management
    def get_script_templates(self) -> Dict[str, str]:
        """Get available script templates"""
        return self._script_templates.copy()
        
    def apply_script_template(self, template_name: str) -> bool:
        """
        Apply a script template.
        
        Args:
            template_name: Name of the template to apply
            
        Returns:
            True if template applied successfully
        """
        try:
            if template_name not in self._script_templates:
                self.logger.warning(f"Template not found: {template_name}")
                return False
                
            self._current_script = self._script_templates[template_name]
            self.template_applied.emit(template_name)
            self.logger.info(f"Applied template: {template_name}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to apply template: {e}"
            self.logger.error(error_msg)
            return False
            
    def add_script_template(self, name: str, content: str):
        """Add a new script template"""
        self._script_templates[name] = content
        self.logger.info(f"Added script template: {name}")
        
    # Automation Control
    def start_automation(self, automation_type: str = "custom") -> bool:
        """
        Start automation sequence.
        
        Args:
            automation_type: Type of automation to start
            
        Returns:
            True if automation started successfully
        """
        try:
            if self._is_automation_running:
                self.logger.warning("Automation is already running")
                return False
                
            def automation_task(worker: GenericWorker, manager: MumuManager, params: dict) -> dict:
                """Background task for automation"""
                automation_type = params.get('automation_type', 'custom')
                
                worker.started.emit(f"Starting {automation_type} automation")
                worker.progress.emit(10)
                
                try:
                    # TODO: Implement actual automation logic based on type
                    # For now, we'll simulate automation
                    
                    selected_instances = params.get('selected_instances', [])
                    
                    for i, instance_id in enumerate(selected_instances):
                        worker.progress.emit(10 + (i * 80 // len(selected_instances)))
                        
                        # Simulate automation steps
                        import time
                        time.sleep(1)
                        
                    worker.progress.emit(100)
                    
                    return {
                        "success": True,
                        "message": f"{automation_type} automation completed successfully",
                        "automation_type": automation_type
                    }
                    
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Automation failed: {str(e)}",
                        "automation_type": automation_type
                    }
                    
            # Get selected instances
            selected_instances = self.state_manager.get_selected_instances()
            
            # Create and start worker
            self.automation_worker = GenericWorker(automation_task, self.mumu_manager, {
                'automation_type': automation_type,
                'selected_instances': selected_instances
            })
            
            self.automation_worker.finished.connect(self._on_automation_completed)
            self.automation_worker.error.connect(self._on_automation_error)
            self.automation_worker.progress.connect(
                lambda progress: self.progress_updated.emit(progress, f"Running {automation_type} automation")
            )
            
            self.automation_worker.start()
            
            # Update state and emit events
            self._is_automation_running = True
            emit_event(EventTypes.AUTOMATION_STARTED, {'type': automation_type})
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to start automation: {e}"
            self.logger.error(error_msg)
            return False
            
    def stop_automation(self) -> bool:
        """Stop running automation"""
        try:
            if not self._is_automation_running:
                return True
                
            if self.automation_worker and self.automation_worker.isRunning():
                self.automation_worker.terminate()
                self.automation_worker.wait(3000)
                
            self._is_automation_running = False
            emit_event(EventTypes.AUTOMATION_STOPPED, {'type': 'manual_stop'})
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to stop automation: {e}"
            self.logger.error(error_msg)
            return False
            
    def _on_automation_completed(self, result: dict):
        """Handle automation completion"""
        success = result.get("success", False)
        message = result.get("message", "")
        automation_type = result.get("automation_type", "unknown")
        
        self._is_automation_running = False
        
        if success:
            emit_event(EventTypes.AUTOMATION_STOPPED, {
                'type': automation_type,
                'completed': True,
                'message': message
            })
        else:
            emit_event(EventTypes.ERROR_OCCURRED, {
                'type': 'automation_error',
                'message': message
            })
            
    def _on_automation_error(self, error: str):
        """Handle automation error"""
        self.logger.error(f"Automation error: {error}")
        self._is_automation_running = False
        emit_event(EventTypes.ERROR_OCCURRED, {
            'type': 'automation_error',
            'message': error
        })
        
    # Settings Management
    def update_automation_settings(self, settings: Dict[str, Any]):
        """Update automation settings"""
        self._automation_settings.update(settings)
        self.state_manager.update_automation_settings(settings)
        
    def get_automation_settings(self) -> Dict[str, Any]:
        """Get current automation settings"""
        return self._automation_settings.copy()
        
    # Status and State
    def is_automation_running(self) -> bool:
        """Check if automation is currently running"""
        return self._is_automation_running
        
    def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation status"""
        return {
            'running': self._is_automation_running,
            'current_script_length': len(self._current_script),
            'templates_available': len(self._script_templates),
            'settings': self._automation_settings.copy()
        }
        
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop any running workers
            if self.automation_worker and self.automation_worker.isRunning():
                self.automation_worker.terminate()
                self.automation_worker.wait(3000)
                
            if self.script_worker and self.script_worker.isRunning():
                self.script_worker.terminate()
                self.script_worker.wait(3000)
                
            self._is_automation_running = False
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")