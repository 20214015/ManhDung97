# Optimization modules for MumuManager
from .app_config import AppConstants, app_config, get_config, set_config
from .cache_manager import global_cache_manager, cache_result, get_cache_stats
from .worker_manager import global_worker_manager, submit_task, get_running_workers
from .performance_monitor import global_performance_monitor, create_timer, get_performance_summary
from .backend_optimized import global_optimized_backend, get_instance_list_cached

__all__ = [
    'AppConstants', 'app_config', 'get_config', 'set_config',
    'global_cache_manager', 'cache_result', 'get_cache_stats',
    'global_worker_manager', 'submit_task', 'get_running_workers',
    'global_performance_monitor', 'create_timer', 'get_performance_summary',
    'global_optimized_backend', 'get_instance_list_cached'
]
