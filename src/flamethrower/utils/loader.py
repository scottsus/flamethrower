import sys
import time
import threading
import itertools
from contextlib import contextmanager
from pydantic import BaseModel, ConfigDict
from typing import Any, Generator
from flamethrower.utils.special_keys import CLEAR_FROM_START, CLEAR_TO_END, CURSOR_TO_START
from flamethrower.utils.colors import STDIN_YELLOW, STDIN_DEFAULT

class Loader(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    loading_message: str
    completion_message: str = ''
    with_newline: bool = True
    will_report_timing: bool = False
    requires_cooked_mode: bool = True
    done: bool = False

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._spinner: itertools.cycle = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self._start_time: float = time.time()
        if kwargs.get('loading_message') == '':
            self.loading_message = '🧠 Thinking...'
    
    @property
    def spinner(self) -> itertools.cycle:
        return self._spinner
    
    @property
    def start_time(self) -> float:
        return self._start_time

    def spin(self) -> None:
        if self.with_newline:
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
    def managed_loader(self) -> Generator[None, None, None]:
        loader_thread = threading.Thread(target=self.spin)
        loader_thread.start()

        try:
            record_start_time = time.time()
            if self.requires_cooked_mode:
                from flamethrower.containers.container import container
                
                shell_manager = container.shell_manager()
                with shell_manager.cooked_mode():
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
