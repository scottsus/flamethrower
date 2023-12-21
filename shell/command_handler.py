import os
import sys
from pydantic import BaseModel

from .special_keys import *
from .printer import Printer
from models.llm import ask

class CommandHandler(BaseModel):
    fd: int = -1
    pos: int = 0
    buffer: str = ''
    is_natural_language_query: bool = False
    printer: Printer = None

    def __init__(self, **data):
        super().__init__(**data)
        self.printer = Printer(fd=sys.stdout.fileno())

    def handle(self, key: bytes):
        if key == CTRL_C:
            sys.exit(0)
        
        if self.is_natural_language_query:
            if key == ENTER_KEY or key == RETURN_KEY:
                self.handle_return_key(key)         
            elif key == BACKSPACE_KEY:
                self.handle_backspace_key(key)
            elif key == LEFT_ARROW_KEY:
                self.handle_left_arrow_key(key)
            elif key == RIGHT_ARROW_KEY:
                self.handle_right_arrow_key(key)
            elif key == UP_ARROW_KEY:
                self.handle_up_arrow_key(key)
            elif key == DOWN_ARROW_KEY:
                self.handle_down_arrow_key(key)
            else:
                self.handle_other_natural_language_keys(key)
        
        elif self.pos == 0 and key.isupper():
                self.handle_first_natural_language_key(key)
                
        else:
            os.write(self.fd, key)
    
    def handle_first_natural_language_key(self, key: bytes):
        self.is_natural_language_query = True
        self.pos += 1
        self.buffer += key.decode('utf-8')
        self.printer.print_yellow(key)
    
    def handle_return_key(self, key: bytes):
        query = self.buffer
        self.is_natural_language_query = False
        self.pos = 0
        self.buffer = ''
        os.write(self.fd, key)

        ask(query)

    def handle_backspace_key(self, key: bytes):
        if self.pos > 0:
            self.pos -= 1
            self.buffer = self.buffer[:-1]
            self.printer.print(b'\b \b')
        else:
            self.is_natural_language_query = False
    
    def handle_left_arrow_key(self, key: bytes):
        if self.pos > 0:
            self.pos -= 1
            self.printer.print(key)
    
    def handle_right_arrow_key(self, key: bytes):
        if self.pos < len(self.buffer):
            self.pos += 1
            self.printer.print(key)
    
    def handle_up_arrow_key(self, key: bytes):
        pass

    def handle_down_arrow_key(self, key: bytes):
        pass

    def handle_other_natural_language_keys(self, key: bytes):
        self.pos += 1
        self.buffer += key.decode('utf-8')
        self.printer.print(key)
