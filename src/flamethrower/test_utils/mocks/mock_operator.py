from unittest.mock import MagicMock
from flamethrower.agents.operator import Operator

from flamethrower.test_utils.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.test_utils.mocks.mock_prompt_generator import mock_prompt_generator
from flamethrower.test_utils.mocks.mock_printer import mock_printer

def mock_operator() -> Operator:
    return MagicMock(
        Operator,
        conv_manager=mock_conv_manager(),
        prompt_generator=mock_prompt_generator(),
        printer=mock_printer()
    )