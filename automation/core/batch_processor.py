"""
Batch Processor - Intelligent Batch Management
==============================================
Handles batch processing with retry logic, error recovery, and performance optimization.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import psutil
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QThread, QRunnable, QThreadPool


class BatchStatus(Enum):
    """Batch processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class BatchResult:
    """Result of batch processing"""
    batch_id: int
    instances: List[int]
    status: BatchStatus
    successful_instances: List[int]
    failed_instances: List[int]
    error_messages: Dict[int, str]
    processing_time: float
    retry_count: int = 0


class RetryManager:
    """Intelligent retry management system"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.retry_history = {}
        
    def should_retry(self, instance_id: int, error: str, attempt_count: int) -> Tuple[bool, float]:
        """Determine if instance should be retried and calculate delay"""
        if attempt_count >= self.max_retries:
            return False, 0.0
            
        # Analyze error pattern
        if self._is_temporary_error(error):
            delay = self._calculate_backoff_delay(attempt_count)
            return True, delay
            
        return False, 0.0
    
    def _is_temporary_error(self, error: str) -> bool:
        """Check if error is likely temporary"""
        temporary_keywords = [
            "timeout", "connection", "busy", "resource", "temporary",
            "network", "unavailable", "overloaded"
        ]
        error_lower = error.lower()
        return any(keyword in error_lower for keyword in temporary_keywords)
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        return self.base_delay * (2 ** attempt)


class BatchWorker(QRunnable):
    """Worker thread for processing batches"""
    
    def __init__(self, batch_id: int, instances: List[int], backend_manager, 
                 retry_manager: RetryManager):
        super().__init__()
        self.batch_id = batch_id
        self.instances = instances
        self.backend_manager = backend_manager
        self.retry_manager = retry_manager
        self.result = None
        self.signals = BatchWorkerSignals()
        
    def run(self):
        """Execute batch processing"""
        start_time = time.time()
        
        try:
            self.signals.batch_started.emit(self.batch_id, self.instances)
            
            result = BatchResult(
                batch_id=self.batch_id,
                instances=self.instances,
                status=BatchStatus.PROCESSING,
                successful_instances=[],
                failed_instances=[],
                error_messages={},
                processing_time=0.0
            )
            
            # Process each instance in the batch
            for instance_id in self.instances:
                success, message = self._process_instance(instance_id)
                
                if success:
                    result.successful_instances.append(instance_id)
                else:
                    result.failed_instances.append(instance_id)
                    result.error_messages[instance_id] = message
                
                self.signals.instance_processed.emit(instance_id, success, message)
            
            # Update final result
            result.processing_time = time.time() - start_time
            result.status = BatchStatus.COMPLETED if len(result.failed_instances) == 0 else BatchStatus.FAILED
            
            self.result = result
            self.signals.batch_completed.emit(result)
            
        except Exception as e:
            error_result = BatchResult(
                batch_id=self.batch_id,
                instances=self.instances,
                status=BatchStatus.FAILED,
                successful_instances=[],
                failed_instances=self.instances,
                error_messages={instance_id: str(e) for instance_id in self.instances},
                processing_time=time.time() - start_time
            )
            
            self.result = error_result
            self.signals.batch_error.emit(self.batch_id, str(e))
    
    def _process_instance(self, instance_id: int) -> Tuple[bool, str]:
        """Process single instance with retry logic"""
        attempt = 0
        
        while attempt <= self.retry_manager.max_retries:
            try:
                # Simulate processing - replace with actual backend call
                if self.backend_manager:
                    # result = self.backend_manager.start_instance(instance_id)
                    # return result.success, result.message
                    pass
                
                # Simulation
                import random
                success = random.random() > 0.05  # 95% success rate
                message = f"Instance {instance_id} processed successfully" if success else f"Instance {instance_id} failed"
                
                if success:
                    return True, message
                else:
                    # Check if should retry
                    should_retry, delay = self.retry_manager.should_retry(instance_id, message, attempt)
                    if should_retry:
                        time.sleep(delay)
                        attempt += 1
                        continue
                    else:
                        return False, message
                        
            except Exception as e:
                error_msg = str(e)
                should_retry, delay = self.retry_manager.should_retry(instance_id, error_msg, attempt)
                
                if should_retry:
                    time.sleep(delay)
                    attempt += 1
                    continue
                else:
                    return False, error_msg
        
        return False, f"Instance {instance_id} failed after {self.retry_manager.max_retries} retries"


class BatchWorkerSignals(QObject):
    """Signals for batch worker communication"""
    batch_started = pyqtSignal(int, list)  # batch_id, instances
    batch_completed = pyqtSignal(object)  # BatchResult
    batch_error = pyqtSignal(int, str)  # batch_id, error_message
    instance_processed = pyqtSignal(int, bool, str)  # instance_id, success, message


class EnhancedBatchProcessor(QObject):
    """
    Enhanced batch processor with intelligent scheduling and error recovery
    """
    
    # Signals
    batch_queued = pyqtSignal(int, list)  # batch_id, instances
    batch_started = pyqtSignal(int, list)  # batch_id, instances
    batch_completed = pyqtSignal(object)  # BatchResult
    batch_failed = pyqtSignal(int, str)  # batch_id, error
    all_batches_completed = pyqtSignal(list)  # List[BatchResult]
    progress_updated = pyqtSignal(int, int)  # completed_batches, total_batches
    
    def __init__(self, backend_manager=None, max_concurrent_batches: int = 2):
        super().__init__()
        
        self.backend_manager = backend_manager
        self.max_concurrent_batches = max_concurrent_batches
        self.retry_manager = RetryManager()
        
        # Thread pool for batch processing
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_concurrent_batches)
        
        # Batch management
        self.batch_queue: List[Tuple[int, List[int]]] = []
        self.active_batches: Dict[int, BatchWorker] = {}
        self.completed_batches: List[BatchResult] = []
        self.failed_batches: List[BatchResult] = []
        
        # Processing state
        self.is_processing = False
        self.current_batch_id = 0
        
        # Performance tracking
        self.start_time: Optional[datetime] = None
        self.total_instances_processed = 0
        self.successful_instances = 0
        
        # Adaptive scheduling
        self.batch_scheduler = QTimer()
        self.batch_scheduler.timeout.connect(self._schedule_next_batch)
        self.batch_scheduler.setSingleShot(True)
        
        self.logger = logging.getLogger(__name__)
    
    def start_batch_processing(self, instance_batches: List[List[int]], 
                             batch_delay: float = 2.0) -> bool:
        """Start processing multiple batches"""
        try:
            if self.is_processing:
                self.logger.warning("Batch processing already in progress")
                return False
            
            # Reset state
            self.batch_queue.clear()
            self.active_batches.clear()
            self.completed_batches.clear()
            self.failed_batches.clear()
            self.current_batch_id = 0
            self.total_instances_processed = 0
            self.successful_instances = 0
            
            # Queue all batches
            for instances in instance_batches:
                self.current_batch_id += 1
                self.batch_queue.append((self.current_batch_id, instances))
                self.batch_queued.emit(self.current_batch_id, instances)
            
            self.is_processing = True
            self.start_time = datetime.now()
            
            # Start processing
            self._schedule_next_batch()
            
            self.logger.info(f"Started batch processing: {len(instance_batches)} batches queued")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting batch processing: {e}")
            return False
    
    def stop_batch_processing(self) -> bool:
        """Stop batch processing"""
        try:
            if not self.is_processing:
                return True
            
            self.is_processing = False
            self.batch_scheduler.stop()
            
            # Stop thread pool
            self.thread_pool.clear()
            if self.thread_pool.activeThreadCount() > 0:
                self.thread_pool.waitForDone(5000)
            
            self.logger.info("Batch processing stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping batch processing: {e}")
            return False
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        total_batches = len(self.completed_batches) + len(self.failed_batches) + len(self.batch_queue) + len(self.active_batches)
        completed_batches = len(self.completed_batches)
        
        stats = {
            'is_processing': self.is_processing,
            'total_batches': total_batches,
            'completed_batches': completed_batches,
            'failed_batches': len(self.failed_batches),
            'active_batches': len(self.active_batches),
            'queued_batches': len(self.batch_queue),
            'total_instances_processed': self.total_instances_processed,
            'successful_instances': self.successful_instances,
            'failed_instances': self.total_instances_processed - self.successful_instances,
            'success_rate': (self.successful_instances / max(1, self.total_instances_processed)) * 100,
            'throughput': self._calculate_throughput()
        }
        
        return stats
    
    def _schedule_next_batch(self):
        """Schedule next batch for processing"""
        try:
            if not self.is_processing:
                return
            
            # Check if we have available capacity and queued batches
            if (len(self.active_batches) < self.max_concurrent_batches and 
                len(self.batch_queue) > 0):
                
                # Get next batch
                batch_id, instances = self.batch_queue.pop(0)
                
                # Create and start batch worker
                worker = BatchWorker(batch_id, instances, self.backend_manager, self.retry_manager)
                worker.signals.batch_started.connect(self.batch_started.emit)
                worker.signals.batch_completed.connect(self._on_batch_completed)
                worker.signals.batch_error.connect(self._on_batch_error)
                worker.signals.instance_processed.connect(self._on_instance_processed)
                
                self.active_batches[batch_id] = worker
                self.thread_pool.start(worker)
                
                # Schedule next batch if needed
                if len(self.batch_queue) > 0:
                    delay = self._calculate_adaptive_delay()
                    self.batch_scheduler.start(int(delay * 1000))
            
            elif len(self.batch_queue) == 0 and len(self.active_batches) == 0:
                # All batches completed
                self._complete_processing()
                
        except Exception as e:
            self.logger.error(f"Error scheduling batch: {e}")
    
    def _on_batch_completed(self, result: BatchResult):
        """Handle batch completion"""
        try:
            batch_id = result.batch_id
            
            if batch_id in self.active_batches:
                del self.active_batches[batch_id]
            
            if result.status == BatchStatus.COMPLETED:
                self.completed_batches.append(result)
            else:
                self.failed_batches.append(result)
            
            self.batch_completed.emit(result)
            
            # Update progress
            total_completed = len(self.completed_batches) + len(self.failed_batches)
            total_batches = total_completed + len(self.batch_queue) + len(self.active_batches)
            self.progress_updated.emit(total_completed, total_batches)
            
            # Schedule next batch
            self._schedule_next_batch()
            
        except Exception as e:
            self.logger.error(f"Error handling batch completion: {e}")
    
    def _on_batch_error(self, batch_id: int, error_message: str):
        """Handle batch error"""
        try:
            if batch_id in self.active_batches:
                del self.active_batches[batch_id]
            
            self.batch_failed.emit(batch_id, error_message)
            
            # Schedule next batch
            self._schedule_next_batch()
            
        except Exception as e:
            self.logger.error(f"Error handling batch error: {e}")
    
    def _on_instance_processed(self, instance_id: int, success: bool, message: str):
        """Handle individual instance processing"""
        self.total_instances_processed += 1
        if success:
            self.successful_instances += 1
    
    def _complete_processing(self):
        """Complete batch processing"""
        try:
            self.is_processing = False
            
            all_results = self.completed_batches + self.failed_batches
            self.all_batches_completed.emit(all_results)
            
            stats = self.get_processing_stats()
            self.logger.info(f"Batch processing completed: {stats}")
            
        except Exception as e:
            self.logger.error(f"Error completing processing: {e}")
    
    def _calculate_adaptive_delay(self) -> float:
        """Calculate adaptive delay based on system performance"""
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            
            # Base delay of 2 seconds
            base_delay = 2.0
            
            # Adjust based on system load
            if cpu_usage > 80 or memory_usage > 85:
                return base_delay * 3.0  # Slow down significantly
            elif cpu_usage > 60 or memory_usage > 70:
                return base_delay * 2.0  # Moderate slowdown
            elif cpu_usage < 30 and memory_usage < 50:
                return base_delay * 0.5  # Speed up
            else:
                return base_delay
                
        except Exception as e:
            self.logger.error(f"Error calculating adaptive delay: {e}")
            return 2.0
    
    def _calculate_throughput(self) -> float:
        """Calculate processing throughput (instances per minute)"""
        try:
            if self.start_time and self.total_instances_processed > 0:
                elapsed = datetime.now() - self.start_time
                if elapsed.total_seconds() > 0:
                    return (self.total_instances_processed / elapsed.total_seconds()) * 60
            return 0.0
        except Exception as e:
            self.logger.error(f"Error calculating throughput: {e}")
            return 0.0
