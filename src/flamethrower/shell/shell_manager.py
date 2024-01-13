import sys
import tty
import termios
from pydantic import BaseModel
from contextlib import contextmanager

class ShellManager(BaseModel):
    old_settings: list

    @contextmanager    
    def cooked_mode(self):
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            yield
        except Exception:
            raise
        finally:
            tty.setraw(sys.stdin)
