"""
1-Click Diagnostics System
==========================

Quick diagnostic checks for CLI path, version, permissions, ADB, qemu-img.
Provides results and fix suggestions.
"""

import os
import subprocess
import shutil
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QProgressBar


class DiagnosticStatus(Enum):
    """Diagnostic check status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    UNKNOWN = "unknown"


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check"""
    name: str
    status: DiagnosticStatus
    message: str
    details: str = ""
    fix_suggestion: str = ""


class DiagnosticsWorker(QThread):
    """Background worker for diagnostic checks"""
    
    progress_updated = pyqtSignal(int, str)  # progress, current_check
    check_completed = pyqtSignal(DiagnosticResult)
    all_completed = pyqtSignal(list)  # List[DiagnosticResult]
    
    def __init__(self):
        super().__init__()
        self.results = []
        
    def run(self):
        """Run all diagnostic checks"""
        checks = [
            ("MuMu Manager Executable", self._check_mumu_executable),
            ("MuMu Manager Version", self._check_mumu_version),
            ("Process Permissions", self._check_permissions),
            ("ADB Installation", self._check_adb),
            ("QEMU Tools", self._check_qemu_img),
            ("System Resources", self._check_system_resources),
            ("Network Connectivity", self._check_network),
        ]
        
        total_checks = len(checks)
        
        for i, (name, check_func) in enumerate(checks):
            self.progress_updated.emit(int((i / total_checks) * 100), name)
            
            try:
                result = check_func()
                self.results.append(result)
                self.check_completed.emit(result)
            except Exception as e:
                error_result = DiagnosticResult(
                    name=name,
                    status=DiagnosticStatus.FAIL,
                    message=f"Check failed: {str(e)}",
                    fix_suggestion="Contact support if this error persists."
                )
                self.results.append(error_result)
                self.check_completed.emit(error_result)
                
        self.progress_updated.emit(100, "Diagnostics Complete")
        self.all_completed.emit(self.results)
        
    def _check_mumu_executable(self) -> DiagnosticResult:
        """Check if MuMu Manager executable exists and is accessible"""
        possible_paths = [
            r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe",
            r"C:\Program Files\Netease\MuMuPlayer-12.0\shell\MuMuManager.exe",
            r"C:\Program Files (x86)\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe",
            r"C:\Program Files (x86)\Netease\MuMuPlayer-12.0\shell\MuMuManager.exe"
        ]
        
        found_paths = []
        for path in possible_paths:
            if os.path.isfile(path):
                found_paths.append(path)
                
        if found_paths:
            primary_path = found_paths[0]
            try:
                # Test if executable is accessible
                result = subprocess.run([primary_path, "--help"], 
                                      capture_output=True, timeout=10)
                return DiagnosticResult(
                    name="MuMu Manager Executable",
                    status=DiagnosticStatus.PASS,
                    message=f"Found and accessible: {primary_path}",
                    details=f"Found {len(found_paths)} installation(s): {', '.join(found_paths)}"
                )
            except Exception as e:
                return DiagnosticResult(
                    name="MuMu Manager Executable",
                    status=DiagnosticStatus.WARNING,
                    message=f"Found but not accessible: {primary_path}",
                    details=f"Error: {e}",
                    fix_suggestion="Check if MuMu Manager is properly installed and not corrupted."
                )
        else:
            return DiagnosticResult(
                name="MuMu Manager Executable",
                status=DiagnosticStatus.FAIL,
                message="MuMu Manager executable not found",
                fix_suggestion="Install MuMu Player from the official website: https://www.mumuplayer.com/"
            )
            
    def _check_mumu_version(self) -> DiagnosticResult:
        """Check MuMu Manager version"""
        # Find executable first
        possible_paths = [
            r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe",
            r"C:\Program Files\Netease\MuMuPlayer-12.0\shell\MuMuManager.exe",
            r"C:\Program Files (x86)\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe",
            r"C:\Program Files (x86)\Netease\MuMuPlayer-12.0\shell\MuMuManager.exe"
        ]
        
        executable_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                executable_path = path
                break
                
        if not executable_path:
            return DiagnosticResult(
                name="MuMu Manager Version",
                status=DiagnosticStatus.FAIL,
                message="Cannot check version - executable not found",
                fix_suggestion="Install MuMu Player first"
            )
            
        try:
            result = subprocess.run([executable_path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_info = result.stdout.strip()
                return DiagnosticResult(
                    name="MuMu Manager Version",
                    status=DiagnosticStatus.PASS,
                    message=f"Version check successful",
                    details=version_info or "Version information available"
                )
            else:
                return DiagnosticResult(
                    name="MuMu Manager Version",
                    status=DiagnosticStatus.WARNING,
                    message="Version check returned error",
                    details=f"Return code: {result.returncode}, Error: {result.stderr}",
                    fix_suggestion="Try reinstalling MuMu Player"
                )
        except subprocess.TimeoutExpired:
            return DiagnosticResult(
                name="MuMu Manager Version",
                status=DiagnosticStatus.WARNING,
                message="Version check timed out",
                fix_suggestion="MuMu Manager may be slow to respond. Try again later."
            )
        except Exception as e:
            return DiagnosticResult(
                name="MuMu Manager Version",
                status=DiagnosticStatus.FAIL,
                message=f"Version check failed: {str(e)}",
                fix_suggestion="Check if MuMu Manager is properly installed"
            )
            
    def _check_permissions(self) -> DiagnosticResult:
        """Check if running with appropriate permissions"""
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            
            if is_admin:
                return DiagnosticResult(
                    name="Process Permissions",
                    status=DiagnosticStatus.PASS,
                    message="Running with administrator privileges",
                    details="Full system access available"
                )
            else:
                return DiagnosticResult(
                    name="Process Permissions",
                    status=DiagnosticStatus.WARNING,
                    message="Not running as administrator",
                    details="Some operations may require elevated permissions",
                    fix_suggestion="Right-click the application and 'Run as administrator' if you encounter permission issues"
                )
        except Exception:
            return DiagnosticResult(
                name="Process Permissions",
                status=DiagnosticStatus.UNKNOWN,
                message="Could not determine permission level",
                fix_suggestion="If you encounter permission errors, try running as administrator"
            )
            
    def _check_adb(self) -> DiagnosticResult:
        """Check ADB installation and accessibility"""
        # Check if adb is in PATH
        adb_path = shutil.which("adb")
        
        if adb_path:
            try:
                result = subprocess.run(["adb", "version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_info = result.stdout.strip().split('\n')[0] if result.stdout else "Unknown version"
                    return DiagnosticResult(
                        name="ADB Installation",
                        status=DiagnosticStatus.PASS,
                        message=f"ADB found and working: {adb_path}",
                        details=version_info
                    )
                else:
                    return DiagnosticResult(
                        name="ADB Installation",
                        status=DiagnosticStatus.WARNING,
                        message=f"ADB found but not working properly: {adb_path}",
                        details=f"Error: {result.stderr}",
                        fix_suggestion="Reinstall Android SDK Platform Tools"
                    )
            except Exception as e:
                return DiagnosticResult(
                    name="ADB Installation",
                    status=DiagnosticStatus.WARNING,
                    message=f"ADB found but failed to execute: {adb_path}",
                    details=f"Error: {e}",
                    fix_suggestion="Check ADB installation and permissions"
                )
        else:
            return DiagnosticResult(
                name="ADB Installation",
                status=DiagnosticStatus.FAIL,
                message="ADB not found in system PATH",
                fix_suggestion="Install Android SDK Platform Tools and add to PATH, or use MuMu's built-in ADB"
            )
            
    def _check_qemu_img(self) -> DiagnosticResult:
        """Check for QEMU tools (for disk image operations)"""
        qemu_img_path = shutil.which("qemu-img")
        
        if qemu_img_path:
            try:
                result = subprocess.run(["qemu-img", "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_info = result.stdout.strip().split('\n')[0] if result.stdout else "Unknown version"
                    return DiagnosticResult(
                        name="QEMU Tools",
                        status=DiagnosticStatus.PASS,
                        message=f"QEMU tools found: {qemu_img_path}",
                        details=version_info
                    )
                else:
                    return DiagnosticResult(
                        name="QEMU Tools",
                        status=DiagnosticStatus.WARNING,
                        message="QEMU tools found but not working",
                        fix_suggestion="Reinstall QEMU or check installation"
                    )
            except Exception:
                return DiagnosticResult(
                    name="QEMU Tools",
                    status=DiagnosticStatus.WARNING,
                    message="QEMU tools found but failed to execute",
                    fix_suggestion="Check QEMU installation"
                )
        else:
            return DiagnosticResult(
                name="QEMU Tools",
                status=DiagnosticStatus.WARNING,
                message="QEMU tools not found",
                details="Optional for advanced disk operations",
                fix_suggestion="Install QEMU if you need advanced disk image features"
            )
            
    def _check_system_resources(self) -> DiagnosticResult:
        """Check system resources (RAM, disk space)"""
        try:
            import psutil
            
            # Check RAM
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            
            # Check disk space on system drive
            disk = psutil.disk_usage('C:\\' if sys.platform == 'win32' else '/')
            free_gb = disk.free / (1024**3)
            
            warnings = []
            if memory_gb < 4:
                warnings.append(f"Low RAM: {memory_gb:.1f}GB (recommend 8GB+)")
            if free_gb < 10:
                warnings.append(f"Low disk space: {free_gb:.1f}GB free (recommend 20GB+)")
                
            if warnings:
                return DiagnosticResult(
                    name="System Resources",
                    status=DiagnosticStatus.WARNING,
                    message="System resources may be limited",
                    details="; ".join(warnings),
                    fix_suggestion="Consider upgrading hardware or freeing up resources"
                )
            else:
                return DiagnosticResult(
                    name="System Resources",
                    status=DiagnosticStatus.PASS,
                    message=f"Adequate resources: {memory_gb:.1f}GB RAM, {free_gb:.1f}GB free disk"
                )
                
        except ImportError:
            return DiagnosticResult(
                name="System Resources",
                status=DiagnosticStatus.UNKNOWN,
                message="Cannot check system resources (psutil not available)",
                fix_suggestion="Install psutil package for resource monitoring"
            )
        except Exception as e:
            return DiagnosticResult(
                name="System Resources",
                status=DiagnosticStatus.UNKNOWN,
                message=f"Error checking resources: {e}"
            )
            
    def _check_network(self) -> DiagnosticResult:
        """Check network connectivity"""
        try:
            result = subprocess.run(["ping", "-n" if sys.platform == "win32" else "-c", "1", "8.8.8.8"], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                return DiagnosticResult(
                    name="Network Connectivity",
                    status=DiagnosticStatus.PASS,
                    message="Network connectivity working"
                )
            else:
                return DiagnosticResult(
                    name="Network Connectivity",
                    status=DiagnosticStatus.WARNING,
                    message="Network connectivity issues detected",
                    fix_suggestion="Check internet connection and firewall settings"
                )
        except subprocess.TimeoutExpired:
            return DiagnosticResult(
                name="Network Connectivity",
                status=DiagnosticStatus.WARNING,
                message="Network check timed out",
                fix_suggestion="Check internet connection"
            )
        except Exception as e:
            return DiagnosticResult(
                name="Network Connectivity",
                status=DiagnosticStatus.UNKNOWN,
                message=f"Could not test network: {e}"
            )


class DiagnosticsDialog(QDialog):
    """1-Click diagnostics dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Diagnostics")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
        self.worker = None
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("System Diagnostics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Current check label
        self.current_check_label = QLabel("")
        self.current_check_label.setVisible(False)
        layout.addWidget(self.current_check_label)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("Run Diagnostics")
        self.run_button.clicked.connect(self.run_diagnostics)
        button_layout.addWidget(self.run_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def run_diagnostics(self):
        """Start diagnostic checks"""
        self.run_button.setEnabled(False)
        self.progress.setVisible(True)
        self.current_check_label.setVisible(True)
        self.results_text.clear()
        
        self.worker = DiagnosticsWorker()
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.check_completed.connect(self.on_check_completed)
        self.worker.all_completed.connect(self.on_all_completed)
        self.worker.start()
        
    def on_progress_updated(self, progress: int, current_check: str):
        """Handle progress update"""
        self.progress.setValue(progress)
        self.current_check_label.setText(f"Checking: {current_check}")
        
    def on_check_completed(self, result: DiagnosticResult):
        """Handle individual check completion"""
        status_colors = {
            DiagnosticStatus.PASS: "#4CAF50",
            DiagnosticStatus.WARNING: "#FF9800", 
            DiagnosticStatus.FAIL: "#F44336",
            DiagnosticStatus.UNKNOWN: "#9E9E9E"
        }
        
        status_symbols = {
            DiagnosticStatus.PASS: "✅",
            DiagnosticStatus.WARNING: "⚠️",
            DiagnosticStatus.FAIL: "❌",
            DiagnosticStatus.UNKNOWN: "❓"
        }
        
        color = status_colors[result.status]
        symbol = status_symbols[result.status]
        
        html = f"""
        <div style="margin: 10px 0; padding: 10px; border-left: 4px solid {color};">
            <h3 style="margin: 0; color: {color};">{symbol} {result.name}</h3>
            <p style="margin: 5px 0;"><strong>Status:</strong> {result.message}</p>
        """
        
        if result.details:
            html += f"<p style='margin: 5px 0;'><strong>Details:</strong> {result.details}</p>"
            
        if result.fix_suggestion:
            html += f"<p style='margin: 5px 0; color: #2196F3;'><strong>Fix:</strong> {result.fix_suggestion}</p>"
            
        html += "</div>"
        
        self.results_text.append(html)
        
    def on_all_completed(self, results: List[DiagnosticResult]):
        """Handle all diagnostics completion"""
        self.progress.setVisible(False)
        self.current_check_label.setVisible(False)
        self.run_button.setEnabled(True)
        
        # Summary
        pass_count = sum(1 for r in results if r.status == DiagnosticStatus.PASS)
        warning_count = sum(1 for r in results if r.status == DiagnosticStatus.WARNING)
        fail_count = sum(1 for r in results if r.status == DiagnosticStatus.FAIL)
        
        summary_html = f"""
        <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-radius: 5px;">
            <h2 style="margin: 0 0 10px 0;">Summary</h2>
            <p style="margin: 0;">
                ✅ Passed: {pass_count} | 
                ⚠️ Warnings: {warning_count} | 
                ❌ Failed: {fail_count}
            </p>
        </div>
        """
        
        self.results_text.append(summary_html)