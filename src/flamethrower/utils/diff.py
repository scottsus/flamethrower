import os
import git
from pydantic import BaseModel, ConfigDict
from flamethrower.shell.printer import Printer
from typing import Any, List

class Diff(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    base_path: str = os.getcwd()
    printer: Printer

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._repo = git.Repo(self.base_path)
    
    @property
    def repo(self) -> git.Repo:
        return self._repo

    def get_diffs(self) -> List[str]:
        if not self.repo.is_dirty(untracked_files=True):
            return []
        
        diffs = self.repo.git.diff(None).split('\n')
        if not isinstance(diffs, list):
            return []
        
        return diffs
