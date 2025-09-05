"""
Core Package
============

Core components for MumuM application architecture:
- EventManager: Centralized event handling
- StateManager: Centralized state management
- EventTypes: Event type definitions
"""

from .event_manager import EventManager, get_event_manager, emit_event, subscribe_event
from .state_manager import StateManager, get_state_manager
from .event_types import EventTypes

__all__ = [
    'EventManager', 'get_event_manager', 'emit_event', 'subscribe_event',
    'StateManager', 'get_state_manager',
    'EventTypes'
]