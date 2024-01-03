from pydantic import BaseModel
import  flamethrower.config.constants as config
from flamethrower.models.llm import LLM
from flamethrower.utils.token_counter import TokenCounter

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
    llm: LLM = None
    token_counter: TokenCounter = None

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = LLM(
            system_message=system_message,
            token_counter=self.token_counter,
        )
    
    def infer_target_file_paths(self, description: str, dir_structure: str, user_query: str) -> list[str]:
        dir_info = ''
        with open(config.get_dir_dict_path(), 'r') as f:
            try:
                dir_info = f.read()
            except FileNotFoundError:
                print('Workspace has not been analyzed. Please restart flamethrower.')
                pass
        
        query = (
            f'This workspace is about [{description}].'
            f'The directory structure is given as:\n{dir_structure}\n'
            f'Each file in the workspace has its own function summarized, and is given as a json object:\n{dir_info}'
            f'Given the coding job [{user_query}], return a list of `file_paths` that are **relevant to the user query**.'
        )
        res = self.llm.new_json_request(
            query=query,
            json_schema=json_schema,
            loading_message='🗃️  Choosing relevant files...',
        )
        
        # TODO: allow user to select which files
        file_paths = res['file_paths'][:self.max_files_used]
        
        return file_paths
    