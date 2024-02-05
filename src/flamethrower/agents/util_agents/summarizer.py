from pydantic import BaseModel
from flamethrower.models.llm import LLM
from flamethrower.models.models import OPENAI_GPT_3_TURBO
from typing import Any

system_message = """
You are an extremely experienced senior engineer and have seen many different codebases.
Given a file in a repository, you can easily summarize the function of the file as part of a larger codebase.
This file can take any text form from code (.py, .ts, ... ) to descriptive files (.json, .md, ... ).
Given:
  1. A description of what the entire project is about
  2. A single file in the project
You have a single, crucial objective: **Summarize the function/content of the file as part of the larger project in 2-3 sentences.**
Start every file by saying:
  - If it's a README file, say "This folder is about...", describing the general function of the folder.
  - Otherwise, say "This file is about...", describing the specific function of the file.
"""

class Summarizer(BaseModel):
    max_file_len: int = 30_000 # TODO: count actual tokens and cut accordingly

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._llm: LLM = LLM(system_message=system_message, model=OPENAI_GPT_3_TURBO)
    
    @property
    def llm(self) -> LLM:
        return self._llm
    
    async def summarize_file(self, main_project_description: str, file_contents: str) -> str:
        file_contents = file_contents[:self.max_file_len]

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
        except Exception as e:
            return f'Error: {str(e)}'
    
    def summarize_readme(self, readme_file_contents: str) -> str:
        try:
            query = (
                'This is the repository main readme file.\n'
                f'\n```\n{readme_file_contents}\n```\n'
                'Read it carefully and summarize what the project is about, and what technology stack is being used.\n'
                'Start the summary by saying "This project is about..."\n'
            )

            return self.llm.new_chat_request(
                messages=[{
                    'role': 'user',
                    'content': query,
                }]
            )
        except Exception:
            raise
