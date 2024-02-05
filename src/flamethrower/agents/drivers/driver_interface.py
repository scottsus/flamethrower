from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, List, Iterator, Optional

class Driver(ABC, BaseModel):
    @abstractmethod
    def respond_to(self, messages: List[Dict[str, str]]) -> Optional[Iterator[str]]:
        pass
