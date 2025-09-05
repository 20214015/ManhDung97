# backend.py - Xử lý tương tác với công cụ dòng lệnh MuMuManager.exe

import os
import json
import shlex
from typing import List, Tuple, Any, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, QObject

# Import CommandBus for QProcess-based execution
from cli.command_bus import get_command_bus, CommandPriority, CommandResult

# Constants để tránh magic numbers
DEFAULT_TIMEOUT = 10  # Increased from 5 to 10 seconds to give more time
MAX_INSTANCES_CREATE = 50
MAX_INSTANCES_CLONE = 20
MAX_NAME_LENGTH = 100

def find_mumu_instance_path(instance_index: int) -> str:
    """Try to find the actual path of a MuMu instance by checking common locations."""
    # Common MuMu installation paths (updated with user's actual path)
    possible_base_paths = [
        r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\vms",  # User's actual path
        r"C:\Program Files\Netease\MuMuPlayer-12.0\vms",
        r"C:\Program Files (x86)\Netease\MuMuPlayerGlobal-12.0\vms",
        r"C:\Program Files (x86)\Netease\MuMuPlayer-12.0\vms", 
        r"C:\Users\Public\Documents\MuMu\vms",
        r"C:\ProgramData\MuMu\vms",
        r"D:\Program Files\Netease\MuMuPlayerGlobal-12.0\vms",
        r"D:\Program Files\Netease\MuMuPlayer-12.0\vms",
        r"D:\MuMu\vms"
    ]
    
    # Try different naming patterns
    possible_names = [
        f"MuMuPlayerGlobal-12.0-{instance_index}",
        f"MuMuPlayer-12.0-{instance_index}",
        f"MuMu{instance_index}",
        f"vm_{instance_index}",
        f"instance_{instance_index}",
        str(instance_index)
    ]
    
    for base_path in possible_base_paths:
        if os.path.exists(base_path):
            for name in possible_names:
                full_path = os.path.join(base_path, name)
                if os.path.exists(full_path):
                    return full_path
    
    return ""

def calculate_folder_size(folder_path: str) -> int:
    """Calculate the total size of a folder in bytes."""
    if not folder_path or not os.path.exists(folder_path):
        return 0
    
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    # Skip files that can't be accessed
                    continue
    except (OSError, IOError):
        # Return 0 if folder can't be accessed
        return 0
    return total_size

def format_size(size_bytes: int) -> str:
    """Format size in bytes to human readable string."""
    if size_bytes == 0:
        return "0MB"
    
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            if unit == 'B':
                return f"{int(size)}{unit}"
            else:
                return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}PB"

