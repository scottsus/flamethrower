import os
from datetime import datetime
from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.agents.file_chooser import FileChooser
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.agents.summarizer import Summarizer
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.shell.printer import Printer
from flamethrower.utils.pretty import pretty_print
from flamethrower.utils.colors import *

class PromptGenerator(BaseModel):
    greeting: str = ''
    description: str = ''
    dir_structure: str = ''
    summarizer: Summarizer = None
    conv_manager: ConversationManager
    token_counter: TokenCounter
    printer: Printer

    def __init__(self, **data):
        super().__init__(**data)
        self.greeting = generate_greeting()
        self.summarizer = Summarizer()
        self.description = self.summarizer.summarize_readme()
        self.dir_structure = get_dir_structure()
    
    def construct_greeting(self) -> str:
        green = STDIN_GREEN.decode('utf-8')
        orange = STDIN_ORANGE.decode('utf-8')
        default = STDIN_DEFAULT.decode('utf-8')

        return (
            f'{self.greeting}\n\n'
            f'{self.description}\n\n'
            f'- For now, feel free to use me as a regular shell for commands like {green}ls{default} or {green}cd{default}.\n'
            '- When you need my help, write your query in the terminal starting with a capital letter.\n'
            '- The command should turn light green, and I will have the necessary context from your workspace and stdout to assist you.\n'
            f'- To try it out, type {orange}"Refactor /path/to/file"{default} in the terminal.\n\n'
        )

    def construct_messages(self, query: str = '') -> list:
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

        try:
            target_file_names = FileChooser().infer_target_file_paths(
                self.description,
                self.dir_structure,
                query
            )
            if target_file_names:
                self.printer.print_regular(f'🔭 Focusing on the following files: {target_file_names}\n')
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

        conv = self.load_pretty_conv()
        append_meta_information(
            role='user',
            content=f'Here are the most recent conversations between the human, stdout logs, and assistant:\n{conv}\n' if conv else ''
        )

        append_meta_information(
            role='user',
            content=(
                f'Given the context, here is your **crucial task: {query}**\n'
                'If it is a coding problem, write code to achieve the crucial task above.\n'
                'Otherwise, just reply in a straightforward fashion.'
            )
        )

        with open(config.get_last_prompt_path(), 'w') as f:
            f.write(pretty_print(meta_information))

        return meta_information
    
    def load_pretty_conv(self) -> str:
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
    