# error_handler.py - Enhanced centralized error handling và logging system

import traceback
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional, Any, Dict, Callable
from PyQt6.QtWidgets import QMessageBox, QApplication, QWidget
from PyQt6.QtCore import QObject, pyqtSignal

class ErrorHandler(QObject):
    """Enhanced error handler với signals và advanced logging"""
    
    error_occurred = pyqtSignal(str, str)  # error_type, message
    warning_occurred = pyqtSignal(str, str)  # component, message
    
    def __init__(self, log_file: Optional[str] = None):
        super().__init__()
        self.log_file = log_file or os.path.join(os.path.expanduser("~"), "mumu_manager_errors.log")
        self.error_count = 0
        self.parent_widget: Optional[QWidget] = None
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup structured logging"""
        self.logger = logging.getLogger('MumuManager')
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)

            file_handler = RotatingFileHandler(
                self.log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
            )
            file_handler.setFormatter(formatter)

            self.logger.addHandler(stream_handler)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)
            
    def set_parent_widget(self, widget: QWidget):
        """Set parent widget for error dialogs"""
        self.parent_widget = widget
        
    def handle_exception(self, exc_type, exc_value, exc_traceback, 
                        show_dialog: bool = True, operation: str = "Unknown"):
        """Enhanced exception handling với categorization"""
        self.error_count += 1
        
        # Create structured error message
        error_msg = f"{exc_type.__name__}: {str(exc_value)}"
        full_traceback = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Log với structured format
        self.logger.error(f"Exception in {operation}: {error_msg}")
        self.logger.debug(f"Full traceback:\n{full_traceback}")
        
        # Legacy file logging
        self._log_to_file(exc_type, exc_value, exc_traceback, operation)
        
        # Show dialog if requested and GUI is available
        if show_dialog and (QApplication.instance() and self.parent_widget):
            self._show_error_dialog(error_msg, full_traceback, operation)
            
        # Emit signal for other components
        self.error_occurred.emit(exc_type.__name__, error_msg)
        
        return error_msg
    
    def handle_backend_error(self, operation: str, error: Exception, 
                           show_dialog: bool = True) -> bool:
        """Handle specific backend operation errors"""
        try:
            error_msg = f"Backend operation '{operation}' failed: {str(error)}"
            self.logger.error(error_msg)
            
            if show_dialog and self.parent_widget:
                user_msg = self._get_user_friendly_message(operation, error)
                self._show_error_dialog(user_msg, str(error), operation)
                
            self.error_occurred.emit("BackendError", error_msg)
            return True
            
        except Exception as e:
            self.logger.critical(f"Error in error handler: {e}")
            return False
    
    def handle_worker_error(self, worker_name: str, error: Exception) -> bool:
        """Handle worker thread errors"""
        try:
            error_msg = f"Worker '{worker_name}' encountered error: {str(error)}"
            self.logger.error(error_msg)
            
            # For worker errors, usually don't show dialog unless critical
            if "critical" in str(error).lower() and self.parent_widget:
                self._show_error_dialog(f"Background task '{worker_name}' failed", str(error))
                                          
            self.error_occurred.emit("WorkerError", error_msg)
            return True
            
        except Exception as e:
            self.logger.critical(f"Error handling worker error: {e}")
            return False
    
    def _get_user_friendly_message(self, operation: str, error: Exception) -> str:
        """Convert technical error to user-friendly message"""
        error_str = str(error).lower()
        
        if "permission" in error_str or "access" in error_str:
            return f"Permission denied for '{operation}'. Check if MumuPlayer is running as administrator."
        elif "not found" in error_str:
            return f"Required component not found for '{operation}'. Check MumuPlayer installation."
        elif "timeout" in error_str:
            return f"Operation '{operation}' timed out. The system may be busy."
        elif "json" in error_str:
            return f"Failed to parse response from MumuPlayer for '{operation}'."
        else:
            return f"Operation '{operation}' failed: {str(error)}"
        
    def _log_to_file(self, exc_type, exc_value, exc_traceback, operation: str = "Unknown"):
        """Enhanced file logging với operation context"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Error #{self.error_count}\n")
                f.write(f"Operation: {operation}\n")
                f.write(f"Exception: {exc_type.__name__}: {exc_value}\n")
                f.write("Traceback:\n")
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
                f.write(f"{'='*60}\n")
        except Exception as e:
            self.logger.error(f"Cannot write to log file: {e}")
    
    def _show_error_dialog(self, error_msg: str, details: str = "", operation: str = "Unknown"):
        """Enhanced error dialog với details và operation context"""
        try:
            msg_box = QMessageBox(self.parent_widget)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(f"Application Error - {operation}")
            msg_box.setText(f"An error occurred during operation:\n\n{error_msg}")
            
            if details:
                msg_box.setDetailedText(details)
                
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
        except Exception as e:
            self.logger.error(f"Cannot show error dialog: {e}")
    
    def log_warning(self, message: str, component: str = "Unknown"):
        """Enhanced warning logging với signals"""
        try:
            self.logger.warning(f"{component}: {message}")
            self.warning_occurred.emit(component, message)
        except Exception as e:
            print(f"[WARNING] {component}: {message}")
            self.logger.error(f"Failed to log warning: {e}")
    
    def log_info(self, message: str, component: str = "Unknown"):
        """Enhanced info logging"""
        try:
            self.logger.info(f"{component}: {message}")
        except Exception as e:
            print(f"[INFO] {component}: {message}")
            self.logger.error(f"Failed to log info: {e}")
    
    def create_safe_executor(self):
        """Create a SafeExecutor instance linked to this error handler"""
        return SafeExecutor(self)
    
    def safe_execute(self, func: Callable, operation_name: str = "Unknown", 
                    default_return=None, show_dialog: bool = True):
        """Safely execute a function with error handling"""
        try:
            return func()
        except Exception as e:
            self.handle_backend_error(operation_name, e, show_dialog)
            return default_return

