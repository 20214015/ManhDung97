"""
CPU Monitor Demo
================

Demo để test CPU Monitor feature trong tab Automation
"""

import sys
import threading
import time
import multiprocessing

def cpu_stress_test(duration=30):
    """Tạo tải CPU để test CPU monitor"""
    print(f"🔥 Bắt đầu stress test CPU trong {duration} giây...")
    
    def stress_worker():
        """Worker để tạo tải CPU"""
        end_time = time.time() + duration
        while time.time() < end_time:
            # Tính toán để tạo tải CPU
            for i in range(1000000):
                _ = i ** 2
    
    # Tạo nhiều thread để tăng CPU usage
    threads = []
    num_threads = multiprocessing.cpu_count()
    
    print(f"🚀 Tạo {num_threads} threads để stress CPU...")
    
    for i in range(num_threads):
        thread = threading.Thread(target=stress_worker)
        thread.start()
        threads.append(thread)
    
    # Đợi các threads hoàn thành
    for thread in threads:
        thread.join()
    
    print("✅ Stress test hoàn thành!")

if __name__ == "__main__":
    print("=" * 60)
    print("🖥️ CPU Monitor Demo - MuMu Manager Pro")
    print("=" * 60)
    print()
    print("Hướng dẫn test CPU Monitor:")
    print("1. Mở ứng dụng MuMu Manager Pro")
    print("2. Vào tab 'Automation' (🤖)")
    print("3. Tìm nút '🖥️ CPU Monitor' bên trên đường dẫn APK")
    print("4. Click nút để bật CPU Monitor")
    print("5. Chạy script này để tạo tải CPU cao")
    print("6. Quan sát CPU Monitor và log khi CPU > 70%")
    print()
    
    choice = input("Bạn có muốn chạy stress test không? (y/n): ")
    
    if choice.lower() == 'y':
        duration = int(input("Nhập số giây để stress test (mặc định 30): ") or "30")
        cpu_stress_test(duration)
    else:
        print("💡 Bạn có thể chạy các ứng dụng khác để tăng CPU usage và test CPU Monitor")
    
    print("\n🎯 Kết quả mong đợi:")
    print("- CPU Monitor hiển thị % CPU real-time")
    print("- Khi CPU > 70%: màu đỏ và tự động dừng instances")
    print("- Log ghi lại hành động dừng instances")
    print("- Automation cũng bị dừng nếu đang chạy")
