import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from optimizations.smart_cache import global_smart_cache

CONFIG_PATH = os.path.expanduser("~/.mumu_cache_config.json")


def migrate():
    """Ensure cache TTL and persistence settings are preserved."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        global_smart_cache.ttl_map.update(data.get('ttl_map', {}))
        global_smart_cache.persistent = data.get('persistent', global_smart_cache.persistent)
        print("Loaded existing cache configuration")
    else:
        data = {
            'ttl_map': global_smart_cache.ttl_map,
            'persistent': global_smart_cache.persistent,
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print("Saved default cache configuration")


if __name__ == "__main__":
    migrate()
