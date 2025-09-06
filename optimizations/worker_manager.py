# worker_manager.py - Advanced worker thread management system

from typing import Dict, Optional, List, Callable, Any
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, QTimer
import uuid
import time
from enum import Enum
from dataclasses import dataclass
from optimizations.app_config import AppConstants, get_config
try:
    from optimizations.error_handler import global_error_handler
except ImportError:
    # Fallback if error_handler not available
    class SimpleErrorHandler:
        def log_info(self, msg, category): print(f"[{category}] {msg}")
        def log_warning(self, msg, category): print(f"[{category}] WARNING: {msg}")
        def log_error(self, msg, category): print(f"[{category}] ERROR: {msg}")
        def handle_worker_error(self, name, error): print(f"[Worker] ERROR in {name}: {error}")
    global_error_handler = SimpleErrorHandler()

class WorkerStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class WorkerInfo:
    """Information about a worker"""
    worker_id: str
    name: str
    status: WorkerStatus
    created_at: float
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    error_message: Optional[str] = None
    result: Any = None

class WorkerRunnable(QObject, QRunnable):
    """Runnable worker executed in a thread pool"""

    finished = pyqtSignal(str, object)  # worker_id, result
    error = pyqtSignal(str, str)  # worker_id, error_message
    progress = pyqtSignal(str, int)  # worker_id, percentage
    status_changed = pyqtSignal(str, str)  # worker_id, status

    def __init__(self, worker_id: str, name: str, task_func: Callable, *args, **kwargs):
        QObject.__init__(self)
        QRunnable.__init__(self)
        self.worker_id = worker_id
        self.name = name
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.status = WorkerStatus.IDLE
        self._cancelled = False

    def cancel(self):
        """Cancel the worker"""
        self._cancelled = True
        self.status = WorkerStatus.CANCELLED
        self.status_changed.emit(self.worker_id, self.status.value)

    def is_cancelled(self) -> bool:
        """Check if worker was cancelled"""
        return self._cancelled

    def run(self):
        """Execute the worker task"""
        try:
            if self._cancelled:
                return

            self.status = WorkerStatus.RUNNING
            self.status_changed.emit(self.worker_id, self.status.value)

            result = self.task_func(*self.args, **self.kwargs)

            if not self._cancelled:
                self.status = WorkerStatus.FINISHED
                self.status_changed.emit(self.worker_id, self.status.value)
                self.finished.emit(self.worker_id, result)

        except Exception as e:
            if not self._cancelled:
                error_msg = str(e)
                self.status = WorkerStatus.ERROR
                self.status_changed.emit(self.worker_id, self.status.value)
                self.error.emit(self.worker_id, error_msg)
                global_error_handler.handle_worker_error(self.name, e)

