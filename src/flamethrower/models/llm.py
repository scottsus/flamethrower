from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, List, Union, Iterator, Optional

class LLM(ABC, BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @abstractmethod
    def new_chat_request(self, messages: List[Dict[str, str]], loading_message: str) -> str:
        pass

    @abstractmethod
    async def new_async_chat_request(self, messages: List[Dict[str, str]]) -> str:
        pass

    @abstractmethod
    def new_streaming_chat_request(self, messages: List[Dict[str, str]]) -> Optional[Iterator[str]]:
        pass

    @abstractmethod
    def new_json_request(
        self,
        query: str,
        json_schema: Dict[str, Any],
        loading_message: str,
        completion_message: str = ''
    ) -> Optional[Union[Dict[Any, Any], List[Dict[Any, Any]]]]:
        pass
