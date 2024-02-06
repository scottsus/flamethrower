from flamethrower.agents.drivers.driver_interface import Driver
from flamethrower.models.llm import LLM
from flamethrower.models.models import OPENAI_GPT_3_TURBO
from typing import Any, Dict, List, Iterator, Optional

system_message = f"""
You are part of a while-loop in a program used as an effective multi-agent build & debug system.
In particular, you are a specialized agent that is only called when a job is about to be completed.
In this case:
  - Summarize the entire conversation so far (including the problem and the solution) using bullet points and creative ✨ emojis.
  - Do not **provide any further suggestions, optimizations, or tests**.

Finally, thank the user for their patience and indicate the job is completed.
"""

class DoneDriver(Driver):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._llm: LLM = LLM(system_message=system_message, model=OPENAI_GPT_3_TURBO)
    
    @property
    def llm(self) -> LLM:
        return self._llm
    
    def respond_to(self, messages: List[Dict[str, str]]) -> Optional[Iterator[str]]:
        return self.llm.new_streaming_chat_request(messages)
