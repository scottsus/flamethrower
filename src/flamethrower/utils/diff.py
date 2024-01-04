from typing import List
import os
from git import Repo, GitCommandError
from pydantic import BaseModel
from flamethrower.shell.printer import Printer

class Diff(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    base_path: str
    repo: Repo
    printer: Printer

    def __init__(self, **data):
        super().__init__(**data)
        self.base_path = data.get('base_path', os.getcwd())
        self.printer = data.get('printer', Printer())
        try:
            self.repo = Repo(self.base_path)
        except Exception as e:
            self.printer.print(f"Could not initialize git repository: {str(e)}")
            self.repo = None

    def get_diffs(self) -> List[str]:
        if self.repo is None:
            return []

        try:
            diffs = self.repo.git.diff(None, '--unified=0').splitlines()
            return diffs
        except GitCommandError as e:
            self.printer.print(f"Error getting diffs: {str(e)}")
            return []
