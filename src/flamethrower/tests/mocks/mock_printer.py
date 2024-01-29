import sys
import pytest
from unittest.mock import MagicMock

from flamethrower.shell.printer import Printer
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.shell.shell_manager import ShellManager
from flamethrower.utils.token_counter import TokenCounter

from flamethrower.tests.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.tests.mocks.mock_shell_manager import mock_shell_manager
from flamethrower.tests.mocks.mock_token_counter import mock_token_counter

@pytest.fixture
def mock_printer(
    mock_conv_manager: ConversationManager,
    mock_shell_manager: ShellManager,
    mock_token_counter: TokenCounter
) -> Printer:
    return MagicMock(
        Printer,
        leader_fd=sys.stdout.fileno(),
        stdout_fd=sys.stdout.fileno(),
        conv_manager=mock_conv_manager,
        shell_manager=mock_shell_manager,
        token_counter=mock_token_counter,
    )