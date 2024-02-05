from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.models.llm import LLM
from flamethrower.exceptions.exceptions import *
from typing import Any, List

json_schema = {
    'type': 'object',
    'properties': {
        'file_paths': {
            'type': 'array',
            'items': {
                'type': 'string'
            }
        }
    },
    'required': ['file_paths']
}

system_message = f"""
You are an extremely experienced senior engineer pair programming with a junior engineer.
The junior engineer's job is debugging some issue in the workspace.
You have a single, crucial objective: **given a coding job, look at the files in the workspace and accurately determine which files are relevant to the job.**
You must be strict about whether or not a file deserves to be considered to complete the job, returning a minimal set of files.
You must return a JSON object with a list of file names. The JSON schema is given for your reference.
    {json_schema}
Important notes:
 - The file names need to include their relative paths.
 - Together, the **file paths MUST exist in the directory structure** which will be provided.
 - If you think no files are relevant, return an empty list.
"""

class FileChooser(BaseModel):
    max_files_used: int = 8

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._llm: LLM = LLM(system_message=system_message)
    
    @property
    def llm(self) -> LLM:
        return self._llm
    
    def infer_target_file_paths(self, description: str, dir_structure: str, conv: str) -> List[str]:
        dir_info = ''
        try:
            with open(config.get_dir_dict_path(), 'r') as f:
                dir_info = f.read()
        except FileNotFoundError:
            pass
        
        try:
            query = (
                f'{description}.\n'
                f'The directory structure is given as:\n{dir_structure}\n'
                f'Each file in the workspace has its own function summarized, and is given as a json object:\n{dir_info}\n'
                f'Here is the most recent conversation between the you and the user:\n{conv}\n'
                'Given all this conversation history, return a list of `file_paths` that are **most relevant to the conversation**.'
            )

            res = self.llm.new_json_request(
                query=query,
                json_schema=json_schema
            )

            if not res:
                raise Exception('FileChooser.infer_target_file_paths: res is empty')
            
            if not isinstance(res, dict):
                raise Exception(f'FileChooser.infer_target_file_paths: expected a dict, got {type(res)}')
            
            file_paths = res.get('file_paths', [])[:self.max_files_used]
            if not isinstance(file_paths, list):
                raise Exception(f'FileChooser.infer_target_file_paths: expected a list, got {type(file_paths)}')
            
            self.write_to_current_files(file_paths)
            return file_paths
        except KeyboardInterrupt:
            raise
        except QuotaExceededException:
            raise
        except Exception:
            return []

    def write_to_current_files(self, file_paths: List[str]) -> None:
        with open(config.get_current_files_path(), 'w') as f:
            for file_path in file_paths:
                f.write(file_path + '\n')
