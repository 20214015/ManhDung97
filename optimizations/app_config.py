# app_config.py - Centralized configuration và constants

from dataclasses import dataclass
from typing import Dict, Any
import os

@dataclass(frozen=True)
class AppConstants:
    """Centralized constants cho toàn bộ ứng dụng"""
    
    # Application Info
    APP_NAME = "MumuManager"
    APP_VERSION = "Pro"
    ORG_NAME = "MumuMasters"
    ORG_DOMAIN = "mumumasters.dev"
    
    # Performance Settings
    class Performance:
        DEFAULT_COMMAND_TIMEOUT = 30
        UI_REFRESH_INTERVAL = 100  # Will be optimized by adaptive config
        AUTO_REFRESH_INTERVAL = 30  # Will be optimized by adaptive config
        WORKER_CHECK_INTERVAL = 50  # Will be optimized by adaptive config
        TABLE_UPDATE_BATCH_SIZE = 50  # Will be optimized by adaptive config
        CACHE_TTL_SECONDS = 30  # Will be optimized by adaptive config
        MAX_CONCURRENT_WORKERS = 4  # Will be optimized by adaptive config
        
        # New adaptive performance settings
        MEMORY_CLEANUP_THRESHOLD = 0.8  # Trigger cleanup at 80% usage
        ADAPTIVE_SCALING_ENABLED = True
        PERFORMANCE_MONITORING_INTERVAL = 5000  # 5 seconds
        LOAD_BALANCING_ENABLED = True
        
    # UI Configuration
    class UI:
        WINDOW_MIN_WIDTH = 1200
        WINDOW_MIN_HEIGHT = 800
        WINDOW_DEFAULT_WIDTH = 1600
        WINDOW_DEFAULT_HEIGHT = 900
        
        # Table settings
        TABLE_REFRESH_INTERVAL = 200
        TABLE_ROW_HEIGHT = 40
        TABLE_HEADER_HEIGHT = 35
        
        # Progress and loading
        PROGRESS_UPDATE_INTERVAL = 100
        STARTUP_DELAY_MS = 50
        
    # Business Logic Limits
    class Limits:
        MAX_INSTANCES_CREATE = 50
        MAX_INSTANCES_CLONE = 20
        MAX_NAME_LENGTH = 100
        MAX_SELECTED_INSTANCES = 100
        MAX_BATCH_SIZE = 20
        MIN_BATCH_DELAY = 100  # ms
        MAX_BATCH_DELAY = 5000  # ms
        
        # Adaptive limits based on system performance
        DYNAMIC_BATCH_SIZING = True
        MAX_MEMORY_USAGE_MB = 1024  # 1GB limit for instance operations
        CONNECTION_POOL_SIZE = 10  # Maximum concurrent connections
        
    # File and Path Settings
    class Paths:
        ASSETS_DIR = "assets"
        FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
        CONFIG_DIR = "config"
        LOGS_DIR = "logs"
        TEMP_DIR = "temp"
        
        # Required fonts
        REQUIRED_FONTS = [
            "Inter-Regular.ttf",
            "Inter-Bold.ttf", 
            "JetBrainsMono-Regular.ttf",
            "JetBrainsMono-Bold.ttf"
        ]
        
    # Logging Configuration
    class Logging:
        MAX_LOG_ENTRIES = 5000  # Will be optimized by adaptive config
        LOG_CLEANUP_THRESHOLD = 20  # percent
        AUTO_CLEANUP_ENABLED = True
        DEFAULT_LOG_LEVEL = "INFO"
        
        # Export settings
        EXPORT_INCLUDE_METADATA = True
        EXPORT_AUTO_TIMESTAMP = True
        
        # Performance optimizations
        BATCH_LOG_WRITES = True
        LOG_COMPRESSION_ENABLED = True
        ASYNC_LOG_PROCESSING = True
        
    # Theme và Colors
    class Theme:
        DEFAULT_THEME = "dark"
        AVAILABLE_THEMES = ["light", "dark", "auto"]
        
        # Status colors
        STATUS_COLORS = {
            "running": "#28a745",    # Green
            "offline": "#631119",    # Dark red
            "starting": "#3498db",   # Blue
            "stopping": "#f39c12",   # Orange
            "restarting": "#8e44ad", # Purple
            "error": "#dc3545"       # Red
        }

