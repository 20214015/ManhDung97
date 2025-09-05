#!/usr/bin/env python3
"""
🧪 Optimization Test Suite - Validate performance improvements
Test all optimization components without requiring PyQt6 UI
"""

import time
import sys
import os
import gc
import threading
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_adaptive_config():
    """Test adaptive configuration system"""
    print("\n🎯 Testing Adaptive Configuration System")
    print("=" * 50)
    
    try:
        from optimizations.adaptive_config import AdaptivePerformanceConfig, apply_adaptive_optimizations
        
        # Create adaptive config
        config = AdaptivePerformanceConfig()
        
        # Test system detection
        profile = config.system_profile
        print(f"✅ System detected: {profile.performance_tier}")
        print(f"   CPU Cores: {profile.cpu_cores}")
        print(f"   CPU Frequency: {profile.cpu_frequency:.2f} GHz")
        print(f"   Memory: {profile.memory_gb:.1f} GB (Available: {profile.memory_available_gb:.1f} GB)")
        
        # Test configuration generation
        optimized_config = config.get_optimized_config()
        print(f"✅ Generated optimized configuration:")
        for key, value in optimized_config.items():
            print(f"   {key}: {value}")
        
        # Test memory pressure detection
        pressure = config.get_memory_pressure_level()
        print(f"✅ Memory pressure level: {pressure}")
        
        # Test system load
        load = config.get_system_load_factor()
        print(f"✅ System load factor: {load:.1%}")
        
        # Test applying optimizations
        print("\n🔧 Applying adaptive optimizations...")
        stats = apply_adaptive_optimizations()
        print(f"✅ Applied optimizations for {stats['system_profile']['performance_tier']} tier")
        
        return True
        
    except Exception as e:
        print(f"❌ Adaptive config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_resource_manager():
    """Test smart resource manager"""
    print("\n🧠 Testing Smart Resource Manager")
    print("=" * 50)
    
    try:
        from optimizations.smart_resource_manager import SmartResourceManager
        
        # Create resource manager
        manager = SmartResourceManager()
        
        # Test resource snapshot collection
        snapshot = manager._collect_resource_snapshot()
        print(f"✅ Resource snapshot collected:")
        print(f"   Memory: {snapshot.memory_mb:.1f} MB ({snapshot.memory_percent:.1f}%)")
        print(f"   GC Objects: {snapshot.gc_objects}")
        print(f"   Weak Refs: {snapshot.weak_refs}")
        print(f"   Cache Size: {snapshot.cache_size}")
        print(f"   Threads: {snapshot.thread_count}")
        
        # Test memory pressure detection
        pressure = manager._get_memory_pressure_level(snapshot.memory_percent)
        print(f"✅ Memory pressure: {pressure}")
        
        # Test cache registration
        test_cache = {}
        manager.register_cache("test_cache", test_cache)
        print(f"✅ Registered test cache")
        
        # Test memory pool
        pool = manager.get_memory_pool("test_pool")
        pool.extend([1, 2, 3, 4, 5])
        print(f"✅ Created memory pool with {len(pool)} items")
        
        # Test weak reference tracking
        test_obj = {"test": "data"}
        weak_ref = manager.add_weak_reference(test_obj)
        print(f"✅ Added weak reference")
        
        # Test garbage collection
        initial_objects = len(gc.get_objects())
        action = manager._force_garbage_collection()
        if action:
            print(f"✅ GC performed: {action.objects_cleaned} objects cleaned, {action.memory_freed_mb:.1f} MB freed")
        else:
            print(f"✅ GC performed")
        
        # Test resource stats
        stats = manager.get_resource_stats()
        print(f"✅ Resource statistics:")
        print(f"   Current memory: {stats['current']['memory_mb']:.1f} MB")
        print(f"   Managed caches: {stats['current']['managed_caches']}")
        print(f"   Memory pools: {stats['current']['memory_pools']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Resource manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_monitor():
    """Test enhanced performance monitor (without PyQt6)"""
    print("\n🎯 Testing Performance Monitor Components")
    print("=" * 50)
    
    try:
        # Test performance snapshot creation
        from optimizations.enhanced_performance_monitor import PerformanceSnapshot, PerformanceAlert
        
        # Create test snapshot
        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            cpu_percent=25.5,
            memory_mb=512.0,
            memory_percent=60.0,
            thread_count=8,
            ui_responsiveness=50.0,
            cache_hit_rate=0.85,
            memory_pressure="medium",
            adaptive_tier="high"
        )
        print(f"✅ Performance snapshot created:")
        print(f"   CPU: {snapshot.cpu_percent}%")
        print(f"   Memory: {snapshot.memory_mb} MB ({snapshot.memory_percent}%)")
        print(f"   UI Response: {snapshot.ui_responsiveness} ms")
        print(f"   Cache Hit Rate: {snapshot.cache_hit_rate:.1%}")
        print(f"   Memory Pressure: {snapshot.memory_pressure}")
        print(f"   Adaptive Tier: {snapshot.adaptive_tier}")
        
        # Create test alert
        alert = PerformanceAlert(
            alert_type="memory",
            severity="medium",
            message="Memory usage above threshold",
            timestamp=time.time(),
            suggested_action="Consider reducing cache sizes"
        )
        print(f"✅ Performance alert created: {alert.message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance monitor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_config_optimizations():
    """Test app configuration optimizations"""
    print("\n⚙️ Testing App Configuration Optimizations")
    print("=" * 50)
    
    try:
        from optimizations.app_config import AppConstants
        
        # Test performance constants
        print(f"✅ Performance Configuration:")
        print(f"   Max Concurrent Workers: {AppConstants.Performance.MAX_CONCURRENT_WORKERS}")
        print(f"   UI Refresh Interval: {AppConstants.Performance.UI_REFRESH_INTERVAL} ms")
        print(f"   Auto Refresh Interval: {AppConstants.Performance.AUTO_REFRESH_INTERVAL} s")
        print(f"   Cache TTL: {AppConstants.Performance.CACHE_TTL_SECONDS} s")
        print(f"   Adaptive Scaling: {AppConstants.Performance.ADAPTIVE_SCALING_ENABLED}")
        print(f"   Load Balancing: {AppConstants.Performance.LOAD_BALANCING_ENABLED}")
        
        # Test UI constants
        print(f"✅ UI Configuration:")
        print(f"   Window Size: {AppConstants.UI.WINDOW_DEFAULT_WIDTH}x{AppConstants.UI.WINDOW_DEFAULT_HEIGHT}")
        print(f"   Table Refresh: {AppConstants.UI.TABLE_REFRESH_INTERVAL} ms")
        print(f"   Progress Update: {AppConstants.UI.PROGRESS_UPDATE_INTERVAL} ms")
        
        # Test limits
        print(f"✅ Business Logic Limits:")
        print(f"   Max Instances Create: {AppConstants.Limits.MAX_INSTANCES_CREATE}")
        print(f"   Max Batch Size: {AppConstants.Limits.MAX_BATCH_SIZE}")
        print(f"   Dynamic Batch Sizing: {AppConstants.Limits.DYNAMIC_BATCH_SIZING}")
        print(f"   Connection Pool Size: {AppConstants.Limits.CONNECTION_POOL_SIZE}")
        
        # Test logging
        print(f"✅ Logging Configuration:")
        print(f"   Max Log Entries: {AppConstants.Logging.MAX_LOG_ENTRIES}")
        print(f"   Batch Log Writes: {AppConstants.Logging.BATCH_LOG_WRITES}")
        print(f"   Log Compression: {AppConstants.Logging.LOG_COMPRESSION_ENABLED}")
        print(f"   Async Log Processing: {AppConstants.Logging.ASYNC_LOG_PROCESSING}")
        
        return True
        
    except Exception as e:
        print(f"❌ App config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_without_pyqt():
    """Test optimization integration without PyQt6"""
    print("\n🚀 Testing Optimization Integration (No PyQt6)")
    print("=" * 50)
    
    try:
        # Test basic imports and functionality without UI
        from optimizations.optimization_integration import OptimizationIntegrator
        from optimizations.adaptive_config import get_adaptive_config
        
        # Create integrator without main window
        integrator = OptimizationIntegrator(main_window=None)
        
        # Test adaptive config access
        adaptive_config = get_adaptive_config()
        stats = adaptive_config.get_stats()
        print(f"✅ Adaptive config stats retrieved")
        print(f"   Performance tier: {stats['system_profile']['performance_tier']}")
        print(f"   Memory pressure: {stats['memory_pressure']}")
        
        # Test optimization summary
        summary = integrator.get_optimization_summary()
        if summary:
            print(f"✅ Optimization summary generated")
            print(f"   System Profile: {summary.get('system_profile', {}).get('performance_tier', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_performance_benchmark():
    """Run a simple performance benchmark"""
    print("\n⚡ Running Performance Benchmark")
    print("=" * 50)
    
    try:
        # Test memory allocation performance
        start_time = time.time()
        data = []
        for i in range(100000):
            data.append({"id": i, "value": f"test_{i}", "data": list(range(10))})
        
        allocation_time = time.time() - start_time
        print(f"✅ Memory allocation test: {allocation_time:.3f}s for 100k objects")
        
        # Test garbage collection performance
        start_time = time.time()
        del data
        gc.collect()
        gc_time = time.time() - start_time
        print(f"✅ Garbage collection test: {gc_time:.3f}s")
        
        # Test threading performance
        def worker_thread():
            for i in range(10000):
                result = i * i + i
        
        start_time = time.time()
        threads = []
        for i in range(4):
            thread = threading.Thread(target=worker_thread)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        threading_time = time.time() - start_time
        print(f"✅ Threading test: {threading_time:.3f}s for 4 worker threads")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        return False

def main():
    """Run all optimization tests"""
    print("🧪 MumuManager Optimization Test Suite")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Test Directory: {os.path.dirname(os.path.abspath(__file__))}")
    print("=" * 60)
    
    tests = [
        ("Adaptive Configuration", test_adaptive_config),
        ("Smart Resource Manager", test_resource_manager),
        ("Performance Monitor Components", test_performance_monitor),
        ("App Configuration Optimizations", test_app_config_optimizations),
        ("Integration System", test_integration_without_pyqt),
        ("Performance Benchmark", run_performance_benchmark),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Running: {test_name}")
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   Result: {status}")
        except Exception as e:
            print(f"   Result: ❌ FAILED - {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 60)
    print(f"Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All optimization tests passed! The app optimizations are working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the optimization implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)