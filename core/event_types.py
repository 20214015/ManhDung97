"""
Event Types Definition
======================

Centralized definition of all event types used in the application.
"""

from enum import Enum, auto


class EventTypes(Enum):
    """
    Centralized event type definitions for the application.
    """
    
    # Instance Management Events
    INSTANCES_UPDATED = auto()
    INSTANCE_SELECTED = auto()
    INSTANCE_DESELECTED = auto()
    INSTANCE_CREATED = auto()
    INSTANCE_DELETED = auto()
    INSTANCE_STARTED = auto()
    INSTANCE_STOPPED = auto()
    INSTANCE_CLONED = auto()
    
    # UI Events
    PAGE_CHANGED = auto()
    TAB_CHANGED = auto()
    THEME_CHANGED = auto()
    UI_STATE_CHANGED = auto()
    UI_PAGE_CHANGED = auto()
    UI_RENDER_TIME = auto()
    
    # Progress Events
    PROGRESS_UPDATE = auto()
    
    # Logging Events
    LOG_ERROR = auto()
    LOG_INFO = auto()
    LOG_WARNING = auto()
    
    # Application Events
    APP_STARTING = auto()
    APP_READY = auto()
    APP_CLOSING = auto()
    
    # Automation Events
    AUTOMATION_STARTED = auto()
    AUTOMATION_STOPPED = auto()
    AUTOMATION_PAUSED = auto()
    AUTOMATION_RESUMED = auto()
    SCRIPT_EXECUTED = auto()
    
    # System Events
    REFRESH_REQUESTED = auto()
    CACHE_UPDATED = auto()
    SERVICE_STARTED = auto()
    SERVICE_STOPPED = auto()
    ERROR_OCCURRED = auto()
    
    # Worker Events
    WORKER_STARTED = auto()
    WORKER_FINISHED = auto()
    WORKER_PROGRESS = auto()
    WORKER_ERROR = auto()
    
    # File Events
    APK_INSTALLED = auto()
    PACKAGE_UNINSTALLED = auto()
    FILE_SELECTED = auto()
    
    # Component Events
    COMPONENT_LOADED = auto()
    COMPONENT_UNLOADED = auto()
    COMPONENT_ERROR = auto()
    
    # Status Events
    STATUS_UPDATE = auto()
    STATUS_CHANGED = auto()
    
    # Refresh Events
    INSTANCES_REFRESHED = auto()
    
    # Custom Events
    CUSTOM_EVENT = auto()