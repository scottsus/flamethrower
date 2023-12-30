import os
import re
from pydantic import BaseModel
from models.llm import LLM

system_message = """
You are an extremely powerful programming assistant that can write flawless code.
You have a single, crucial task: Given an expert engineer's coding response and a target file:
  1. Read the target file, if it exists
  2. Understand the expert engineer's response and extract the code
  3. Meaningfully incorporate the extracted code into the target file
You are completely overwriting the existing target file, so it is imperative that 
the code you write is both syntactically and semantically correct.
"""

class FileWriter(BaseModel):
    llm: LLM = None

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = LLM(system_message=system_message)
    
    def write_code(self, target_path: str, assistant_implementation: str) -> None:
        old_contents = ''
        target_path = os.path.join(os.getcwd(), target_path)
        try:
            with open(target_path, 'r') as f:
                old_contents = f.read()
        except FileNotFoundError:
            pass

        query = (
            f'This is the starting code: {old_contents}.\n'
            f'This is the solution provided by an expert engineer: {assistant_implementation}.\n'
            'Your job is to **incorporate the solution above into the starting code**, following the steps outlined above.\n'
            'Do not add explanations, and ensure that the code you write is both syntactically and semantically correct.\n'
        )

        llm_res = self.llm.new_chat_request(
            messages=[
                {
                    'role': 'system',
                    'content': self.llm.system_message,
                },
                {
                    'role': 'user',
                    'content': query,
                }
            ],
            loading_message=f'✍️  Writing the changes to {target_path}...',
        )

        new_contents = self.clean_backticks(llm_res)
        
        with open(target_path, 'w') as f:
            f.write(new_contents)

    def clean_backticks(self, text: str) -> str:
        try:
            pattern = r"```(?:\w+\n)?(.*?)```"
            return re.search(pattern, text, re.DOTALL).group(1)
        except AttributeError:
            return text
