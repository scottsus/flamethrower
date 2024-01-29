import pytest

from flamethrower.shell.command_handler import CommandHandler
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.context.prompt import PromptGenerator
from flamethrower.agents.operator import Operator
from flamethrower.shell.printer import Printer

from flamethrower.tests.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.tests.mocks.mock_prompt_generator import mock_prompt_generator
from flamethrower.tests.mocks.mock_operator import mock_operator
from flamethrower.tests.mocks.mock_printer import mock_printer
from flamethrower.tests.mocks.mock_shell_manager import mock_shell_manager
from flamethrower.tests.mocks.mock_token_counter import mock_token_counter

@pytest.fixture
def mock_command_handler(
    mock_conv_manager: ConversationManager,
    mock_prompt_generator: PromptGenerator,
    mock_operator: Operator,
    mock_printer: Printer,
) -> CommandHandler:
    return CommandHandler(
        conv_manager=mock_conv_manager,
        prompt_generator=mock_prompt_generator,
        operator=mock_operator,
        printer=mock_printer,
    )

def test_command_handler_init(mock_command_handler: CommandHandler):
    command_handler = mock_command_handler

    assert command_handler.pos == 0
    assert command_handler.buffer == ''
    assert command_handler.is_nl_query == False
    assert isinstance(command_handler.conv_manager, ConversationManager)
    assert isinstance(command_handler.prompt_generator, PromptGenerator)
    assert isinstance(command_handler.operator, Operator)
    assert isinstance(command_handler.printer, Printer)

"""
TODO: other tests
"""