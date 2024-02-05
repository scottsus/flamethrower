from unittest.mock import MagicMock

from flamethrower.context.prompt import PromptGenerator
from flamethrower.test_utils.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.test_utils.mocks.mock_token_counter import mock_token_counter
from flamethrower.test_utils.mocks.mock_printer import mock_printer

def mock_prompt_generator() -> PromptGenerator:
    return MagicMock(
        PromptGenerator,
        conv_manager=mock_conv_manager(),
        token_counter=mock_token_counter(),
        printer=mock_printer()
    )
