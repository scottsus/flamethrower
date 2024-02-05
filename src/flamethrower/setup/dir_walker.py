import os
import io
import json
import asyncio
from pathspec import PathSpec
from importlib import resources
from pydantic import BaseModel, ConfigDict

import flamethrower.config.constants as config
from flamethrower.agents.util_agents.summarizer import Summarizer
from flamethrower.setup.summary_manager import SummaryManager
from flamethrower.utils.loader import Loader
from typing import Any, Dict, Union

class DirectoryWalker(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    workspace_summary: str
    target_dir: str = os.getcwd()
    file_paths: Dict[str, str] = {}

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._base_dir: str = os.getcwd()
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(10)
        self._summarizer = Summarizer()
        self._summary_manager = SummaryManager()

        try:
            with open(config.get_dir_dict_path(), 'r') as dir_dict_file:
                self.file_paths = json.loads(dir_dict_file.read())
        except FileNotFoundError:
            with open(config.get_dir_dict_path(), 'w') as dir_dict_file:
                dir_dict_file.write('')
    
    @property
    def base_dir(self) -> str:
        return self._base_dir
    
    @property
    def lock(self) -> asyncio.Lock:
        return self._lock

    @property
    def semaphore(self) -> asyncio.Semaphore:
        return self._semaphore
    
    @property
    def summarizer(self) -> Summarizer:
        return self._summarizer
    
    @property
    def summary_manager(self) -> SummaryManager:
        return self._summary_manager

    async def generate_directory_summary(self) -> None:
        with open(config.get_dir_tree_path(), 'w') as dir_tree_file:
            self.process_directory(self.base_dir, dir_tree_file, self.get_gitignore())
        
        try:
            tasks_completed = await self.summary_manager.get_summarizations_with_timeout() or []
            num_tasks_completed = 0
            for task in tasks_completed:
                if isinstance(task, int):
                    num_tasks_completed += task # task can be 0 or 1
            
            if num_tasks_completed > 0:
                print(f'📚 Learned {num_tasks_completed} files in the workspace.')

            with open(config.get_dir_dict_path(), 'w') as dir_dict_file:
                dir_dict_file.write(json.dumps(self.file_paths, indent=2))
            
        except KeyboardInterrupt:
            raise
        except Exception:
            raise

    def process_directory(
        self,
        dir_path: str,
        summary_file: io.TextIOWrapper,
        gitignore: PathSpec,
        prefix: str = '',
    ) -> None:
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
            is_last = (i == len(sorted_entries) - 1)

            if os.path.isdir(path):
                self.process_subdirectory(
                    path,
                    entry,
                    prefix,
                    is_last,
                    self.is_within_target(path),
                    summary_file,
                    gitignore
                )
            else:
                self.write_file_entry(
                    entry,
                    is_last,
                    prefix,
                    summary_file
                )
                self.summary_manager.add_summarization_task(
                    asyncio.create_task(self.update_file_paths(path)),  # original
                    asyncio.create_task(self.update_file_paths(path))   # copy
                )

    def process_subdirectory(
        self,
        path: str,
        entry: str,
        prefix: str,
        is_last: bool,
        is_target: bool,
        summary_file: io.TextIOWrapper,
        gitignore: PathSpec,
    ) -> None:
        connector = '├──' if not is_last else '└──'
        new_prefix = '│   ' if not is_last else '    '
        
        if is_target:
            summary_file.write(f'{prefix}{connector} {entry}\n')
            self.process_directory(path, summary_file, gitignore, prefix=(prefix + new_prefix))
        else:
            summary_file.write(f'{prefix}{connector} {entry}\n')
            if os.listdir(path):
                summary_file.write(f'{prefix}{new_prefix}└── ...\n')

    def write_file_entry(
        self,
        file_name: str,
        is_last: bool,
        prefix: str,
        summary_file: io.TextIOWrapper,
    ) -> None:
        connector = '├──' if not is_last else '└──'
        summary_file.write(f'{prefix}{connector} {file_name}\n')

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
    
    """
    Helper functions
    """
    
    def get_directory_tree(self) -> str:
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
    
    def is_within_target(self, path: str) -> bool:
        return path in self.target_dir or self.target_dir in path

def setup_workspace_summary() -> str:
    summary_path = config.get_workspace_summary_path()
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as summary_file:
            return summary_file.read()
    
    try:
        with open(os.path.join(os.getcwd(), 'README.md'), 'r') as readme_file:
            readme_file_contents = readme_file.read()

            with Loader(
                loading_message='📚 Learning workspace...',
                requires_cooked_mode=False
            ).managed_loader():
                summary = Summarizer().summarize_readme(readme_file_contents)

    except FileNotFoundError:
        summary = 'This project does not have a README. Infer from other files the purpose of this project.'
    except Exception as e:
        summary = f'Unable to summarize README: {str(e)}'
    finally:
        with open(summary_path, 'w') as summary_file:
            summary_file.write(summary)
        
        return summary

def setup_dir_summary(target_dir: str) -> Union[None, Exception]:
    dir_walker = DirectoryWalker(
        workspace_summary=setup_workspace_summary(),
        target_dir=os.path.join(os.getcwd(), target_dir)
    )
    try:
        # Python 3.8 prefers this over asyncio.run()
        asyncio.get_event_loop().run_until_complete(dir_walker.generate_directory_summary())
    except KeyboardInterrupt:
        print('\nLearning process interrupted. Workspace knowledge may be incomplete.')
    except Exception as e:
        return e
    
    return None
