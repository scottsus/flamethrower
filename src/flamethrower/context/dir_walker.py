import os
import json
import asyncio
from pathspec import PathSpec
from pydantic import BaseModel
from typing import IO
import flamethrower.config.constants as config
from flamethrower.agents.summarizer import Summarizer
from flamethrower.utils.loader import Loader
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.context.sample_gitignore import sample_gitignore

class DirectoryWalker(BaseModel):
    base_dir: str = os.getcwd()
    file_paths: dict = {}
    summarization_tasks: list = []
    summarizer: Summarizer = None
    token_counter: TokenCounter = None
    loader: Loader = None

    def __init__(self, **data):
        super().__init__(**data)
        self.summarizer = Summarizer(
            token_counter=self.token_counter
        )

        try:
            with open(config.get_dir_dict_path(), 'r') as dir_dict_file:
                self.file_paths = json.loads(dir_dict_file.read())
        except FileNotFoundError:
            pass
    
    def get_directory_tree(self) -> None:
        with open(config.get_dir_tree_path(), 'r') as dir_tree_file:
            return dir_tree_file.read()

    async def generate_directory_summary(self, start_path) -> None:
        gitignore = None
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as gitignore_file:
                gitignore = PathSpec.from_lines('gitwildmatch', gitignore_file.readlines())
        else:
            gitignore = PathSpec.from_lines('gitwildmatch', sample_gitignore.splitlines())

        with Loader(
            loading_message='🔧  Performing workspace first time setup (should take about 30s)...',
            completion_message='📖 Workspace analyzed.',
            will_report_timing=True
        ).managed_loader():
            with open(config.get_dir_tree_path(), 'w') as dir_tree_file:
                self.process_directory(start_path, dir_tree_file, gitignore=gitignore)

            await asyncio.gather(*self.summarization_tasks)
            with open(config.get_dir_dict_path(), 'w') as dir_dict_file:
                dir_dict_file.write(json.dumps(self.file_paths, indent=2))

    def process_directory(self, dir_path: str, summary_file: str, prefix: IO[str] = '', gitignore: PathSpec = None) -> None:
        entries = os.listdir(dir_path)

        if gitignore:
            entries = [
                e for e in entries if (
                    not gitignore.match_file(os.path.join(dir_path, e))
                    and e != '.git'
                    and e != '.flamethrower'
                )
            ]

        hidden_dirs = [
            d for d in entries
            if os.path.isdir(os.path.join(dir_path, d))
            and d.startswith('.')
        ]
        regular_dirs = [
            d for d in entries
            if os.path.isdir(os.path.join(dir_path, d))
            and not d.startswith('.')
        ]
        files = [
            f for f in entries
            if os.path.isfile(os.path.join(dir_path, f))
        ]

        hidden_dirs.sort()
        regular_dirs.sort()
        files.sort()

        sorted_entries = hidden_dirs + regular_dirs + files
        for i, entry in enumerate(sorted_entries):
            path = os.path.join(dir_path, entry)

            if os.path.isdir(path):
                self.process_subdirectory(path, i, len(sorted_entries), summary_file, prefix, gitignore)
            else:
                self.write_file_entry(entry, i, len(sorted_entries), summary_file, prefix)
                self.summarization_tasks.append(self.update_file_paths(path))

    def process_subdirectory(self, path: str, index: int, total: int, summary_file: IO[str], prefix: str, gitignore: PathSpec) -> None:
        connector = '├──' if index < total - 1 else '└──'
        summary_file.write(f'{prefix}{connector} {os.path.basename(path)}\n')

        ext_prefix = '│   ' if index < total - 1 else '    '
        self.process_directory(path, summary_file, prefix=(prefix + ext_prefix), gitignore=gitignore)

    def write_file_entry(self, file_name: str, index: int, total: int, summary_file: IO[str], prefix: str) -> None:
        connector = '├──' if index < total - 1 else '└──'
        summary_file.write(f'{prefix}{connector} {file_name}\n')

    async def update_file_paths(self, file_path: str) -> None:
        relative_path = os.path.relpath(file_path, self.base_dir)
        if relative_path in self.file_paths:
            return
        
        file_contents = await self.summarizer.summarize_file(
            main_project_description='',
            file_name=file_path
        )
        
        self.file_paths[relative_path] = file_contents
