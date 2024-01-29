import pytest
from unittest.mock import MagicMock
from flamethrower.agents.operator import Operator
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.context.prompt import PromptGenerator
from flamethrower.shell.printer import Printer

@pytest.fixture
def mock_operator(
    mock_conv_manager: ConversationManager,
    mock_prompt_generator: PromptGenerator,
    mock_printer: Printer
) -> Operator:
    return MagicMock(
        Operator,
        conv_manager=mock_conv_manager,
        prompt_generator=mock_prompt_generator,
        printer=mock_printer
    )