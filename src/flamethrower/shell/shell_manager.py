import sys
import tty
import termios
from pydantic import BaseModel
from contextlib import contextmanager

class ShellManager(BaseModel):
    old_settings: list
    in_cooked_mode: bool = False

    @contextmanager    
    def cooked_mode(self):
        if self.in_cooked_mode:
            yield
            return
        
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            self.in_cooked_mode = True
            yield
        except Exception:
            raise
        finally:
            tty.setraw(sys.stdin)
            self.in_cooked_mode = False
