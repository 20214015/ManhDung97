#!/usr/bin/env python3
"""
🎯 Adaptive Configuration System - Dynamic Performance Optimization
Automatically adjusts app performance settings based on system capabilities
"""

import os
import psutil
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass
from optimizations.app_config import AppConstants

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
            cpu_cores = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            cpu_frequency = cpu_freq.current / 1000 if cpu_freq else 2.0  # Default 2GHz
            
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            memory_available_gb = memory.available / (1024**3)
            
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
            # Fallback to conservative defaults
            return cls(
                cpu_cores=4,
                cpu_frequency=2.0,
                memory_gb=8.0,
                memory_available_gb=4.0,
                performance_tier="medium"
            )

class AdaptivePerformanceConfig:
    """🚀 Adaptive performance configuration based on system capabilities"""
    
    def __init__(self):
        self.system_profile = SystemProfile.detect_system()
        self._optimized_config = self._calculate_optimal_settings()
        self._lock = threading.RLock()
        
    def _calculate_optimal_settings(self) -> Dict[str, Any]:
        """Calculate optimal settings based on system profile"""
        profile = self.system_profile
        
        # Base configurations for different performance tiers
        configs = {
            "low": {
                "max_concurrent_workers": 2,
                "cache_ttl_seconds": 60,  # Longer cache for slower systems
                "ui_refresh_interval": 200,  # Slower refresh
                "auto_refresh_interval": 60,  # Less frequent auto-refresh
                "table_update_batch_size": 25,  # Smaller batches
                "worker_check_interval": 100,  # Less frequent checks
                "memory_cleanup_threshold": 0.7,  # More aggressive cleanup
                "table_refresh_interval": 500,  # Slower table refresh
                "progress_update_interval": 200,
                "max_log_entries": 2500,  # Fewer log entries
            },
            "medium": {
                "max_concurrent_workers": min(4, profile.cpu_cores),
                "cache_ttl_seconds": 45,
                "ui_refresh_interval": 150,
                "auto_refresh_interval": 45,
                "table_update_batch_size": 40,
                "worker_check_interval": 75,
                "memory_cleanup_threshold": 0.8,
                "table_refresh_interval": 300,
                "progress_update_interval": 150,
                "max_log_entries": 4000,
            },
            "high": {
                "max_concurrent_workers": min(6, profile.cpu_cores),
                "cache_ttl_seconds": 30,
                "ui_refresh_interval": 100,
                "auto_refresh_interval": 30,
                "table_update_batch_size": 60,
                "worker_check_interval": 50,
                "memory_cleanup_threshold": 0.85,
                "table_refresh_interval": 200,
                "progress_update_interval": 100,
                "max_log_entries": 6000,
            },
            "ultra": {
                "max_concurrent_workers": min(8, profile.cpu_cores),
                "cache_ttl_seconds": 20,  # Shorter cache for faster refresh
                "ui_refresh_interval": 75,  # Faster UI updates
                "auto_refresh_interval": 20,  # More frequent updates
                "table_update_batch_size": 100,  # Larger batches
                "worker_check_interval": 25,  # More frequent checks
                "memory_cleanup_threshold": 0.9,  # Less aggressive cleanup
                "table_refresh_interval": 150,  # Faster table refresh
                "progress_update_interval": 75,
                "max_log_entries": 8000,  # More log entries
            }
        }
        
        base_config = configs[profile.performance_tier]
        
        # Apply memory-based adjustments
        if profile.memory_available_gb < 2:
            # Memory pressure - be more conservative
            base_config["max_concurrent_workers"] = max(1, base_config["max_concurrent_workers"] // 2)
            base_config["table_update_batch_size"] = max(10, base_config["table_update_batch_size"] // 2)
            base_config["max_log_entries"] = max(1000, base_config["max_log_entries"] // 2)
            base_config["memory_cleanup_threshold"] = 0.6
            
        elif profile.memory_available_gb > 8:
            # Plenty of memory - be more aggressive
            base_config["max_concurrent_workers"] = min(profile.cpu_cores, base_config["max_concurrent_workers"] + 2)
            base_config["table_update_batch_size"] = min(200, int(base_config["table_update_batch_size"] * 1.5))
            base_config["max_log_entries"] = min(15000, int(base_config["max_log_entries"] * 1.5))
            
        return base_config
    
    def get_optimized_config(self) -> Dict[str, Any]:
        """Get the optimized configuration"""
        with self._lock:
            return self._optimized_config.copy()
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a specific optimized configuration value"""
        with self._lock:
            return self._optimized_config.get(key, default)
    
    def refresh_system_profile(self) -> bool:
        """Re-detect system profile and update configuration"""
        try:
            with self._lock:
                old_tier = self.system_profile.performance_tier
                self.system_profile = SystemProfile.detect_system()
                
                # Only recalculate if tier changed
                if old_tier != self.system_profile.performance_tier:
                    self._optimized_config = self._calculate_optimal_settings()
                    return True
                    
                return False
        except Exception:
            return False
    
    def get_memory_pressure_level(self) -> str:
        """Get current memory pressure level"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent > 90:
                return "critical"
            elif usage_percent > 80:
                return "high"
            elif usage_percent > 70:
                return "medium"
            else:
                return "low"
        except Exception:
            return "unknown"
    
    def get_system_load_factor(self) -> float:
        """Get current system load factor (0.0 to 1.0+)"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            return min(1.0, cpu_percent / 100.0)
        except Exception:
            return 0.5  # Default moderate load
    
    def apply_to_app_constants(self) -> None:
        """Apply optimized configuration to AppConstants (monkey patch)"""
        config = self.get_optimized_config()
        
        # Update Performance class
        AppConstants.Performance.MAX_CONCURRENT_WORKERS = config["max_concurrent_workers"]
        AppConstants.Performance.CACHE_TTL_SECONDS = config["cache_ttl_seconds"]
        AppConstants.Performance.UI_REFRESH_INTERVAL = config["ui_refresh_interval"]
        AppConstants.Performance.AUTO_REFRESH_INTERVAL = config["auto_refresh_interval"]
        AppConstants.Performance.TABLE_UPDATE_BATCH_SIZE = config["table_update_batch_size"]
        AppConstants.Performance.WORKER_CHECK_INTERVAL = config["worker_check_interval"]
        
        # Update UI class
        AppConstants.UI.TABLE_REFRESH_INTERVAL = config["table_refresh_interval"]
        AppConstants.UI.PROGRESS_UPDATE_INTERVAL = config["progress_update_interval"]
        
        # Update Logging class  
        AppConstants.Logging.MAX_LOG_ENTRIES = config["max_log_entries"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get configuration statistics for monitoring"""
        return {
            "system_profile": {
                "cpu_cores": self.system_profile.cpu_cores,
                "cpu_frequency": self.system_profile.cpu_frequency,
                "memory_gb": self.system_profile.memory_gb,
                "memory_available_gb": self.system_profile.memory_available_gb,
                "performance_tier": self.system_profile.performance_tier,
            },
            "optimized_config": self.get_optimized_config(),
            "memory_pressure": self.get_memory_pressure_level(),
            "system_load": self.get_system_load_factor(),
        }

# Global adaptive configuration instance
adaptive_config = AdaptivePerformanceConfig()

def get_adaptive_config() -> AdaptivePerformanceConfig:
    """Get the global adaptive configuration instance"""
    return adaptive_config

def apply_adaptive_optimizations() -> Dict[str, Any]:
    """Apply adaptive optimizations and return stats"""
    adaptive_config.apply_to_app_constants()
    return adaptive_config.get_stats()

if __name__ == "__main__":
    # Demo the adaptive configuration
    config = AdaptivePerformanceConfig()
    print("🎯 Adaptive Configuration Demo")
    print("=" * 40)
    
    stats = config.get_stats()
    print(f"System Profile: {stats['system_profile']}")
    print(f"Performance Tier: {stats['system_profile']['performance_tier']}")
    print(f"Memory Pressure: {stats['memory_pressure']}")
    print(f"System Load: {stats['system_load']:.1%}")
    print()
    print("Optimized Configuration:")
    for key, value in stats['optimized_config'].items():
        print(f"  {key}: {value}")