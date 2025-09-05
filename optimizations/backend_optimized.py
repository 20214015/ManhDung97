# backend_optimized.py - Optimized backend wrapper với caching và async operations

import asyncio
import subprocess
import json
import time
from typing import Dict, List, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from optimizations.app_config import AppConstants, get_config
from error_handler import global_error_handler, safe_execute
from optimizations.cache_manager import global_cache_manager, cache_result
from optimizations.performance_monitor import create_timer
from optimizations.worker_manager import submit_task

@dataclass
class CommandResult:
    """Result of a backend command execution"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    from_cache: bool = False

class OptimizedBackend:
    """Optimized backend wrapper with caching, async operations, and performance monitoring"""
    
    def __init__(self):
        self.timeout = get_config("performance.command_timeout", AppConstants.Performance.DEFAULT_COMMAND_TIMEOUT)
        self.cache_enabled = get_config("performance.enable_caching", True)
        self.executor = ThreadPoolExecutor(
            max_workers=get_config("performance.backend_workers", 2),
            thread_name_prefix="BackendWorker"
        )
        
        global_error_handler.log_info("OptimizedBackend initialized", "Backend")
    
    def _execute_command_sync(self, command: List[str], operation_name: str = "command") -> CommandResult:
        """Execute command synchronously with performance monitoring"""
        with create_timer(f"backend_{operation_name}") as timer:
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False
                )
                
                execution_time = (time.perf_counter() - timer.start_time) * 1000
                
                if result.returncode == 0:
                    return CommandResult(
                        success=True,
                        data=result.stdout.strip(),
                        execution_time=execution_time
                    )
                else:
                    error_msg = result.stderr.strip() or f"Command failed with code {result.returncode}"
                    return CommandResult(
                        success=False,
                        error=error_msg,
                        execution_time=execution_time
                    )
                    
            except subprocess.TimeoutExpired:
                timer.mark_error()
                return CommandResult(
                    success=False,
                    error=f"Command timed out after {self.timeout} seconds"
                )
            except Exception as e:
                timer.mark_error()
                return CommandResult(
                    success=False,
                    error=str(e)
                )
    
    async def _execute_command_async(self, command: List[str], operation_name: str = "command") -> CommandResult:
        """Execute command asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._execute_command_sync,
            command,
            operation_name
        )
    
    @cache_result(cache_name="instance_list", ttl=15.0)
    def get_instance_list(self) -> CommandResult:
        """Get VM instance list with caching"""
        try:
            from backend import MumuBackend  # Import here to avoid circular imports
            backend = MumuBackend()
            
            with create_timer("get_instance_list"):
                result = safe_execute(
                    lambda: backend.get_instance_list(),
                    "get_instance_list",
                    default_return=[]
                )
                
                if result is not None:
                    return CommandResult(success=True, data=result)
                else:
                    return CommandResult(success=False, error="Failed to get instance list")
                    
        except Exception as e:
            global_error_handler.handle_backend_error("get_instance_list", e)
            return CommandResult(success=False, error=str(e))
    
    async def get_instance_list_async(self) -> CommandResult:
        """Get VM instance list asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.get_instance_list
        )
    
    @cache_result(cache_name="backend_commands", ttl=30.0)
    def get_instance_info(self, instance_index: int) -> CommandResult:
        """Get detailed instance info with caching"""
        try:
            from backend import MumuBackend
            backend = MumuBackend()
            
            with create_timer(f"get_instance_info_{instance_index}"):
                result = safe_execute(
                    lambda: backend.get_instance_info(instance_index),
                    f"get_instance_info_{instance_index}",
                    default_return=None
                )
                
                if result is not None:
                    return CommandResult(success=True, data=result)
                else:
                    return CommandResult(success=False, error=f"Failed to get info for instance {instance_index}")
                    
        except Exception as e:
            global_error_handler.handle_backend_error(f"get_instance_info_{instance_index}", e)
            return CommandResult(success=False, error=str(e))
    
    def start_instance(self, instance_index: int) -> CommandResult:
        """Start VM instance (no caching for state-changing operations)"""
        try:
            from backend import MumuBackend
            backend = MumuBackend()
            
            # Invalidate related caches
            self._invalidate_instance_caches(instance_index)
            
            with create_timer(f"start_instance_{instance_index}"):
                result = safe_execute(
                    lambda: backend.start_instance(instance_index),
                    f"start_instance_{instance_index}",
                    default_return=False
                )
                
                if result:
                    return CommandResult(success=True, data=f"Instance {instance_index} started")
                else:
                    return CommandResult(success=False, error=f"Failed to start instance {instance_index}")
                    
        except Exception as e:
            global_error_handler.handle_backend_error(f"start_instance_{instance_index}", e)
            return CommandResult(success=False, error=str(e))
    
    def stop_instance(self, instance_index: int) -> CommandResult:
        """Stop VM instance"""
        try:
            from backend import MumuBackend
            backend = MumuBackend()
            
            # Invalidate related caches
            self._invalidate_instance_caches(instance_index)
            
            with create_timer(f"stop_instance_{instance_index}"):
                result = safe_execute(
                    lambda: backend.stop_instance(instance_index),
                    f"stop_instance_{instance_index}",
                    default_return=False
                )
                
                if result:
                    return CommandResult(success=True, data=f"Instance {instance_index} stopped")
                else:
                    return CommandResult(success=False, error=f"Failed to stop instance {instance_index}")
                    
        except Exception as e:
            global_error_handler.handle_backend_error(f"stop_instance_{instance_index}", e)
            return CommandResult(success=False, error=str(e))
    
    def restart_instance(self, instance_index: int) -> CommandResult:
        """Restart VM instance"""
        try:
            from backend import MumuBackend
            backend = MumuBackend()
            
            # Invalidate related caches
            self._invalidate_instance_caches(instance_index)
            
            with create_timer(f"restart_instance_{instance_index}"):
                result = safe_execute(
                    lambda: backend.restart_instance(instance_index),
                    f"restart_instance_{instance_index}",
                    default_return=False
                )
                
                if result:
                    return CommandResult(success=True, data=f"Instance {instance_index} restarted")
                else:
                    return CommandResult(success=False, error=f"Failed to restart instance {instance_index}")
                    
        except Exception as e:
            global_error_handler.handle_backend_error(f"restart_instance_{instance_index}", e)
            return CommandResult(success=False, error=str(e))
    
    def batch_operation(self, operation: str, instance_indices: List[int]) -> Dict[int, CommandResult]:
        """Execute operation on multiple instances with intelligent batching"""
        max_batch_size = get_config("performance.max_batch_size", AppConstants.Limits.MAX_BATCH_SIZE)
        batch_delay = get_config("performance.batch_delay", AppConstants.Limits.MIN_BATCH_DELAY)
        
        results = {}
        
        # Split into batches to avoid overwhelming the system
        for i in range(0, len(instance_indices), max_batch_size):
            batch = instance_indices[i:i + max_batch_size]
            
            global_error_handler.log_info(f"Processing batch {i//max_batch_size + 1}: {len(batch)} instances", "Backend")
            
            # Execute batch
            for instance_index in batch:
                if operation == "start":
                    results[instance_index] = self.start_instance(instance_index)
                elif operation == "stop":
                    results[instance_index] = self.stop_instance(instance_index)
                elif operation == "restart":
                    results[instance_index] = self.restart_instance(instance_index)
                else:
                    results[instance_index] = CommandResult(
                        success=False,
                        error=f"Unknown operation: {operation}"
                    )
            
            # Add delay between batches (except for last batch)
            if i + max_batch_size < len(instance_indices):
                time.sleep(batch_delay / 1000.0)  # Convert ms to seconds
        
        return results
    
    def batch_operation_async(self, operation: str, instance_indices: List[int]) -> str:
        """Execute batch operation asynchronously using worker manager"""
        worker_id = submit_task(
            f"batch_{operation}",
            self.batch_operation,
            operation,
            instance_indices
        )
        
        if worker_id:
            global_error_handler.log_info(f"Started async batch {operation} for {len(instance_indices)} instances", "Backend")
            return worker_id
        else:
            global_error_handler.log_warning(f"Failed to start async batch {operation}", "Backend")
            return None
    
    def _invalidate_instance_caches(self, instance_index: int = None):
        """Invalidate caches related to instances"""
        # Invalidate instance list cache
        global_cache_manager.invalidate_cache("instance_list")
        
        # Invalidate specific instance cache if provided
        if instance_index is not None:
            global_cache_manager.invalidate_cache("backend_commands", f"get_instance_info_{instance_index}")
    
    def invalidate_all_caches(self):
        """Invalidate all backend-related caches"""
        count = global_cache_manager.invalidate_cache("backend_commands")
        count += global_cache_manager.invalidate_cache("instance_list")
        global_error_handler.log_info(f"Invalidated {count} backend cache entries", "Backend")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get backend performance statistics"""
        cache_stats = global_cache_manager.get_all_stats()
        
        return {
            "cache_stats": cache_stats,
            "timeout": self.timeout,
            "cache_enabled": self.cache_enabled,
            "executor_info": {
                "max_workers": self.executor._max_workers,
                "threads": len(self.executor._threads) if hasattr(self.executor, '_threads') else 0
            }
        }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.executor.shutdown(wait=True)
            global_error_handler.log_info("OptimizedBackend cleaned up", "Backend")
        except Exception as e:
            global_error_handler.log_warning(f"Error during backend cleanup: {e}", "Backend")

