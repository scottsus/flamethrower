import sys
import time
import threading
import itertools
from contextlib import contextmanager
from pydantic import BaseModel
from flamethrower.shell.shell_manager import ShellManager
from flamethrower.utils.special_keys import CLEAR_FROM_START, CLEAR_TO_END, CURSOR_TO_START
from flamethrower.utils.colors import STDIN_YELLOW, STDIN_DEFAULT

class Loader(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    loading_message: str
    completion_message: str = ''
    will_report_timing: bool = False
    shell_manager: ShellManager = None
    requires_cooked_mode: bool = True
    
    done: bool = False
    spinner: itertools.cycle = None
    start_time: float = 0.0
    

    def __init__(self, **data):
        super().__init__(**data)
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.start_time = time.time()
        if data.get('loading_message') == '':
            self.loading_message = '🧠 Thinking...'
        
        if self.requires_cooked_mode:
            from flamethrower.containers.container import container
            self.shell_manager = container.shell_manager()

    def spin(self) -> None:
        sys.stdout.write('\n')
        while not self.done:
            speed = 0.1
            sys.stdout.write(f'{STDIN_YELLOW.decode("utf-8")}\r{next(self.spinner)} {self.loading_message}{STDIN_DEFAULT.decode("utf-8")}')
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
            if self.requires_cooked_mode:
                with self.shell_manager.cooked_mode():
                    yield
            else:
                yield
        except (KeyboardInterrupt, Exception):
            raise
        finally:
            record_end_time = time.time()
            self.stop()

            time_elapsed = record_end_time - record_start_time
            time_elapsed_message = ''
            if self.will_report_timing:
                time_elapsed_message = f' Time taken: {time_elapsed:.2f}s\n'
            
            sys.stdout.write(f'{self.completion_message}{time_elapsed_message}')
            sys.stdout.flush()
