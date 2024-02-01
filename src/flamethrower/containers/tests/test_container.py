from unittest.mock import patch, mock_open
from flamethrower.containers.container import Container
from flamethrower.shell.command_handler import CommandHandler
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.context.prompt import PromptGenerator
from flamethrower.agents.operator import Operator
from flamethrower.shell.shell_manager import ShellManager
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.shell.printer import Printer

"""
Don't use pytest.fixtures as mock_open only works for 1 level of abstraction?
Need to look more into this.
"""
def mock_container() -> Container:
    container = Container()
    container.tty_settings.override([])
    container.leader_fd.override(1)
    container.base_dir.override('/user/tester')
    
    return container

def test_container_init() -> None:
    with patch('builtins.open', mock_open()):
        container = mock_container()
        
        assert isinstance(container.conv_manager(), ConversationManager)
        assert isinstance(container.token_counter(), TokenCounter)
        assert isinstance(container.shell_manager(), ShellManager)
        assert isinstance(container.printer(), Printer)
        assert isinstance(container.prompt_generator(), PromptGenerator)
        assert isinstance(container.operator(), Operator)
        assert isinstance(container.command_handler(), CommandHandler)

def test_container_wiring() -> None:
    with patch('builtins.open', mock_open()):
        container = mock_container()

        shell_manager = container.shell_manager()
        assert shell_manager.old_settings == container.tty_settings()

        printer = container.printer()
        assert printer.conv_manager is container.conv_manager()
        assert printer.shell_manager is container.shell_manager()
        assert printer.token_counter is container.token_counter()

        prompt_generator = container.prompt_generator()
        assert prompt_generator.conv_manager is container.conv_manager()
        assert prompt_generator.token_counter is container.token_counter()
        assert prompt_generator.printer is container.printer()

        operator = container.operator()
        assert operator.base_dir == container.base_dir()
        assert operator.conv_manager is container.conv_manager()
        assert operator.prompt_generator is container.prompt_generator()
        assert operator.printer is container.printer()

        command_handler = container.command_handler()
        assert command_handler.conv_manager is container.conv_manager()
        assert command_handler.prompt_generator is container.prompt_generator()
        assert command_handler.operator is container.operator()
        assert command_handler.printer is container.printer()
