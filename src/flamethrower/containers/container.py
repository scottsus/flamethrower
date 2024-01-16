import sys
from dependency_injector import containers, providers
from flamethrower.shell.command_handler import CommandHandler
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.context.prompt import PromptGenerator
from flamethrower.agents.operator import Operator
from flamethrower.shell.shell_manager import ShellManager
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.shell.printer import Printer

class Container(containers.DeclarativeContainer):
    conv_manager = providers.Singleton(ConversationManager)
    
    token_counter = providers.Singleton(TokenCounter)

    tty_settings = providers.Dependency()
    shell_manager = providers.Singleton(
        ShellManager,
        old_settings=tty_settings
    )
    
    leader_fd = providers.Dependency()
    printer = providers.Singleton(
        Printer,
        leader_fd=leader_fd,
        stdout_fd=sys.stdout.fileno(),
        conv_manager=conv_manager,
        shell_manager=shell_manager,
        token_counter=token_counter
    )

    prompt_generator = providers.Singleton(
        PromptGenerator,
        conv_manager=conv_manager,
        token_counter=token_counter,
        printer=printer
    )

    base_dir = providers.Dependency()
    operator = providers.Singleton(
        Operator,
        base_dir=base_dir,
        conv_manager=conv_manager,
        printer=printer
    )

    command_handler = providers.Singleton(
        CommandHandler,
        conv_manager=conv_manager,
        prompt_generator=prompt_generator,
        operator=operator,
        printer=printer,
    )

container = Container()