import os
import sys
import pty
import tty
import termios
from subprocess import Popen
from select import select
from pydantic import BaseModel
import flamethrower.shell.setup as setup
from flamethrower.shell.command_handler import CommandHandler
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.context.prompt import PromptGenerator
from flamethrower.agents.executor import Executor
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.shell.printer import Printer

class Shell(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    block_size: int = 1024
    leader_fd: int = 0
    follower_fd: int = 0
    child_process: Popen[bytes] = None
    command_handler: CommandHandler = None
    conv_manager: ConversationManager = None
    prompt_generator: PromptGenerator = None
    executor: Executor = None
    token_counter: TokenCounter = None
    printer: Printer = None

    def run(self):
        env = setup.setup_zsh_env()
        self.leader_fd, self.follower_fd = pty.openpty()
        self.child_process = Popen(
            ['zsh'],
            env=env,
            stdin=self.follower_fd,
            stdout=self.follower_fd,
            stderr=self.follower_fd
        )

        # Set stdin in raw mode
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin)

        # Instantiate other classes
        self.conv_manager = ConversationManager()
        self.token_counter = TokenCounter()
        self.printer = Printer(
            leader_fd=self.leader_fd,
            stdout_fd=sys.stdout.fileno(),
            tty_settings=old_settings,
            conv_manager=self.conv_manager,
            token_counter=self.token_counter
        )
        self.prompt_generator = PromptGenerator(
            conv_manager=self.conv_manager,
            token_counter=self.token_counter,
            printer=self.printer
        )
        self.executor = Executor(
            conv_manager=self.conv_manager,
            token_counter=self.token_counter,
            printer=self.printer
        )
        self.command_handler = CommandHandler(
            prompt_generator=self.prompt_generator,
            printer=self.printer,
            conv_manager=self.conv_manager,
            executor=self.executor
        )

        setup.setup_dir_summary(self.token_counter)
        self.printer.print_regular(self.prompt_generator.construct_greeting())

        try:
            while True:
                timeout = 0.5 # seconds
                r, w, e = select([self.leader_fd, sys.stdin], [], [], timeout)

                # From leader process
                if self.leader_fd in r:
                    data = os.read(self.leader_fd, self.block_size)
                    if not data:
                        break

                    # Write to stdout and to logfile
                    os.write(sys.stdout.fileno(), data)
                    self.conv_manager.update_conv_from_stdout(data)
                
                # From user input
                if sys.stdin in r:
                    key = os.read(sys.stdin.fileno(), self.block_size)
                    if not key:
                        break
                    self.command_handler.handle(key)
                
                if self.child_process.poll() is not None:
                    break
                    
        finally:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except termios.error as e:
                pass

            os.close(self.leader_fd)
            os.close(self.follower_fd)

            if self.child_process:
                self.child_process.terminate()
            
            """
            Outside the pty, these should be the only `print` statements
            that do not use the Printer class.
            """
            print(self.token_counter.return_cost_analysis())
            print('\n👋 Goodbye!')
