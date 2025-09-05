"""
Services Package
================

Centralized service management for MumuM application.
This package provides unified access to all application services.
"""

from .service_manager import ServiceManager, get_service_manager

__all__ = ['ServiceManager', 'get_service_manager']