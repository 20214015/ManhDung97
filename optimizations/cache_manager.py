# cache_manager.py - Intelligent caching system for backend operations

import time
import hashlib
import threading
from typing import Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from collections import OrderedDict
from optimizations.app_config import AppConstants, get_config
from error_handler import global_error_handler

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0
    ttl: float = 30.0  # Time to live in seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() - self.timestamp > self.ttl
    
    def access(self) -> Any:
        """Access the cached value and update stats"""
        self.access_count += 1
        self.last_access = time.time()
        return self.value

class IntelligentCache:
    """Thread-safe intelligent cache with LRU eviction and TTL"""
    
    def __init__(self, max_size: int = 100, default_ttl: float = 30.0):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        
    def _make_key(self, func_name: str, *args, **kwargs) -> str:
        """Create a cache key from function name and arguments"""
        # Create a stable hash from arguments
        key_data = f"{func_name}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    # Move to end (most recently used)
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return entry.access()
                else:
                    # Remove expired entry
                    del self._cache[key]
            
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache"""
        with self._lock:
            # Use default TTL if not provided
            if ttl is None:
                ttl = self.default_ttl
                
            # Create cache entry
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl
            )
            
            # Add to cache
            self._cache[key] = entry
            self._cache.move_to_end(key)  # Mark as most recently used
            
            # Evict oldest entries if over max size
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
    
    def invalidate(self, pattern: str = None) -> int:
        """Invalidate cache entries matching pattern or all if pattern is None"""
        with self._lock:
            if pattern is None:
                count = len(self._cache)
                self._cache.clear()
                return count
            
            keys_to_remove = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self._cache[key]
            return len(keys_to_remove)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }
    
    def reset_stats(self):
        """Reset cache statistics"""
        with self._lock:
            self._hits = 0
            self._misses = 0

class CacheManager:
    """Global cache manager with multiple cache instances"""
    
    def __init__(self):
        self.enabled = get_config("performance.enable_caching", True)
        self.default_ttl = get_config("performance.cache_ttl", AppConstants.Performance.CACHE_TTL_SECONDS)
        
        # Different caches for different types of data
        self.caches = {
            "backend_commands": IntelligentCache(max_size=50, default_ttl=self.default_ttl),
            "instance_list": IntelligentCache(max_size=20, default_ttl=15.0),  # Shorter TTL for dynamic data
            "system_info": IntelligentCache(max_size=10, default_ttl=60.0),    # Longer TTL for stable data
            "validation": IntelligentCache(max_size=100, default_ttl=300.0),   # Very long TTL for validation
        }
        
        global_error_handler.log_info(f"CacheManager initialized with caching {'enabled' if self.enabled else 'disabled'}", "CacheManager")
    
    def get_cache(self, cache_name: str) -> IntelligentCache:
        """Get a specific cache instance"""
        return self.caches.get(cache_name, self.caches["backend_commands"])
    
    def cache_result(self, cache_name: str = "backend_commands", ttl: Optional[float] = None):
        """Decorator to cache function results"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                cache = self.get_cache(cache_name)
                cache_key = cache._make_key(func.__name__, *args, **kwargs)
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    global_error_handler.log_info(f"Cache hit for {func.__name__}", "CacheManager")
                    return cached_result
                
                # Execute function and cache result
                try:
                    result = func(*args, **kwargs)
                    cache.set(cache_key, result, ttl)
                    global_error_handler.log_info(f"Cached result for {func.__name__}", "CacheManager")
                    return result
                except Exception as e:
                    global_error_handler.log_warning(f"Function {func.__name__} failed, not caching: {e}", "CacheManager")
                    raise
                    
            wrapper.__wrapped__ = func  # Preserve original function
            return wrapper
        return decorator
    
    def invalidate_cache(self, cache_name: str, pattern: str = None) -> int:
        """Invalidate specific cache or pattern"""
        if cache_name in self.caches:
            count = self.caches[cache_name].invalidate(pattern)
            global_error_handler.log_info(f"Invalidated {count} entries from {cache_name} cache", "CacheManager")
            return count
        return 0
    
    def invalidate_all(self) -> Dict[str, int]:
        """Invalidate all caches"""
        results = {}
        for name, cache in self.caches.items():
            results[name] = cache.invalidate()
        global_error_handler.log_info(f"Invalidated all caches: {results}", "CacheManager")
        return results
    
    def cleanup_expired(self) -> Dict[str, int]:
        """Cleanup expired entries from all caches"""
        results = {}
        for name, cache in self.caches.items():
            results[name] = cache.cleanup_expired()
        
        total_cleaned = sum(results.values())
        if total_cleaned > 0:
            global_error_handler.log_info(f"Cleaned {total_cleaned} expired entries: {results}", "CacheManager")
        return results
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches"""
        return {name: cache.get_stats() for name, cache in self.caches.items()}
    
    def get_total_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        all_stats = self.get_all_stats()
        
        total_size = sum(stats["size"] for stats in all_stats.values())
        total_hits = sum(stats["hits"] for stats in all_stats.values())
        total_misses = sum(stats["misses"] for stats in all_stats.values())
        total_requests = total_hits + total_misses
        overall_hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "enabled": self.enabled,
            "total_size": total_size,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "overall_hit_rate": overall_hit_rate,
            "cache_details": all_stats
        }

# Global cache manager instance
global_cache_manager = CacheManager()

# Convenience functions
def cache_result(cache_name: str = "backend_commands", ttl: Optional[float] = None):
    """Decorator to cache function results"""
    return global_cache_manager.cache_result(cache_name, ttl)

def invalidate_cache(cache_name: str, pattern: str = None) -> int:
    """Invalidate cache entries"""
    return global_cache_manager.invalidate_cache(cache_name, pattern)

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return global_cache_manager.get_total_stats()

def cleanup_caches() -> Dict[str, int]:
    """Cleanup expired cache entries"""
    return global_cache_manager.cleanup_expired()
