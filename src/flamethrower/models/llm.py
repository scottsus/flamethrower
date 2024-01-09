from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Iterator, Optional

class LLM(ABC, BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    @abstractmethod
    def new_chat_request(self, messages: list, loading_message: str) -> Optional[str]:
        pass

    @abstractmethod
    def new_async_chat_request(self, messages: list) -> Optional[str]:
        pass

    @abstractmethod
    def new_streaming_chat_request(self, messages: list) -> Iterator[Optional[str]]:
        pass

    @abstractmethod
    def new_json_request(self, messages: list) -> Optional[dict]:
        pass
