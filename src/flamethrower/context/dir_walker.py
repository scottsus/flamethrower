import os
import json
import asyncio
from pathspec import PathSpec
from pydantic import BaseModel
from typing import IO
from rich.progress import Progress
import flamethrower.config.constants as config
from flamethrower.agents.summarizer import Summarizer
from flamethrower.shell.printer import Printer
from flamethrower.shell.shell_manager import ShellManager
from flamethrower.utils.colors import *

class SummaryManager(BaseModel):
    max_summarization_tasks: int = 100
    summarization_tasks: list = []
    summarization_tasks_copy: list = []
    timeout: float = 0.2

    async def get_summarizations_with_timeout(self) -> list:
        if len(self.summarization_tasks) > self.max_summarization_tasks:
            await self.cancel_summarization_tasks(self.summarization_tasks)
            await self.cancel_summarization_tasks(self.summarization_tasks_copy)
            error_message = (
                f'📚 Workspace too large ({len(self.summarization_tasks)}/100). '
                f'{STDIN_DEFAULT.decode("utf-8")}Please consider narrowing your workspace by using\n\n'
                f'  $ `{STDIN_GREEN.decode("utf-8")}flamethrower{STDIN_DEFAULT.decode("utf-8")} '
                f'{STDIN_UNDERLINE.decode("utf-8")}./more/specific/folder`{STDIN_DEFAULT.decode("utf-8")}\n\n'
                'Otherwise, consider adding some folders to your `.gitignore` file.\n'
            )
            raise Exception(error_message)

        try:
            res_list = await asyncio.wait_for(asyncio.gather(*self.summarization_tasks_copy), timeout=self.timeout)
            await self.cancel_summarization_tasks(self.summarization_tasks)
        except asyncio.TimeoutError:
            with Progress() as progress:
                task_id = progress.add_task("[cyan]🏗️  Learning workspace...", total=len(self.summarization_tasks))
                summarization_tasks_with_progress = [
                    self.perform_async_task(summarization_task, progress, task_id)
                    for summarization_task in self.summarization_tasks
                ]
                res_list = await asyncio.gather(*summarization_tasks_with_progress)
            await self.cancel_summarization_tasks(self.summarization_tasks_copy)
        
        return res_list
    
    async def perform_async_task(self, task: None, progress: Progress, task_id: int, step: int = 1):
        res = await task
        progress.update(task_id, advance=step)

        return res
    
    async def cancel_summarization_tasks(self, task_list: list) -> None:
        tasks = [
            asyncio.create_task(t) 
            if not isinstance(t, asyncio.Task)
            else t for t in task_list
        ]

        for task in tasks:
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def add_summarization_task(self, task: None, task_copy: None) -> None:
        self.summarization_tasks.append(task)
        self.summarization_tasks_copy.append(task_copy)

class DirectoryWalker(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    base_dir: str
    file_paths: dict = {}
    workspace_summary: str = ''
    semaphore: asyncio.Semaphore = None
    summarizer: Summarizer = None
    summary_manager: SummaryManager = None
    printer: Printer

    def __init__(self, **data):
        super().__init__(**data)
        self.semaphore = asyncio.Semaphore(10)
        self.summarizer = Summarizer()
        self.summary_manager = SummaryManager()

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

    async def generate_directory_summary(self) -> None:
        try:
            with open(config.get_dir_tree_path(), 'w') as dir_tree_file:
                self.process_directory(self.base_dir, dir_tree_file, gitignore=self.get_gitignore())
        except FileNotFoundError:
            raise Exception(f'The given subdirectory {self.base_dir} does not exist.')
        
        try:
            self.printer.print_regular(with_newline=True)
            num_tasks_completed = sum(await self.summary_manager.get_summarizations_with_timeout())
            if num_tasks_completed > 0:
                self.printer.print_default(f'🏗️  Learned {num_tasks_completed} new files.\n\n')

            with open(config.get_dir_dict_path(), 'w') as dir_dict_file:
                dir_dict_file.write(json.dumps(self.file_paths, indent=2))
        except KeyboardInterrupt:
            raise
        except Exception:
            raise

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
                self.summary_manager.add_summarization_task(self.update_file_paths(path), self.update_file_paths(path))

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

    async def update_file_paths(self, file_path: str) -> int:
        relative_path = os.path.relpath(file_path, self.base_dir)
        if relative_path in self.file_paths:
            return 0
        
        async with self.semaphore:
            with open(file_path) as f:
                try:
                    file_contents = f.read()
                    file_summary = await self.summarizer.summarize_file(
                        main_project_description=self.workspace_summary,
                        file_contents=file_contents
                    )
                    
                    self.file_paths[relative_path] = file_summary
                    return 1
                except FileNotFoundError:
                    return 0
                except UnicodeDecodeError:
                    return 0

def setup_dir_summary(base_dir: str, printer: Printer, shell_manager: ShellManager) -> None:
    dir_walker = DirectoryWalker(
        base_dir=os.path.join(os.getcwd(), base_dir),
        printer=printer
    )
    try:
        with shell_manager.cooked_mode():
            asyncio.run(dir_walker.generate_directory_summary())
    except KeyboardInterrupt:
        printer.print_yellow('\nLearning process interrupted. Workspace knowledge may be incomplete.\n', reset=True)
    except Exception:
        raise
