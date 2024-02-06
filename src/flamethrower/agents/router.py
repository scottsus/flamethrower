from pydantic import BaseModel
from flamethrower.models.llm import LLM
from flamethrower.models.models import OPENAI_GPT_3_TURBO
from typing import Any, Dict, List

json_schema = {
    'type': 'object',
    'properties': {
        'agent': {
            'type': 'string',
            'enum': ['feature', 'debugging', 'done']
        }
    },
    'required': ['agent']
}

system_message = f"""
You are a router that routes natural language queries to the appropriate agent.
Here are 3 types of agents, and their expected characteristics:
  1. Feature agent: Explains current code, creates new features, refactors existing ones, usually more creative.
    - "Make a new ...", "Refactor ...", "Explain this ...", "What is X about ..." etc.
  2. Debugging agent: Debugs code, writes print statements, runs commands, finding out more information about the underlying problem.
    - "Why is this happening?", "What is ...", "Wtf?", etc.
    - STDOUT logs: Error: ...

Additionally, you need to understand that you are being called as part of a cycle, meaning that sometimes you will be called 
when evaluating a near-done state, for which you should indicate that the job is completed with a third `done` agent.
  3. Done agent: Indicates that the job is completed.
    - STDOUT: # Some success message **that solves the user's problem**
    - "Thank you sir", "That worked", etc.
    - If the code still has excessive debugging print statements, then it is NOT done yet.

Importantly:
  - You are part of a while-loop in a program used as an effective multi-agent build & debug system.
  - Make **effective use of context to make the right judgement**.
    - **look at the last user message, and see if it is related to the messages before it**
      - e.g. "Wtf?" is usually related to the messages before it, even suggesting debugging is needed
    - however, if this last message is unrelated to the messages before, and is truly not programming-related
      - then you should route it to the `general` agent.

With the above in mind, you must return a JSON object with a single key `agent` with a value of one of the 4 agents.
The JSON schema is given for your reference.
    {json_schema}
"""

class Router(BaseModel):
    max_file_len: int = 30_000 # TODO: count actual tokens and cut accordingly
    json_schema: Dict[str, Any] = json_schema

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._llm: LLM = LLM(system_message=system_message, model=OPENAI_GPT_3_TURBO)
    
    @property
    def llm(self) -> LLM:
        return self._llm
    
    def get_driver(self, messages: List[Dict[str, str]]) -> str:
        messages_str = str(messages)[:self.max_file_len]

        json_obj = self.llm.new_json_request(
            query=messages_str,
            json_schema=self.json_schema
        )

        if not json_obj or not isinstance(json_obj, dict):
            return ''

        return json_obj.get('agent') or ''
