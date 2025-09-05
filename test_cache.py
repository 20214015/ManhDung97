#!/usr/bin/env python3
"""
Simple Cache System Test
Test basic cache functionality without GUI
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from backend import MumuManager

def test_cache_system():
    """Test cache system functionality."""
    print("🧪 Testing MuMu Manager Cache System")
    print("=" * 50)

    # Initialize QApplication for Qt components FIRST
    app = QApplication(sys.argv)
    if not app:
        print("❌ Failed to create QApplication")
        return

    # Initialize backend AFTER QApplication
    try:
        backend = MumuManager(r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe")
        print("✅ Backend initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize backend: {e}")
        return

    # Test 1: Initial cache refresh
    print("\n1️⃣ Testing initial cache refresh...")
    success, message = backend.refresh_cache()
    if success:
        print(f"✅ Initial refresh: {message}")
    else:
        print(f"❌ Initial refresh failed: {message}")
        return

    # Test 2: Get cached data
    print("\n2️⃣ Testing cached data retrieval...")
    cache = backend.get_cached_instances()
    print(f"📊 Cache contains {len(cache)} instances")

    for vm_index, data in sorted(cache.items())[:3]:  # Show first 3
        name = data.get('name', 'Unknown')
        status = data.get('status', 'Unknown')
        print(f"  VM{vm_index}: {name} | Status: {status}")

    # Test 3: Cache validation
    print("\n3️⃣ Testing cache validation...")
    is_valid = backend.is_cache_valid(30)
    print(f"📅 Cache valid (30s): {is_valid}")

    # Test 4: Cached vs Direct calls
    print("\n4️⃣ Testing cached vs direct calls...")

    # Cached call
    start_time = time.time()
    success1, data1 = backend.get_all_info_cached(use_cache=True)
    cached_time = time.time() - start_time

    # Direct call
    start_time = time.time()
    success2, data2 = backend.get_all_info_direct()
    direct_time = time.time() - start_time

    print(f"📈 Cached: {len(data1) if isinstance(data1, dict) else 0} instances")
    print(f"📈 Direct: {len(data2) if isinstance(data2, dict) else 0} instances")
    print(f"⚡ Performance - Cached: {cached_time:.4f}s, Direct: {direct_time:.4f}s")
    # Test 5: Auto refresh
    print("\n5️⃣ Testing auto refresh...")
    backend.start_auto_refresh(5000)  # 5 seconds
    print("🔄 Auto refresh started (5s interval)")

    # Wait for 2 auto refreshes
    print("⏳ Waiting for auto refresh...")
    time.sleep(12)

    backend.stop_auto_refresh()
    print("⏹️ Auto refresh stopped")

    # Test 6: Cache callbacks
    print("\n6️⃣ Testing cache callbacks...")
    callback_count = 0

    def test_callback():
        nonlocal callback_count
        callback_count += 1
        print(f"📡 Callback triggered #{callback_count}")

    backend.add_cache_callback(test_callback)

    # Trigger manual refresh
    backend.refresh_cache()
    print(f"📞 Callbacks triggered: {callback_count}")

    # Test 7: Clear cache
    print("\n7️⃣ Testing cache clear...")
    backend.clear_cache()
    cache_after_clear = backend.get_cached_instances()
    print(f"🗑️ Cache after clear: {len(cache_after_clear)} instances")

    print("\n🎉 Cache system test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_cache_system()
