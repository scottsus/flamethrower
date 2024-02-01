from unittest.mock import MagicMock
from flamethrower.shell.shell_manager import ShellManager

def mock_shell_manager() -> ShellManager:
    return MagicMock(spec=ShellManager)
