import os
from datetime import datetime
from pydantic import BaseModel
from context.dir_walker import generate_directory_summary

def generate_greeting():
    now = datetime.now()
    current_hour = now.hour

    if current_hour < 12:
        return 'Good morning 👋'
    elif current_hour < 18:
        return 'Good afternoon 👋'
    else:
        return 'Good evening 👋'

def generate_description():
    target_file = 'README.md'
    if os.path.exists(target_file):
        with open(target_file, 'r') as f:
            readme = f.read()
            return readme[:100]
    else:
        return ''

def generate_dir_structure():
    generate_directory_summary(os.getcwd())

    target_file = 'tree.txt'
    target_path = os.path.join(os.getcwd(), '.flamethrower', target_file)
    if os.path.exists(target_path):
        with open(target_path, 'r') as f:
            tree = f.read()
            return tree
    else:
        return ''

class Prompt(BaseModel):
    greeting: str = ''
    description: str = ''
    dir_structure: str = ''

    def __init__(self, **data):
        super().__init__(**data)
        self.greeting = generate_greeting()
        self.description = generate_description()
        self.dir_structure = generate_dir_structure()
    
    def generate_initial_prompt(self):
        return (f'{self.greeting} {self.description} '
                f'The directory structure looks like:\n{self.dir_structure}\n'
                '- For now, feel free to use me as a regular shell.\n'
                '- When you need my help, write your query in the terminal starting with a capital letter.\n'
                '- The command should turn orange, and I will have the necessary context from your workspace and stdout to assist you.\n'
                '- To try it out, type "Help me with the TwoSum problem" in the terminal.'
                )

        
    