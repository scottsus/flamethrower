import asyncio
from asyncio import Task
from rich.progress import Progress, TaskID
from pydantic import BaseModel, ConfigDict
from flamethrower.utils.colors import *
from typing import Any, Coroutine, List, Optional, Union, TypeVar, Generic

T = TypeVar('T')
class Task(asyncio.Task, Generic[T]): # type: ignore
    pass

class SummaryManager(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    max_summarization_tasks: int = 100
    summarization_tasks: List[Task[int]] = []
    summarization_tasks_copy: List[Task[int]] = []
    instant_timeout: float = 0.5
    summarization_timeout: int = 75

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._lock = asyncio.Lock()
    
    @property
    def lock(self) -> asyncio.Lock:
        return self._lock

    async def get_summarizations_with_timeout(self) -> Optional[List[Any]]:
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
            res_list = []
            res_list = await asyncio.wait_for(
                self.safe_gather(self.summarization_tasks_copy),
                timeout=self.instant_timeout
            )
        
        except asyncio.TimeoutError:
            try:
                with Progress() as progress:
                    task_id = progress.add_task(
                        f'[cyan]🏗️  Learning workspace structure (max {self.summarization_timeout}s)...',
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
    
    async def perform_async_task(
        self,
        task: Task[int],
        progress: Progress,
        task_id: TaskID,
        step: int = 1
    ) -> Optional[int]:
        try:
            return await task
        except asyncio.CancelledError:
            return 0
        finally:
            with await self.lock:
                progress.update(task_id, advance=step, refresh=True)
    
    async def cancel_summarization_tasks(self, task_list: List[Task[int]]) -> None:
        for task in task_list:
            if isinstance(task, Task) and not task.done() and not task.cancelled():
                task.cancel()
        
        cancelled_tasks = [task for task in task_list if isinstance(task, Task)]
        if cancelled_tasks:
            await asyncio.gather(*cancelled_tasks, return_exceptions=True)
    
    def add_summarization_task(self, task: Task[int], task_copy: Task[int]) -> None:
        self.summarization_tasks.append(task)
        self.summarization_tasks_copy.append(task_copy)

    async def safe_gather(
        self,
        task_list: Union[List[Task[int]], List[Coroutine[Any, Any, Any]]]
    ) -> List[Any]:
        """
        This can take any coroutine, be it an update_task or a cancel_task, and safely
        gathers it without raising an exception.
        """

        try:
            return await asyncio.gather(*task_list, return_exceptions=True)
        except Exception:
            # especially for the _FutureGather exception
            return []