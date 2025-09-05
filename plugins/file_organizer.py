"""
Example Plugin: File Organizer
==============================

A demonstration automation plugin that provides file organization
actions for MuMuManager Pro.
"""

import shutil
from typing import Dict, Any, List
from pathlib import Path

from core.plugin_system import AutomationPlugin

class FileOrganizerPlugin(AutomationPlugin):
    """File organization automation plugin for MuMuManager Pro"""

    def __init__(self):
        self.main_window = None

    @property
    def name(self) -> str:
        return "File Organizer"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Automated file organization and cleanup actions"

    def initialize(self, main_window: Any) -> bool:
        """Initialize the file organizer plugin"""
        try:
            self.main_window = main_window
            print("✅ File Organizer plugin initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize File Organizer plugin: {e}")
            return False

    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        print("🧹 File Organizer plugin cleaned up")

    def get_automation_actions(self) -> List[Dict[str, Any]]:
        """Return list of automation actions provided by this plugin"""
        return [
            {
                "id": "organize_by_extension",
                "name": "Organize Files by Extension",
                "description": "Move files into folders based on their extensions",
                "parameters": {
                    "source_dir": {"type": "string", "description": "Source directory path"},
                    "target_dir": {"type": "string", "description": "Target directory path"},
                    "create_folders": {"type": "boolean", "default": True, "description": "Create extension folders"}
                }
            },
            {
                "id": "cleanup_temp_files",
                "name": "Clean Temporary Files",
                "description": "Remove temporary files and empty directories",
                "parameters": {
                    "target_dir": {"type": "string", "description": "Directory to clean"},
                    "patterns": {"type": "list", "default": ["*.tmp", "*.temp", "*.log"], "description": "File patterns to remove"}
                }
            },
            {
                "id": "organize_by_date",
                "name": "Organize Files by Date",
                "description": "Move files into folders based on creation/modification date",
                "parameters": {
                    "source_dir": {"type": "string", "description": "Source directory path"},
                    "target_dir": {"type": "string", "description": "Target directory path"},
                    "date_format": {"type": "string", "default": "%Y-%m", "description": "Date format for folders"}
                }
            }
        ]

    def execute_action(self, action_id: str, parameters: Dict[str, Any]) -> bool:
        """Execute a specific automation action"""
        try:
            if action_id == "organize_by_extension":
                return self._organize_by_extension(
                    parameters.get("source_dir", ""),
                    parameters.get("target_dir", ""),
                    parameters.get("create_folders", True)
                )
            elif action_id == "cleanup_temp_files":
                return self._cleanup_temp_files(
                    parameters.get("target_dir", ""),
                    parameters.get("patterns", ["*.tmp", "*.temp", "*.log"])
                )
            elif action_id == "organize_by_date":
                return self._organize_by_date(
                    parameters.get("source_dir", ""),
                    parameters.get("target_dir", ""),
                    parameters.get("date_format", "%Y-%m")
                )
            else:
                print(f"Unknown action: {action_id}")
                return False

        except Exception as e:
            print(f"Error executing action {action_id}: {e}")
            return False

    def _organize_by_extension(self, source_dir: str, target_dir: str, create_folders: bool) -> bool:
        """Organize files by their extensions"""
        try:
            source_path = Path(source_dir)
            target_path = Path(target_dir)

            if not source_path.exists():
                print(f"Source directory does not exist: {source_dir}")
                return False

            target_path.mkdir(parents=True, exist_ok=True)

            organized_count = 0
            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    extension = file_path.suffix.lower()
                    if extension:
                        ext_dir = target_path / extension[1:]  # Remove the dot
                        if create_folders:
                            ext_dir.mkdir(exist_ok=True)

                        new_path = ext_dir / file_path.name
                        shutil.move(str(file_path), str(new_path))
                        organized_count += 1

            print(f"✅ Organized {organized_count} files by extension")
            return True

        except Exception as e:
            print(f"Error organizing files by extension: {e}")
            return False

    def _cleanup_temp_files(self, target_dir: str, patterns: List[str]) -> bool:
        """Clean up temporary files"""
        try:
            target_path = Path(target_dir)

            if not target_path.exists():
                print(f"Target directory does not exist: {target_dir}")
                return False

            removed_count = 0
            for pattern in patterns:
                for file_path in target_path.rglob(pattern):
                    if file_path.is_file():
                        file_path.unlink()
                        removed_count += 1

            # Remove empty directories
            empty_dirs_count = 0
            for dir_path in target_path.rglob("*"):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    empty_dirs_count += 1

            print(f"✅ Removed {removed_count} temp files and {empty_dirs_count} empty directories")
            return True

        except Exception as e:
            print(f"Error cleaning temp files: {e}")
            return False

    def _organize_by_date(self, source_dir: str, target_dir: str, date_format: str) -> bool:
        """Organize files by their modification date"""
        try:
            import datetime

            source_path = Path(source_dir)
            target_path = Path(target_dir)

            if not source_path.exists():
                print(f"Source directory does not exist: {source_dir}")
                return False

            target_path.mkdir(parents=True, exist_ok=True)

            organized_count = 0
            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    mtime = file_path.stat().st_mtime
                    date_str = datetime.datetime.fromtimestamp(mtime).strftime(date_format)

                    date_dir = target_path / date_str
                    date_dir.mkdir(exist_ok=True)

                    new_path = date_dir / file_path.name
                    shutil.move(str(file_path), str(new_path))
                    organized_count += 1

            print(f"✅ Organized {organized_count} files by date")
            return True

        except Exception as e:
            print(f"Error organizing files by date: {e}")
            return False
