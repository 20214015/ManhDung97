# constants.py - Các hằng số và enum dùng trong toàn bộ ứng dụng

from enum import IntEnum

APP_NAME = "MumuManager"
APP_VERSION = "Pro"
ORG_NAME = "MumuMasters"
ORG_DOMAIN = "mumumasters.dev"

class Action:
    """Định nghĩa các hằng số cho hành động điều khiển MuMuManager."""
    LAUNCH = 'launch'
    SHUTDOWN = 'shutdown'
    RESTART = 'restart'
    SHOW = 'show_window'
    HIDE = 'hide_window'

class TableColumn(IntEnum):
    """Định nghĩa chỉ số các cột cho bảng máy ảo chính."""
    CHECKBOX = 0
    STT = 1         # Index column - hiển thị VM index thay vì số thứ tự
    NAME = 2        # Name column - hiển thị tên VM
    STATUS = 3
    ADB = 4
    DISK_USAGE = 5
    SPACER = 6      # Cột trống để căn chỉnh
