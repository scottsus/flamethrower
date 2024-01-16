import os
import sys
import pty
import tty
import termios
from pydantic import BaseModel
from subprocess import Popen
from select import select
import flamethrower.setup.setup as setup
from flamethrower.containers.container import container
from flamethrower.context.dir_walker import setup_dir_summary

class Shell(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    block_size: int = 1024
    leader_fd: int = 0
    follower_fd: int = 0
    child_process: Popen[bytes] = None

    def run(self):
        if len(sys.argv) > 2:
            print('Usage: `flamethrower` or `flamethrower ./more/specific/directory`')
            return

        if (len(sys.argv) == 2):
            base_dir = os.path.abspath(sys.argv[1])
        else:
            base_dir = os.getcwd()

        env = setup.setup_zsh_env()
        if not env:
            return
        
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

        # Container dependencies
        container.tty_settings.override(old_settings)
        container.leader_fd.override(self.leader_fd)
        container.base_dir.override(base_dir)
        container.wire(modules=[__name__])

        # Container singletons
        command_handler = container.command_handler()
        conv_manager = container.conv_manager()
        prompt_generator = container.prompt_generator()
        token_counter = container.token_counter()
        shell_manager = container.shell_manager()
        printer = container.printer()

        error = None
        try:
            setup_dir_summary(
                base_dir=base_dir,
                printer=printer,
                shell_manager=shell_manager
            )
            printer.print_regular(prompt_generator.construct_greeting())

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
                    conv_manager.update_conv_from_stdout(data)
                
                # From user input
                if sys.stdin in r:
                    key = os.read(sys.stdin.fileno(), self.block_size)
                    if not key:
                        break
                    command_handler.handle(key)
                
                if self.child_process.poll() is not None:
                    break
        except Exception as e:
            error = e
        finally:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except termios.error as e:
                print(
                    f'Unable to return pty to old settings due to error: {e}\n'
                    'Please restart your terminal instance by pressing `exit`\n'
                )
                pass
            
            os.close(self.leader_fd)
            os.close(self.follower_fd)

            if self.child_process:
                self.child_process.terminate()
            
            if error:
                printer.print_err(f'Error: {str(error)}')
            else:
                print(token_counter.return_cost_analysis())
                print('\n👋 Goodbye!')
