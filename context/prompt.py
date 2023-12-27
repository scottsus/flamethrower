import os
import re
import time
import hashlib
from datetime import datetime
from pydantic import BaseModel
from context.dir_walker import generate_directory_summary
from models.llm import LLM

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
    
    def generate_initial_prompt(self):
        return (
            f'{self.greeting} {self.description} '
            f'The directory structure looks like:\n{self.dir_structure}\n'
            '- For now, feel free to use me as a regular shell.\n'
            '- When you need my help, write your query in the terminal starting with a capital letter.\n'
            '- The command should turn orange, and I will have the necessary context from your workspace and stdout to assist you.\n'
            '- To try it out, type "Refactor /path/to/file" in the terminal.'
        )

    def generate_chat_completions_prompt(self, query: str = '', stdout_log: str = ''):
        description_line = ''
        if self.description:
            description_line = f'This project is about {self.description}. '
        
        dir_structure_line = ''
        if self.dir_structure:
            dir_structure_line = f'The directory structure looks like:\n{self.dir_structure}\n'

        if not self.target_file_names:
            self.target_file_names = self.infer_target_file_names(query)

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
        
        query_line = ''
        if query:
            query_line = f'Given the context, here is your crucial task: {query}\n'

        stdout_log_line = ''
        if stdout_log:
            stdout_log_line = f'Here is the stdout log: {stdout_log}\n'

        prompt = (
            description_line
            + dir_structure_line
            + target_file_contents
            + query_line
            + stdout_log_line
            + 'If it is a coding problem, write code to achieve the crucial task above.\n'
            + 'Otherwise, just reply in a straightforward fashion.'
        )

        last_prompt_path = os.path.join(os.getcwd(), '.flamethrower', 'last_prompt.txt')
        with open(last_prompt_path, 'w') as f:
            f.write(prompt)

        return prompt
    
    def infer_target_file_names(self, query: str):
        tools = [
            {
                'type': 'function',
                'function': {
                    'name': 'blah',
                    'description': 'Infer target file names relevant to user query',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'file_names': {
                                'type': 'array',
                                'items': {
                                    'type': 'string'
                                }
                            }
                        },
                        'required': ['file_names']
                    }
                }
            }
        ]

        res = self.llm.new_json_request(
            f'This workspace is about {self.description}. '
            f'Given the directory structure {self.dir_structure}, '
            f'determine which files are relevant to the following user query: {query}. '
            'Only use the files which you think are absolutely necessary to complete the user query. '
            'If the user is asking some generic non-workspace-related question, just return an empty list.',
            tools=tools,
            model='gpt-4'
        )

        max_files_used = 5
        file_names = res['file_names'][:max_files_used]
        # TODO: allow user to select which files
        print('Focusing on the following files:', file_names)
        return file_names

    def get_answer(self, basic_query: str):
        prompted_query = self.generate_chat_completions_prompt(basic_query)

        key = self.generate_cache_key(prompted_query)
        cache_dir = os.path.join(os.getcwd(), '.flamethrower', 'response_cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

        cache_path = os.path.join(cache_dir, key)
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cached_response = f.read()
                # this splits ```, ' ', and '\n' into separate tokens
                tokens = re.findall(r'```|\S+|\s+', cached_response)
                for token in tokens:
                    nice_delay = 0.03
                    time.sleep(nice_delay)
                    yield token
                yield None
        
        else:
            stream = self.llm.new_chat_request(prompted_query)
            response = ''

            try:
                for chunk in stream:
                    token = chunk.choices[0].delta.content or ''
                    response += token
                    yield token
            except AttributeError:
                pass
            finally:
                with open(cache_path, 'w') as f:
                    f.write(response)

                yield None
        

    def generate_cache_key(self, query: str):
        return hashlib.md5(query.encode()).hexdigest() + '.txt'
