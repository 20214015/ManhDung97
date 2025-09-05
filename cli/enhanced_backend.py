"""
Enhanced Backend - QProcess-based MuMu Manager
==============================================

Non-blocking backend using QProcess and CommandBus for better UI responsiveness.
"""

import os
import json
from typing import List, Tuple, Any, Dict, Optional, Callable
from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal

from cli.command_bus import get_command_bus, CommandPriority, CommandResult
from backend import find_mumu_instance_path, calculate_folder_size  # Reuse existing utilities


class EnhancedMumuManager(QObject):
    """QProcess-based MuMu Manager for non-blocking operations"""
    
    # Signals for UI updates
    instance_list_updated = pyqtSignal(dict)  # {success: bool, data: dict/str}
    instance_info_updated = pyqtSignal(int, dict)  # index, {success: bool, data: dict/str}
    operation_completed = pyqtSignal(str, bool, str)  # operation, success, message
    progress_updated = pyqtSignal(str, int)  # operation, progress percentage
    
    def __init__(self, executable_path: str = None):
        super().__init__()
        
        # Use existing path detection logic
        if executable_path:
            self.executable_path = executable_path
        else:
            # Auto-detect MuMu Manager path
            possible_paths = [
                r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe",
                r"C:\Program Files\Netease\MuMuPlayer-12.0\shell\MuMuManager.exe",
                r"C:\Program Files (x86)\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe",
                r"C:\Program Files (x86)\Netease\MuMuPlayer-12.0\shell\MuMuManager.exe"
            ]
            
            self.executable_path = ""
            for path in possible_paths:
                if os.path.isfile(path):
                    self.executable_path = path
                    break
                    
        self.command_bus = get_command_bus()
        
    def is_valid(self) -> bool:
        """Check if executable path is valid"""
        return os.path.isfile(self.executable_path)
        
    def get_instance_list_async(self, callback: Optional[Callable] = None):
        """Get instance list asynchronously"""
        def on_result(result: CommandResult):
            if result.success:
                try:
                    # Parse JSON output
                    data = self._parse_json_output(result.output)
                    success_data = {"success": True, "data": data[1] if data[0] else {}}
                except Exception as e:
                    success_data = {"success": False, "data": f"JSON parse error: {e}"}
            else:
                success_data = {"success": False, "data": result.error}
                
            self.instance_list_updated.emit(success_data)
            if callback:
                callback(success_data)
                
        self.command_bus.execute_command(
            self.executable_path,
            ['info', '-v', 'all'],
            CommandPriority.NORMAL,
            timeout=30,
            callback=on_result
        )
        
    def get_instance_info_async(self, instance_index: int, callback: Optional[Callable] = None):
        """Get specific instance info asynchronously"""
        def on_result(result: CommandResult):
            if result.success:
                try:
                    data = json.loads(result.output) if result.output.strip() else {}
                    success_data = {"success": True, "data": data}
                except Exception as e:
                    success_data = {"success": False, "data": f"JSON parse error: {e}"}
            else:
                success_data = {"success": False, "data": result.error}
                
            self.instance_info_updated.emit(instance_index, success_data)
            if callback:
                callback(instance_index, success_data)
                
        self.command_bus.execute_command(
            self.executable_path,
            ['info', '-v', str(instance_index)],
            CommandPriority.NORMAL,
            timeout=15,
            callback=on_result
        )
        
    def start_instance_async(self, instance_index: int, callback: Optional[Callable] = None):
        """Start instance asynchronously"""
        def on_result(result: CommandResult):
            operation = f"start_instance_{instance_index}"
            self.operation_completed.emit(operation, result.success, 
                                        result.output if result.success else result.error)
            if callback:
                callback(result)
                
        self.command_bus.execute_command(
            self.executable_path,
            ['control', '-v', str(instance_index), 'launch'],
            CommandPriority.HIGH,  # Start operations have high priority
            timeout=60,
            callback=on_result
        )
        
    def stop_instance_async(self, instance_index: int, callback: Optional[Callable] = None):
        """Stop instance asynchronously"""
        def on_result(result: CommandResult):
            operation = f"stop_instance_{instance_index}"
            self.operation_completed.emit(operation, result.success,
                                        result.output if result.success else result.error)
            if callback:
                callback(result)
                
        self.command_bus.execute_command(
            self.executable_path,
            ['control', '-v', str(instance_index), 'shutdown'],
            CommandPriority.CRITICAL,  # Stop operations have highest priority
            timeout=30,
            callback=on_result
        )
        
    def batch_start_instances_async(self, instance_indices: List[int], 
                                  callback: Optional[Callable] = None):
        """Start multiple instances with progress tracking"""
        total = len(instance_indices)
        completed = 0
        results = {}
        
        def on_single_result(index, result):
            nonlocal completed, results
            completed += 1
            results[index] = result.success
            
            # Emit progress
            progress = int((completed / total) * 100)
            self.progress_updated.emit("batch_start", progress)
            
            if completed == total:
                # All done
                success_count = sum(1 for success in results.values() if success)
                operation = f"batch_start_{len(instance_indices)}_instances"
                message = f"Started {success_count}/{total} instances successfully"
                self.operation_completed.emit(operation, success_count > 0, message)
                
                if callback:
                    callback(results)
        
        # Start all instances
        for index in instance_indices:
            self.start_instance_async(index, lambda result, idx=index: on_single_result(idx, result))
            
    def batch_stop_instances_async(self, instance_indices: List[int],
                                 callback: Optional[Callable] = None):
        """Stop multiple instances with progress tracking"""
        total = len(instance_indices)
        completed = 0
        results = {}
        
        def on_single_result(index, result):
            nonlocal completed, results
            completed += 1
            results[index] = result.success
            
            # Emit progress
            progress = int((completed / total) * 100)
            self.progress_updated.emit("batch_stop", progress)
            
            if completed == total:
                # All done
                success_count = sum(1 for success in results.values() if success)
                operation = f"batch_stop_{len(instance_indices)}_instances"
                message = f"Stopped {success_count}/{total} instances successfully"
                self.operation_completed.emit(operation, success_count > 0, message)
                
                if callback:
                    callback(results)
        
        # Stop all instances
        for index in instance_indices:
            self.stop_instance_async(index, lambda result, idx=index: on_single_result(idx, result))
            
    def install_apk_async(self, instance_index: int, apk_path: str, 
                         callback: Optional[Callable] = None):
        """Install APK asynchronously"""
        def on_result(result: CommandResult):
            operation = f"install_apk_{instance_index}"
            self.operation_completed.emit(operation, result.success,
                                        result.output if result.success else result.error)
            if callback:
                callback(result)
                
        self.command_bus.execute_command(
            self.executable_path,
            ['control', '-v', str(instance_index), 'install_apk', apk_path],
            CommandPriority.LOW,  # Install operations have low priority
            timeout=120,  # APK installs can take longer
            callback=on_result
        )
        
    def _parse_json_output(self, output: str) -> Tuple[bool, Dict[str, Any]]:
        """Parse JSON output (reuse existing logic from backend.py)"""
        if not output.strip():
            return True, {}
            
        try:
            # Handle multi-line JSON objects
            json_lines = [line.strip() for line in output.strip().split('\n') 
                         if line.strip() and line.startswith('{')]
            
            if len(json_lines) > 1:
                # Multiple JSON objects
                json_objects = [json.loads(line) for line in json_lines]
                if all('index' in obj for obj in json_objects):
                    parsed_data = {str(obj['index']): obj for obj in json_objects}
                    # Add disk usage calculation
                    self._calculate_disk_usage_for_all(parsed_data)
                    return True, parsed_data
                else:
                    return True, {"raw_objects": json_objects}
            else:
                # Single JSON object or array
                data = json.loads(output.strip())
                if isinstance(data, dict):
                    return True, {"0": data}
                elif isinstance(data, list):
                    return True, {str(i): item for i, item in enumerate(data)}
                else:
                    return True, {"result": data}
                    
        except json.JSONDecodeError as e:
            return False, f"JSON parse error: {e}"
            
    def _calculate_disk_usage_for_all(self, parsed_data: Dict[str, Any]):
        """Calculate disk usage for all instances (reuse from backend.py)"""
        for index_str, info in parsed_data.items():
            if isinstance(info, dict) and 'index' in info:
                try:
                    instance_index = info['index']
                    instance_path = find_mumu_instance_path(instance_index)
                    
                    if instance_path and os.path.exists(instance_path):
                        disk_size_bytes = calculate_folder_size(instance_path)
                        info['disk_size_bytes'] = disk_size_bytes
                        
                        # Human readable format
                        if disk_size_bytes > 0:
                            gb = disk_size_bytes / (1024**3)
                            if gb >= 1:
                                info['disk_usage'] = f"{gb:.2f} GB"
                            else:
                                mb = disk_size_bytes / (1024**2)
                                info['disk_usage'] = f"{mb:.2f} MB"
                        else:
                            info['disk_usage'] = "0MB"
                    else:
                        info['disk_size_bytes'] = 0
                        info['disk_usage'] = "N/A"
                        
                except Exception as e:
                    info['disk_size_bytes'] = 0
                    info['disk_usage'] = f"Error: {e}"


# Global enhanced backend instance
_global_enhanced_backend = None

def get_enhanced_backend() -> EnhancedMumuManager:
    """Get global enhanced backend instance"""
    global _global_enhanced_backend
    if _global_enhanced_backend is None:
        _global_enhanced_backend = EnhancedMumuManager()
    return _global_enhanced_backend