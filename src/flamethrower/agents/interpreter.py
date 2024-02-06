from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.models.llm import LLM
from typing import Any, Dict, List

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
                        'enum': ['run', 'write', 'completed'] # exclude need_context for now
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
                ]
            }
        },
    },
    'required': ['actions']
}

system_message = f"""
You are an extremely powerful programming assistant that lives inside the unix terminal.
You have a single, crucial task: to categorize LM responses into a list of 3 possible actions:
  1. Run a command on the terminal and observe its output
  2. Rewrite code in a given target file
  3. Indicate that the job is completed.

You **should choose multiple actions to perform**. For example:
  - If you are writing to a file, you **must also return a `run` action to test what you wrote.**
  - If you obtained a code snippet, it is likely code you would need to implement and write to a file.

Other notes:
  - Sometimes, the responses are explanations with some code snippets.
    - as is the case with pure explanations, they are informative, so no further action is required.
    - in this case, you should just return a `completed` action.

It is crucial that you return a JSON object with the following JSON Schema:
    {json_schema}
"""

class Interpreter(BaseModel):
    json_schema: Dict[str, Any] = json_schema

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._llm: LLM = LLM(system_message=system_message)
    
    @property
    def llm(self) -> LLM:
        return self._llm
    
    def make_decision_from(self, objective: str, last_response: str) -> List[Dict[Any, Any]]:
        target_files = self.get_target_files()
        target_files_line = f'Currently you are working with the following files: {target_files}\n' if target_files else ''

        query = (
            f'This is the objective:\n{objective}.\n'
            f'This is the last response:\n{last_response}\n'
            f'{target_files_line}'
            'Given this objective and response, choose a possible action.'
        )

        try:
            res = self.llm.new_json_request(
                query=query,
                json_schema=self.json_schema
            )
            
            if not res:
                raise Exception('interpreter.make_decision_from: res is None')
            
            if not isinstance(res, dict):
                raise Exception(f'interpreter.make_decision_from: res not type dict, got {type(res)}')
            
            actions = res.get('actions', [{}])
            if not isinstance(actions, list):
                raise Exception(f'interpreter.make_decision_from: actions not type list, got {type(actions)}')
            
            if len(actions) > 1:
                last_action = actions[-1].get('action', '')
                if last_action == 'completed':
                    return actions[:-1]
            
            return actions

        except KeyboardInterrupt:
            raise
        except Exception:
            raise

    def get_target_files(self) -> List[str]:
        try:
            with open(config.get_current_files_path(), 'r') as f:
                return f.read().split('\n')
        except FileNotFoundError:
            return []
    