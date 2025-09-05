"""
EventManager - Centralized Event Handling
=========================================

Provides event-driven architecture to decouple components and improve maintainability.
"""

import logging
from typing import Dict, List, Callable, Any
from .event_types import EventTypes

try:
    from PyQt6.QtCore import QObject, pyqtSignal
    _QT_AVAILABLE = True
except ImportError:
    _QT_AVAILABLE = False
    class QObject:
        def __init__(self):
            pass


class EventManager:
    """
    Central event management system for the application.
    
    Provides event subscription and emission functionality to enable
    loose coupling between components.
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
        self.listeners: Dict[EventTypes, List[Callable]] = {}
        self.logger = logging.getLogger('EventManager')
        
    def subscribe(self, event_type: EventTypes, callback: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to an event type.
        
        Args:
            event_type: The event type to subscribe to
            callback: Function to call when event is emitted
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
            
        if callback not in self.listeners[event_type]:
            self.listeners[event_type].append(callback)
            self.logger.debug(f"Subscribed to {event_type.name}")
            
    def unsubscribe(self, event_type: EventTypes, callback: Callable[[Dict[str, Any]], None]):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: The event type to unsubscribe from
            callback: The callback function to remove
        """
        if event_type in self.listeners and callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)
            self.logger.debug(f"Unsubscribed from {event_type.name}")
            
    def emit(self, event_type: EventTypes, data: Dict[str, Any] = None):
        """
        Emit an event to all subscribers.
        
        Args:
            event_type: The event type to emit
            data: Optional data to pass to subscribers
        """
        if data is None:
            data = {}
            
        self.logger.debug(f"Emitting {event_type.name} with data: {data}")
        
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error in event callback for {event_type.name}: {e}")
                    
    def get_listeners(self, event_type: EventTypes) -> List[Callable]:
        """
        Get all listeners for an event type.
        
        Args:
            event_type: The event type
            
        Returns:
            List of callback functions
        """
        return self.listeners.get(event_type, [])
        
    def clear_listeners(self, event_type: EventTypes = None):
        """
        Clear listeners for an event type or all listeners.
        
        Args:
            event_type: Event type to clear. If None, clears all listeners.
        """
        if event_type is None:
            self.listeners.clear()
            self.logger.info("Cleared all event listeners")
        else:
            self.listeners[event_type] = []
            self.logger.info(f"Cleared listeners for {event_type.name}")


# Global event manager instance
_event_manager = None


def get_event_manager() -> EventManager:
    """
    Get the global EventManager instance.
    
    Returns:
        EventManager singleton instance
    """
    global _event_manager
    if _event_manager is None:
        _event_manager = EventManager()
    return _event_manager


def emit_event(event_type: EventTypes, data: Dict[str, Any] = None):
    """
    Convenience function to emit an event.
    
    Args:
        event_type: The event type to emit
        data: Optional data to pass to subscribers
    """
    get_event_manager().emit(event_type, data)


def subscribe_event(event_type: EventTypes, callback: Callable[[Dict[str, Any]], None]):
    """
    Convenience function to subscribe to an event.
    
    Args:
        event_type: The event type to subscribe to
        callback: Function to call when event is emitted
    """
    get_event_manager().subscribe(event_type, callback)