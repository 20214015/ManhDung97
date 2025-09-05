#!/usr/bin/env python3
"""
Simple Cache Test
"""

from PyQt6.QtWidgets import QApplication
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize QApplication
app = QApplication(sys.argv)

# Import and test
import backend
m = backend.MumuManager('dummy.exe')
print('Has refresh_cache:', hasattr(m, 'refresh_cache'))

if hasattr(m, 'refresh_cache'):
    print('Method found!')
    try:
        result = m.refresh_cache()
        print('Refresh result:', result)
    except Exception as e:
        print('Error calling refresh_cache:', e)
        import traceback
        traceback.print_exc()
else:
    print('Method NOT found!')
    print('Available methods:', [method for method in dir(m) if 'cache' in method.lower()])