class AppConfig:
    """Runtime configuration manager"""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._load_defaults()
        
    def _load_defaults(self):
        """Load default configuration values"""
        self._config = {
            "performance": {
                "enable_caching": True,
                "enable_async_operations": True,
                "worker_pool_size": AppConstants.Performance.MAX_CONCURRENT_WORKERS,
                "cache_ttl": AppConstants.Performance.CACHE_TTL_SECONDS
            },
            "ui": {
                "auto_refresh_enabled": True,
                "auto_refresh_interval": AppConstants.Performance.AUTO_REFRESH_INTERVAL,
                "theme": AppConstants.Theme.DEFAULT_THEME,
                "table_virtual_mode": False  # Enable for large datasets
            },
            "logging": {
                "level": AppConstants.Logging.DEFAULT_LOG_LEVEL,
                "max_entries": AppConstants.Logging.MAX_LOG_ENTRIES,
                "auto_cleanup": AppConstants.Logging.AUTO_CLEANUP_ENABLED
            }
        }
    
    def get(self, key: str, default=None):
        """Get configuration value using dot notation với validation"""
        try:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
        except Exception:
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation với validation"""
        try:
            keys = key.split('.')
            if not keys or not all(k.strip() for k in keys):
                return False
                
            config = self._config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                elif not isinstance(config[k], dict):
                    config[k] = {}  # Convert to dict if needed
                config = config[k]
                
            config[keys[-1]] = value
            return True
        except Exception:
            return False
    
    def validate_config(self) -> bool:
        """Validate configuration values"""
        try:
            # Validate performance settings
            worker_pool_size = self.get("performance.worker_pool_size", 4)
            if not isinstance(worker_pool_size, int) or worker_pool_size < 1 or worker_pool_size > 16:
                self.set("performance.worker_pool_size", 4)
                
            cache_ttl = self.get("performance.cache_ttl", 30)
            if not isinstance(cache_ttl, (int, float)) or cache_ttl < 1:
                self.set("performance.cache_ttl", 30)
                
            # Validate UI settings
            refresh_interval = self.get("ui.auto_refresh_interval", 30)
            if not isinstance(refresh_interval, int) or refresh_interval < 5:
                self.set("ui.auto_refresh_interval", 30)
                
            return True
        except Exception:
            return False
    
    def update_from_qsettings(self, qsettings):
        """Update configuration from QSettings với error handling"""
        try:
            # Performance settings với validation
            enable_caching = qsettings.value("performance/enable_caching", True, type=bool)
            self.set("performance.enable_caching", enable_caching)
            
            auto_refresh_enabled = qsettings.value("auto_refresh/enabled", True, type=bool)
            self.set("ui.auto_refresh_enabled", auto_refresh_enabled)
            
            auto_refresh_interval = qsettings.value("auto_refresh/interval", 30, type=int)
            # Validate interval range
            if auto_refresh_interval < 5:
                auto_refresh_interval = 30
            elif auto_refresh_interval > 300:
                auto_refresh_interval = 300
            self.set("ui.auto_refresh_interval", auto_refresh_interval)
            
            # UI settings với validation
            theme = qsettings.value("theme/name", AppConstants.Theme.DEFAULT_THEME, type=str)
            if theme not in AppConstants.Theme.AVAILABLE_THEMES:
                theme = AppConstants.Theme.DEFAULT_THEME
            self.set("ui.theme", theme)
            
            # Worker pool size với validation
            worker_pool_size = qsettings.value("performance/worker_pool_size", 4, type=int)
            if worker_pool_size < 1:
                worker_pool_size = 1
            elif worker_pool_size > 16:
                worker_pool_size = 16
            self.set("performance.worker_pool_size", worker_pool_size)
            
            # Validate configuration after loading
            self.validate_config()
            
        except Exception as e:
            print(f"Warning: Failed to load some settings: {e}")
            # Ensure we have valid defaults
            self._load_defaults()
            self.validate_config()
    
    def save_to_qsettings(self, qsettings):
        """Save configuration to QSettings"""
        try:
            qsettings.setValue("performance/enable_caching", self.get("performance.enable_caching"))
            qsettings.setValue("auto_refresh/enabled", self.get("ui.auto_refresh_enabled"))
            qsettings.setValue("auto_refresh/interval", self.get("ui.auto_refresh_interval"))
            qsettings.setValue("theme/name", self.get("ui.theme"))
            qsettings.setValue("performance/worker_pool_size", self.get("performance.worker_pool_size"))
        except Exception as e:
            print(f"Warning: Failed to save some settings: {e}")
    
    def clear_config(self):
        """Clear configuration cache"""
        self._config.clear()
        self._load_defaults()

# Global config instance
app_config = AppConfig()

# Convenience functions
def get_constant(path: str, default=None):
    """Get constant value using dot notation (e.g., 'UI.WINDOW_MIN_WIDTH')"""
    try:
        parts = path.split('.')
        value = AppConstants
        for part in parts:
            value = getattr(value, part)
        return value
    except AttributeError:
        return default

def get_config(key: str, default=None):
    """Get runtime config value"""
    return app_config.get(key, default)

def set_config(key: str, value):
    """Set runtime config value"""
    app_config.set(key, value)
