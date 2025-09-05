"""
Managers Package
================

Modular managers for different aspects of the MumuM application.
Extracted from the monolithic main_window.py to improve maintainability.
"""

from .instance_manager import InstanceManager
from .automation_manager import AutomationManager
from .ui_manager import UIManager
from core.event_manager import EventManager
from .sidebar_manager import SidebarManager
from .content_manager import ContentManager
from .status_bar_manager import StatusBarManager

__all__ = [
    'InstanceManager',
    'AutomationManager',
    'UIManager',
    'EventManager',
    'SidebarManager',
    'ContentManager',
    'StatusBarManager'
]