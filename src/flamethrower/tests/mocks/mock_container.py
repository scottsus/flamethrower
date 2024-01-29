import pytest
from unittest.mock import MagicMock
from flamethrower.containers.container import Container
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.shell.shell_manager import ShellManager
from flamethrower.shell.printer import Printer
from flamethrower.context.prompt import PromptGenerator
from flamethrower.agents.operator import Operator
from flamethrower.shell.command_handler import CommandHandler
from flamethrower.tests.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.tests.mocks.mock_token_counter import mock_token_counter
from flamethrower.tests.mocks.mock_shell_manager import mock_shell_manager
from flamethrower.tests.mocks.mock_printer import mock_printer
from flamethrower.tests.mocks.mock_prompt_generator import mock_prompt_generator
from flamethrower.tests.mocks.mock_operator import mock_operator
from flamethrower.tests.mocks.mock_command_handler import mock_command_handler

@pytest.fixture
def mock_container(
    conv_manager: ConversationManager,
    token_counter: TokenCounter,
    shell_manager: ShellManager,
    printer: Printer,
    prompt_generator: PromptGenerator,
    operator: Operator,
    command_handler: CommandHandler,
) -> Container:
    return MagicMock(
        spec=Container,
        conv_manager=conv_manager,
        token_counter=token_counter,
        shell_manager=shell_manager,
        printer=printer,
        prompt_generator=prompt_generator,
        operator=operator,
        command_handler=command_handler,
    )
