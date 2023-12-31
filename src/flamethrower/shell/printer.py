import os
import sys
import tty
import termios
from pydantic import BaseModel
from rich.console import Console
from rich.syntax import Syntax
from rich.live import Live
from flamethrower.context.conv_manager import ConversationManager
import flamethrower.config.constants as config
from flamethrower.utils.special_keys import (
    ENTER_KEY,
    CLEAR_FROM_START,
    CURSOR_TO_START,
)
from flamethrower.utils.colors import *

class Printer(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    leader_fd: int = 0
    stdout_fd: int = 0
    tty_settings: list = []
    conv_manager: ConversationManager = None

    def write_leader(self, data: bytes) -> None:
        if self.leader_fd:
            os.write(self.leader_fd, data)

    def print_stdout(self, data: bytes) -> None:
        if self.stdout_fd:
            os.write(self.stdout_fd, data)

    def print_color(self, data: bytes, color: bytes, reset: bool = False) -> None:
        if self.stdout_fd:
            os.write(self.stdout_fd, color)
            self.print_stdout(data)
        if reset:
            os.write(self.stdout_fd, STDIN_DEFAULT)

    def print_default(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_DEFAULT, reset=reset)
    
    def print_red(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_RED, reset=reset)
    
    def print_yellow(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_YELLOW, reset=reset)
    
    def print_green(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_GREEN, reset=reset)
    
    def print_blue(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_BLUE, reset=reset)
    
    def print_cyan(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_CYAN, reset=reset)
    
    def print_gray(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_GRAY, reset=reset)

    def print_white(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_WHITE, reset=reset)

    def print_light_green(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_LIGHT_GREEN, reset=reset)
    
    def print_light_blue(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_LIGHT_BLUE, reset=reset)

    def print_light_cyan(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_LIGHT_CYAN, reset=reset)
    
    def print_light_magenta(self, data: bytes, reset: bool = False) -> None:
        self.print_color(data, STDIN_LIGHT_MAGENTA, reset=reset)

    def print_llm_response(self, stream) -> None:
        """
        1. Swap out of pty back into main shell
        2. Print the code using Python Rich
        3. Swap back into pty
        """

        def is_programming_language(name: str) -> bool:
            programming_languages = [
                'bash',
                'c',
                'c++',
                'java',
                'javascript',
                'typescript',
                'python',
                'go',
                'rust',
                'ruby',
                'php',
                'swift',
            ]
            return name in programming_languages

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.tty_settings)
        
        self.print_default(ENTER_KEY + CLEAR_FROM_START + CURSOR_TO_START)
        def append_conv(content: str) -> None:
            self.conv_manager.append_conv(
                role='assistant',
                content=content,
            )
        
        def log_last_response(content: str) -> None:
            with open(config.get_last_response_path(), 'w') as f:
                f.write(content)

        nl_content, code_content, complete_content = '', '', ''
        try:
            while True:
                # Natural language responses
                prev = ''
                for token in stream:
                    if token == '```':
                        break
                    elif prev == '``' and token.startswith('`'):
                        break
                    prev = token or ''
                    
                    self.print_stdout(token.encode('utf-8'))
                    nl_content += token or ''
                
                complete_content += nl_content
                nl_content = ''
                    
                # Coding responses
                console, lang = Console(), 'python'
                with Live(console=console, refresh_per_second=2) as live:
                    is_first = True
                    for token in stream:                        
                        if is_first:
                            is_first = False
                            if is_programming_language(token):
                                lang = token
                                continue
                        
                        if token == '```':
                            break
                        elif prev == '``' and token.startswith('`'):
                            break
                        prev = token or ''
                        if token == '``':
                            continue
                        
                        code_content += token or ''
                        syntax = Syntax(code_content, lang, theme='monokai', line_numbers=False)
                        live.update(syntax, refresh=True)
                    
                    complete_content += f'\n```{code_content}\n```\n'
                    code_content = ''
        except AttributeError:
            # that means EOF was reached
            pass
        finally:
            if nl_content:
                complete_content += nl_content
            if code_content:
                complete_content += f'```{code_content}\n```\n'
            append_conv(complete_content)
            log_last_response(complete_content)

        tty.setraw(sys.stdin)
