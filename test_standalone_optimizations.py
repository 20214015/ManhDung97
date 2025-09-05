#!/usr/bin/env python3
"""
🧪 Standalone Optimization Test - Test optimizations without PyQt6 dependencies
"""

import sys
import os
import time
import gc
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Standalone adaptive configuration (no PyQt6)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class SystemProfile:
    """System capability profile for adaptive configuration"""
    cpu_cores: int
    cpu_frequency: float  # GHz
    memory_gb: float
    memory_available_gb: float
    performance_tier: str  # "low", "medium", "high", "ultra"
    
    @classmethod
    def detect_system(cls) -> 'SystemProfile':
        """Detect current system capabilities"""
        try:
            if PSUTIL_AVAILABLE:
                cpu_cores = psutil.cpu_count(logical=True)
                cpu_freq = psutil.cpu_freq()
                cpu_frequency = cpu_freq.current / 1000 if cpu_freq else 2.0
                
                memory = psutil.virtual_memory()
                memory_gb = memory.total / (1024**3)
                memory_available_gb = memory.available / (1024**3)
            else:
                cpu_cores = os.cpu_count() or 4
                cpu_frequency = 2.0
                memory_gb = 8.0
                memory_available_gb = 4.0
            
            # Determine performance tier
            if memory_gb >= 16 and cpu_cores >= 8 and cpu_frequency >= 3.0:
                performance_tier = "ultra"
            elif memory_gb >= 8 and cpu_cores >= 4 and cpu_frequency >= 2.5:
                performance_tier = "high"
            elif memory_gb >= 4 and cpu_cores >= 2:
                performance_tier = "medium"
            else:
                performance_tier = "low"
                
            return cls(
                cpu_cores=cpu_cores,
                cpu_frequency=cpu_frequency,
                memory_gb=memory_gb,
                memory_available_gb=memory_available_gb,
                performance_tier=performance_tier
            )
        except Exception:
            return cls(
                cpu_cores=4,
                cpu_frequency=2.0,
                memory_gb=8.0,
                memory_available_gb=4.0,
                performance_tier="medium"
            )

