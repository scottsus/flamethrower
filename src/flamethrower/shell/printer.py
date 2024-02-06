import os
from pydantic import BaseModel
from rich.console import Console
from rich.syntax import Syntax
from rich.live import Live
import flamethrower.config.constants as config
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.shell.shell_manager import ShellManager
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.models.models import OPENAI_GPT_4_TURBO
from flamethrower.utils.special_keys import *
from flamethrower.utils.colors import *
from typing import Any, Dict, List, Union, Iterator

class Printer(BaseModel):
    leader_fd: int
    stdout_fd: int
    conv_manager: ConversationManager
    shell_manager: ShellManager
    token_counter: TokenCounter

    def write_leader(self, data: bytes) -> None:
        if self.leader_fd:
            os.write(self.leader_fd, data)

    def print_stdout(self, data: Union[bytes, str]) -> None:
        if self.stdout_fd:
            if isinstance(data, str):
                with self.shell_manager.cooked_mode():
                    os.write(self.stdout_fd, data.encode('utf-8'))
            else:
                os.write(self.stdout_fd, data)
    
    def print_err(self, err: str) -> None:
        self.print_red(f'\n{err}\n', reset=True)

    def print_color(self, data: Union[bytes, str], color: bytes, reset: bool = False) -> None:
        os.write(self.stdout_fd, color)
        self.print_stdout(data)
        
        if reset:
            os.write(self.stdout_fd, STDIN_DEFAULT)
            self.set_cursor_to_start(with_newline=True)

    def print_default(self, data: Union[bytes, str]) -> None:
        self.print_color(data, STDIN_DEFAULT)
    
    def print_red(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_RED, reset=reset)
    
    def print_yellow(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_YELLOW, reset=reset)
    
    def print_green(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_GREEN, reset=reset)
    
    def print_blue(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_BLUE, reset=reset)
    
    def print_cyan(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_CYAN, reset=reset)
    
    def print_gray(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_GRAY, reset=reset)

    def print_white(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_WHITE, reset=reset)

    def print_light_green(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_LIGHT_GREEN, reset=reset)
    
    def print_light_blue(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_LIGHT_BLUE, reset=reset)

    def print_light_cyan(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_LIGHT_CYAN, reset=reset)
    
    def print_light_magenta(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_LIGHT_MAGENTA, reset=reset)
    
    def print_orange(self, data: Union[bytes, str], reset: bool = False) -> None:
        self.print_color(data, STDIN_ORANGE, reset=reset)
    

    def print_llm_response(self, stream: Iterator[str]) -> None:
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
                'sh',
            ]
            return name in programming_languages

        with self.shell_manager.cooked_mode():
            self.set_cursor_to_start(with_newline=True)

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
                    with Live(console=console, refresh_per_second=10) as live:
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
                pass
            except KeyboardInterrupt:
                raise
            finally:
                if nl_content:
                    complete_content += nl_content
                if code_content:
                    complete_content += f'```{code_content}\n```\n'

                self.token_counter.add_streaming_output_tokens(complete_content, model=OPENAI_GPT_4_TURBO)
                append_conv(complete_content)
                log_last_response(complete_content)
                self.print_regular(with_newline=True)

    
    def print_code(self, code: str, language: str = 'bash') -> None:
        with self.shell_manager.cooked_mode():
            self.set_cursor_to_start(with_newline=True)
            syntax = Syntax(f'\n🔥 {code}\n', language, theme='monokai')
            console = Console()
            console.print(syntax)
    
    def print_actions(self, actions: List[Dict[Any, Any]]) -> None:
        # actions is confirmed to have at least one action
        
        with self.shell_manager.cooked_mode():
            self.set_cursor_to_start()
            self.print_cyan('Next actions:\n')
            for obj in actions:
                action, command, file_paths = obj.get('action'), obj.get('command'), obj.get('file_paths')
                if action == 'run':
                    self.print_cyan(f'  - Run command: {command}\n')
                elif action == 'write':
                    self.print_cyan(f'  - Write to: {file_paths}\n')
                elif action == 'debug':
                    self.print_cyan(f'  - Add debugging statements to: {file_paths}\n')
                elif action == 'stuck':
                    # This is handled in operator.py
                    pass
                elif action == 'cleanup':
                    self.print_cyan(f'  - Cleanup: {file_paths}\n')
                elif action == 'completed':
                    self.print_cyan('  - Done')
                else:
                    self.print_err('Printer.print_actions: Unknown action')
            self.print_default('')
    
    def print_files(self, files: List[str]) -> None:
        with self.shell_manager.cooked_mode():
            self.set_cursor_to_start()
            if files:
                self.print_cyan('Focusing on the following files 🔭:\n')
                for file in files:
                    self.print_cyan(f'  - {file}\n')
            else:
                self.print_cyan('No files used as context.\n')
            
            self.print_default('')
    
    def print_diffs(self, diffs: List[str]) -> None:
        with self.shell_manager.cooked_mode():
            self.set_cursor_to_start(with_newline=True)
            for line in diffs:
                if line.startswith('+'):
                    self.print_green(line + '\n', reset=True)
                elif line.startswith('-'):
                    self.print_red(line + '\n', reset=True)
                else:
                    self.print_default(line + '\n')
    
    def set_cursor_to_start(self, with_newline: bool = False) -> None:
        if with_newline:
            self.print_stdout(ENTER_KEY + CLEAR_FROM_START + CLEAR_TO_END + CURSOR_TO_START)
        else:
            self.print_stdout(CLEAR_FROM_START + CLEAR_TO_END + CURSOR_TO_START)

    def print_regular(self, message: str = '', with_newline: bool = False) -> None:
        with self.shell_manager.cooked_mode():
            self.set_cursor_to_start(with_newline)
            self.print_stdout(message)
    