from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict
from typing import Iterator, Optional

class LLM(ABC, BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @abstractmethod
    def new_chat_request(self, messages: list, loading_message: str) -> str:
        pass

    @abstractmethod
    def new_async_chat_request(self, messages: list) -> str:
        pass

    @abstractmethod
    def new_streaming_chat_request(self, messages: list) -> Iterator:
        pass

    @abstractmethod
    def new_json_request(self, query: str, json_schema: dict, loading_message: str, completion_message: str = '') -> dict:
        pass
