import sys
import time
import threading
import itertools
from contextlib import contextmanager
from pydantic import BaseModel
from .special_keys import CLEAR_FROM_START, CLEAR_TO_END, CURSOR_TO_START
from .colors import STDIN_YELLOW, STDIN_DEFAULT

class Loader(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    loading_message: str
    completion_message: str = ''
    will_report_timing: bool = False
    
    done: bool = False
    spinner: itertools.cycle = None
    start_time: float = 0.0
    

    def __init__(self, **data):
        super().__init__(**data)
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.start_time = time.time()
        if data.get('loading_message') == '':
            self.loading_message = '🧠 Thinking...'

    def spin(self) -> None:
        sys.stdout.write('\n')
        while not self.done:
            elapsed = time.time() - self.start_time
            speed = 0.1 if elapsed < 3 else 0.05
            sys.stdout.write(f'{STDIN_YELLOW.decode("utf-8")}\r{self.loading_message} {next(self.spinner)}{STDIN_DEFAULT.decode("utf-8")}')
            sys.stdout.flush()
            time.sleep(speed)

    def stop(self) -> None:
        self.done = True
        sys.stdout.write((CLEAR_FROM_START + CLEAR_TO_END + CURSOR_TO_START).decode("utf-8"))
        sys.stdout.flush()

    @contextmanager
    def managed_loader(self) -> None:
        loader_thread = threading.Thread(target=self.spin)
        loader_thread.start()
        try:
            record_start_time = time.time()
            yield
        finally:
            record_end_time = time.time()
            self.stop()

            time_elapsed = record_end_time - record_start_time
            time_elapsed_message = ''
            if self.will_report_timing:
                time_elapsed_message = f' Time taken: {time_elapsed:.2f}s\n'
            
            sys.stdout.write(f'{self.completion_message}{time_elapsed_message}')
            sys.stdout.flush()