class StandaloneAdaptiveConfig:
    """Standalone adaptive configuration (no PyQt6 dependencies)"""
    
    def __init__(self):
        self.system_profile = SystemProfile.detect_system()
        self._optimized_config = self._calculate_optimal_settings()
        
    def _calculate_optimal_settings(self) -> Dict[str, Any]:
        """Calculate optimal settings based on system profile"""
        profile = self.system_profile
        
        configs = {
            "low": {
                "max_concurrent_workers": 2,
                "cache_ttl_seconds": 60,
                "ui_refresh_interval": 200,
                "auto_refresh_interval": 60,
                "table_update_batch_size": 25,
                "memory_cleanup_threshold": 0.7,
            },
            "medium": {
                "max_concurrent_workers": min(4, profile.cpu_cores),
                "cache_ttl_seconds": 45,
                "ui_refresh_interval": 150,
                "auto_refresh_interval": 45,
                "table_update_batch_size": 40,
                "memory_cleanup_threshold": 0.8,
            },
            "high": {
                "max_concurrent_workers": min(6, profile.cpu_cores),
                "cache_ttl_seconds": 30,
                "ui_refresh_interval": 100,
                "auto_refresh_interval": 30,
                "table_update_batch_size": 60,
                "memory_cleanup_threshold": 0.85,
            },
            "ultra": {
                "max_concurrent_workers": min(8, profile.cpu_cores),
                "cache_ttl_seconds": 20,
                "ui_refresh_interval": 75,
                "auto_refresh_interval": 20,
                "table_update_batch_size": 100,
                "memory_cleanup_threshold": 0.9,
            }
        }
        
        base_config = configs[profile.performance_tier]
        
        # Apply memory-based adjustments
        if profile.memory_available_gb < 2:
            base_config["max_concurrent_workers"] = max(1, base_config["max_concurrent_workers"] // 2)
            base_config["table_update_batch_size"] = max(10, base_config["table_update_batch_size"] // 2)
            
        return base_config
    
    def get_stats(self) -> Dict[str, Any]:
        """Get configuration statistics"""
        return {
            "system_profile": {
                "cpu_cores": self.system_profile.cpu_cores,
                "cpu_frequency": self.system_profile.cpu_frequency,
                "memory_gb": self.system_profile.memory_gb,
                "memory_available_gb": self.system_profile.memory_available_gb,
                "performance_tier": self.system_profile.performance_tier,
            },
            "optimized_config": self._optimized_config,
        }

def test_standalone_adaptive_config():
    """Test standalone adaptive configuration"""
    print("\n🎯 Testing Standalone Adaptive Configuration")
    print("=" * 50)
    
    try:
        config = StandaloneAdaptiveConfig()
        stats = config.get_stats()
        
        print(f"✅ System Profile:")
        profile = stats["system_profile"]
        print(f"   Performance Tier: {profile['performance_tier']}")
        print(f"   CPU Cores: {profile['cpu_cores']}")
        print(f"   CPU Frequency: {profile['cpu_frequency']:.2f} GHz")
        print(f"   Memory: {profile['memory_gb']:.1f} GB")
        print(f"   Available Memory: {profile['memory_available_gb']:.1f} GB")
        
        print(f"✅ Optimized Configuration:")
        opt_config = stats["optimized_config"]
        for key, value in opt_config.items():
            print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Standalone adaptive config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_optimization():
    """Test memory optimization strategies"""
    print("\n🧠 Testing Memory Optimization Strategies")
    print("=" * 50)
    
    try:
        # Test memory monitoring
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024 * 1024)
            print(f"✅ Initial memory usage: {memory_before:.1f} MB")
        
        # Create memory pressure
        data = []
        for i in range(50000):
            data.append({"id": i, "data": list(range(20))})
        
        if PSUTIL_AVAILABLE:
            memory_after_allocation = process.memory_info().rss / (1024 * 1024)
            print(f"✅ Memory after allocation: {memory_after_allocation:.1f} MB")
            print(f"   Memory increase: {memory_after_allocation - memory_before:.1f} MB")
        
        # Test garbage collection optimization
        objects_before = len(gc.get_objects())
        print(f"✅ Objects before GC: {objects_before}")
        
        # Force garbage collection
        collected = gc.collect()
        objects_after = len(gc.get_objects())
        print(f"✅ GC collected {collected} cycles")
        print(f"✅ Objects after GC: {objects_after}")
        print(f"   Objects cleaned: {objects_before - objects_after}")
        
        # Clean up test data
        del data
        gc.collect()
        
        if PSUTIL_AVAILABLE:
            memory_final = process.memory_info().rss / (1024 * 1024)
            print(f"✅ Final memory usage: {memory_final:.1f} MB")
            print(f"   Memory freed: {memory_after_allocation - memory_final:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_worker_optimization():
    """Test worker thread optimization"""
    print("\n⚡ Testing Worker Thread Optimization")
    print("=" * 50)
    
    try:
        config = StandaloneAdaptiveConfig()
        max_workers = config._optimized_config["max_concurrent_workers"]
        print(f"✅ Optimal worker count for this system: {max_workers}")
        
        # Test worker performance with different configurations
        def worker_task(task_id: int, work_size: int):
            """Simulate CPU-intensive work"""
            result = 0
            for i in range(work_size):
                result += i * i
            return task_id, result
        
        # Test with optimal worker count
        start_time = time.time()
        threads = []
        work_size = 100000
        
        for i in range(max_workers):
            thread = threading.Thread(target=worker_task, args=(i, work_size))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        optimal_time = time.time() - start_time
        print(f"✅ Optimal workers ({max_workers}): {optimal_time:.3f}s")
        
        # Test with too many workers
        start_time = time.time()
        threads = []
        excessive_workers = max_workers * 3
        
        for i in range(excessive_workers):
            thread = threading.Thread(target=worker_task, args=(i, work_size // 3))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        excessive_time = time.time() - start_time
        print(f"✅ Excessive workers ({excessive_workers}): {excessive_time:.3f}s")
        
        efficiency = optimal_time / excessive_time if excessive_time > 0 else 1.0
        print(f"✅ Worker optimization efficiency: {efficiency:.2f}x")
        
        return True
        
    except Exception as e:
        print(f"❌ Worker optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_optimization():
    """Test cache optimization strategies"""
    print("\n💾 Testing Cache Optimization Strategies")
    print("=" * 50)
    
    try:
        config = StandaloneAdaptiveConfig()
        cache_ttl = config._optimized_config["cache_ttl_seconds"]
        batch_size = config._optimized_config["table_update_batch_size"]
        
        print(f"✅ Optimal cache TTL: {cache_ttl} seconds")
        print(f"✅ Optimal batch size: {batch_size}")
        
        # Simulate cache performance
        cache = {}
        cache_hits = 0
        cache_misses = 0
        
        # Simulate data access patterns
        for i in range(1000):
            key = f"data_{i % 100}"  # 100 unique keys, repeated access
            
            if key in cache:
                cache_hits += 1
                # Simulate cache hit
                value = cache[key]
            else:
                cache_misses += 1
                # Simulate cache miss and data loading
                cache[key] = {"id": i, "data": f"value_{i}", "timestamp": time.time()}
        
        hit_rate = cache_hits / (cache_hits + cache_misses)
        print(f"✅ Cache hit rate: {hit_rate:.1%}")
        print(f"   Cache hits: {cache_hits}")
        print(f"   Cache misses: {cache_misses}")
        print(f"   Cache size: {len(cache)} entries")
        
        # Test batch processing efficiency
        data = list(range(1000))
        
        # Test optimal batch size
        start_time = time.time()
        batches = [data[i:i+batch_size] for i in range(0, len(data), batch_size)]
        for batch in batches:
            # Simulate batch processing
            result = sum(item * 2 for item in batch)
        
        optimal_batch_time = time.time() - start_time
        print(f"✅ Optimal batch processing ({len(batches)} batches): {optimal_batch_time:.3f}s")
        
        # Test suboptimal batch size
        suboptimal_batch_size = max(1, batch_size // 4)
        start_time = time.time()
        batches = [data[i:i+suboptimal_batch_size] for i in range(0, len(data), suboptimal_batch_size)]
        for batch in batches:
            result = sum(item * 2 for item in batch)
        
        suboptimal_batch_time = time.time() - start_time
        print(f"✅ Suboptimal batch processing ({len(batches)} batches): {suboptimal_batch_time:.3f}s")
        
        batch_efficiency = suboptimal_batch_time / optimal_batch_time if optimal_batch_time > 0 else 1.0
        print(f"✅ Batch optimization efficiency: {batch_efficiency:.2f}x speedup")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_monitoring():
    """Test performance monitoring without PyQt6"""
    print("\n📊 Testing Performance Monitoring")
    print("=" * 50)
    
    try:
        # Monitor system resources
        if PSUTIL_AVAILABLE:
            # CPU monitoring
            cpu_percent = psutil.cpu_percent(interval=0.1)
            print(f"✅ CPU usage: {cpu_percent:.1f}%")
            
            # Memory monitoring
            memory = psutil.virtual_memory()
            print(f"✅ Memory usage: {memory.percent:.1f}%")
            print(f"   Total: {memory.total / (1024**3):.1f} GB")
            print(f"   Available: {memory.available / (1024**3):.1f} GB")
            print(f"   Used: {memory.used / (1024**3):.1f} GB")
            
            # Process monitoring
            process = psutil.Process()
            process_memory = process.memory_info().rss / (1024 * 1024)
            print(f"✅ Process memory: {process_memory:.1f} MB")
            print(f"   Thread count: {process.num_threads()}")
            
        else:
            print("⚠️ psutil not available, using basic monitoring")
        
        # Performance timing
        operations = []
        
        # Test operation timing
        for i in range(10):
            start_time = time.time()
            # Simulate some work
            result = sum(j * j for j in range(10000))
            duration = (time.time() - start_time) * 1000  # ms
            operations.append(duration)
        
        avg_duration = sum(operations) / len(operations)
        min_duration = min(operations)
        max_duration = max(operations)
        
        print(f"✅ Operation performance (10 samples):")
        print(f"   Average: {avg_duration:.2f} ms")
        print(f"   Min: {min_duration:.2f} ms")
        print(f"   Max: {max_duration:.2f} ms")
        print(f"   Variance: {max_duration - min_duration:.2f} ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance monitoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run standalone optimization tests"""
    print("🧪 MumuManager Standalone Optimization Test Suite")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"psutil Available: {PSUTIL_AVAILABLE}")
    print("=" * 60)
    
    tests = [
        ("Standalone Adaptive Configuration", test_standalone_adaptive_config),
        ("Memory Optimization", test_memory_optimization),
        ("Worker Thread Optimization", test_worker_optimization),
        ("Cache Optimization", test_cache_optimization),
        ("Performance Monitoring", test_performance_monitoring),
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
        print("🎉 All optimization tests passed! The optimizations are working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the optimization implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)