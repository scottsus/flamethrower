import pytest
from unittest.mock import MagicMock

from flamethrower.context.prompt import PromptGenerator
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.shell.printer import Printer

from flamethrower.tests.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.tests.mocks.mock_token_counter import mock_token_counter
from flamethrower.tests.mocks.mock_printer import mock_printer

@pytest.fixture
def mock_prompt_generator(
    mock_conv_manager: ConversationManager,
    mock_token_counter: TokenCounter,
    mock_printer: Printer
) -> PromptGenerator:
    return MagicMock(
        PromptGenerator,
        conv_manager=mock_conv_manager,
        token_counter=mock_token_counter,
        printer=mock_printer
    )
