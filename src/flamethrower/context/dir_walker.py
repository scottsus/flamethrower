import os
import json
import asyncio
from pathspec import PathSpec
from pydantic import BaseModel
from typing import IO
import flamethrower.config.constants as config
from flamethrower.agents.summarizer import Summarizer
from flamethrower.utils.loader import Loader

class DirectoryWalker(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    base_dir: str = os.getcwd()
    file_paths: dict = {}
    workspace_summary: str = ''
    summarization_tasks: list = []
    semaphore: asyncio.Semaphore = None
    summarizer: Summarizer = None

    def __init__(self, **data):
        super().__init__(**data)
        self.semaphore = asyncio.Semaphore(10)
        self.summarizer = Summarizer()

        try:
            with open(config.get_dir_dict_path(), 'r') as dir_dict_file:
                self.file_paths = json.loads(dir_dict_file.read())
        except FileNotFoundError:
            pass
        
        try:
            with open(config.get_workspace_summary_path(), 'r') as workspace_summary_file:
                self.workspace_summary = workspace_summary_file.read()
        except FileNotFoundError:
            pass

    async def generate_directory_summary(self, start_path) -> None:
        with Loader(
            loading_message='🔧 Performing workspace first time setup (should take about 30s)...',
        ).managed_loader():
            with open(config.get_dir_tree_path(), 'w') as dir_tree_file:
                self.process_directory(start_path, dir_tree_file, gitignore=self.get_gitignore())

            await asyncio.gather(*self.summarization_tasks)
            with open(config.get_dir_dict_path(), 'w') as dir_dict_file:
                dir_dict_file.write(json.dumps(self.file_paths, indent=2))

    def process_directory(self, dir_path: str, summary_file: str, prefix: IO[str] = '', gitignore: PathSpec = None) -> None:
        entries = os.listdir(dir_path)
        
        if gitignore:
            entries = [
                e for e in entries if (
                    not gitignore.match_file(e)
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
    
    def get_directory_tree(self) -> None:
        with open(config.get_dir_tree_path(), 'r') as dir_tree_file:
            return dir_tree_file.read()
    
    def get_gitignore(self) -> PathSpec:
        patterns = []
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as gitignore_file:
                for line in gitignore_file:
                    patterns.append(line.strip().lstrip('/').rstrip('/'))
            return PathSpec.from_lines('gitwildmatch', patterns)
        else:
            sample_gitignore_path = os.path.join(
                os.getcwd(), 'src', 'flamethrower', 'setup', 'src', '.sample.gitignore'
            )
            with open(sample_gitignore_path, 'r') as f:
                return PathSpec.from_lines('gitwildmatch', f.read().splitlines())

    async def update_file_paths(self, file_path: str) -> None:
        relative_path = os.path.relpath(file_path, self.base_dir)
        if relative_path in self.file_paths:
            return
        
        async with self.semaphore:
            with open(file_path) as f:
                try:
                    file_contents = f.read()
                    file_summary = await self.summarizer.summarize_file(
                        main_project_description=self.workspace_summary,
                        file_contents=file_contents
                    )
                    
                    self.file_paths[relative_path] = file_summary
                except FileNotFoundError:
                    pass
                except UnicodeDecodeError:
                    pass

def setup_dir_summary() -> None:
    dir_walker = DirectoryWalker()
    asyncio.run(dir_walker.generate_directory_summary(
        os.path.join(os.getcwd())
    ))