class MumuManager:
    """Lớp bao (wrapper) mạnh mẽ để tương tác với công cụ dòng lệnh MuMuManager.exe."""

    def __init__(self, executable_path: str):
        # Auto-detect MuMu Manager path if not provided
        if not executable_path or executable_path.isspace():
            possible_paths = [
                r"C:\Program Files\Netease\MuMuPlayer\nx_main\MuMuManager.exe",  # From error message
                r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe",
                r"C:\Program Files\Netease\MuMuPlayer-12.0\shell\MuMuManager.exe",
                r"C:\Program Files (x86)\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe",
                r"C:\Program Files (x86)\Netease\MuMuPlayer-12.0\shell\MuMuManager.exe",
                r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\nx_main\MuMuManager.exe",
                r"C:\Program Files\Netease\MuMuPlayer-12.0\nx_main\MuMuManager.exe"
            ]
            
            self.executable_path = ""
            for path in possible_paths:
                if os.path.isfile(path):
                    self.executable_path = path
                    print(f"✅ Auto-detected MuMuManager.exe at: {path}")
                    break
            
            if not self.executable_path:
                print("⚠️ Could not auto-detect MuMuManager.exe path")
        else:
            self.executable_path = executable_path
        
        if not os.path.exists(self.executable_path):
            # Only show warning for Windows platform where MuMu is expected
            import sys
            if sys.platform == "win32":
                print(f"Cảnh báo: Không tìm thấy MuMuManager.exe tại {self.executable_path}")
            # On Linux/other platforms, this is expected behavior
            elif self.executable_path and not self.executable_path.isspace():
                print(f"Info: MuMuManager path not available on {sys.platform} platform")

        # Initialize CommandBus for QProcess-based execution
        self.command_bus = get_command_bus()
        self._pending_commands = {}  # Track pending async commands
        
        # Cache system for instance data
        self._instance_cache: Dict[int, Dict[str, Any]] = {}
        self._last_refresh_time = 0
        self._refresh_interval = 3000  # 3 seconds default
        self._auto_refresh_timer = QTimer()
        self._auto_refresh_timer.timeout.connect(self._auto_refresh_instances)
        self._cache_callbacks: List[Callable[[], None]] = []

    def is_valid(self) -> bool:
        """Kiểm tra xem đường dẫn thực thi đã cấu hình có hợp lệ không."""
        return os.path.isfile(self.executable_path)
    
    def get_version_info(self) -> Tuple[bool, str]:
        """Lấy thông tin version của MuMuManager."""
        return self._run_command_sync(['--version'], CommandPriority.LOW)
    
    def _validate_indices(self, indices: List[int]) -> Tuple[bool, str]:
        """Validate danh sách indices."""
        if not indices:
            return False, "Không có instance nào được chọn"
        if any(idx < 0 for idx in indices):
            return False, "Index không thể âm"
        if len(indices) > 100:  # Giới hạn an toàn
            return False, "Quá nhiều instances được chọn (tối đa 100)"
        return True, ""

    def _run_command_sync(self, args: List[str], priority: CommandPriority = CommandPriority.NORMAL, timeout: int = DEFAULT_TIMEOUT) -> Tuple[bool, str]:
        """Thực thi một lệnh đồng bộ và nhận output. Sử dụng CommandBus với QProcess."""
        print(f"🔍 DEBUG: _run_command_sync called with args: {args}")
        if not self.is_valid():
            print(f"🔍 DEBUG: is_valid() returned False")
            return False, f"Lỗi: Không tìm thấy '{os.path.basename(self.executable_path)}'."

        # Import QApplication for event loop
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QEventLoop

        app = QApplication.instance()
        if not app:
            return False, "QApplication not available for synchronous command execution"

        loop = QEventLoop()
        result = None

        def on_command_finished(cmd_result: CommandResult):
            nonlocal result
            result = cmd_result
            loop.quit()

        # Execute command asynchronously
        command_id = self.command_bus.execute_command(
            self.executable_path,
            args,
            priority,
            timeout=timeout,
            callback=on_command_finished
        )

        # Wait for completion using event loop
        loop.exec()

        if result is None:
            return False, f"Lỗi: Lệnh bị quá thời gian chờ ({timeout}s). Args={' '.join(args)}"

        print(f"🔍 DEBUG: CommandBus completed, returncode={result.return_code}")

        # Kiểm tra return code và xây dựng error message có cấu trúc
        if result.return_code != 0:
            error_parts = [f"Lệnh thất bại (return code: {result.return_code})"]
            if result.return_code == 4294967275:  # -21 in two's complement
                error_parts.append("MuMu executable returned error -21 (possibly needs different parameters or environment)")
            if result.error:
                error_parts.append(f"Error: {result.error.strip()}")
            if result.output:
                error_parts.append(f"Output: {result.output.strip()}")
            return False, "\n".join(error_parts)

        # Hợp nhất output và error một cách thông minh
        output_parts = []
        if result.output:
            output_parts.append(result.output.strip())
        if result.error:
            output_parts.append(result.error.strip())

        return True, "\n".join(output_parts) if output_parts else ""

    def _run_command(self, args: List[str]) -> Tuple[bool, str]:
        """Thực thi một lệnh và nhận output. Backward compatibility method."""
        return self._run_command_sync(args)

    def get_all_info_cached(self, use_cache: bool = True, max_age_seconds: int = 30) -> Tuple[bool, Any]:
        """Lấy thông tin tất cả instances với cache support."""
        if use_cache and self.is_cache_valid(max_age_seconds):
            # Trả về data từ cache
            cached_data = {}
            for vm_index, instance_data in self._instance_cache.items():
                # Convert back to string keys như format gốc
                cached_data[str(vm_index)] = instance_data.copy()
            return True, cached_data
        else:
            # Refresh cache và trả về data mới
            success, message = self.refresh_cache()
            if success:
                # Trả về data từ cache sau khi refresh
                cached_data = {}
                for vm_index, instance_data in self._instance_cache.items():
                    cached_data[str(vm_index)] = instance_data.copy()
                return True, cached_data
            else:
                # Fallback to direct call nếu cache refresh thất bại
                return self.get_all_info_direct()

    def get_all_info_direct(self) -> Tuple[bool, Any]:
        """Lấy thông tin cho tất cả máy ảo, xử lý nhiều định dạng JSON một cách thông minh."""
        print(f"🔍 DEBUG: get_all_info called, executable_path='{self.executable_path}'")
        print(f"🔍 DEBUG: is_valid() = {self.is_valid()}")

        # MuMu Manager requires --vmindex parameter, skip simple command and use verbose directly
        print("🔍 DEBUG: Using verbose command with --vmindex all...")
        success, output = self._run_command_sync(['info', '-v', 'all'], CommandPriority.LOW)
        print(f"🔍 DEBUG: Verbose command returned: success={success}")

        if not success:
            print(f"🔍 DEBUG: Verbose command failed: {output}")
            return False, output

        # Early return cho output rỗng
        if not output.strip():
            return True, {}

        try:
            return self._parse_json_output(output)
        except json.JSONDecodeError:
            error_details = f"Lỗi phân tích JSON. Dữ liệu nhận được không hợp lệ.\n--- Dữ liệu thô ---\n{output}\n--- Kết thúc ---"
            return False, error_details

    def get_all_info(self) -> Tuple[bool, Any]:
        """Alias cho get_all_info_direct để backward compatibility."""
        return self.get_all_info_direct()
        """Lấy thông tin một instance với cache support."""
        if use_cache and self.is_cache_valid(max_age_seconds):
            cached_instance = self.get_cached_instance(vm_index)
            if cached_instance:
                return True, cached_instance.copy()

        # Fallback to direct call
        return self.get_single_info(vm_index)
        """Lấy thông tin cho tất cả máy ảo, xử lý nhiều định dạng JSON một cách thông minh."""
        print(f"🔍 DEBUG: get_all_info called, executable_path='{self.executable_path}'")
        print(f"🔍 DEBUG: is_valid() = {self.is_valid()}")

        # MuMu Manager requires --vmindex parameter, skip simple command and use verbose directly
        print("🔍 DEBUG: Using verbose command with --vmindex all...")
        success, output = self._run_command_sync(['info', '-v', 'all'], CommandPriority.LOW)
        print(f"🔍 DEBUG: Verbose command returned: success={success}")

        if not success:
            print(f"🔍 DEBUG: Verbose command failed: {output}")
            return False, output

        # Early return cho output rỗng
        if not output.strip():
            return True, {}

        try:
            return self._parse_json_output(output)
        except json.JSONDecodeError:
            error_details = f"Lỗi phân tích JSON. Dữ liệu nhận được không hợp lệ.\n--- Dữ liệu thô ---\n{output}\n--- Kết thúc ---"
            return False, error_details
    
    def _parse_json_output(self, output: str) -> Tuple[bool, Dict[str, Any]]:
        """Helper method để parse JSON output với nhiều format khác nhau."""
        # Thử parse multi-line JSON objects trước
        json_lines = [line.strip() for line in output.strip().split('\n') 
                     if line.strip() and line.startswith('{')]
        
        if len(json_lines) > 1:
            # Multiple JSON objects, một object per line
            json_objects = [json.loads(line) for line in json_lines]
            if all('index' in obj for obj in json_objects):
                parsed_data = {str(obj['index']): obj for obj in json_objects}
                # Add real disk usage calculation
                self._calculate_disk_usage_for_all(parsed_data)
                return True, parsed_data

        # Thử parse như single JSON object
        data = json.loads(output)
        
        # Xử lý các format khác nhau
        if isinstance(data, list):
            # Array of objects
            if all(isinstance(obj, dict) and 'index' in obj for obj in data):
                parsed_data = {str(obj['index']): obj for obj in data}
                self._calculate_disk_usage_for_all(parsed_data)
                return True, parsed_data
            # Array without index, sử dụng position
            parsed_data = {str(i): obj for i, obj in enumerate(data)}
            self._calculate_disk_usage_for_all(parsed_data)
            return True, parsed_data
        
        if isinstance(data, dict):
            # Dictionary with indexed objects
            if all(isinstance(v, dict) and 'index' in v for v in data.values()):
                self._calculate_disk_usage_for_all(data)
                return True, data
            # Single object with index
            if 'index' in data:
                parsed_data = {str(data['index']): data}
                self._calculate_disk_usage_for_all(parsed_data)
                return True, parsed_data
            # Dictionary format khác
            self._calculate_disk_usage_for_all(data)
            return True, data
                
        return False, f"Định dạng dữ liệu không được hỗ trợ:\n{output}"

    def _calculate_disk_usage_for_all(self, instances_data: Dict[str, Any]) -> None:
        """Calculate real disk usage for all instances."""
        for instance_key, instance_data in instances_data.items():
            if isinstance(instance_data, dict):
                self._calculate_disk_usage_for_instance(instance_data)
    
    def _calculate_disk_usage_for_instance(self, instance_data: Dict[str, Any]) -> None:
        """Calculate real disk usage for a single instance."""
        try:
            instance_id = instance_data.get('index', 'unknown')
            
            # First, check if MuMuManager already provided disk_size_bytes
            disk_bytes = instance_data.get('disk_size_bytes', 0)
            if disk_bytes and disk_bytes > 0:
                # Use the data from MuMuManager directly
                formatted_size = format_size(disk_bytes)
                instance_data['disk_usage'] = formatted_size
                instance_data['disk_size_bytes'] = disk_bytes
                
                # Log for debugging (first few instances only)
                if int(str(instance_id)) <= 3:
                    print(f"💾 Instance {instance_id}: Using MuMu data -> {formatted_size} ({disk_bytes} bytes)")
                return
            
            # If no disk_size_bytes from MuMu, try to calculate manually
            path = instance_data.get('path', '')
            
            # If no path provided, try to find it automatically
            if not path or path == '':
                path = find_mumu_instance_path(int(str(instance_id)))
                if path:
                    # Update the instance data with found path
                    instance_data['path'] = path
            
            # Debug: Log path info for first few instances
            if int(str(instance_id)) <= 3:
                print(f"🔍 Instance {instance_id}: path='{path}', exists={os.path.exists(path) if path else False}")
            
            if path and os.path.exists(path):
                # Calculate the actual disk usage manually
                disk_bytes = calculate_folder_size(path)
                formatted_size = format_size(disk_bytes)
                
                # Update the instance data with calculated disk usage
                instance_data['disk_usage'] = formatted_size
                instance_data['disk_size_bytes'] = disk_bytes
                
                # Log for debugging (first few instances only)
                if int(str(instance_id)) <= 3:
                    print(f"💾 Instance {instance_id}: Calculated {path} -> {formatted_size} ({disk_bytes} bytes)")
            else:
                # No valid path and no MuMu data, keep as 0MB
                if int(str(instance_id)) <= 3:
                    print(f"❌ Instance {instance_id}: No data available - keeping 0MB")
                instance_data['disk_usage'] = "0MB"
                instance_data['disk_size_bytes'] = 0
        except Exception as e:
            # If anything fails, keep original values
            instance_data['disk_usage'] = instance_data.get('disk_usage', '0MB')
            instance_data['disk_size_bytes'] = 0
            print(f"⚠️ Error calculating disk usage for instance {instance_data.get('index', 'unknown')}: {e}")

    def get_single_info(self, index: int) -> Tuple[bool, Any]:
        """Lấy thông tin cho một máy ảo duy nhất với error handling tốt hơn."""
        success, output = self._run_command_sync(['info', '-v', str(index)], CommandPriority.LOW)
        if not success:
            return False, f"Command failed: {output}"
        
        if not output.strip():
            return False, f"Không có dữ liệu cho máy ảo index {index}"
            
        try:
            data = json.loads(output)
            
            # Validate that data is not empty and contains expected structure
            if data is None:
                return False, f"Dữ liệu là None cho máy ảo {index}"
                
            if not isinstance(data, dict):
                return False, f"Dữ liệu không phải dict cho máy ảo {index}: {type(data)} = {data}"
            
            if len(data) == 0:
                return False, f"Dữ liệu dict rỗng cho máy ảo {index}"
            
            # Check for essential fields that should exist in VM info
            if 'index' not in data and 'name' not in data:
                return False, f"Dữ liệu thiếu thông tin cơ bản cho máy ảo {index}: {list(data.keys())}"
            
            # Ensure index field exists and matches
            if 'index' not in data:
                data['index'] = index
            
            # Calculate real disk usage for this instance
            self._calculate_disk_usage_for_instance(data)
                
            return True, data
        except json.JSONDecodeError as e:
            return False, f"Lỗi phân tích JSON cho máy ảo {index}: {e}\nDữ liệu: {output}"

    def control_instance(self, indices: List[int], action: str) -> Tuple[bool, str]:
        """Điều khiển instances với validation và priority-based execution."""
        if not indices:
            return False, "Không có instance nào được chọn"
        if not action:
            return False, "Action không được để trống"

        # Determine priority based on action
        if action in ['launch', 'start']:
            priority = CommandPriority.HIGH  # Start operations have high priority
        elif action in ['shutdown', 'stop', 'kill']:
            priority = CommandPriority.CRITICAL  # Stop operations have highest priority
        else:
            priority = CommandPriority.NORMAL

        return self._run_command_sync(['control', '--vmindex', ",".join(map(str, indices)), action], priority)

    def create_instance(self, count: int) -> Tuple[bool, str]:
        """Tạo instances mới với validation."""
        if count <= 0:
            return False, "Số lượng instance phải lớn hơn 0"
        if count > MAX_INSTANCES_CREATE:  # Sử dụng constant
            return False, f"Không thể tạo quá {MAX_INSTANCES_CREATE} instances cùng lúc"
        return self._run_command_sync(['create', '-n', str(count)], CommandPriority.NORMAL)

    def clone_instance(self, source_index: int, count: int) -> Tuple[bool, str]:
        """Clone instance với validation."""
        if count <= 0:
            return False, "Số lượng clone phải lớn hơn 0"
        if count > MAX_INSTANCES_CLONE:  # Sử dụng constant
            return False, f"Không thể clone quá {MAX_INSTANCES_CLONE} instances cùng lúc"
        return self._run_command_sync(['clone', '-v', str(source_index), '-n', str(count)], CommandPriority.NORMAL)

    def delete_instance(self, indices: List[int]) -> Tuple[bool, str]:
        """Xóa instances với validation."""
        if not indices:
            return False, "Không có instance nào được chọn để xóa"
        return self._run_command_sync(['delete', '-v', ",".join(map(str, indices))], CommandPriority.HIGH)

    def rename_instance(self, index: int, new_name: str) -> Tuple[bool, str]:
        """Đổi tên instance với validation."""
        if not new_name or not new_name.strip():
            return False, "Tên mới không được để trống"
        if len(new_name.strip()) > MAX_NAME_LENGTH:  # Sử dụng constant
            return False, f"Tên instance quá dài (tối đa {MAX_NAME_LENGTH} ký tự)"
        return self._run_command_sync(['rename', '-v', str(index), '-n', new_name.strip()], CommandPriority.NORMAL)

    def run_adb_command(self, indices: List[int], command_str: str) -> Tuple[bool, str]:
        """Chạy ADB command với validation và security checks."""
        if not indices:
            return False, "Không có instance nào được chọn"
        if not command_str or not command_str.strip():
            return False, "Lệnh ADB không được để trống"
        
        # Basic security validation
        dangerous_commands = ['rm -rf', 'format', 'factory', 'wipe', 'delete', 'dd if=']
        command_lower = command_str.lower()
        if any(dangerous in command_lower for dangerous in dangerous_commands):
            return False, f"Lệnh có thể nguy hiểm và không được phép: {command_str}"
        
        try:
            cmd_parts = shlex.split(command_str.strip())
            if not cmd_parts:
                return False, "Lệnh ADB không hợp lệ sau khi parse"
            return self._run_command_sync(['adb', '-v', ",".join(map(str, indices)), '-c'] + cmd_parts, CommandPriority.HIGH)
        except ValueError as e:
            return False, f"Lỗi parse command: {e}"

    def set_simulation_value(self, indices: List[int], key: str, value: str) -> Tuple[bool, str]:
        """Set simulation value với validation."""
        if not indices:
            return False, "Không có instance nào được chọn"
        if not key or not key.strip():
            return False, "Key không được để trống"
        return self._run_command_sync(['simulation', '-v', ",".join(map(str, indices)), '-sk', key.strip(), '-sv', value], CommandPriority.NORMAL)

    def get_settings_info(self, index: int) -> Tuple[bool, str]:
        """Lấy thông tin settings với error handling."""
        return self._run_command_sync(['setting', '-v', str(index), '-i'], CommandPriority.LOW)

    def get_writable_settings_values(self, index: int) -> Tuple[bool, str]:
        """Lấy giá trị settings có thể write với error handling."""
        return self._run_command_sync(['setting', '-v', str(index), '-aw'], CommandPriority.LOW)

    def set_settings(self, indices: List[int], settings: Dict[str, str]) -> Tuple[bool, str]:
        """Set multiple settings với validation và optimization."""
        if not indices:
            return False, "Không có instance nào được chọn"
        if not settings:
            return True, "Không có cài đặt nào được thay đổi."
        
        # Validate settings
        invalid_settings = []
        for key, value in settings.items():
            if not key or not key.strip():
                invalid_settings.append(f"Key rỗng với value: {value}")
        
        if invalid_settings:
            return False, f"Settings không hợp lệ: {'; '.join(invalid_settings)}"
        
        # Build command efficiently
        args = ['setting', '-v', ",".join(map(str, indices))]
        for key, value in settings.items():
            args.extend(['-k', key.strip(), '-val', str(value)])
            
        return self._run_command_sync(args, CommandPriority.NORMAL)

    # ===== CACHE SYSTEM METHODS =====

    def start_auto_refresh(self, interval_ms: int = 3000) -> None:
        """Bắt đầu auto refresh với interval chỉ định (ms)."""
        self._refresh_interval = interval_ms
        if not self._auto_refresh_timer.isActive():
            self._auto_refresh_timer.start(self._refresh_interval)
            print(f"🔄 Auto refresh started with {interval_ms}ms interval")

    def stop_auto_refresh(self) -> None:
        """Dừng auto refresh."""
        if self._auto_refresh_timer.isActive():
            self._auto_refresh_timer.stop()
            print("⏹️ Auto refresh stopped")

    def set_refresh_interval(self, interval_ms: int) -> None:
        """Thay đổi interval của auto refresh."""
        self._refresh_interval = interval_ms
        if self._auto_refresh_timer.isActive():
            self._auto_refresh_timer.setInterval(interval_ms)
            print(f"🔄 Refresh interval updated to {interval_ms}ms")

    def add_cache_callback(self, callback: Callable[[], None]) -> None:
        """Thêm callback được gọi khi cache được cập nhật."""
        if callback not in self._cache_callbacks:
            self._cache_callbacks.append(callback)

    def remove_cache_callback(self, callback: Callable[[], None]) -> None:
        """Xóa callback."""
        if callback in self._cache_callbacks:
            self._cache_callbacks.remove(callback)

    def _notify_cache_callbacks(self) -> None:
        """Thông báo cho tất cả callbacks rằng cache đã được cập nhật."""
        for callback in self._cache_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"⚠️ Cache callback error: {e}")

    def _auto_refresh_instances(self) -> None:
        """Auto refresh instances data."""
        try:
            self.refresh_cache()
        except Exception as e:
            print(f"⚠️ Auto refresh error: {e}")

    def refresh_cache(self, force: bool = False) -> Tuple[bool, str]:
        """Refresh cache với so sánh thông minh để chỉ emit changes cần thiết."""
        try:
            # Lấy dữ liệu mới
            success, new_data = self.get_all_info()
            if not success:
                return False, f"Failed to get instance data: {new_data}"

            # Chuẩn hóa new_data thành dict theo vmIndex
            if isinstance(new_data, dict):
                new_instances = new_data
            else:
                return False, "Invalid data format from get_all_info"

            # Lấy danh sách vmIndex cũ và mới
            old_indices = set(self._instance_cache.keys())
            new_indices = set()

            # Xử lý từng instance mới
            changes = {
                'added': [],
                'removed': [],
                'modified': []
            }

            for vm_index_str, instance_data in new_instances.items():
                try:
                    vm_index = int(vm_index_str)
                    new_indices.add(vm_index)

                    # Chuẩn hóa instance data
                    normalized_data = self._normalize_instance_data(instance_data)

                    # So sánh với cache cũ
                    if vm_index not in self._instance_cache:
                        # Instance mới
                        changes['added'].append(vm_index)
                        self._instance_cache[vm_index] = normalized_data
                    else:
                        # So sánh để tìm thay đổi
                        old_data = self._instance_cache[vm_index]
                        if self._has_instance_changed(old_data, normalized_data):
                            changes['modified'].append(vm_index)
                            self._instance_cache[vm_index] = normalized_data

                except (ValueError, KeyError) as e:
                    print(f"⚠️ Error processing instance {vm_index_str}: {e}")
                    continue

            # Tìm instances bị xóa
            removed_indices = old_indices - new_indices
            for vm_index in removed_indices:
                changes['removed'].append(vm_index)
                del self._instance_cache[vm_index]

            # Cập nhật timestamp
            from time import time
            self._last_refresh_time = time()

            # Thông báo changes nếu có
            if any(changes.values()):
                self._emit_cache_changes(changes)

            # Thông báo callbacks
            self._notify_cache_callbacks()

            return True, f"Cache refreshed: +{len(changes['added'])} -{len(changes['removed'])} ~{len(changes['modified'])}"

        except Exception as e:
            return False, f"Cache refresh error: {e}"

    def _normalize_instance_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Chuẩn hóa instance data để so sánh."""
        normalized = {}

        # Các trường quan trọng để so sánh
        important_fields = [
            'index', 'name', 'status', 'cpu', 'memory', 'disk_usage',
            'disk_size_bytes', 'path', 'version', 'running'
        ]

        for field in important_fields:
            if field in data:
                normalized[field] = data[field]
            else:
                normalized[field] = None

        # Thêm timestamp để track changes
        from time import time
        normalized['_last_updated'] = time()

        return normalized

    def _has_instance_changed(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """Kiểm tra xem instance có thay đổi không."""
        # Các trường cần so sánh
        compare_fields = [
            'name', 'status', 'cpu', 'memory', 'disk_usage', 'running'
        ]

        for field in compare_fields:
            old_value = old_data.get(field)
            new_value = new_data.get(field)

            # Xử lý None values
            if old_value is None and new_value is None:
                continue
            if old_value is None or new_value is None:
                return True

            # So sánh values
            if str(old_value).strip() != str(new_value).strip():
                return True

        return False

    def _emit_cache_changes(self, changes: Dict[str, List[int]]) -> None:
        """Emit cache changes cho UI update."""
        print(f"🔄 Cache changes: +{len(changes['added'])} -{len(changes['removed'])} ~{len(changes['modified'])}")

        # Emit cho từng loại change
        for change_type, indices in changes.items():
            if indices:
                print(f"  {change_type.upper()}: {indices}")

    def get_cached_instances(self) -> Dict[int, Dict[str, Any]]:
        """Lấy toàn bộ cache hiện tại."""
        return self._instance_cache.copy()

    def get_cached_instance(self, vm_index: int) -> Optional[Dict[str, Any]]:
        """Lấy instance từ cache theo vmIndex."""
        return self._instance_cache.get(vm_index)

    def is_cache_valid(self, max_age_seconds: int = 30) -> bool:
        """Kiểm tra cache có còn hợp lệ không."""
        from time import time
        return (time() - self._last_refresh_time) < max_age_seconds

    def clear_cache(self) -> None:
        """Xóa toàn bộ cache."""
        self._instance_cache.clear()
        self._last_refresh_time = 0
        print("🗑️ Cache cleared")
