#!/usr/bin/env python3
"""
Test script for disk cleanup functionality
Tests the updated OTA.vdi search path and functionality
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_default_path():
    """Test if the default path has been updated correctly"""
    from managers.content_manager import ContentManager
    
    # Create a mock parent for testing
    class MockParent:
        def __init__(self):
            pass
    
    # Test ContentManager default path
    mock_parent = MockParent()
    content_manager = ContentManager(mock_parent)
    
    # Create cleanup page to check default path
    cleanup_page = content_manager._create_cleanup_page()
    disk_path_edit = cleanup_page.findChild(content_manager.QLineEdit, "disk_path_edit")
    
    if disk_path_edit:
        default_path = disk_path_edit.text()
        print(f"✅ Default path from ContentManager: {default_path}")
        
        expected_path = r"C:\Program Files\Netease\MuMuPlayer\vms"
        if default_path == expected_path:
            print("✅ Default path is correct!")
            return True
        else:
            print(f"❌ Default path mismatch. Expected: {expected_path}, Got: {default_path}")
            return False
    else:
        print("❌ Could not find disk_path_edit widget")
        return False

def test_worker_task():
    """Test the find_disk_files_task with the new path"""
    from workers import find_disk_files_task, GenericWorker
    from backend import MumuManager
    
    # Create a mock worker and manager
    class MockWorker:
        def __init__(self):
            self.logs = []
            self.progress_values = []
            
        def started(self, msg):
            self.logs.append(f"STARTED: {msg}")
            
        def log(self, msg):
            self.logs.append(f"LOG: {msg}")
            
        def progress(self, value):
            self.progress_values.append(value)
            
        def check_status(self):
            pass
            
        def emit(self, signal_name):
            pass
    
    class MockMumuManager:
        pass
    
    worker = MockWorker()
    manager = MockMumuManager()
    
    # Test with the new default path
    params = {
        'vms_path': r"C:\Program Files\Netease\MuMuPlayer\vms",
        'type': 'ota.vdi',
        'exclude_dir': 'MuMuPlayer-base'
    }
    
    print(f"🔍 Testing find_disk_files_task with path: {params['vms_path']}")
    
    try:
        result = find_disk_files_task(worker, manager, params)
        print(f"✅ Task completed successfully")
        print(f"📋 Found {len(result.get('files', []))} files")
        print(f"📊 Worker logs: {len(worker.logs)} messages")
        
        # Print some logs for debugging
        for log in worker.logs[:5]:  # First 5 logs
            print(f"   {log}")
        
        if len(worker.logs) > 5:
            print(f"   ... and {len(worker.logs) - 5} more logs")
            
        return True
        
    except Exception as e:
        print(f"❌ Task failed with error: {e}")
        return False

def test_path_exclusion():
    """Test that the exclude_dir parameter was updated correctly"""
    # Check workers.py for the correct exclude_dir value
    
    print("🔍 Testing exclude_dir parameter...")
    
    # Test the exclude_dir in main_window.py
    import inspect
    from main_window import MainWindow
    
    # Get the source of _start_find_disk_files method
    source = inspect.getsource(MainWindow._start_find_disk_files)
    
    if 'MuMuPlayer-base' in source:
        print("✅ exclude_dir updated to 'MuMuPlayer-base'")
        return True
    elif 'MuMuPlayerGlobal-12.0-base' in source:
        print("❌ exclude_dir still using old value 'MuMuPlayerGlobal-12.0-base'")
        return False
    else:
        print("⚠️ exclude_dir parameter not found in source")
        return False

if __name__ == "__main__":
    print("🧪 Testing Disk Cleanup Functionality")
    print("=" * 50)
    
    tests = [
        ("Default Path Test", test_default_path),
        ("Worker Task Test", test_worker_task),
        ("Path Exclusion Test", test_path_exclusion),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Disk cleanup functionality updated successfully.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