class WorkerManager(QObject):
    """Advanced worker pool manager với resource management"""
    
    worker_started = pyqtSignal(str, str)  # worker_id, name
    worker_finished = pyqtSignal(str, object)  # worker_id, result
    worker_error = pyqtSignal(str, str)  # worker_id, error
    worker_cancelled = pyqtSignal(str)  # worker_id
    
    def __init__(self, max_workers: Optional[int] = None, parent=None):
        super().__init__(parent)
        self.max_workers = max_workers or get_config("performance.worker_pool_size", 
                                                    AppConstants.Performance.MAX_CONCURRENT_WORKERS)
        
        self._thread_pool = QThreadPool.globalInstance()
        self._thread_pool.setMaxThreadCount(int(self.max_workers))
        self._workers: Dict[str, WorkerRunnable] = {}
        self._worker_info: Dict[str, WorkerInfo] = {}
        self._cleanup_timer = None  # Lazy initialization
        self._cleanup_started = False
        
        global_error_handler.log_info(f"WorkerManager initialized with {self.max_workers} max workers", "WorkerManager")
    
    def _ensure_cleanup_started(self):
        """🔧 Lazy initialization of cleanup timer"""
        if not self._cleanup_started and self.parent():
            self._cleanup_timer = QTimer(self.parent())
            self._cleanup_timer.timeout.connect(self._cleanup_finished_workers)
            cleanup_interval = get_config("performance.cleanup_interval", 30000)
            if isinstance(cleanup_interval, (int, float)):
                self._cleanup_timer.start(int(cleanup_interval))
            else:
                self._cleanup_timer.start(30000)  # Default 30 seconds
            self._cleanup_started = True
    
    def submit_task(self, name: str, task_func: Callable, *args, 
                   priority: int = 0, **kwargs) -> Optional[str]:
        """
        Submit a task to be executed by a worker
        
        Args:
            name: Human readable name for the task
            task_func: Function to execute
            *args: Arguments for the function
            priority: Task priority (higher = more important) 
            **kwargs: Keyword arguments for the function
            
        Returns:
            str: Worker ID if successful, None if failed
        """
        # Start cleanup timer if not already started
        self._ensure_cleanup_started()
        
        # Check if we can start a new worker
        max_workers = self.max_workers
        if isinstance(max_workers, (int, float)):
            max_workers = int(max_workers)
        else:
            max_workers = 4  # Default
            
        if self._get_running_worker_count() >= max_workers:
            global_error_handler.log_warning(
                f"Cannot start worker '{name}': maximum workers ({self.max_workers}) reached",
                "WorkerManager"
            )
            return None
        
        # Create worker
        worker_id = str(uuid.uuid4())
        worker = WorkerRunnable(worker_id, name, task_func, *args, **kwargs)

        # Connect signals
        worker.finished.connect(self._on_worker_finished)
        worker.error.connect(self._on_worker_error)
        worker.status_changed.connect(self._on_worker_status_changed)

        # Store worker and info
        self._workers[worker_id] = worker
        self._worker_info[worker_id] = WorkerInfo(
            worker_id=worker_id,
            name=name,
            status=WorkerStatus.IDLE,
            created_at=time.time()
        )

        # Start worker in thread pool
        self._thread_pool.start(worker, priority)
        self._worker_info[worker_id].started_at = time.time()
        self._worker_info[worker_id].status = WorkerStatus.RUNNING
        self.worker_started.emit(worker_id, name)
        global_error_handler.log_info(f"Started worker '{name}' ({worker_id})", "WorkerManager")
        return worker_id
    
    def cancel_worker(self, worker_id: str) -> bool:
        """Cancel a specific worker"""
        if worker_id not in self._workers:
            return False
            
        worker = self._workers[worker_id]
        worker.cancel()
        try:
            self._thread_pool.cancel(worker)
        except AttributeError:
            pass  # cancel may not be available in some Qt versions
        
        if worker_id in self._worker_info:
            self._worker_info[worker_id].status = WorkerStatus.CANCELLED
            self._worker_info[worker_id].finished_at = time.time()
        
        self.worker_cancelled.emit(worker_id)
        global_error_handler.log_info(f"Cancelled worker {worker_id}", "WorkerManager")
        return True
    
    def cancel_all_workers(self):
        """Cancel all running workers"""
        worker_ids = list(self._workers.keys())
        for worker_id in worker_ids:
            self.cancel_worker(worker_id)
        
        global_error_handler.log_info(f"Cancelled {len(worker_ids)} workers", "WorkerManager")
    
    def get_worker_info(self, worker_id: str) -> Optional[WorkerInfo]:
        """Get information about a specific worker"""
        return self._worker_info.get(worker_id)
    
    def get_running_workers(self) -> List[WorkerInfo]:
        """Get list of currently running workers"""
        return [info for info in self._worker_info.values() 
                if info.status == WorkerStatus.RUNNING]
    
    def get_all_workers(self) -> List[WorkerInfo]:
        """Get list of all workers (including finished)"""
        return list(self._worker_info.values())
    
    def _get_running_worker_count(self) -> int:
        """Get count of currently running workers"""
        return len([w for w in self._worker_info.values() 
                   if w.status == WorkerStatus.RUNNING])
    
    def _on_worker_finished(self, worker_id: str, result: Any):
        """Handle worker finished signal"""
        if worker_id in self._worker_info:
            self._worker_info[worker_id].status = WorkerStatus.FINISHED
            self._worker_info[worker_id].finished_at = time.time()
            self._worker_info[worker_id].result = result
        
        self.worker_finished.emit(worker_id, result)
        
        # Log completion time
        if worker_id in self._worker_info:
            info = self._worker_info[worker_id]
            if info.started_at:
                duration = time.time() - info.started_at
                global_error_handler.log_info(
                    f"Worker '{info.name}' completed in {duration:.2f}s", 
                    "WorkerManager"
                )
    
    def _on_worker_error(self, worker_id: str, error_message: str):
        """Handle worker error signal"""
        if worker_id in self._worker_info:
            self._worker_info[worker_id].status = WorkerStatus.ERROR
            self._worker_info[worker_id].finished_at = time.time()
            self._worker_info[worker_id].error_message = error_message
        
        self.worker_error.emit(worker_id, error_message)
    
    def _on_worker_status_changed(self, worker_id: str, status: str):
        """Handle worker status change"""
        if worker_id in self._worker_info:
            try:
                self._worker_info[worker_id].status = WorkerStatus(status)
            except ValueError:
                pass  # Invalid status
    
    def _cleanup_finished_workers(self):
        """Cleanup finished workers to prevent memory leaks"""
        current_time = time.time()
        cleanup_age = 300  # 5 minutes
        
        workers_to_remove = []
        for worker_id, info in self._worker_info.items():
            if (info.status in [WorkerStatus.FINISHED, WorkerStatus.ERROR, WorkerStatus.CANCELLED] 
                and info.finished_at 
                and current_time - info.finished_at > cleanup_age):
                workers_to_remove.append(worker_id)
        
        for worker_id in workers_to_remove:
            if worker_id in self._workers:
                del self._workers[worker_id]
            if worker_id in self._worker_info:
                del self._worker_info[worker_id]
        
        if workers_to_remove:
            global_error_handler.log_info(
                f"Cleaned up {len(workers_to_remove)} finished workers", 
                "WorkerManager"
            )
    
    def cleanup(self):
        """Cleanup all workers and resources"""
        if self._cleanup_timer:
            self._cleanup_timer.stop()
        self.cancel_all_workers()
        
        # Wait for workers to finish
        try:
            self._thread_pool.waitForDone(2000)
        except Exception:
            pass
        
        self._workers.clear()
        self._worker_info.clear()
        
        global_error_handler.log_info("WorkerManager cleaned up", "WorkerManager")

# Global worker manager instance
# Global worker manager instance (lazy initialization)
global_worker_manager = None

def get_global_worker_manager(parent=None):
    """Get or create global worker manager with proper parent"""
    global global_worker_manager
    if global_worker_manager is None:
        global_worker_manager = WorkerManager(parent=parent)
    return global_worker_manager

# Convenience functions
def submit_task(name: str, task_func: Callable, *args, **kwargs) -> Optional[str]:
    """Submit a task to the global worker manager"""
    manager = get_global_worker_manager()
    return manager.submit_task(name, task_func, *args, **kwargs)

def cancel_worker(worker_id: str) -> bool:
    """Cancel a worker in the global worker manager"""
    manager = get_global_worker_manager()
    return manager.cancel_worker(worker_id)

def get_running_workers() -> List[WorkerInfo]:
    """Get running workers from global worker manager"""
    manager = get_global_worker_manager()
    return manager.get_running_workers()
