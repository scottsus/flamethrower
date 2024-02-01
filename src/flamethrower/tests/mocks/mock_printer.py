import sys
from unittest.mock import MagicMock
from flamethrower.shell.printer import Printer
from flamethrower.tests.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.tests.mocks.mock_shell_manager import mock_shell_manager
from flamethrower.tests.mocks.mock_token_counter import mock_token_counter

def mock_printer() -> Printer:
    return MagicMock(
        spec=Printer,
        leader_fd=sys.stdout.fileno(),
        stdout_fd=sys.stdout.fileno(),
        conv_manager=mock_conv_manager(),
        shell_manager=mock_shell_manager(),
        token_counter=mock_token_counter(),
    )