# Global optimized backend instance
global_optimized_backend = OptimizedBackend()

# Convenience functions
def get_instance_list_cached() -> CommandResult:
    """Get cached instance list"""
    return global_optimized_backend.get_instance_list()

async def get_instance_list_async() -> CommandResult:
    """Get instance list asynchronously"""
    return await global_optimized_backend.get_instance_list_async()

def get_instance_info_cached(instance_index: int) -> CommandResult:
    """Get cached instance info"""
    return global_optimized_backend.get_instance_info(instance_index)

def batch_start_instances(instance_indices: List[int]) -> Union[Dict[int, CommandResult], str]:
    """Batch start instances (returns worker_id if async)"""
    if len(instance_indices) > AppConstants.Limits.MAX_BATCH_SIZE:
        return global_optimized_backend.batch_operation_async("start", instance_indices)
    else:
        return global_optimized_backend.batch_operation("start", instance_indices)

def batch_stop_instances(instance_indices: List[int]) -> Union[Dict[int, CommandResult], str]:
    """Batch stop instances (returns worker_id if async)"""
    if len(instance_indices) > AppConstants.Limits.MAX_BATCH_SIZE:
        return global_optimized_backend.batch_operation_async("stop", instance_indices)
    else:
        return global_optimized_backend.batch_operation("stop", instance_indices)

def invalidate_backend_caches():
    """Invalidate all backend caches"""
    global_optimized_backend.invalidate_all_caches()
