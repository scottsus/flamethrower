from pydantic import BaseModel
from flamethrower.models.llm import LLM

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
You are an extremely experienced senior engineer who can understand projects easily.
Given a task, you're really good at looking at files in the workspace and determining which ones are relevant to the task.
You have a single, crucial objective: **given a user query, determine which files are most relevant to the query**.
You must be strict about whether or not a file deserves to be considered to complete the task, returning a minimal set of files.
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
        self.llm = LLM(system_message=system_message)
    
    def infer_target_file_paths(self, description: str, dir_structure: str, query: str) -> list[str]:
        query = (
            f'This workspace is about {description}. '
            f'Given the directory structure {dir_structure}, '
            f'Determine which files are relevant to the following user query: "{query}". '
        )
        res = self.llm.new_json_request(
            query=query,
            json_schema=json_schema,
            loading_message='🗃️  Choosing relevant files...'
        )

        # TODO: allow user to select which files
        file_paths = res['file_paths'][:self.max_files_used]
        
        print('👀 Focusing on the following files:', file_paths)
        return file_paths