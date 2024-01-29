import os
import json
import asyncio
from pathspec import PathSpec
from importlib import resources
from pydantic import BaseModel, ConfigDict
from typing import IO
from rich.progress import Progress
import flamethrower.config.constants as config
from flamethrower.agents.summarizer import Summarizer
from flamethrower.shell.shell_manager import ShellManager
from flamethrower.shell.printer import Printer
from flamethrower.utils.colors import *

class SummaryManager(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    max_summarization_tasks: int = 100
    summarization_tasks: list = []
    summarization_tasks_copy: list = []
    instant_timeout: float = 0.5
    summarization_timeout: int = 75
    lock: asyncio.Lock = None

    def __init__(self, **data):
        super().__init__(**data)
        self.lock = asyncio.Lock()

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
            res_list = await asyncio.wait_for(
                self.safe_gather(self.summarization_tasks_copy),
                timeout=self.instant_timeout
            )
        
        except asyncio.TimeoutError:
            try:
                with Progress() as progress:
                    task_id = progress.add_task(
                        f'[cyan]🏗️  Learning workspace (max {self.summarization_timeout}s)...',
                        total=len(self.summarization_tasks)
                    )
                    summarization_tasks_with_progress = [
                        self.perform_async_task(summarization_task, progress, task_id)
                        for summarization_task in self.summarization_tasks
                    ]
                    res_list = await asyncio.wait_for(
                        self.safe_gather(summarization_tasks_with_progress),
                        timeout=self.summarization_timeout
                    )
            except asyncio.TimeoutError:
                pass
        
        except Exception:
            raise
        
        finally:
            try:
                await self.cancel_summarization_tasks(self.summarization_tasks)
                await self.cancel_summarization_tasks(self.summarization_tasks_copy)
            except Exception as e:
                print(f'get_summarizations_with_timeout: {e}')
        
            return res_list
    
    async def perform_async_task(self, task: None, progress: Progress, task_id: int, step: int = 1):
        try:
            return await task
        except asyncio.CancelledError:
            pass
        finally:
            with await self.lock:
                progress.update(task_id, advance=step, refresh=True)

    
    async def cancel_summarization_tasks(self, task_list: list) -> None:
        for task in task_list:
            if isinstance(task, asyncio.Task) and not task.done() and not task.cancelled():
                task.cancel()
        
        cancelled_tasks = [task for task in task_list if isinstance(task, asyncio.Task)]
        if cancelled_tasks:
            await asyncio.gather(*cancelled_tasks, return_exceptions=True)
    
    def add_summarization_task(self, task: None, task_copy: None) -> None:
        self.summarization_tasks.append(task)
        self.summarization_tasks_copy.append(task_copy)

    async def safe_gather(self, task_list: list) -> list:
        try:
            return await asyncio.gather(*task_list, return_exceptions=True)
        except Exception:
            """
            especially for _FutureGather exception which took so long to debug 🤬
            """
            pass

class DirectoryWalker(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    base_dir: str
    file_paths: dict = {}
    workspace_summary: str = ''
    lock: asyncio.Lock = None
    semaphore: asyncio.Semaphore = None
    summarizer: Summarizer = None
    summary_manager: SummaryManager = None
    printer: Printer

    def __init__(self, **data):
        super().__init__(**data)
        self.lock = asyncio.Lock()
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

    def process_directory(self, dir_path: str, summary_file: str, prefix: IO = '', gitignore: PathSpec = None) -> None:
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
                self.summary_manager.add_summarization_task(
                    asyncio.create_task(self.update_file_paths(path)),  # original
                    asyncio.create_task(self.update_file_paths(path))   # copy
                )

    def process_subdirectory(self, path: str, index: int, total: int, summary_file: IO, prefix: str, gitignore: PathSpec) -> None:
        connector = '├──' if index < total - 1 else '└──'
        summary_file.write(f'{prefix}{connector} {os.path.basename(path)}\n')

        ext_prefix = '│   ' if index < total - 1 else '    '
        self.process_directory(path, summary_file, prefix=(prefix + ext_prefix), gitignore=gitignore)

    def write_file_entry(self, file_name: str, index: int, total: int, summary_file: IO, prefix: str) -> None:
        connector = '├──' if index < total - 1 else '└──'
        summary_file.write(f'{prefix}{connector} {file_name}\n')
    
    def get_directory_tree(self) -> None:
        with open(config.get_dir_tree_path(), 'r') as dir_tree_file:
            return dir_tree_file.read()
    
    def get_gitignore(self) -> PathSpec:
        patterns = set()
        
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as gitignore_file:
                for line in gitignore_file:
                    patterns.add(line.strip().lstrip('/').rstrip('/'))
        
        with resources.path(f'{config.FLAMETHROWER_PACKAGE_NAME}.data', '.sample.gitignore') as sample_gitignore_file_path:
            with open(sample_gitignore_file_path, 'r') as sample_gitignore_file:
                for line in sample_gitignore_file:
                    patterns.add(line.strip().lstrip('/').rstrip('/'))
        
        return PathSpec.from_lines('gitwildmatch', list(patterns))

    async def update_file_paths(self, file_path: str) -> int:
        try:
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
                        
                        async with self.lock:
                            self.file_paths[relative_path] = file_summary
                        return 1
                    except FileNotFoundError:
                        return 0
                    except UnicodeDecodeError:
                        return 0
                    except Exception:
                        return 0
        except asyncio.CancelledError:
            return 0

def setup_dir_summary(base_dir: str, printer: Printer, shell_manager: ShellManager) -> None:
    dir_walker = DirectoryWalker(
        base_dir=os.path.join(os.getcwd(), base_dir),
        printer=printer
    )
    try:
        with shell_manager.cooked_mode():
            # Python 3.8 prefers this over asyncio.run()
            asyncio.get_event_loop().run_until_complete(dir_walker.generate_directory_summary())
    except KeyboardInterrupt:
        printer.print_yellow('\nLearning process interrupted. Workspace knowledge may be incomplete.\n', reset=True)
    except Exception:
        raise
