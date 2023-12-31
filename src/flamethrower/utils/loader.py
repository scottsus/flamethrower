import sys
import time
import itertools
from pydantic import BaseModel
from .special_keys import CLEAR_FROM_START, CLEAR_TO_END, CURSOR_TO_START
from .colors import STDIN_YELLOW, STDIN_DEFAULT

class Loader(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    done: bool = False
    spinner: itertools.cycle = None
    message: str = ''
    start_time: float = 0.0

    def __init__(self, **data):
        super().__init__(**data)
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.start_time = time.time()
        if data.get('message') == '':
            self.message = '🧠 Thinking...'

    def spin(self) -> None:
        sys.stdout.write('\n')
        while not self.done:
            elapsed = time.time() - self.start_time
            speed = 0.1 if elapsed < 3 else 0.05
            sys.stdout.write(f'{STDIN_YELLOW.decode("utf-8")}\r{self.message} {next(self.spinner)}{STDIN_DEFAULT.decode("utf-8")}')
            sys.stdout.flush()
            time.sleep(speed)

    def stop(self) -> None:
        self.done = True
        sys.stdout.write((CLEAR_FROM_START + CLEAR_TO_END + CURSOR_TO_START).decode("utf-8"))
        sys.stdout.flush()
