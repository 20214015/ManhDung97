"""
ServiceManager - Unified Service Management
==========================================

Provides centralized access to all application services using singleton pattern.
Replaces the complex import pattern in main_window.py.
"""

import logging
from typing import Dict, Any, Optional

try:
    from PyQt6.QtCore import QObject, pyqtSignal
    _QT_AVAILABLE = True
except ImportError:
    # Fallback for systems without PyQt6
    _QT_AVAILABLE = False
    class QObject:
        def __init__(self):
            pass
    
    def pyqtSignal(*args):
        return None


class ServiceManagerQt(QObject):
    """Qt-enabled ServiceManager with proper signal support"""
    service_started = pyqtSignal(str)
    service_stopped = pyqtSignal(str)
    service_error = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()


class ServiceManager:
    """
    Singleton service manager that provides unified access to all services.
    
    This replaces the complex optimization imports in main_window.py:
    - from optimizations.smart_cache import global_smart_cache
    - from optimizations.progressive_loading import ProgressiveLoader
    - from optimizations.ai_optimizer import get_ai_optimizer
    - ... and 20+ other imports
    
    With a simple:
    - from services import get_service_manager
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
            
        self.initialized = True
        self.services: Dict[str, Any] = {}
        self.logger = logging.getLogger('ServiceManager')
        
        # Setup Qt signals if available
        if _QT_AVAILABLE:
            # Create Qt object for signal support
            self._qt_object = ServiceManagerQt()
            # Expose signals through the Qt object
            self.service_started = self._qt_object.service_started
            self.service_stopped = self._qt_object.service_stopped  
            self.service_error = self._qt_object.service_error
        else:
            # Create dummy signals for non-Qt environments
            class DummySignal:
                def emit(self, *args): pass
                def connect(self, *args): pass
            self.service_started = DummySignal()
            self.service_stopped = DummySignal()
            self.service_error = DummySignal()
        
        self._setup_services()
        
    def _setup_services(self):
        """Initialize all available services"""
        try:
            # Cache Service
            self._init_cache_service()
            
            # Database Service  
            self._init_database_service()
            
            # Performance Service
            self._init_performance_service()
            
            # Memory Service
            self._init_memory_service()
            
            self.logger.info(f"ServiceManager initialized with {len(self.services)} services")
            
        except Exception as e:
            self.logger.error(f"Failed to setup services: {e}")
            
    def _init_cache_service(self):
        """Initialize cache service with fallback"""
        try:
            # Try to import optimized cache
            from optimizations.smart_cache import global_smart_cache
            self.services['cache'] = global_smart_cache
            self.service_started.emit('cache')
        except ImportError:
            # Fallback to simple dict cache
            self.services['cache'] = {}
            self.logger.warning("Using fallback dict cache")
            
    def _init_database_service(self):
        """Initialize database service with fallback"""
        try:
            from optimizations.ultra_database import get_ultra_database
            self.services['database'] = get_ultra_database()
            self.service_started.emit('database')
        except ImportError:
            # Fallback to None
            self.services['database'] = None
            self.logger.warning("Database service not available")
            
    def _init_performance_service(self):
        """Initialize performance service with fallback"""
        try:
            from optimizations.performance_acceleration import get_acceleration_manager
            self.services['performance'] = get_acceleration_manager()
            self.service_started.emit('performance')
        except ImportError:
            # Fallback to None
            self.services['performance'] = None
            self.logger.warning("Performance service not available")
            
    def _init_memory_service(self):
        """Initialize memory service with fallback"""
        try:
            from optimizations.memory_pool import get_memory_manager
            self.services['memory'] = get_memory_manager()
            self.service_started.emit('memory')
        except ImportError:
            # Fallback to None
            self.services['memory'] = None
            self.logger.warning("Memory service not available")
    
    # Service Access Methods
    def get_cache(self):
        """Get cache service"""
        return self.services.get('cache')
        
    def get_database(self):
        """Get database service"""
        return self.services.get('database')
        
    def get_performance(self):
        """Get performance service"""
        return self.services.get('performance')
        
    def get_memory(self):
        """Get memory service"""
        return self.services.get('memory')
        
    def get_service(self, name: str):
        """Get service by name"""
        return self.services.get(name)
        
    def get_available_services(self) -> list:
        """Get list of available service names"""
        return [name for name, service in self.services.items() if service is not None]
        
    def start_all_services(self):
        """Start all available services"""
        for name, service in self.services.items():
            if service is not None and hasattr(service, 'start'):
                try:
                    service.start()
                    self.service_started.emit(name)
                except Exception as e:
                    self.service_error.emit(name, str(e))
                    
    def stop_all_services(self):
        """Stop all running services"""
        for name, service in self.services.items():
            if service is not None and hasattr(service, 'stop'):
                try:
                    service.stop()
                    self.service_stopped.emit(name)
                except Exception as e:
                    self.service_error.emit(name, str(e))


# Global service manager instance
_service_manager = None


def get_service_manager() -> ServiceManager:
    """
    Get the global ServiceManager instance.
    
    This is the main entry point for accessing services throughout the app.
    Usage:
        from services import get_service_manager
        
        service_mgr = get_service_manager()
        cache = service_mgr.get_cache()
        ai = service_mgr.get_ai()
    """
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager