import os
import re
from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.models.llm import LLM
from flamethrower.models.openai_client import OpenAIClient

system_message = """
You are an extremely powerful programming assistant that can write flawless code.
You have a single, crucial task: Given an expert engineer's coding response and a target file:
  1. Read the target file, if it exists
  2. Understand the expert engineer's response and extract the code
  3. Meaningfully incorporate the extracted code into the target file

You are completely overwriting the existing target file, so it is imperative that the code you write is both syntactically and semantically correct.
"""

class FileWriter(BaseModel):
    llm: LLM = None

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = OpenAIClient(system_message=system_message)
    
    def write_code(self, target_path: str, assistant_implementation: str) -> None:
        old_contents = ''
        strict_target_path = self.choose_file_path(target_path)
        complete_target_path = os.path.join(os.getcwd(), strict_target_path)
        dir_path = os.path.dirname(complete_target_path)
        
        try:
            os.makedirs(dir_path, exist_ok=True)
            with open(complete_target_path, 'r') as f:
                old_contents = f.read()
        except FileNotFoundError:
            pass

        context = ''
        if not old_contents:
            context = 'You are writing to a new file.'
        else:
            context = f'This is the starting code: {old_contents}\n'

        query = (
            f'{context}'
            f'This is the solution provided by an expert engineer: {assistant_implementation}.\n'
            'Your job is to **incorporate the solution above into the starting code**, following the steps outlined above.\n'
            'Do not add explanations, and ensure that the code you write is both syntactically and semantically correct.\n'
        )

        llm_res = self.llm.new_chat_request(
            messages=[{
                'role': 'user',
                'content': query,
            }],
            loading_message=f'✍️  Writing the changes to {strict_target_path}...',
        )

        new_contents = self.clean_backticks(llm_res)
        
        with open(complete_target_path, 'w') as f:
            f.write(new_contents)
    
    def choose_file_path(self, given_file_path: str) -> str:
        with open(config.get_current_files_path(), 'r') as f:
            strict_file_paths = f.read().split('\n')

            for strict_file_path in strict_file_paths:
                if given_file_path in strict_file_path:
                    return strict_file_path
        
        return given_file_path

    def clean_backticks(self, text: str) -> str:
        try:
            pattern = r"```(?:\w+\n)?(.*?)```"
            return re.search(pattern, text, re.DOTALL).group(1)
        except AttributeError:
            return text
