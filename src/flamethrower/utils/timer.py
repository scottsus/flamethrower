import time
from contextlib import contextmanager
from pydantic import BaseModel
from flamethrower.shell.printer import Printer
from typing import Generator

class Timer(BaseModel):
    printer: Printer

    @contextmanager
    def get_execution_time(self) -> Generator[None, None, None]:
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            exec_time_message = self.format_exec_time_message(start_time, end_time)
            
            self.printer.print_light_green(exec_time_message)

    def format_exec_time_message(self, start_time: float, end_time: float) -> str:
        exec_time = end_time - start_time
        num_mins = f'{int(exec_time // 60)}m ' if exec_time >= 60 else ''
        num_secs = f'{exec_time % 60:.1f}s' if exec_time < 60 else f'{int(exec_time % 60)}s'
        
        return f'\nThis run took {num_mins}{num_secs} 🚀'
