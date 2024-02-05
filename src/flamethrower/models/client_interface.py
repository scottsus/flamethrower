from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, List, Iterator, Tuple

class LLMClient(ABC, BaseModel):
    system_message: str

    @abstractmethod
    def new_basic_chat_request(self, messages: List[Dict[str, str]]) -> Tuple[str, int, int, str]:
        pass

    @abstractmethod
    def new_streaming_chat_request(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        pass
    
    @abstractmethod
    async def new_basic_async_chat_request(self, messages: List[Dict[str, str]]) -> Tuple[str, int, int, str]:
        pass

    @abstractmethod
    def new_json_request(self, messages: List[Dict[str, str]]) -> Tuple[str, int, int, str]:
        pass
