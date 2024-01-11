import os
from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.models.llm import LLM
from flamethrower.models.openai_client import OpenAIClient

system_message = """
You are an extremely experienced senior engineer and have seen many different codebases.
Given a file in a repository, you can easily summarize the function of the file as part of a larger codebase.
This file can take any text form from code (.py, .ts, ... ) to descriptive files (.json, .md, ... ).
Given:
  1. A description of what the entire project is about
  2. A single file in the project
You have a single, crucial objective: **Summarize the function/content of the file as part of the larger project in 2-3 sentences.**
Start every file by saying "This file is about..."
"""

class Summarizer(BaseModel):
    llm: LLM = None

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = OpenAIClient(system_message=system_message)
    
    async def summarize_file(self, main_project_description: str, file_contents: str) -> str:
        try:
            query = (
                f'This project is about {main_project_description}.\n'
                'This is the file to summarize:'
                f'\n```\n{file_contents}\n```\n'
                'Summarize this file as part of the larger project.'
            )

            return await self.llm.new_async_chat_request(
                messages=[{
                    'role': 'user',
                    'content': query,
                }],
            )
        except Exception:
            # Other exceptions from the LLM
            return 'Encountered error summarizing this file'
    
    def summarize_readme(self) -> str:
        summary_path = config.get_workspace_summary_path()
        if os.path.exists(summary_path):
            with open(summary_path, 'r') as summary_file:
                return summary_file.read()
        
        summary = ''
        try:
            with open(os.path.join(os.getcwd(), 'README.md'), 'r') as readme_file:
                file_contents = readme_file.read()
                query = (
                    'This is the repository main readme file.\n'
                    f'\n```\n{file_contents}\n```\n'
                    'Read it carefully and summarize what the project is about, and what technology stack is being used.\n'
                )

                summary = self.llm.new_chat_request(
                    messages=[{
                        'role': 'user',
                        'content': query,
                    }],
                    loading_message=f'📚 Learning project...',
                )
        except FileNotFoundError:
            summary = 'This project does not have a README. Infer from other files the purpose of this project.'
        except Exception:
            summary = 'Unable to summarize README.'
        finally:
            with open(summary_path, 'w') as summary_file:
                    summary_file.write(summary)
                
            return summary
