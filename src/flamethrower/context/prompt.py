import os
from datetime import datetime
from pydantic import BaseModel

import flamethrower.config.constants as config
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.agents.util_agents.file_chooser import FileChooser
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.shell.printer import Printer
from flamethrower.utils.pretty import pretty_print
from flamethrower.utils.colors import *

from typing import Dict, List

class PromptGenerator(BaseModel):
    conv_manager: ConversationManager
    token_counter: TokenCounter
    printer: Printer

    def __init__(
        self,
        conv_manager: ConversationManager,
        token_counter: TokenCounter,
        printer: Printer,
    ) -> None:
        super().__init__(
            conv_manager=conv_manager, 
            token_counter=token_counter, 
            printer=printer
        )
        self._greeting: str = generate_greeting()
        self._description: str = get_project_description()
        self._dir_structure: str = get_dir_structure()
    
    @property
    def greeting(self) -> str:
        return self._greeting
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def dir_structure(self) -> str:
        return self._dir_structure
    
    def construct_greeting(self) -> str:
        green = STDIN_GREEN.decode('utf-8')
        orange = STDIN_ORANGE.decode('utf-8')
        default = STDIN_DEFAULT.decode('utf-8')

        return (
            f'\n{self.greeting}\n\n'
            f'{self.description}\n\n'
            f'- For now, feel free to use me as a regular shell for commands like {green}ls{default} or {green}cd{default}.\n'
            '- When you need my help, write your query in the terminal starting with a capital letter.\n'
            '- The command should turn light green, and I will have the necessary context from your workspace and stdout to assist you.\n'
            f'- To try it out, type {orange}"Refactor /path/to/file"{default} in the terminal.\n\n'
        )

    def construct_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Think of this as the `headers` for the LLM that will be attached to every new query.
        """

        meta_information = []

        def append_meta_information(role: str, content: str, name: str = 'human') -> None:
            new_message = { 'role': role, 'content': content, 'name': name }
            meta_information.append(new_message)

        append_meta_information(
            role='user',
            content=f'This project is about {self.description}.\n' if self.description else ''
        )
        
        append_meta_information(
            role='user',
            content=f'Here is the directory structure:\n{self.dir_structure}\n' if self.dir_structure else ''
        )

        conv = pretty_print(messages)

        try:
            target_file_names = FileChooser().infer_target_file_paths(
                self.description,
                self.dir_structure,
                conv,
            )
            self.printer.print_files(target_file_names)
        except KeyboardInterrupt:
            raise
        except Exception:
            raise

        target_file_contents = ''
        for file_name in target_file_names:
            file_path = os.path.join(os.getcwd(), file_name)
            try:
                with open(file_path, 'r') as file:
                    target_file_contents += (
                        f'{file_name}\n'
                        f'```\n{file.read().strip()}\n```\n'
                    )
            except UnicodeDecodeError:
                pass
            except FileNotFoundError:
                pass
        
        append_meta_information(
            role='user',
            content=f'Currently you are working with these files:\n{target_file_contents}\n' if target_file_contents else ''
        )
        
        append_meta_information(
            role='user',
            content=f'Here are the most recent conversations between the human, stdout logs, and assistant:\n{conv}\n' if conv else ''
        )

        with open(config.get_last_prompt_path(), 'w') as f:
            f.write(pretty_print(meta_information))

        return meta_information

"""
Helper functions
"""

def generate_greeting() -> str:
    now = datetime.now()
    current_hour = now.hour

    if current_hour < 12:
        return 'Good morning 👋'
    elif current_hour < 18:
        return 'Good afternoon 👋'
    else:
        return 'Good evening 👋'

def get_dir_structure() -> str:
    try:
        with open(config.get_dir_tree_path(), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ''

def get_project_description() -> str:
    try:
        with open(config.get_workspace_summary_path(), 'r') as f:
            return f.read()
    except FileNotFoundError:
        return 'Workspace summary not found.'
