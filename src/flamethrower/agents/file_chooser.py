from pydantic import BaseModel
import  flamethrower.config.constants as config
from flamethrower.models.llm import LLM
from flamethrower.models.openai_client import OpenAIClient

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
    llm: LLM = None
    max_files_used: int = 8

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = OpenAIClient(system_message=system_message)
    
    def infer_target_file_paths(self, description: str, dir_structure: str, user_query: str) -> list[str]:
        dir_info = ''
        try:
            with open(config.get_dir_dict_path(), 'r') as f:
                dir_info = f.read()
        except FileNotFoundError:
            print('Workspace has not been analyzed. Please restart flamethrower.')
            pass
        
        try:
            with open(config.get_pretty_conversation_path(), 'r') as f:
                stdout_logs = f.read()
                stdout_logs = f'Here are the most recent stdout logs {stdout_logs}' if stdout_logs else ''
            
                query = (
                    f'This workspace is about [{description}].'
                    f'The directory structure is given as:\n{dir_structure}\n'
                    f'Each file in the workspace has its own function summarized, and is given as a json object:\n{dir_info}'
                    f'{stdout_logs}'
                    f'Given the logs and the coding job [{user_query}], return a list of `file_paths` that are **relevant to the user query**.'
                )

                res = self.llm.new_json_request(
                    query=query,
                    json_schema=json_schema,
                    loading_message='🗃️  Choosing relevant files...', # 2 whitespaces to render properly
                )
                
                # TODO: allow user to select which files
                file_paths = res['file_paths'][:self.max_files_used]
                self.write_to_current_files(file_paths)
                
                return file_paths
        except FileNotFoundError:
            pass
        except Exception:
            return []

    def write_to_current_files(self, file_paths: list) -> None:
        with open(config.get_current_files_path(), 'w') as f:
            for file_path in file_paths:
                f.write(file_path + '\n')
