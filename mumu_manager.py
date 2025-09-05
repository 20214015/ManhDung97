"""
MuMu Manager Module
Provides global access to MuMu manager instance and utility functions.
"""

from backend import MumuManager

# Global MuMu manager instance
mumu_manager = None

def get_mumu_instances_fast():
    """
    Get list of MuMu instances quickly.
    Returns dict with instances data if manager available, empty dict otherwise.
    """
    if mumu_manager:
        try:
            success, data = mumu_manager.get_all_info()
            if success:
                if isinstance(data, dict):
                    instances_list = list(data.values())
                    return {
                        'total_instances': len(instances_list),
                        'running_instances': sum(1 for inst in instances_list if inst.get('is_running', False)),
                        'instances': instances_list,
                        'error': None
                    }
                elif isinstance(data, list):
                    return {
                        'total_instances': len(data),
                        'running_instances': sum(1 for inst in data if inst.get('is_running', False)),
                        'instances': data,
                        'error': None
                    }
                else:
                    return {
                        'total_instances': 0,
                        'running_instances': 0,
                        'instances': [],
                        'error': 'Invalid data format'
                    }
            else:
                return {
                    'total_instances': 0,
                    'running_instances': 0,
                    'instances': [],
                    'error': str(data) if data else 'Unknown error'
                }
        except Exception as e:
            return {
                'total_instances': 0,
                'running_instances': 0,
                'instances': [],
                'error': str(e)
            }
    return {
        'total_instances': 0,
        'running_instances': 0,
        'instances': [],
        'error': 'MuMu Manager not available'
    }

def check_mumu_available():
    """
    Check if MuMu is available.
    Returns True if manager is available.
    """
    return mumu_manager is not None

def set_global_mumu_manager(manager):
    """
    Set the global MuMu manager instance.
    """
    global mumu_manager
    mumu_manager = manager
