"""
🚀 SMART CACHING SYSTEM  
Cache ADB commands và API calls để tăng tốc đáng kể
"""

import time
import json
import hashlib
import threading
from typing import Any, Optional, Dict, Tuple, List
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

class CacheStrategy(Enum):
    """Chiến lược cache khác nhau"""
    IMMEDIATE = "immediate"      # Cache ngay lập tức
    LAZY = "lazy"               # Cache khi cần
    AGGRESSIVE = "aggressive"    # Cache mọi thứ
    SMART = "smart"             # Cache thông minh

@dataclass
class CacheEntry:
    """Entry trong cache với metadata"""
    data: Any
    timestamp: float
    access_count: int
    ttl: float  # Time to live
    size_bytes: int
    cache_key: str
    
    @property
    def is_expired(self) -> bool:
        return time.time() > (self.timestamp + self.ttl)
    
    @property 
    def age(self) -> float:
        return time.time() - self.timestamp

class SmartCache(QObject):
    """Smart caching system cho ADB commands với signals và error handling"""
    
    # Signals for monitoring
    cache_hit = pyqtSignal(str)
    cache_miss = pyqtSignal(str)
    cache_evicted = pyqtSignal(str)
    cache_cleared = pyqtSignal()
    
    def __init__(self, max_size_mb: int = 50, strategy: CacheStrategy = CacheStrategy.SMART, persistent: bool = False):
        super().__init__()
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.strategy = strategy
        self.cache: Dict[str, CacheEntry] = {}
        self.hit_count = 0
        self.miss_count = 0
        self.persistent = persistent
        
        # TTL defaults for different command types
        self.ttl_map = {
            'adb_devices': 5.0,           # Device list changes rarely
            'instance_list': 3.0,         # Instances change moderately  
            'app_list': 30.0,             # Apps change slowly
            'system_info': 60.0,          # System info very stable
            'file_operations': 1.0,       # File ops change quickly
        }
    
    def _generate_key(self, command: str, params: Dict = None) -> str:
        """Generate unique cache key"""
        key_data = {'cmd': command, 'params': params or {}}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _estimate_size(self, data: Any) -> int:
        """Estimate memory size of data"""
        try:
            return len(json.dumps(data, default=str).encode())
        except (TypeError, ValueError, OverflowError):
            return len(str(data).encode())
    
    def _evict_if_needed(self, required_size: int):
        """LRU eviction khi cache đầy với signal emission"""
        current_size = sum(entry.size_bytes for entry in self.cache.values())
        
        if current_size + required_size <= self.max_size_bytes:
            return
            
        # Sort by access frequency and age (LRU + LFU hybrid)
        entries_by_priority = sorted(
            self.cache.items(),
            key=lambda x: (x[1].access_count, -x[1].age)
        )
        
        for key, entry in entries_by_priority:
            del self.cache[key]
            current_size -= entry.size_bytes
            self.cache_evicted.emit(key)
            if current_size + required_size <= self.max_size_bytes:
                break
    
    def get(self, command: str, params: Dict = None, command_type: str = 'default') -> Optional[Any]:
        """Get from cache với enhanced monitoring"""
        cache_key = self._generate_key(command, params)
        
        if cache_key not in self.cache:
            self.miss_count += 1
            self.cache_miss.emit(cache_key)
            return None
            
        entry = self.cache[cache_key]
        
        # Check expiration
        if entry.is_expired:
            del self.cache[cache_key]
            self.miss_count += 1
            self.cache_miss.emit(cache_key)
            return None
            
        # Update access stats
        entry.access_count += 1
        self.hit_count += 1
        self.cache_hit.emit(cache_key)
        
        return entry.data
    
    def set(self, command: str, data: Any, command_type: str = 'default', params: Dict = None):
        """Set cache entry"""
        cache_key = self._generate_key(command, params)
        data_size = self._estimate_size(data)
        
        # Evict if needed
        self._evict_if_needed(data_size)
        
        # Determine TTL
        ttl = self.ttl_map.get(command_type, 10.0)
        
        # Smart TTL adjustment based on command type and data size
        if self.strategy == CacheStrategy.SMART:
            if data_size > 1024 * 100:  # Large data gets longer TTL
                ttl *= 2
            if command_type in ['system_info', 'app_list']:
                ttl *= 3  # Stable data gets longer TTL
        
        entry = CacheEntry(
            data=data,
            timestamp=time.time(),
            access_count=1,
            ttl=ttl,
            size_bytes=data_size,
            cache_key=cache_key
        )
        
        self.cache[cache_key] = entry
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern với improved performance"""
        to_remove = [
            key for key in self.cache.keys() 
            if pattern in key
        ]
        for key in to_remove:
            del self.cache[key]
            self.cache_evicted.emit(key)
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        self.cache_cleared.emit()
    
    def cleanup_expired(self):
        """Remove expired entries to free memory"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired
        ]
        for key in expired_keys:
            del self.cache[key]
            self.cache_evicted.emit(key)
        return len(expired_keys)
    
    def get_stats(self) -> Dict:
        """Get comprehensive cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        total_size = sum(entry.size_bytes for entry in self.cache.values())
        avg_entry_size = total_size / len(self.cache) if self.cache else 0
        
        # Calculate TTL distribution
        ttl_distribution = {}
        for entry in self.cache.values():
            ttl_bucket = f"{entry.ttl:.0f}s"
            ttl_distribution[ttl_bucket] = ttl_distribution.get(ttl_bucket, 0) + 1
        
        return {
            'hit_rate': f"{hit_rate:.1f}%",
            'total_entries': len(self.cache),
            'total_size_mb': f"{total_size / 1024 / 1024:.2f}",
            'avg_entry_size_kb': f"{avg_entry_size / 1024:.2f}",
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'memory_usage_percent': f"{(total_size / self.max_size_bytes * 100):.1f}%",
            'ttl_distribution': ttl_distribution,
            'strategy': self.strategy.value
        }

class PredictiveCache(SmartCache):
    """🔮 Advanced cache với predictive capabilities"""

    def __init__(self, max_size_mb: int = 50, strategy: CacheStrategy = CacheStrategy.SMART, persistent: bool = False):
        super().__init__(max_size_mb, strategy, persistent)

        # Predictive features
        self.access_patterns = AccessPatternAnalyzer()
        self.prefetch_engine = PrefetchEngine()
        self.cache_predictor = CachePredictor()
        self.temporal_analyzer = TemporalAnalyzer()

        # Prediction settings
        self.prefetch_enabled = True
        self.predictive_ttl_enabled = True
        self.pattern_learning_enabled = True

    def get_with_prediction(self, command: str, params: Dict = None, command_type: str = 'default') -> Optional[Any]:
        """Get from cache với predictive enhancements"""

        # Record access pattern
        if self.pattern_learning_enabled:
            self.access_patterns.record_access(command, params, command_type)

        # Get from cache
        result = self.get(command, params, command_type)

        if result is not None:
            # Predict related data to prefetch
            if self.prefetch_enabled:
                self._predict_and_prefetch(command, params, command_type)

        return result

    def put_with_prediction(self, command: str, data: Any, params: Dict = None,
                           command_type: str = 'default', custom_ttl: float = None):
        """Put to cache với predictive TTL"""

        # Predict optimal TTL
        if self.predictive_ttl_enabled and custom_ttl is None:
            custom_ttl = self.cache_predictor.predict_optimal_ttl(command_type, data)

        # Store in cache
        self.put(command, data, params, command_type, custom_ttl)

        # Update patterns
        if self.pattern_learning_enabled:
            self.access_patterns.update_patterns(command, params, command_type, data)

    def _predict_and_prefetch(self, command: str, params: Dict, command_type: str):
        """Predict và prefetch related data"""
        try:
            # Get prediction candidates
            candidates = self.prefetch_engine.predict_related_commands(command, params, command_type)

            # Prefetch high-confidence candidates
            for candidate in candidates[:3]:  # Limit to top 3
                if candidate['confidence'] > 0.7:
                    # Schedule prefetch (async)
                    self.prefetch_engine.schedule_prefetch(candidate)

        except Exception as e:
            print(f"⚠️ Prefetch prediction failed: {e}")

class AccessPatternAnalyzer:
    """📊 Analyze access patterns để predict future requests"""

    def __init__(self):
        self.access_history = []
        self.command_sequences = {}
        self.temporal_patterns = {}
        self.max_history = 1000

    def record_access(self, command: str, params: Dict, command_type: str):
        """Record access pattern"""
        access_record = {
            'command': command,
            'params': params,
            'command_type': command_type,
            'timestamp': time.time(),
            'hour_of_day': time.localtime().tm_hour,
            'day_of_week': time.localtime().tm_wday
        }

        self.access_history.append(access_record)

        # Keep history bounded
        if len(self.access_history) > self.max_history:
            self.access_history = self.access_history[-self.max_history:]

        # Update sequence patterns
        self._update_sequence_patterns(access_record)

    def _update_sequence_patterns(self, current_access: Dict):
        """Update command sequence patterns"""
        if len(self.access_history) < 2:
            return

        prev_access = self.access_history[-2]

        sequence_key = f"{prev_access['command']} -> {current_access['command']}"
        time_diff = current_access['timestamp'] - prev_access['timestamp']

        if sequence_key not in self.command_sequences:
            self.command_sequences[sequence_key] = {
                'count': 1,
                'avg_time_diff': time_diff,
                'confidence': 0.5
            }
        else:
            seq = self.command_sequences[sequence_key]
            seq['count'] += 1
            seq['avg_time_diff'] = (seq['avg_time_diff'] * (seq['count'] - 1) + time_diff) / seq['count']
            seq['confidence'] = min(1.0, seq['count'] / 10)  # Increase confidence with more samples

    def predict_next_commands(self, current_command: str, current_params: Dict) -> List[Dict]:
        """Predict next commands based on patterns"""
        predictions = []

        for sequence_key, pattern in self.command_sequences.items():
            if sequence_key.startswith(f"{current_command} -> "):
                next_command = sequence_key.split(" -> ")[1]
                predictions.append({
                    'command': next_command,
                    'confidence': pattern['confidence'],
                    'expected_delay': pattern['avg_time_diff'],
                    'params': current_params  # Assume similar params
                })

        # Sort by confidence
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        return predictions[:5]  # Top 5 predictions

class PrefetchEngine:
    """🚀 Engine để prefetch predicted data"""

    def __init__(self):
        self.prefetch_queue = []
        self.prefetch_workers = {}
        self.max_concurrent_prefetches = 3

    def predict_related_commands(self, command: str, params: Dict, command_type: str) -> List[Dict]:
        """Predict related commands to prefetch"""
        related = []

        # Command-specific predictions
        if command_type == 'instance_list':
            related.extend([
                {'command': 'instance_details', 'confidence': 0.8, 'params': params},
                {'command': 'instance_status', 'confidence': 0.6, 'params': params}
            ])
        elif command_type == 'adb_devices':
            related.extend([
                {'command': 'device_info', 'confidence': 0.7, 'params': params},
                {'command': 'app_list', 'confidence': 0.5, 'params': params}
            ])

        return related

    def schedule_prefetch(self, candidate: Dict):
        """Schedule prefetch của predicted command"""
        if len(self.prefetch_workers) >= self.max_concurrent_prefetches:
            return  # Too many active prefetches

        # Add to queue for background processing
        self.prefetch_queue.append(candidate)

        # Process queue
        self._process_prefetch_queue()

    def _process_prefetch_queue(self):
        """Process prefetch queue trong background"""
        while self.prefetch_queue and len(self.prefetch_workers) < self.max_concurrent_prefetches:
            candidate = self.prefetch_queue.pop(0)

            # Start prefetch worker
            worker_id = f"prefetch_{time.time()}"
            worker = PrefetchWorker(worker_id, candidate)
            worker.start()

            self.prefetch_workers[worker_id] = worker

class PrefetchWorker(threading.Thread):
    """Worker để execute prefetch tasks"""

    def __init__(self, worker_id: str, candidate: Dict):
        super().__init__()
        self.worker_id = worker_id
        self.candidate = candidate
        self.daemon = True

    def run(self):
        """Execute prefetch task"""
        try:
            # Simulate prefetch execution
            time.sleep(0.1)  # Small delay to avoid overwhelming

            # Here you would actually execute the command
            # For now, just mark as prefetched
            print(f"🔄 Prefetched: {self.candidate['command']}")

        except Exception as e:
            print(f"⚠️ Prefetch failed: {e}")

class CachePredictor:
    """🔮 Predict optimal cache settings"""

    def __init__(self):
        self.command_performance = {}
        self.data_volatility = {}

    def predict_optimal_ttl(self, command_type: str, data: Any) -> float:
        """Predict optimal TTL dựa trên data characteristics"""

        # Base TTL by command type
        base_ttl = {
            'adb_devices': 5.0,
            'instance_list': 3.0,
            'app_list': 30.0,
            'system_info': 60.0,
            'file_operations': 1.0
        }.get(command_type, 10.0)

        # Adjust based on data volatility
        volatility_factor = self._assess_data_volatility(data)
        adjusted_ttl = base_ttl * (1 - volatility_factor)

        return max(1.0, adjusted_ttl)

    def _assess_data_volatility(self, data: Any) -> float:
        """Assess data volatility (0.0 = stable, 1.0 = highly volatile)"""
        try:
            # Simple heuristics for volatility
            data_str = str(data)

            # Check for timestamps or counters
            if any(keyword in data_str.lower() for keyword in ['time', 'count', 'status', 'running']):
                return 0.7  # Moderately volatile

            # Check for static data
            if any(keyword in data_str.lower() for keyword in ['version', 'name', 'id']):
                return 0.2  # Relatively stable

            return 0.5  # Default moderate volatility

        except:
            return 0.5

class TemporalAnalyzer:
    """⏰ Analyze temporal access patterns"""

    def __init__(self):
        self.hourly_patterns = {}
        self.daily_patterns = {}
        self.weekly_patterns = {}

    def analyze_temporal_pattern(self, command: str, timestamp: float):
        """Analyze temporal access pattern"""
        local_time = time.localtime(timestamp)

        hour = local_time.tm_hour
        day = local_time.tm_wday

        # Update hourly pattern
        hour_key = f"{command}_{hour}"
        self.hourly_patterns[hour_key] = self.hourly_patterns.get(hour_key, 0) + 1

        # Update daily pattern
        day_key = f"{command}_{day}"
        self.daily_patterns[day_key] = self.daily_patterns.get(day_key, 0) + 1

    def predict_access_probability(self, command: str, future_timestamp: float) -> float:
        """Predict access probability tại future time"""
        local_time = time.localtime(future_timestamp)
        hour = local_time.tm_hour
        day = local_time.tm_wday

        hour_key = f"{command}_{hour}"
        day_key = f"{command}_{day}"

        hour_count = self.hourly_patterns.get(hour_key, 0)
        day_count = self.daily_patterns.get(day_key, 0)

        # Simple probability calculation
        total_hourly = sum(count for key, count in self.hourly_patterns.items() if key.startswith(command))
        total_daily = sum(count for key, count in self.daily_patterns.items() if key.startswith(command))

        hour_prob = hour_count / total_hourly if total_hourly > 0 else 0.1
        day_prob = day_count / total_daily if total_daily > 0 else 0.1

        return (hour_prob + day_prob) / 2

# Global cache instance with persistence for better startup performance
global_smart_cache = SmartCache(max_size_mb=100, strategy=CacheStrategy.SMART, persistent=True)

# Global predictive cache instance
global_predictive_cache = PredictiveCache(max_size_mb=100, strategy=CacheStrategy.SMART, persistent=True)
