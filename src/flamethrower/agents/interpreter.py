from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.models.llm import LLM
from flamethrower.models.openai_client import OpenAIClient

json_schema = {
    'type': 'object',
    'properties': {
        'actions': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'action': {
                        'type': 'string',
                        'enum': ['run', 'write', 'debug', 'stuck', 'cleanup', 'completed'] # exclude need_context for now
                    },
                    'command': { 'type': 'string' },
                    # TODO: file_paths should be a list of strings
                    'file_paths': { 'type': 'string' }
                },
                'required': ['action'],
                'allOf': [
                    {
                        'if': { 'properties': { 'action': { 'const': 'run' } } },
                        'then': { 'required': ['command'] }
                    },
                    {
                        'if': { 'properties': { 'action': { 'const': 'write' } } },
                        'then': { 'required': ['file_paths'] }
                    },
                    {
                        'if': { 'properties': { 'action': { 'const': 'debug' } } },
                        'then': { 'required': ['file_paths'] }
                    },
                    {
                        'if': { 'properties': { 'action': { 'const': 'cleanup' } } },
                        'then': { 'required': ['file_paths'] }
                    },
                ]
            }
        },
    },
    'required': ['actions']
}

system_message = f"""
You are an extremely powerful programming assistant that lives inside the unix terminal.
You have a single, crucial task: to categorize LLM responses into a list of 6 possible actions:
  1. Run a command on the terminal and observe its output
  2. Rewrite code in a given target file
  3. If you encounter an error, write print statements to the target file to debug for the next iteration.
  4. If you have been trying for awhile with no success, indicate that you are stuck and need help.
  5. As best as possible, be extremely concise in code, and clean the file of print statements
  6. Indicate that your job has been completed. **If so, don't recommend other tests or suggestions.**

You **should choose multiple actions to perform**. For example:
- If you are writing to a file, you **must also return a `run` action to test what you wrote.**
- If you are debugging, you **must also follow it up with a `run` action and further `write` actions to identify the issue.**
  - Once you tested the new code and realized you got a positive output, indicate your job is completed.
- However, **never include a `completed` action with other actions. It should be the only action in the list**.

Importantly, **you are lazy**. If a job appears to be completed, mark it as completed, and don't recommend other tests or suggestions.
Other notes:
  - If you obtained a code snippet, it is likely code you would need to implement and write to a file.
  - Favor running python3 versus python, and pip3 versus pip.
  - Favor running the file itself with python3, versus testing the file with pytest or other testing frameworks.

It is crucial that you return a JSON object with the following JSON Schema:
    {json_schema}
"""

class Interpreter(BaseModel):
    llm: LLM = None
    json_schema: dict = json_schema

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = OpenAIClient(system_message=system_message)
    
    def make_decision_from(self, objective: str, last_response: str) -> dict:
        target_files = self.get_target_files()
        target_files_line = f'Currently you are working with the following files: {target_files}\n' if target_files else ''

        query = (
            f'This is the objective:\n{objective}.\n'
            f'This is the last response:\n{last_response}\n'
            f'{target_files_line}'
            'Given this objective and response, choose a possible action.'
        )

        try:
            return self.llm.new_json_request(
                query=query,
                json_schema=self.json_schema,
                loading_message='🤖 Determining next step...',
            )
        except KeyboardInterrupt:
            raise
        except Exception:
            return None

    def get_target_files(self) -> list:
        try:
            with open(config.get_current_files_path(), 'r') as f:
                return f.read().split('\n')
        except FileNotFoundError:
            return ''
        
