import os
import re
from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.models.llm import LLM
from flamethrower.models.models import OPENAI_GPT_3_TURBO
from flamethrower.models.openai_client import OpenAIClient

json_schema = {
    'type': 'object',
    'properties': {
        'needs_editing': {
            'type': 'boolean',
        },
        'edited_code': {
            'type': 'string',
        },
    },
    'required': ['needs_editing'],
    'allOf': [
        {
            'if': { 'properties': { 'needs_editing': { 'const': True } } },
            'then': { 'required': ['edited_code'] }
        },
    ]
}

system_message = f"""
You are an incredible software engineer but terribly lazy.
You have the **talent to write amazing quality code, but if someone else has already done it, you'd rather just copy and paste it**.
You have a single, crucial task: Given a current working file and another engineer's suggestions on how to fix this current file (which contains code) you must:
  1. Understand the suggestion carefully
  2. Look at the new code
  3. If the code snippet is a complete solution that completes the current working file, then simply indicate that needs_editing is false.
     Someone else will copy and paste the code for you, and your job is done. Hooray!
  4. Otherwise, if the code snippet is a partial solution, then you must indicate needs_editing is true.
     Not only that, you must completely rewrite the current working file, implementing the new code snippet into the current working file.

Remember, speed is of the essence. You want to get off work ASAP, so you don't want to do any extra work.
At the same time, if you simply copy & paste and the file doesn't even compile, then you'll be in huge trouble.

It is crucial that you return a JSON object with the following schema:
    {json_schema}
"""

class FileWriter(BaseModel):
    base_dir: str
    llm: LLM = None

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = OpenAIClient(system_message=system_message, model=OPENAI_GPT_3_TURBO)
    
    def write_code(self, target_path: str, assistant_implementation: str) -> None:
        old_contents = ''
        strict_target_path = self.choose_file_path(target_path)
        complete_target_path = os.path.join(self.base_dir, strict_target_path)
        dir_path = os.path.dirname(complete_target_path)
        
        try:
            os.makedirs(dir_path, exist_ok=True)
            with open(complete_target_path, 'r') as f:
                old_contents = f.read()
        except FileNotFoundError:
            pass

        context = f'This is the starting code: {old_contents}\n' if old_contents else 'You are writing to a new file'

        query = (
            f'{context}'
            f'This is the solution provided by an expert engineer: {assistant_implementation}.\n'
            'Your job is to **incorporate the solution above into the starting code**, following the steps outlined above.\n'
            'Do not add explanations, and ensure that the code you write is both syntactically and semantically correct.\n'
        )

        try:
            decision = self.llm.new_json_request(
                query=query,
                json_schema=json_schema,
                loading_message=f'✍️  Writing the changes to {strict_target_path}...'
            )
            if decision is None:
                raise Exception('FileWriter unable to write code. You may need to implement suggestions yourself.')
            
            new_contents = ''
            if not decision['needs_editing']:
                new_contents = self.clean_backticks(assistant_implementation)
            else:
                new_contents = self.clean_backticks(decision['edited_code'])
            
            with open(complete_target_path, 'w') as f:
                f.write(new_contents)
        except Exception:
            raise
    
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
