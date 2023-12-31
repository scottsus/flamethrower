import os
from datetime import datetime
from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.context.dir_walker import generate_directory_summary
from flamethrower.models.llm import LLM
from flamethrower.agents.file_chooser import FileChooser
from flamethrower.utils.pretty import pretty_print

class PromptGenerator(BaseModel):
    # at initialization
    greeting: str = ''
    description: str = ''
    dir_structure: str = ''
    llm: LLM = None

    # for every query
    run_script: str = ''
    target_file_names: list = []

    def __init__(self, **data):
        super().__init__(**data)
        self.greeting = generate_greeting()
        self.description = generate_description()
        self.dir_structure = generate_dir_structure()
        self.llm = LLM()
    
    def construct_greeting(self) -> str:
        STDIN_LIGHT_CYAN = '\033[96m'
        STDIN_DEFAULT = '\033[0m'

        return (
            f'{self.greeting}\n\n'
            f'This looks like a coding project about {self.description}.\n'
            f'The directory structure looks like:\n{self.dir_structure}\n'
            '- For now, feel free to use me as a regular shell.\n'
            '- When you need my help, write your query in the terminal starting with a capital letter.\n'
            '- The command should turn orange, and I will have the necessary context from your workspace and stdout to assist you.\n'
            f'- To try it out, type {STDIN_LIGHT_CYAN}"Refactor /path/to/file"{STDIN_DEFAULT} in the terminal.'
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

        if not self.target_file_names:
            self.target_file_names = FileChooser().infer_target_file_paths(
                self.description,
                self.dir_structure,
                query
            )

        target_file_contents = ''
        for file_name in self.target_file_names:
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

        last_prompt_path = config.get_last_prompt_path()

        with open(last_prompt_path, 'w') as f:
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

def generate_description() -> str:
    # TODO: Summarize README
    target_file = 'README.md'
    if os.path.exists(target_file):
        with open(target_file, 'r') as f:
            readme = f.read()
            return readme[:100]
    else:
        return ''

def generate_dir_structure() -> str:
    generate_directory_summary(os.getcwd())

    target_path = config.get_dir_structure_path()
    if os.path.exists(target_path):
        with open(target_path, 'r') as f:
            tree = f.read()
            return tree
    else:
        return ''