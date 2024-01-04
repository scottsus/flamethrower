import os
import git
from pydantic import BaseModel
from flamethrower.shell.printer import Printer

class Diff(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    base_path: str = os.getcwd()
    repo: git.Repo = None
    printer: Printer = None

    def __init__(self, **data):
        super().__init__(**data)
        self.repo = git.Repo(self.base_path)

    def get_diffs(self) -> list:
        if not self.repo.is_dirty(untracked_files=True):
            return []
        
        return self.repo.git.diff(None).split('\n')
