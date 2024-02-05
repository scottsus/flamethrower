import pytest

from flamethrower.shell.command_handler import CommandHandler
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.agents.operator import Operator
from flamethrower.shell.printer import Printer

from flamethrower.test_utils.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.test_utils.mocks.mock_operator import mock_operator
from flamethrower.test_utils.mocks.mock_printer import mock_printer

@pytest.fixture
def mock_command_handler() -> CommandHandler:
    return CommandHandler(
        conv_manager=mock_conv_manager(),
        operator=mock_operator(),
        printer=mock_printer(),
    )

def test_command_handler_init(mock_command_handler: CommandHandler) -> None:
    command_handler = mock_command_handler

    assert command_handler.pos == 0
    assert command_handler.buffer == ''
    assert command_handler.is_nl_query == False
    assert isinstance(command_handler.conv_manager, ConversationManager)
    assert isinstance(command_handler.operator, Operator)
    assert isinstance(command_handler.printer, Printer)

"""
TODO: other tests
"""