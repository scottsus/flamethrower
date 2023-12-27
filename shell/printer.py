import os
import sys
import tty
import termios
from pydantic import BaseModel
from rich.console import Console
from rich.syntax import Syntax
from rich.live import Live
from context.conv_manager import ConversationManager
from utils.special_keys import (
    ENTER_KEY,
    CLEAR_FROM_START,
    CURSOR_TO_START,
)

STDIN_DEFAULT = b'\033[0m'
STDIN_RED = b'\033[31m'
STDIN_YELLOW = b'\033[33m'
STDIN_GREEN = b'\033[92m'
STDIN_BLUE = b'\033[94m'
STDIN_CYAN = b'\033[96m'
STDIN_GRAY = b'\033[90m'
STDIN_WHITE = b'\033[97m'

STDIN_LIGHT_GREEN = b'\033[92m'
STDIN_LIGHT_BLUE = b'\033[94m'
STDIN_LIGHT_CYAN = b'\033[96m'
STDIN_LIGHT_MAGENTA = b'\033[95m'

class Printer(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    leader_fd: int = 0
    stdout_fd: int = 0
    tty_settings: list = []
    conv_manager: ConversationManager = None

    def write_leader(self, data: bytes):
        if self.leader_fd:
            os.write(self.leader_fd, data)

    def print_stdout(self, data: bytes):
        if self.stdout_fd:
            os.write(self.stdout_fd, data)

    def print_color(self, data: bytes, color: bytes, reset: bool = False):
        if self.stdout_fd:
            os.write(self.stdout_fd, color)
            self.print_stdout(data)
        if reset:
            os.write(self.stdout_fd, STDIN_DEFAULT)

    def print_default(self, data: bytes):
        self.print_color(data, STDIN_DEFAULT)
    
    def print_red(self, data: bytes):
        self.print_color(data, STDIN_RED)
    
    def print_yellow(self, data: bytes):
        self.print_color(data, STDIN_YELLOW)
    
    def print_green(self, data: bytes):
        self.print_color(data, STDIN_GREEN)
    
    def print_blue(self, data: bytes):
        self.print_color(data, STDIN_BLUE)
    
    def print_cyan(self, data: bytes):
        self.print_color(data, STDIN_CYAN)
    
    def print_gray(self, data: bytes):
        self.print_color(data, STDIN_GRAY)

    def print_white(self, data: bytes):
        self.print_color(data, STDIN_WHITE)

    def print_light_green(self, data: bytes):
        self.print_color(data, STDIN_LIGHT_GREEN)
    
    def print_light_blue(self, data: bytes):
        self.print_color(data, STDIN_LIGHT_BLUE)

    def print_light_cyan(self, data: bytes):
        self.print_color(data, STDIN_LIGHT_CYAN)
    
    def print_light_magenta(self, data: bytes):
        self.print_color(data, STDIN_LIGHT_MAGENTA)

    def print_llm_response(self, stream):
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
            self.conv_manager.append_message(
                role='assistant',
                content=content,
            )

        nl_content, code_content = '', ''
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
                
                append_conv(nl_content)
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
                    
                    append_conv(f'\n```{code_content}\n```')
                    code_content = ''
        except AttributeError:
            # that means EOF was reached
            pass
        finally:
            if nl_content:
                append_conv(nl_content)
            if code_content:
                append_conv(f'```{code_content}\n```')

        tty.setraw(sys.stdin)
