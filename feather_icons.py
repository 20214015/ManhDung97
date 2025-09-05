# feather_icons.py - Tiện ích để render icon bằng thư viện qtawesome (Sửa lỗi AttributeError)

import qtawesome as qta
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSettings # << THÊM DÒNG NÀY
from PyQt6.QtWidgets import QApplication
from typing import Dict, Optional

# Cache icons to improve performance
_icon_cache: Dict[str, QIcon] = {}

# Bảng màu đặc trưng của Monokai
MONOKAI_COLORS = {
    "foreground": "#F8F8F2",
    "green": "#A6E22E",
    "pink": "#F92672",
    "blue": "#66D9EF",
    "orange": "#FD971F",
    "purple": "#AE81FF"
}

# Ánh xạ tên icon sang màu sắc Monokai tương ứng
MONOKAI_COLOR_MAP = {
    "play": MONOKAI_COLORS["green"], "run": MONOKAI_COLORS["green"], "add": MONOKAI_COLORS["green"],
    "clone": MONOKAI_COLORS["green"], "save": MONOKAI_COLORS["green"],
    "stop": MONOKAI_COLORS["pink"], "delete": MONOKAI_COLORS["pink"], "cleanup": MONOKAI_COLORS["pink"],
    "restart": MONOKAI_COLORS["blue"], "refresh": MONOKAI_COLORS["blue"],
    "edit": MONOKAI_COLORS["orange"], "config": MONOKAI_COLORS["orange"],
    "settings": MONOKAI_COLORS["orange"], "theme": MONOKAI_COLORS["orange"],
    "automation": MONOKAI_COLORS["purple"], "script": MONOKAI_COLORS["purple"],
}

# Ánh xạ tên icon sang qtawesome (Font Awesome 5)
ICON_MAP = {
    "app_icon": "fa5s.database", "dashboard": "fa5s.home", "apps": "fa5s.th-large",
    "adb": "fa5s.code", "script": "fa5s.file-alt", "cleanup": "fa5s.trash-alt",
    "config": "fa5s.tools", "automation": "fa5s.bolt", "settings": "fa5s.cog",
    "theme": "fa5s.palette", "play": "fa5s.play", "stop": "fa5s.square",
    "restart": "fa5s.sync-alt", "add": "fa5s.plus-circle", "clone": "fa5s.clone",
    "delete": "fa5s.trash", "edit": "fa5s.pencil-alt", "refresh": "fa5s.sync",
    "folder": "fa5s.folder", "save": "fa5s.save", "run": "fa5s.play-circle",
    "pause": "fa5s.pause-circle",
}

def get_icon(name: str, color: str = None) -> QIcon:
    """
    Tạo một QIcon bằng qtawesome, tự động áp dụng màu Monokai nếu cần.
    Uses caching to improve performance.
    :param name: Tên của icon (ví dụ: 'play', 'settings').
    :param color: (Tùy chọn) Ghi đè màu mặc định.
    :return: Một đối tượng QIcon.
    """
    # Create cache key
    cache_key = f"{name}_{color or 'auto'}"
    
    # Return cached icon if available
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]
    
    icon_name = ICON_MAP.get(name, "fa5s.question-circle")
    final_color = color
    
    if final_color is None:
        try:
            # SỬA LỖI Ở ĐÂY: Tạo một instance QSettings mới để đọc cài đặt
            settings = QSettings()
            theme_name = settings.value("theme/name", "dark")
            
            if theme_name == "monokai":
                final_color = MONOKAI_COLOR_MAP.get(name, MONOKAI_COLORS["foreground"])
            else:
                # Safe palette access
                try:
                    final_color = QApplication.palette().color(QApplication.palette().ColorRole.WindowText).name()
                except Exception:
                    final_color = "#000000"  # Fallback to black
        except Exception as e:
            print(f"Warning: Settings access failed for icon '{name}': {e}")
            final_color = "#000000"  # Fallback to black

    try:
        icon = qta.icon(icon_name, color=final_color)
        # Cache the icon for future use
        _icon_cache[cache_key] = icon
        return icon
    except Exception as e:
        print(f"Lỗi khi tạo icon '{name}' (qta name: '{icon_name}'): {e}")
        # Create and cache a fallback empty icon
        fallback_icon = QIcon()
        _icon_cache[cache_key] = fallback_icon
        return fallback_icon

def clear_icon_cache():
    """Clear the icon cache to free memory"""
    global _icon_cache
    _icon_cache.clear()

def get_cache_stats() -> Dict[str, int]:
    """Get icon cache statistics"""
    return {
        'cached_icons': len(_icon_cache),
        'memory_estimate_kb': len(_icon_cache) * 4  # Rough estimate
    }