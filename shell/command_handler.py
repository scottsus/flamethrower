import os
import sys
from pydantic import BaseModel

from .special_keys import *
from .printer import Printer

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
                self.is_natural_language_query = False
                self.pos = 0
                self.buffer = ''
                os.write(self.fd, key)                
            elif key == BACKSPACE_KEY:
                if self.pos > 0:
                    self.pos -= 1
                    self.buffer = self.buffer[:-1]
                    self.printer.print(b'\b \b')
                else:
                    self.is_natural_language_query = False
            elif key == LEFT_ARROW_KEY:
                if self.pos > 0:
                    self.pos -= 1
                    self.printer.print(key)
            elif key == RIGHT_ARROW_KEY:
                if self.pos < len(self.buffer):
                    self.pos += 1
                    self.printer.print(key)
            elif key == UP_ARROW_KEY or key == DOWN_ARROW_KEY:
                pass
            else:
                self.pos += 1
                self.buffer += key.decode('utf-8')
                self.printer.print(key)
        
        elif self.pos == 0 and key.isupper():
                self.is_natural_language_query = True
                self.pos += 1
                self.buffer += key.decode('utf-8')
                self.printer.print_yellow(key)
                
        else:
            os.write(self.fd, key)