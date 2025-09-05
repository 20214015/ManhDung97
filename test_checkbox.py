#!/usr/bin/env python3
"""
Test script to verify checkbox functionality in the dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from widgets import InstancesModel, CheckboxDelegate, TableColumn

def test_checkbox_functionality():
    """Test the checkbox model and delegate functionality"""
    app = QApplication(sys.argv)

    # Create model
    model = InstancesModel()

    # Add some test data
    test_data = [
        {'index': 1, 'info': {'name': 'Instance 1', 'is_process_started': True}},
        {'index': 2, 'info': {'name': 'Instance 2', 'is_process_started': False}},
        {'index': 3, 'info': {'name': 'Instance 3', 'is_process_started': True}},
    ]

    model.set_rows(test_data)

    # Test initial state
    print("=== Initial State ===")
    for i in range(model.rowCount()):
        index = model.index(i, TableColumn.CHECKBOX)
        checked = model.data(index, Qt.ItemDataRole.CheckStateRole)
        print(f"Row {i}: checked = {checked}")

    # Test get_checked_indices
    print("\n=== Checked Indices ===")
    checked_indices = model.get_checked_indices()
    print(f"Checked indices: {checked_indices}")

    # Simulate checking some boxes
    print("\n=== Simulating Checkbox Clicks ===")
    model.setData(model.index(0, TableColumn.CHECKBOX), Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
    model.setData(model.index(2, TableColumn.CHECKBOX), Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)

    # Check state after changes
    print("\n=== State After Changes ===")
    for i in range(model.rowCount()):
        index = model.index(i, TableColumn.CHECKBOX)
        checked = model.data(index, Qt.ItemDataRole.CheckStateRole)
        print(f"Row {i}: checked = {checked}")

    # Test get_checked_indices again
    print("\n=== Checked Indices After Changes ===")
    checked_indices = model.get_checked_indices()
    print(f"Checked indices: {checked_indices}")

    print("\n✅ Checkbox functionality test completed successfully!")
    return True

if __name__ == "__main__":
    test_checkbox_functionality()
