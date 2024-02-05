from pydantic import BaseModel
from .printer import Printer
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.agents.operator import Operator
from flamethrower.utils.special_keys import *
from flamethrower.exceptions.exceptions import *
from flamethrower.exceptions.handlers import *
from flamethrower.utils.zsh_history import update_zsh_history

class CommandHandler(BaseModel):
    pos: int = 0
    buffer: str = ''
    is_nl_query: bool = False # is natural language query
    conv_manager: ConversationManager
    operator: Operator
    printer: Printer

    # TODO: Windows support

    def handle(self, key: bytes) -> None:
        if self.pos == 0:
            self.handle_first_key(key)
        elif self.is_nl_query:
            self.handle_nl_key(key)
        else:
            self.handle_regular_key(key)
        
    def handle_first_key(self, key: bytes) -> None:
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
                self.printer.print_orange(key)
            else:
                self.is_nl_query = False
                self.printer.write_leader(key)
            self.pos += 1
            self.buffer += key.decode('utf-8')
    
    def handle_nl_key(self, key: bytes) -> None:
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
    
    def handle_regular_key(self, key: bytes) -> None:
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

    def handle_nl_return_key(self, key: bytes) -> None:
        query = self.buffer
        self.pos = 0
        self.buffer = ''
        self.printer.write_leader(key)
        self.printer.print_regular(with_newline=True)
        
        update_zsh_history(query)
        self.conv_manager.append_conv(
            role='user',
            content=query,
            name='human'
        )

        try:
            self.operator.new_implementation_run()
        except KeyboardInterrupt:
            pass
        except QuotaExceededException:
            self.printer.print_err(get_quota_exceeded_message())
        except Exception:
            raise

    def handle_nl_backspace_key(self, key: bytes) -> None:
        if self.pos > 0:
            self.pos -= 1
            self.buffer = self.buffer[:-1]
            self.printer.print_stdout(b'\b \b')
    
    def handle_nl_left_arrow_key(self, key: bytes) -> None:
        if self.pos > 0:
            self.pos -= 1
            self.printer.print_stdout(key)
    
    def handle_nl_right_arrow_key(self, key: bytes) -> None:
        if self.pos < len(self.buffer):
            self.pos += 1
            self.printer.print_stdout(key)
    
    def handle_nl_up_arrow_key(self, key: bytes) -> None:
        pass

    def handle_nl_down_arrow_key(self, key: bytes) -> None:
        pass

    def handle_other_nl_keys(self, key: bytes) -> None:
        self.pos += 1
        self.buffer += key.decode('utf-8')
        self.printer.print_stdout(key)

    """
    When in regular mode
    """
    
    def handle_regular_return_key(self, key: bytes) -> None:
        command = self.buffer # unused
        self.pos = 0
        self.buffer = ''
        self.printer.write_leader(key)
    
    def handle_regular_backspace_key(self, key: bytes) -> None:
        if self.pos > 0:
            self.pos -= 1
            self.buffer = self.buffer[:-1]
        self.printer.write_leader(key)

    def handle_regular_left_arrow_key(self, key: bytes) -> None:
        if self.pos > 0:
            self.pos -= 1
        self.printer.write_leader(key)
    
    def handle_regular_right_arrow_key(self, key: bytes) -> None:
        if self.pos < len(self.buffer):
            self.pos += 1
        self.printer.write_leader(key)
    
    def handle_regular_up_arrow_key(self, key: bytes) -> None:
        # TODO: Implement history cycling
        pass

    def handle_regular_down_arrow_key(self, key: bytes) -> None:
        # TODO: Implement history cycling
        pass

    def handle_regular_other_keys(self, key: bytes) -> None:
        self.pos += 1
        self.buffer += key.decode('utf-8')
        self.printer.write_leader(key)
