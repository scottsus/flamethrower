import os
from datetime import datetime
from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.agents.file_chooser import FileChooser
from flamethrower.utils.pretty import pretty_print
from flamethrower.agents.summarizer import Summarizer
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.shell.printer import Printer
from flamethrower.utils.colors import *

class PromptGenerator(BaseModel):
    greeting: str = ''
    description: str = ''
    dir_structure: str = ''
    token_counter: TokenCounter = None
    summarizer: Summarizer = None
    printer: Printer = None

    def __init__(self, **data):
        super().__init__(**data)
        self.greeting = generate_greeting()
        self.summarizer = Summarizer(
            token_counter=self.token_counter
        )
        self.description = self.summarizer.summarize_readme()
        self.dir_structure = get_dir_structure()
    
    def construct_greeting(self) -> str:
        green = STDIN_GREEN.decode('utf-8')
        light_green = STDIN_LIGHT_GREEN.decode('utf-8')
        default = STDIN_DEFAULT.decode('utf-8')

        return (
            f'{self.greeting}\n\n'
            f'{self.description}\n\n'
            f'- For now, feel free to use me as a regular shell for commands like {green}ls{default} or {green}cd{default}.\n'
            '- When you need my help, write your query in the terminal starting with a capital letter.\n'
            '- The command should turn light green, and I will have the necessary context from your workspace and stdout to assist you.\n'
            f'- To try it out, type {light_green}"Refactor /path/to/file"{default} in the terminal.\n'
        )

    def construct_messages(self, query: str = '', conv: str = '') -> list:
        messages = []

        description_line = ''
        if self.description:
            description_line = f'This project is about {self.description}. '
            messages.append({
                'role': 'user',
                'content': description_line,
                'name': 'human'
            })
        
        dir_structure_line = ''
        if self.dir_structure:
            dir_structure_line = f'The directory structure looks like:\n{self.dir_structure}\n'
            messages.append({
                'role': 'user',
                'content': dir_structure_line,
                'name': 'human'
            })

        target_file_names = FileChooser(token_counter=self.token_counter).infer_target_file_paths(
            self.description,
            self.dir_structure,
            query
        )
        self.printer.print_regular(f'👀 Focusing on the following files: {target_file_names}\n')

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
        if target_file_contents:
            target_file_contents = f'Currently you are working with these files:\n{target_file_contents}\n'
            messages.append({
                'role': 'user',
                'content': target_file_contents,
                'name': 'human'
            })

        conv = self.load_conv()
        messages.append({
            'role': 'user',
            'content': 'Here is the most recent conversation between the human, stdout logs, and assistant:\n',
            'name': 'user'
        })
        messages.append({
            'role': 'user',
            'content': f'```\n{conv}```\n',
            'name': 'stdout'
        })

        query_line = ''
        if query:
            query_line = (
                f'Given the context, here is your **crucial task: {query}**\n'
                'If it is a coding problem, write code to achieve the crucial task above.\n'
                'Otherwise, just reply in a straightforward fashion.'
            )
            messages.append({
                'role': 'user',
                'content': query_line,
                'name': 'human'
            })

        # TODO: get run script

        with open(config.get_last_prompt_path(), 'w') as f:
            f.write(pretty_print(messages))

        return messages
    
    def load_conv(self) -> str:
        with open(config.get_conversation_path(), 'r') as f:
            conv = f.read()
            pretty = pretty_print(conv)
            
            return pretty

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
    