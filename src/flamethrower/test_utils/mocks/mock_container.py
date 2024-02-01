from unittest.mock import MagicMock
from flamethrower.containers.container import Container
from flamethrower.test_utils.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.test_utils.mocks.mock_token_counter import mock_token_counter
from flamethrower.test_utils.mocks.mock_shell_manager import mock_shell_manager
from flamethrower.test_utils.mocks.mock_printer import mock_printer
from flamethrower.test_utils.mocks.mock_prompt_generator import mock_prompt_generator
from flamethrower.test_utils.mocks.mock_operator import mock_operator
from flamethrower.test_utils.mocks.mock_command_handler import mock_command_handler

def mock_container() -> Container:
    return MagicMock(
        spec=Container,
        conv_manager=mock_conv_manager(),
        token_counter=mock_token_counter(),
        shell_manager=mock_shell_manager(),
        printer=mock_printer(),
        prompt_generator=mock_prompt_generator(),
        operator=mock_operator(),
        command_handler=mock_command_handler(),
    )
