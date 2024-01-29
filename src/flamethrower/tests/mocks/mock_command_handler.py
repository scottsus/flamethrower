import pytest
from unittest.mock import MagicMock
from flamethrower.shell.command_handler import CommandHandler
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.context.prompt import PromptGenerator
from flamethrower.agents.operator import Operator
from flamethrower.shell.printer import Printer

@pytest.fixture
def mock_command_handler(
    conv_manager: ConversationManager,
    prompt_generator: PromptGenerator,
    operator: Operator,
    printer: Printer,
) -> CommandHandler:
    return MagicMock(
        CommandHandler,
        conv_manager=conv_manager,
        prompt_generator=prompt_generator,
        operator=operator,
        printer=printer,
    )
