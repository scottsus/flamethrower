import os
import sys
import tty
import termios
from pydantic import BaseModel
from rich.console import Console
from rich.syntax import Syntax
from rich.live import Live
from .special_keys import (
    ENTER_KEY,
    CLEAR_FROM_START,
    CURSOR_TO_START,
)
from .languages import is_programming_language

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
    fd: int = 0 # should be sys.stdout.fileno()
    tty_settings: list = []

    def print(self, data: bytes):
        if self.fd:
            os.write(self.fd, data)

    def print_color(self, data: bytes, color: bytes, reset: bool = False):
        if self.fd:
            os.write(self.fd, color)
            os.write(self.fd, data)
        if reset:
            os.write(self.fd, STDIN_DEFAULT)

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

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.tty_settings)
        
        self.print_default(ENTER_KEY + CLEAR_FROM_START + CURSOR_TO_START)
        try:
            while True:
                prev = ''
                for chunk in stream:
                    token = chunk.choices[0].delta.content
                    if token == '```':
                        break
                    elif prev == '``' and token.startswith('`'):
                        break
                    prev = token or ''
                    os.write(sys.stdout.fileno(), token.encode('utf-8'))
                    
                console, lang = Console(), 'python'
                with Live(console=console, refresh_per_second=2) as live:
                    accumulated_content = ''
                    is_first = True
                    for chunk in stream:
                        token = chunk.choices[0].delta.content
                        
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
                        
                        accumulated_content += token or ''
                        syntax = Syntax(accumulated_content, lang, theme='monokai', line_numbers=False)
                        live.update(syntax, refresh=True)
        except AttributeError:
            pass
        
        tty.setraw(sys.stdin)