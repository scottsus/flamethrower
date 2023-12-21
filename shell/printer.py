import os
from pydantic import BaseModel

STDIN_DEFAULT = b'\033[0m'
STDIN_RED = b'\033[31m'
STDIN_YELLOW = b'\033[33m'
STDIN_GREEN = b'\033[92m'
STDIN_BLUE = b'\033[94m'
STDIN_GRAY = b'\033[90m'
STDIN_WHITE = b'\033[97m'

class Printer(BaseModel):
    fd: int = 0 # should be sys.stdout.fileno()

    def print(self, data: bytes):
        if self.fd:
            os.write(self.fd, data)

    def print_color(self, data: bytes, color: bytes, reset: bool = False):
        if self.fd:
            os.write(self.fd, color)
            os.write(self.fd, data)
        if reset:
            os.write(self.fd, STDIN_DEFAULT)

    def print_default(self, data: bytes):
        self.print_color(data, STDIN_DEFAULT)
    
    def print_red(self, data: bytes):
        self.print_color(data, STDIN_RED)
    
    def print_yellow(self, data: bytes):
        self.print_color(data, STDIN_YELLOW)
    
    def print_green(self, data: bytes):
        self.print_color(data, STDIN_GREEN)
    
    def print_blue(self, data: bytes):
        self.print_color(data, STDIN_BLUE)
    
    def print_gray(self, data: bytes):
        self.print_color(data, STDIN_GRAY)

    def print_white(self, data: bytes):
        self.print_color(data, STDIN_WHITE)
