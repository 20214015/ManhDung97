"""
CLI Layer - QProcess-based Command Wrapper
==========================================

Replaces subprocess calls with QProcess for non-blocking UI operations.
Implements CommandBus pattern for timeout/retry/logging control.
"""

import os
import time
import heapq
from typing import List, Tuple, Any, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtCore import QObject, QProcess, QTimer, pyqtSignal, QThread
from PyQt6.QtWidgets import QApplication


class CommandPriority(Enum):
    """Command execution priority levels"""
    CRITICAL = 0  # Stop operations
    HIGH = 1      # Start operations
    NORMAL = 2    # Info/list operations
    LOW = 3       # Install/batch operations


@dataclass
class CommandResult:
    """Result from command execution"""
    success: bool
    output: str = ""
    error: str = ""
    return_code: int = 0
    execution_time: float = 0.0


class QProcessCommand(QObject):
    """QProcess-based command executor with signals"""

    finished = pyqtSignal(CommandResult)
    progress = pyqtSignal(str)  # Progress updates

    def __init__(self, executable_path: str, args: List[str],
                 timeout: int = 30, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.executable_path = executable_path
        self.args = args
        self.timeout = timeout
        self.process = None
        self.timer = None
        self.start_time = 0

    def execute(self):
        """Execute command with QProcess"""
        if not os.path.isfile(self.executable_path):
            result = CommandResult(
                success=False,
                error=f"Executable not found: {self.executable_path}"
            )
            self.finished.emit(result)
            return

        self.process = QProcess(self)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)

        # Setup timeout timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timeout)
        self.timer.setSingleShot(True)
        self.timer.start(self.timeout * 1000)

        # Start process
        self.start_time = time.time()
        self.process.start(self.executable_path, self.args)

    def _on_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        """Handle process completion"""
        if self.timer and self.timer.isActive():
            self.timer.stop()

        execution_time = time.time() - self.start_time

        stdout = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        stderr = self.process.readAllStandardError().data().decode('utf-8', errors='replace')

        # Combine output intelligently
        output_parts = []
        if stdout.strip():
            output_parts.append(stdout.strip())
        if stderr.strip():
            output_parts.append(stderr.strip())

        result = CommandResult(
            success=(exit_code == 0),
            output="\n".join(output_parts) if output_parts else "",
            error=stderr.strip() if exit_code != 0 else "",
            return_code=exit_code,
            execution_time=execution_time
        )

        self.finished.emit(result)

    def _on_error(self, error: QProcess.ProcessError):
        """Handle process errors"""
        if self.timer and self.timer.isActive():
            self.timer.stop()

        execution_time = time.time() - self.start_time

        error_messages = {
            QProcess.ProcessError.FailedToStart: "Failed to start process",
            QProcess.ProcessError.Crashed: "Process crashed",
            QProcess.ProcessError.Timedout: "Process timed out",
            QProcess.ProcessError.WriteError: "Write error",
            QProcess.ProcessError.ReadError: "Read error",
            QProcess.ProcessError.UnknownError: "Unknown error"
        }

        result = CommandResult(
            success=False,
            error=error_messages.get(error, f"Process error: {error}"),
            execution_time=execution_time
        )

        self.finished.emit(result)

    def _on_timeout(self):
        """Handle command timeout"""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()

        execution_time = time.time() - self.start_time

        result = CommandResult(
            success=False,
            error=f"Command timed out after {self.timeout} seconds",
            execution_time=execution_time
        )

        self.finished.emit(result)

    def __del__(self):
        """Ensure proper cleanup of QProcess"""
        if hasattr(self, 'process') and self.process is not None:
            if self.process.state() == QProcess.ProcessState.Running:
                self.process.kill()
                self.process.waitForFinished(1000)  # Wait up to 1 second
            self.process.deleteLater()

        if hasattr(self, 'timer') and self.timer is not None:
            if self.timer.isActive():
                self.timer.stop()
            self.timer.deleteLater()


class CommandBus(QObject):
    """Central command bus for controlling timeout/retry/logging"""

    command_started = pyqtSignal(str, list)  # command, args
    command_finished = pyqtSignal(str, CommandResult)
    queue_updated = pyqtSignal(int)  # queue length

    def __init__(self, max_concurrent: int = 6, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.max_concurrent = max_concurrent
        self.active_commands: Dict[str, QProcessCommand] = {}
        # priority queue implemented as a heap
        self.command_queue: List[Tuple[int, str, Callable[[], None]]] = []
        self.command_history: List[Tuple[str, CommandResult]] = []

    def execute_command(self, executable_path: str, args: List[str],
                       priority: CommandPriority = CommandPriority.NORMAL,
                       timeout: int = 30, callback: Optional[Callable[[CommandResult], None]] = None) -> str:
        """Queue command for execution"""
        command_id = f"cmd_{len(self.command_history) + len(self.active_commands)}"

        def execute_func():
            # Don't set parent to avoid threading issues
            command = QProcessCommand(executable_path, args, timeout, None)
            command.finished.connect(
                lambda result: self._on_command_finished(command_id, result, callback)
            )
            self.active_commands[command_id] = command
            self.command_started.emit(executable_path, args)
            command.execute()

        # Add to priority queue using heap for efficiency
        heapq.heappush(self.command_queue, (priority.value, command_id, execute_func))

        self._process_queue()
        self.queue_updated.emit(len(self.command_queue))

        return command_id

    def _process_queue(self):
        """Process next command in queue if capacity available"""
        if (len(self.active_commands) < self.max_concurrent and
            self.command_queue):

            priority, command_id, execute_func = heapq.heappop(self.command_queue)
            execute_func()

    def _on_command_finished(self, command_id: str, result: CommandResult,
                           callback: Optional[Callable[[CommandResult], None]]):
        """Handle command completion"""
        if command_id in self.active_commands:
            del self.active_commands[command_id]

        self.command_history.append((command_id, result))
        self.command_finished.emit(command_id, result)

        if callback:
            callback(result)

        # Process next queued command
        self._process_queue()
        self.queue_updated.emit(len(self.command_queue))

    def get_active_count(self) -> int:
        """Get number of active commands"""
        return len(self.active_commands)

    def get_queue_length(self) -> int:
        """Get queue length"""
        return len(self.command_queue)


# Global command bus instance
_global_command_bus = None

def get_command_bus() -> CommandBus:
    """Get global command bus instance"""
    global _global_command_bus
    if _global_command_bus is None:
        _global_command_bus = CommandBus()
    return _global_command_bus