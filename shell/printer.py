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
from .sequence_parser import *

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
    leader_fd: int = 0
    stdout_fd: int = 0 # should be sys.stdout.fileno()
    tty_settings: list = []
    conversation_path: str = os.path.join(
        os.getcwd(), '.flamethrower', 'conv.log'
    )

    def __init__(self, **data):
        super().__init__(**data)
        # if the file exists, delete it
        if os.path.exists(self.conversation_path):
            os.remove(self.conversation_path)
        if not os.path.exists(self.conversation_path):
            with open(self.conversation_path, 'w') as f:
                f.write('')


    def write_to_file(self, data: bytes, target_file: str = '', is_nl_query: bool = False) -> None:
        with open(target_file or self.conversation_path, 'a') as f:
            if is_nl_query:
                f.write((data + b'\n').decode('utf-8'))
                return

            if is_ansi_escape_sequence(data):
                return
            
            if is_single_key(data):
                return

            def get_user_cmd():                
                with open(os.path.join(os.getcwd(), '.flamethrower', '.zsh_history')) as f:
                    history = f.read()
                    if not history:
                        return ''
                    
                    history = history.split('\n')
                    last_index = -1
                    last_command = history[last_index]
                    
                    while last_command == '':
                        last_index -= 1
                        last_command = history[last_index]

                    return last_command

            if is_prompt_newline(data):
                user_cmd = get_user_cmd()
                if user_cmd == '' or user_cmd.lower() == 'exit':
                    return
                elif is_capitalized(user_cmd):
                    f.write(f'\nThe above was the response of an LLM when executing the query: {user_cmd}\n')
                else:
                    f.write(f'\nThe above was the result of executing the command: [{user_cmd}]\n\n')
            else:
                f.write(data.decode('utf-8'))


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

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.tty_settings)
        
        self.print_default(ENTER_KEY + CLEAR_FROM_START + CURSOR_TO_START)
        try:
            while True:
                prev = ''
                for token in stream:
                    if token == '```':
                        # self.write_to_file('```\n'.encode('utf-8'))
                        break
                    elif prev == '``' and token.startswith('`'):
                        # self.write_to_file('```\n'.encode('utf-8'))
                        break
                    prev = token or ''
                    self.print_stdout(token.encode('utf-8'))
                    
                console, lang = Console(), 'python'
                with Live(console=console, refresh_per_second=2) as live:
                    accumulated_content = ''
                    is_first = True
                    for token in stream:                        
                        if is_first:
                            is_first = False
                            if is_programming_language(token):
                                lang = token
                                continue
                        
                        if token == '```':
                            # self.write_to_file('```\n'.encode('utf-8'))
                            break
                        elif prev == '``' and token.startswith('`'):
                            # self.write_to_file('```\n'.encode('utf-8'))
                            break
                        prev = token or ''
                        if token == '``':
                            continue
                        
                        accumulated_content += token or ''
                        syntax = Syntax(accumulated_content, lang, theme='monokai', line_numbers=False)
                        live.update(syntax, refresh=True)
                    
                    # not forgetting to append conv.log
                    self.write_to_file(accumulated_content.encode('utf-8'))
        except AttributeError:
            pass

        tty.setraw(sys.stdin)
