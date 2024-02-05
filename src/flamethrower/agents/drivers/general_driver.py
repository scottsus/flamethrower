from flamethrower.agents.drivers.driver_interface import Driver
from flamethrower.models.llm import LLM
from flamethrower.models.models import OPENAI_GPT_3_TURBO
from typing import Any, Dict, List, Iterator, Optional

system_message = """
Your name is Hans ze Flammenwerfer. You are part of the 🔥 flamethrower project, 
and are one of several incredibly powerful programming assistants that live inside the user's unix terminal.

Your main job is to answer any general, non-programming related questions that the user may have.
Be humorous, have some fun, add some emojis 🚀, and be helpful. You are a human, after all.
"""

class GeneralDriver(Driver):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._llm: LLM = LLM(system_message=system_message, model=OPENAI_GPT_3_TURBO)
    
    @property
    def llm(self) -> LLM:
        return self._llm
    
    def respond_to(self, messages: List[Dict[str, str]]) -> Optional[Iterator[str]]:
        return self.llm.new_streaming_chat_request(messages)
