"""
Example Plugin: Quick Notes
===========================

A demonstration UI plugin that adds a quick notes widget
to MuMuManager Pro.
"""

import json
from typing import Dict, Any, List, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QGroupBox, QListWidget,
    QListWidgetItem, QInputDialog, QMessageBox
)

from core.plugin_system import UIPlugin

class QuickNotesPlugin(UIPlugin):
    """Quick notes UI plugin for MuMuManager Pro"""

    def __init__(self):
        self.main_window: Optional[Any] = None
        self.notes_widget: Optional[QGroupBox] = None
        self.notes_list: Optional[QListWidget] = None
        self.notes_text: Optional[QTextEdit] = None
        self.notes_data: Dict[str, Dict[str, str]] = {}  # Store notes in memory

    @property
    def name(self) -> str:
        return "Quick Notes"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Quick notes widget for jotting down ideas and reminders"

    def initialize(self, main_window: Any) -> bool:
        """Initialize the quick notes plugin"""
        try:
            self.main_window = main_window

            # Create notes widget
            self._create_notes_widget()

            # Add to main window
            if hasattr(main_window, 'add_dock_widget'):
                main_window.add_dock_widget(
                    self.notes_widget,
                    "Quick Notes",
                    "right"
                )

            print("✅ Quick Notes plugin initialized")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize Quick Notes plugin: {e}")
            return False

    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        if self.notes_widget and self.main_window:
            if hasattr(self.main_window, 'remove_dock_widget'):
                self.main_window.remove_dock_widget(self.notes_widget)

        print("🧹 Quick Notes plugin cleaned up")

    def get_ui_components(self) -> List[Dict[str, Any]]:
        """Return list of UI components provided by this plugin"""
        return [
            {
                "id": "quick_notes_widget",
                "name": "Quick Notes Widget",
                "description": "A widget for quick note-taking",
                "type": "dock_widget"
            }
        ]

    def create_component(self, component_id: str, parent: Any) -> Optional[Any]:
        """Create a UI component instance"""
        if component_id == "quick_notes_widget":
            return self._create_notes_widget()
        return None

    def _create_notes_widget(self) -> QWidget:
        """Create the notes widget"""
        if self.notes_widget is None:
            self.notes_widget = QGroupBox("Quick Notes")
            layout = QVBoxLayout(self.notes_widget)

            # Notes list
            notes_label = QLabel("Notes:")
            self.notes_list = QListWidget()
            if self.notes_list is not None:
                self.notes_list.itemClicked.connect(self._on_note_selected)

            # Buttons
            buttons_layout = QHBoxLayout()
            add_btn = QPushButton("Add Note")
            add_btn.clicked.connect(self._add_note)
            delete_btn = QPushButton("Delete Note")
            delete_btn.clicked.connect(self._delete_note)

            buttons_layout.addWidget(add_btn)
            buttons_layout.addWidget(delete_btn)

            # Notes text area
            text_label = QLabel("Note Content:")
            self.notes_text = QTextEdit()
            self.notes_text.textChanged.connect(self._on_text_changed)

            layout.addWidget(notes_label)
            layout.addWidget(self.notes_list)
            layout.addLayout(buttons_layout)
            layout.addWidget(text_label)
            layout.addWidget(self.notes_text)

            # Set fixed size
            self.notes_widget.setFixedWidth(350)
            self.notes_widget.setFixedHeight(400)

        return self.notes_widget

    def _add_note(self) -> None:
        """Add a new note"""
        title, ok = QInputDialog.getText(
            self.notes_widget, "New Note", "Enter note title:"
        )

        if ok and title.strip():
            note_id = f"note_{len(self.notes_data)}"
            self.notes_data[note_id] = {
                "title": title.strip(),
                "content": ""
            }

            # Add to list
            item = QListWidgetItem(title.strip())
            item.setData(Qt.ItemDataRole.UserRole, note_id)
            self.notes_list.addItem(item)

            print(f"✅ Added note: {title}")

    def _delete_note(self) -> None:
        """Delete the selected note"""
        current_item = self.notes_list.currentItem()
        if current_item is None:
            QMessageBox.warning(
                self.notes_widget, "No Selection",
                "Please select a note to delete."
            )
            return

        note_id = current_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self.notes_widget, "Delete Note",
            f"Are you sure you want to delete '{current_item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from data
            if note_id in self.notes_data:
                del self.notes_data[note_id]

            # Remove from list
            row = self.notes_list.row(current_item)
            self.notes_list.takeItem(row)

            # Clear text area
            self.notes_text.clear()

            print(f"🗑️ Deleted note: {current_item.text()}")

    def _on_note_selected(self, item: QListWidgetItem) -> None:
        """Handle note selection"""
        note_id = item.data(Qt.ItemDataRole.UserRole)
        if note_id in self.notes_data:
            content = self.notes_data[note_id]["content"]
            self.notes_text.setText(content)

    def _on_text_changed(self) -> None:
        """Handle text changes"""
        current_item = self.notes_list.currentItem()
        if current_item is not None:
            note_id = current_item.data(Qt.ItemDataRole.UserRole)
            if note_id in self.notes_data:
                self.notes_data[note_id]["content"] = self.notes_text.toPlainText()
