import os
import sys
import pty
import tty
import termios
import subprocess
from select import select
import flamethrower.config.constants as config
from .setup import setup_zsh_env
from .command_handler import CommandHandler
from .printer import Printer
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.agents.executor import Executor

class Shell:
    def __init__(self):
        self.block_size = 1024
        self.leader_fd, self.follower_fd = pty.openpty()
        self.child_process = None
        self.command_handler = None
        self.conv_manager = None
        self.executor = None
        self.printer = None

    def execute_kill_signal(self):
        sys.exit(0)

    def run(self):
        prompt_generator = setup_zsh_env()
        env = os.environ.copy()
        env['ZDOTDIR'] = config.FLAMETHROWER_DIR
        self.child_process = subprocess.Popen(['zsh'],
                                              env=env,
                                              stdin=self.follower_fd,
                                              stdout=self.follower_fd,
                                              stderr=self.follower_fd)

        # Set stdin in raw mode
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin)

        self.conv_manager = ConversationManager()
        self.printer = Printer(
            leader_fd=self.leader_fd,
            stdout_fd=sys.stdout.fileno(),
            tty_settings=old_settings,
            conv_manager=self.conv_manager
        )
        self.executor = Executor(
            conv_manager=self.conv_manager,
            printer=self.printer
        )
        self.cmdHandler = CommandHandler(
            prompt_generator=prompt_generator,
            printer=self.printer,
            conv_manager=self.conv_manager,
            executor=self.executor
        )

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
                    self.cmdHandler.handle(key)
                
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
            
            print('\n👋 Goodbye!')
