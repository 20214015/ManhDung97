import threading
import sys
import types
import importlib.util
from pathlib import Path

# Stub minimal PyQt6 modules for testing
qtcore = types.ModuleType("PyQt6.QtCore")

class QObject:
    pass

class _Signal:
    def emit(self, *args, **kwargs):
        pass

def pyqtSignal(*args, **kwargs):
    return _Signal()

qtcore.QObject = QObject
qtcore.pyqtSignal = pyqtSignal

pyqt6 = types.ModuleType("PyQt6")
pyqt6.QtCore = qtcore
sys.modules["PyQt6"] = pyqt6
sys.modules["PyQt6.QtCore"] = qtcore

# Dynamically import SmartCache without triggering package imports
spec = importlib.util.spec_from_file_location(
    "smart_cache_module", Path(__file__).resolve().parent / "optimizations" / "smart_cache.py"
)
smart_cache = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smart_cache)
SmartCache = smart_cache.SmartCache


def test_thread_safe_operations():
    cache = SmartCache(max_size_mb=1)
    exceptions = []

    def worker(thread_id):
        try:
            for i in range(50):
                key = f"key_{i % 10}"
                cache.set(key, thread_id)
                cache.get(key)
        except Exception as e:
            exceptions.append(e)

    def invalidator():
        try:
            for _ in range(20):
                cache.invalidate_pattern("key")
        except Exception as e:
            exceptions.append(e)

    def cleaner():
        try:
            for _ in range(20):
                cache.cleanup_expired()
        except Exception as e:
            exceptions.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    threads.append(threading.Thread(target=invalidator))
    threads.append(threading.Thread(target=cleaner))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not exceptions
