import os
import sys
import pty
import tty
import termios
import subprocess
from select import select
from .command_handler import CommandHandler

class Shell:
    def __init__(self):
        self.block_size = 1024
        self.leader_fd, self.follower_fd = pty.openpty()
        self.child_process = None

    def execute_kill_signal(self):
        sys.exit(0)

    def run(self):
        env = os.environ.copy()
        # TODO: Make this configurable
        env['ZDOTDIR'] = os.path.join('/Users', 'scottsus', 'Projects', 'flamethrower', '.flamethrower')
        self.child_process = subprocess.Popen(['zsh'],
                                              env=env,
                                              stdin=self.follower_fd,
                                              stdout=self.follower_fd,
                                              stderr=self.follower_fd)

        # Set stdin in raw mode
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin)

        cmdHandler = CommandHandler(
            fd=self.leader_fd,
            tty_settings=old_settings
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
                    os.write(sys.stdout.fileno(), data)
                
                # From user input
                if sys.stdin in r:
                    key = os.read(sys.stdin.fileno(), self.block_size)
                    if not key:
                        break
                    cmdHandler.handle(key)
                
                if self.child_process.poll() is not None:
                    break
                    
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            os.close(self.leader_fd)
            os.close(self.follower_fd)

            if self.child_process:
                self.child_process.terminate()
            
            print('\n\n👋 Goodbye!')
