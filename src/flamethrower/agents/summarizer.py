import os
from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.models.llm import LLM
from flamethrower.utils.token_counter import TokenCounter

system_message = """
You are an extremely experienced senior engineer and have seen many different codebases.
Given a file in a repository, you can easily summarize the function of the file as part of a larger codebase.
This file can take any text form from code (.py, .ts, ... ) to descriptive files (.json, .md, ... ).
Given:
  1. A description of what the entire project is about
  2. A single file in the project
You have a single, crucial objective: **Summarize the function/content of the file as part of the larger project in 2-3 sentences.**
"""

class Summarizer(BaseModel):
    llm: LLM = None
    token_counter: TokenCounter = None

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = LLM(
            system_message=system_message,
            token_counter=self.token_counter,
        )
    
    async def summarize_file(self, main_project_description: str, file_name: str) -> str:
        file_contents = ''
        with open(os.path.join(os.getcwd(), file_name)) as f:
            try:
                file_contents = f.read()
            except FileNotFoundError:
                print(f'File not found: {file_name}')
            except UnicodeDecodeError:
                pass
        if not file_contents:
            return ''

        query = (
            f'This project is about {main_project_description}.\n'
            'This is the file to summarize:'
            f'\n```\n{file_contents}\n```\n'
            'Summarize this file as part of the larger project.'
        )
        summary = await self.llm.new_async_chat_request(
            messages=[
                {
                    'role': 'system',
                    'content': system_message,
                },
                {
                    'role': 'user',
                    'content': query,
                }
            ],
        )

        return summary
    
    def summarize_readme(self) -> str:
        summary_path = config.get_workspace_summary_path()
        if os.path.exists(summary_path):
            with open(summary_path, 'r') as summary_file:
                return summary_file.read()
        
        readme_file_path = os.path.join(os.getcwd(), 'README.md')
        with open(readme_file_path, 'r') as readme_file:
            try:
                file_contents = readme_file.read()
                query = (
                    'This is the repository main readme file.\n'
                    f'\n```\n{file_contents}\n```\n'
                    'Read it carefully and summarize what the project is about, and what technology stack is being used.\n'
                )
                summary = self.llm.new_chat_request(
                    messages=[
                        {
                            'role': 'system',
                            'content': system_message,
                        },
                        {
                            'role': 'user',
                            'content': query,
                        }
                    ],
                    loading_message=f'📚 Learning project...'
                )
                with open(summary_path, 'w') as summary_file:
                    summary_file.write(summary)
                
                return summary
            except FileNotFoundError:
                # TODO: propagate error upwards
                print(f'File not found: {readme_file}')
