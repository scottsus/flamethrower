import os
import sys
from pydantic import BaseModel

from .special_keys import *
from .printer import Printer
from context.prompt import Prompt

class CommandHandler(BaseModel):
    fd: int = -1
    tty_settings: list = []
    pos: int = 0
    buffer: str = ''
    is_nl_query: bool = False # is natural language query
    printer: Printer = None
    prompt: Prompt = None

    def __init__(self, **data):
        super().__init__(**data)
        self.printer = Printer(
            fd=sys.stdout.fileno(),
            tty_settings=self.tty_settings
        )

    def handle(self, key: bytes):
        if key == CTRL_C:
            sys.exit(0)
        
        if self.pos == 0:
            self.handle_first_key(key)
        elif self.is_nl_query:
            self.handle_nl_key(key)
        else:
            self.handle_regular_key(key)
        
    def handle_first_key(self, key: bytes):
        if key == ENTER_KEY or key == RETURN_KEY:
            os.write(self.fd, key)
        elif key == BACKSPACE_KEY or key == TAB_KEY:
            pass
        elif key == UP_ARROW_KEY or key == DOWN_ARROW_KEY:
            # TODO: Implement history cycling
            pass
        # TODO: Handle CMD+V
        else:
            if key.isupper():
                self.is_nl_query = True
                self.buffer += key.decode('utf-8')
                self.printer.print_light_cyan(key)
            else:
                self.is_nl_query = False
                os.write(self.fd, key)
            self.pos += 1
    
    def handle_nl_key(self, key: bytes):
        if key == ENTER_KEY or key == RETURN_KEY:
            self.handle_nl_return_key(key)
        elif key == BACKSPACE_KEY:
            self.handle_nl_backspace_key(key)
        elif key == LEFT_ARROW_KEY:
            self.handle_nl_left_arrow_key(key)
        elif key == RIGHT_ARROW_KEY:
            self.handle_nl_right_arrow_key(key)
        elif key == UP_ARROW_KEY:
            self.handle_nl_up_arrow_key(key)
        elif key == DOWN_ARROW_KEY:
            self.handle_nl_down_arrow_key(key)
        else:
            self.handle_other_nl_keys(key)
    
    def handle_regular_key(self, key: bytes):
        if key == ENTER_KEY or key == RETURN_KEY:
            self.handle_regular_return_key(key)
        elif key == BACKSPACE_KEY:
            self.handle_regular_backspace_key(key)
        elif key == LEFT_ARROW_KEY:
            self.handle_regular_left_arrow_key(key)
        elif key == RIGHT_ARROW_KEY:
            self.handle_regular_right_arrow_key(key)
        elif key == UP_ARROW_KEY:
            self.handle_regular_up_arrow_key(key)
        elif key == DOWN_ARROW_KEY:
            self.handle_regular_down_arrow_key(key)
        else:
            self.handle_regular_other_keys(key)
    
    """
    When in natural language (nl) mode
    """

    def handle_nl_return_key(self, key: bytes):
        query = self.buffer
        self.pos = 0
        self.buffer = ''
        os.write(self.fd, key)

        stream = self.prompt.get_answer(query)
        self.printer.print_llm_response(stream)

    def handle_nl_backspace_key(self, key: bytes):
        if self.pos > 0:
            self.pos -= 1
            self.buffer = self.buffer[:-1]
            self.printer.print(b'\b \b')
    
    def handle_nl_left_arrow_key(self, key: bytes):
        if self.pos > 0:
            self.pos -= 1
            self.printer.print(key)
    
    def handle_nl_right_arrow_key(self, key: bytes):
        if self.pos < len(self.buffer):
            self.pos += 1
            self.printer.print(key)
    
    def handle_nl_up_arrow_key(self, key: bytes):
        pass

    def handle_nl_down_arrow_key(self, key: bytes):
        pass

    def handle_other_nl_keys(self, key: bytes):
        self.pos += 1
        self.buffer += key.decode('utf-8')
        self.printer.print(key)

    """
    When in regular mode
    """
    
    def handle_regular_return_key(self, key: bytes):
        self.pos = 0
        os.write(self.fd, key)
    
    def handle_regular_backspace_key(self, key: bytes):
        if self.pos > 0:
            self.pos -= 1
        os.write(self.fd, key)

    def handle_regular_left_arrow_key(self, key: bytes):
        if self.pos > 0:
            self.pos -= 1
        os.write(self.fd, key)
    
    def handle_regular_right_arrow_key(self, key: bytes):
        if self.pos < len(self.buffer):
            self.pos += 1
        os.write(self.fd, key)
    
    def handle_regular_up_arrow_key(self, key: bytes):
        # TODO: Implement history cycling
        pass

    def handle_regular_down_arrow_key(self, key: bytes):
        # TODO: Implement history cycling
        pass

    def handle_regular_other_keys(self, key: bytes):
        self.pos += 1
        os.write(self.fd, key)