class SafeExecutor:
    """Enhanced safe execution với advanced error handling"""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
    
    def safe_execute(self, func, *args, default_return=None, component="Unknown", 
                    show_dialog=False, **kwargs):
        """Enhanced safe execution với detailed error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            operation_name = f"{component}.{func.__name__}"
            if show_dialog:
                self.error_handler.handle_backend_error(operation_name, e, True)
            else:
                self.error_handler.log_warning(f"Error in {operation_name}: {e}", component)
            return default_return
    
    def safe_dict_get(self, dictionary: Dict, key: Any, default: Any = None, 
                     component: str = "Dict"):
        """Enhanced safe dictionary access"""
        try:
            if not isinstance(dictionary, dict):
                self.error_handler.log_warning(f"Expected dict, got {type(dictionary)}", component)
                return default
            return dictionary.get(key, default)
        except Exception as e:
            self.error_handler.log_warning(f"Error accessing key '{key}': {e}", component)
            return default
    
    def safe_file_operation(self, operation, file_path: str, *args, 
                           component: str = "FileOp", **kwargs):
        """Enhanced safe file operations"""
        try:
            return operation(file_path, *args, **kwargs)
        except FileNotFoundError:
            self.error_handler.log_warning(f"File not found: {file_path}", component)
            return None
        except PermissionError:
            self.error_handler.log_warning(f"Permission denied: {file_path}", component)
            return None
        except OSError as e:
            self.error_handler.log_warning(f"OS error on {file_path}: {e}", component)
            return None
        except Exception as e:
            self.error_handler.log_warning(f"Unexpected error on {file_path}: {e}", component)
            return None
    
    def safe_json_operation(self, json_str: str, component: str = "JSON"):
        """Safe JSON parsing với detailed error messages and validation"""
        import json
        try:
            if not isinstance(json_str, str):
                self.error_handler.log_warning(f"Expected string for JSON parsing, got {type(json_str)}", component)
                return None
            
            if not json_str.strip():
                self.error_handler.log_warning("Empty JSON string provided", component)
                return None
                
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            self.error_handler.log_warning(f"JSON decode error at line {e.lineno}, col {e.colno}: {e.msg}", component)
            return None
        except Exception as e:
            self.error_handler.log_warning(f"Unexpected JSON error: {e}", component)
            return None
    
    def safe_numeric_operation(self, value: Any, operation: str = "conversion", component: str = "Math"):
        """Safe numeric operations with validation"""
        try:
            if isinstance(value, (int, float)):
                return value
            elif isinstance(value, str):
                # Try int first, then float
                try:
                    return int(value)
                except ValueError:
                    return float(value)
            else:
                self.error_handler.log_warning(f"Cannot convert {type(value)} to number", component)
                return 0
        except (ValueError, TypeError) as e:
            self.error_handler.log_warning(f"Numeric {operation} error: {e}", component)
            return 0
        except Exception as e:
            self.error_handler.log_warning(f"Unexpected numeric error: {e}", component)
            return 0

# Global error handler instance - Enhanced
global_error_handler = ErrorHandler()

def setup_global_exception_handler():
    """Enhanced global exception handler setup"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        # Skip KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        global_error_handler.handle_exception(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = handle_exception

# Convenience functions - Enhanced
def handle_error(operation: str, error: Exception, show_dialog: bool = True) -> bool:
    """Convenience function for handling backend errors"""
    return global_error_handler.handle_backend_error(operation, error, show_dialog)

def handle_worker_error(worker_name: str, error: Exception) -> bool:
    """Convenience function for handling worker errors"""
    return global_error_handler.handle_worker_error(worker_name, error)

def safe_execute(func: Callable, operation_name: str = "Unknown", 
                default_return=None, show_dialog: bool = True):
    """Convenience function for safe execution"""
    return global_error_handler.safe_execute(func, operation_name, default_return, show_dialog)

def log_warning(message: str, component: str = "App"):
    """Convenience function for warnings"""
    global_error_handler.log_warning(message, component)

def log_info(message: str, component: str = "App"):
    """Convenience function for info logging"""
    global_error_handler.log_info(message, component)
