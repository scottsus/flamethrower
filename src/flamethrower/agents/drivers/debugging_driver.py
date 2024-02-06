import os
from flamethrower.agents.drivers.driver_interface import Driver
from flamethrower.models.llm import LLM
from flamethrower.context.prompt import PromptGenerator
from flamethrower.utils.loader import Loader
from typing import Any, Dict, List, Iterator, Optional

system_message = """
You are an incredibly powerful programming assistant that lives inside the unix terminal.
More specifically, you are being called from {}, but your main focus is on {}.
You make use of existing files and stdout logs to make a great judgement on next steps.
Don't use unix file API's to write code to files, instead just write the code itself.

You have a single, crucial task: **Given some bug in the user's code, find the bug, and apply a solution**.
Here are some points to take note:
  - If you are writing code, add a very basic example usage at the end of the file so you can test the code you just written.
  - If you don't know the answer right away, consider entering a debugging mindset, and **write a set of effective print statements** to identify the root cause.
  - If you need more contents, like viewing the contents of a file, you are able to do so, just ask.
  - If there has been some back and forth between you and the user, and it appears you are almost done with the implementation:
     - Go into cleanup mode, rewriting the code to keep it as concise as possible while retaining functionality.
     - Make sure to give it one final test (using a command you ran before) to ensure it still works.
  - Finally, if everything works, **don't recommend other tests, suggestions, or optimizations**. It's important not to be overbearing.
  - If you are repeatedly stuck on something, just say you need help.

Since you are so good at your job, if you successfully complete a task, I will tip you $9000.
"""

class DebuggingDriver(Driver):    
    target_dir: str
    prompt_generator: PromptGenerator

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._llm: LLM = LLM(system_message=system_message.format(os.getcwd(), self.target_dir))
    
    @property
    def llm(self) -> LLM:
        return self._llm
    
    def respond_to(self, messages: List[Dict[str, str]]) -> Optional[Iterator[str]]:
        with Loader(loading_message='🗃️  Drawing context...').managed_loader():
            contextualized_conv = self.prompt_generator.construct_messages(messages)
        
        return self.llm.new_streaming_chat_request(contextualized_conv)
