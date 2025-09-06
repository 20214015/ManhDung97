import time
import os
import shutil
from typing import Callable, Any, Dict, List

from PyQt6.QtCore import QThread, pyqtSignal

# Khai báo trước (Forward declaration) để tránh lỗi import vòng tròn
class MumuManager:
    pass

class GenericWorker(QThread):
    """
    Một worker đa năng để chạy bất kỳ hàm tác vụ nào trong một luồng riêng,
    tránh làm đơ giao diện chính.
    """
    started = pyqtSignal(str)       # Tín hiệu phát ra khi bắt đầu, mang theo thông điệp
    progress = pyqtSignal(int)      # Tín hiệu cập nhật tiến trình (0-100)
    log = pyqtSignal(str)           # Tín hiệu để ghi log
    task_result = pyqtSignal(dict)  # Tín hiệu mang kết quả của tác vụ (dạng dict)
    finished = pyqtSignal(str)      # Tín hiệu phát ra khi hoàn thành, mang theo thông điệp

    def __init__(self, task_func: Callable, manager: MumuManager, params: Dict[str, Any]):
        super().__init__()
        self.task_func = task_func
        self.manager = manager
        self.params = params
        self._is_running = True
        self._is_paused = False

    def run(self):
        """Phương thức chính của luồng, được gọi khi self.start() được gọi."""
        try:
            result = self.task_func(self, self.manager, self.params)
            if result:
                # Debug logging for result structure
                self.log.emit(f"🔍 Worker result: type={type(result)}, keys={list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                self.task_result.emit(result)
            else:
                self.log.emit(f"⚠️ Worker: task_func returned empty result: {result}")
            self.finished.emit("Tác vụ hoàn thành.")
        except InterruptedError:
            self.log.emit("⏹️ Tác vụ đã bị người dùng dừng.")
            self.finished.emit("Tác vụ đã dừng.")
        except Exception as e:
            self.log.emit(f"❌ Lỗi nghiêm trọng trong worker: {e}")
            self.finished.emit(f"Tác vụ kết thúc với lỗi: {e}")

    def stop(self):
        """Yêu cầu dừng worker."""
        self._is_running = False

    def pause(self):
        """Tạm dừng worker."""
        self._is_paused = True

    def resume(self):
        """Tiếp tục worker."""
        self._is_paused = False

    def check_status(self):
        """Kiểm tra xem worker có nên dừng hoặc tạm dừng không. Cần được gọi bên trong task_func."""
        while self._is_paused:
            if not self._is_running:
                raise InterruptedError("Tác vụ đã bị dừng khi đang tạm dừng.")
            self.msleep(50) # Tối ưu: Giảm từ 100ms xuống 50ms để responsive hơn
        
        if not self._is_running:
            raise InterruptedError("Tác vụ đã bị người dùng dừng.")

class InterruptedError(Exception):
    """Ngoại lệ tùy chỉnh cho việc dừng worker."""
    pass

# --- CÁC HÀM TÁC VỤ (TASK FUNCTIONS) ---

def auto_launch_task(worker: GenericWorker, manager: MumuManager, params: Dict[str, Any]):
    """Tác vụ tự động khởi động các máy ảo theo batch."""
    start_idx, end_idx = params['start'], params['end']
    batch_size, inst_delay, batch_delay = params['batch'], params['inst_delay'], params['batch_delay']
    
    indices = list(range(start_idx, end_idx + 1))
    total = len(indices)
    worker.started.emit(f"---   Bắt đầu tự động hóa: {total} máy ảo từ {start_idx} đến {end_idx} ---")
    
    results = {'success': [], 'failed': []}
    
    for i in range(0, total, batch_size):
        worker.check_status()
        batch = indices[i:i+batch_size]
        worker.log.emit(f"\n--- Đang xử lý Batch: {', '.join(map(str, batch))} ---")
        
        for j, index in enumerate(batch):
            worker.check_status()
            worker.log.emit(f"[{index}] Đang khởi động...")
            ok, msg = manager.control_instance([index], 'launch')
            if ok:
                results['success'].append(index)
                worker.log.emit(f"[{index}] Khởi động thành công.")
            else:
                results['failed'].append(index)
                worker.log.emit(f"[{index}] Lỗi: {msg}")
            
            progress_val = int(((i + j + 1) / total) * 100)
            worker.progress.emit(progress_val)
            
            if j < len(batch) - 1:
                worker.msleep(int(inst_delay*1000))

        if i + batch_size < total:
            worker.log.emit(f"--- Hoàn thành Batch. Tạm nghỉ {batch_delay} giây... ---")
            worker.msleep(int(batch_delay*1000))
            
    return results

def batch_sim_edit_task(worker: GenericWorker, manager: MumuManager, tasks: List[Dict[str, Any]]):
    """Tác vụ sửa IMEI/MAC hàng loạt."""
    total = len(tasks)
    worker.started.emit(f"--- 🔧 Bắt đầu sửa thông tin cho {total} máy ảo ---")
    results = {'success': [], 'failed': []}

    for i, task in enumerate(tasks):
        worker.check_status()
        index = task['index']
        imei = task.get('imei')
        
        if imei:
            worker.log.emit(f"[{index}] Đang đổi IMEI thành {imei}...")
            ok, msg = manager.set_simulation_value([index], 'imei', imei)
            if ok:
                results['success'].append(index)
                worker.log.emit(f"[{index}] Đổi IMEI thành công.")
            else:
                results['failed'].append(index)
                worker.log.emit(f"[{index}] Lỗi đổi IMEI: {msg}")

        worker.progress.emit(int(((i + 1) / total) * 100))
        # Tối ưu: Giảm delay từ 100ms xuống 50ms để nhanh hơn
        worker.msleep(50)
        
    return results

def apply_settings_task(worker: GenericWorker, manager: MumuManager, params: Dict[str, Any]):
    """Tác vụ áp dụng các cài đặt đã thay đổi."""
    indices, settings = params['indices'], params['settings']
    worker.started.emit(f"--- ⚙️ Áp dụng {len(settings)} cài đặt cho {len(indices)} máy ảo ---")
    
    ok, msg = manager.set_settings(indices, settings)
    if not ok:
        worker.log.emit(f"❌ Lỗi khi áp dụng cài đặt: {msg}")
        return {'failed': indices}
    
    worker.log.emit("✅ Áp dụng cài đặt thành công.")
    worker.progress.emit(100)
    return {'success': indices}


def restart_instances_task(worker: GenericWorker, manager: MumuManager, params: Dict[str, Any]):
    """Restart multiple instances without blocking the UI."""
    indices: List[int] = params.get('indices', [])
    worker.started.emit(f"🔄 Restarting instances: {indices}")

    results: Dict[str, Any] = {'indices': indices}

    stop_success, stop_message = manager.control_instance(indices, 'shutdown')
    worker.log.emit(
        f"Stop phase result: success={stop_success}, message='{stop_message}'"
    )
    results['stop_success'] = stop_success
    results['stop_message'] = stop_message

    if stop_success:
        # Delay using thread-safe sleep
        worker.msleep(1000)
        start_success, start_message = manager.control_instance(indices, 'launch')
        worker.log.emit(
            f"Start phase result: success={start_success}, message='{start_message}'"
        )
        results['start_success'] = start_success
        results['start_message'] = start_message

    return results

def find_disk_files_task(worker: GenericWorker, manager: MumuManager, params: dict):
    """
    Tìm kiếm các file như ota.vdi hoặc customer_config.json trong thư mục vms.
    Hỗ trợ loại trừ một thư mục con.
    """
    vms_path = params['vms_path']
    file_type = params['type']
    # Lấy tên thư mục cần loại trừ từ params
    exclude_dir = params.get('exclude_dir')

    worker.started.emit(f"Bắt đầu tìm kiếm file '{file_type}' trong '{vms_path}'...")
    found_files = []
    
    # Kiểm tra thư mục có tồn tại không
    if not os.path.exists(vms_path):
        worker.log.emit(f"❌ Thư mục không tồn tại: {vms_path}")
        return {'files': found_files, 'type': file_type}
    
    if not os.path.isdir(vms_path):
        worker.log.emit(f"❌ Đường dẫn không phải là thư mục: {vms_path}")
        return {'files': found_files, 'type': file_type}
    
    # Liệt kê nội dung thư mục gốc để debug
    try:
        root_contents = os.listdir(vms_path)
        worker.log.emit(f"📁 Nội dung thư mục '{vms_path}': {root_contents}")
    except Exception as e:
        worker.log.emit(f"❌ Lỗi đọc thư mục: {e}")
        return {'files': found_files, 'type': file_type}
    
    total_dirs = sum(1 for _ in os.walk(vms_path))
    count = 0

    # os.walk cho phép sửa đổi danh sách 'dirs' để bỏ qua các thư mục con
    for root, dirs, files in os.walk(vms_path):
        worker.check_status()
        
        # Debug: log thư mục hiện tại
        worker.log.emit(f"📂 Đang quét thư mục: {root}")
        worker.log.emit(f"📋 Files trong thư mục: {list(files)}")
        
        # === LOGIC LOẠI TRỪ THƯ MỤC ===
        # Nếu thư mục cần loại trừ nằm trong danh sách các thư mục con sắp duyệt
        if exclude_dir and exclude_dir in dirs:
            # Xóa nó khỏi danh sách. os.walk sẽ không đi vào thư mục này.
            dirs.remove(exclude_dir)
            worker.log.emit(f"⚠️ Đã bỏ qua thư mục: {os.path.join(root, exclude_dir)}")
        # =================================

        for file in files:
            # Debug: in thông tin file hiện tại
            worker.log.emit(f"🔍 Kiểm tra file: '{file}' so với pattern: '{file_type}'")
            
            if file.lower() == file_type.lower():
                full_path = os.path.join(root, file)
                found_files.append(full_path)
                worker.log.emit(f"✅ Đã tìm thấy: {full_path}")
            
            # Kiểm tra thêm các pattern khác có thể
            if 'ota' in file.lower() and '.vdi' in file.lower():
                full_path = os.path.join(root, file)
                if full_path not in found_files:  # Tránh duplicate
                    found_files.append(full_path)
                    worker.log.emit(f"✅ Tìm thấy file OTA VDI: {full_path}")

        count += 1
        if total_dirs > 0:
            worker.progress.emit(int((count / total_dirs) * 100))

    worker.log.emit(f"Tìm kiếm hoàn tất. Tìm thấy {len(found_files)} file.")
    return {'files': found_files, 'type': file_type}

def delete_disk_files_task(worker: GenericWorker, manager: MumuManager, params: Dict[str, Any]):
    """Tác vụ xóa các file ota.vdi."""
    files_to_delete = params['files_to_delete']
    total = len(files_to_delete)
    worker.started.emit(f"--- 🗑️ Bắt đầu xóa {total} file ota.vdi ---")
    results = {'success': [], 'failed': []}
    
    for i, file_path in enumerate(files_to_delete):
        worker.check_status()
        try:
            os.remove(file_path)
            worker.log.emit(f"✅ Đã xóa: {file_path}")
            results['success'].append(file_path)
        except Exception as e:
            worker.log.emit(f"❌ Lỗi khi xóa {file_path}: {e}")
            results['failed'].append(file_path)
        worker.progress.emit(int(((i + 1) / total) * 100))
        
    return results

# --- TÁC VỤ MỚI CHO TAB THAY CONFIG ---

def find_config_files_task(worker: GenericWorker, manager: MumuManager, params: Dict[str, Any]):
    """Tác vụ tìm kiếm các file customer_config.json."""
    vms_path = params[r'C:\Program Files\Netease\MuMuPlayer\vms']
    worker.started.emit(f"--- 🔍 Bắt đầu tìm kiếm file customer_config.json trong {vms_path} ---")
    found_files = []
    
    for root, dirs, files in os.walk(vms_path):
        worker.check_status()
        for file in files:
            if file.lower() == 'customer_config.json':
                full_path = os.path.join(root, file)
                found_files.append(full_path)
                worker.log.emit(f"Tìm thấy: {full_path}")
    
    worker.progress.emit(100)
    return {'files': found_files, 'type': 'customer_config.json'}

def replace_config_files_task(worker: GenericWorker, manager: MumuManager, params: Dict[str, Any]):
    """Tác vụ thay thế các file config."""
    source_file = params['source_file']
    target_files = params['target_files']
    total = len(target_files)
    worker.started.emit(f"--- 🔄 Bắt đầu thay thế {total} file config ---")
    results = {'success': [], 'failed': []}
    
    for i, target_file in enumerate(target_files):
        worker.check_status()
        try:
            shutil.copy2(source_file, target_file)
            worker.log.emit(f"✅ Đã thay thế: {target_file}")
            results['success'].append(target_file)
        except Exception as e:
            worker.log.emit(f"❌ Lỗi khi thay thế {target_file}: {e}")
            results['failed'].append(target_file)
        worker.progress.emit(int(((i + 1) / total) * 100))
        
    return results