from unittest.mock import MagicMock
from flamethrower.shell.shell_manager import ShellManager
from flamethrower.tests.utils.dummy_context_manager import DummyContextManager

def mock_shell_manager() -> ShellManager:
    return MagicMock(spec=ShellManager)
