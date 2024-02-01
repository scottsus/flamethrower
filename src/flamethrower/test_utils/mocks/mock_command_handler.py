import pytest
from unittest.mock import MagicMock
from flamethrower.shell.command_handler import CommandHandler
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.context.prompt import PromptGenerator
from flamethrower.agents.operator import Operator
from flamethrower.shell.printer import Printer

from flamethrower.test_utils.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.test_utils.mocks.mock_prompt_generator import mock_prompt_generator
from flamethrower.test_utils.mocks.mock_operator import mock_operator
from flamethrower.test_utils.mocks.mock_printer import mock_printer

def mock_command_handler() -> CommandHandler:
    return MagicMock(
        CommandHandler,
        conv_manager=mock_conv_manager(),
        prompt_generator=mock_prompt_generator(),
        operator=mock_operator(),
        printer=mock_printer(),
    )
