import sys
from pydantic import BaseModel
from .printer import Printer
from context.prompt import PromptGenerator
from context.conv_manager import ConversationManager
from agents.executor import Executor
from utils.special_keys import *
from utils.zsh_history import update_zsh_history

class CommandHandler(BaseModel):
    pos: int = 0
    buffer: str = ''
    is_nl_query: bool = False # is natural language query
    prompt_generator: PromptGenerator = None
    conv_manager: ConversationManager = None
    executor: Executor = None
    printer: Printer = None

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
            self.printer.write_leader(key)
        elif key == BACKSPACE_KEY or key == TAB_KEY:
            pass
        elif key == UP_ARROW_KEY or key == DOWN_ARROW_KEY:
            # TODO: Implement history cycling
            pass
        # TODO: Handle CMD+V
        else:
            if key.isupper():
                self.is_nl_query = True
                self.printer.print_light_cyan(key)
            else:
                self.is_nl_query = False
                self.printer.write_leader(key)
            self.pos += 1
            self.buffer += key.decode('utf-8')
    
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
        self.printer.write_leader(key)
        
        update_zsh_history(query)
        self.conv_manager.append_conv(
            role='user',
            content=query,
            name='human'
        )

        messages = self.prompt_generator.construct_messages(query)
        self.executor.new_debugging_run(query, messages)

    def handle_nl_backspace_key(self, key: bytes):
        if self.pos > 0:
            self.pos -= 1
            self.buffer = self.buffer[:-1]
            self.printer.print_stdout(b'\b \b')
    
    def handle_nl_left_arrow_key(self, key: bytes):
        if self.pos > 0:
            self.pos -= 1
            self.printer.print_stdout(key)
    
    def handle_nl_right_arrow_key(self, key: bytes):
        if self.pos < len(self.buffer):
            self.pos += 1
            self.printer.print_stdout(key)
    
    def handle_nl_up_arrow_key(self, key: bytes):
        pass

    def handle_nl_down_arrow_key(self, key: bytes):
        pass

    def handle_other_nl_keys(self, key: bytes):
        self.pos += 1
        self.buffer += key.decode('utf-8')
        self.printer.print_stdout(key)

    """
    When in regular mode
    """
    
    def handle_regular_return_key(self, key: bytes):
        command = self.buffer # unused
        self.pos = 0
        self.buffer = ''
        self.printer.write_leader(key)
    
    def handle_regular_backspace_key(self, key: bytes):
        if self.pos > 0:
            self.pos -= 1
            self.buffer = self.buffer[:-1]
        self.printer.write_leader(key)

    def handle_regular_left_arrow_key(self, key: bytes):
        if self.pos > 0:
            self.pos -= 1
        self.printer.write_leader(key)
    
    def handle_regular_right_arrow_key(self, key: bytes):
        if self.pos < len(self.buffer):
            self.pos += 1
        self.printer.write_leader(key)
    
    def handle_regular_up_arrow_key(self, key: bytes):
        # TODO: Implement history cycling
        pass

    def handle_regular_down_arrow_key(self, key: bytes):
        # TODO: Implement history cycling
        pass

    def handle_regular_other_keys(self, key: bytes):
        self.pos += 1
        self.buffer += key.decode('utf-8')
        self.printer.write_leader(key)
