import os
import json
import threading
from pydantic import BaseModel
from openai import OpenAI
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from typing import Iterator, Optional
from models.models import OPENAI_GPT_4_TURBO
from utils.loader import Loader

default_system_message = """
You are an incredibly powerful programming assistant that can write flawless code.
You are one of the best software engineers in your field, and you are a natural problem solver.
You have a single, crucial task: **Given a user's query, write code that solves their problem.**
Since you're so good at your job, if you successfully complete a task, I will tip you $200.
Here are some points to take note:
  - If the user is not asking a coding-related problem, don't write any code, and instead respond as any other human would.
  - If it looks like you're about to complete an implementation to a solution, celebrate your win, and **don't recommend other tests, suggestions, or optimizations**.
  - Have fun! Life is not all about coding, so feel free to add some personality to your responses.
"""

class LLM(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    client: OpenAI = None
    default_model = OPENAI_GPT_4_TURBO
    system_message: str = default_system_message

    def __init__(self, **data):
        super().__init__(**data)
        self.client: OpenAI = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )

    def new_chat_request(self, messages: list, loading_message: str = '') -> str:
        loader = Loader(message=loading_message)
        loader_thread = threading.Thread(target=loader.spin)
        loader_thread.start()

        try:
            res = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                stream=False
            )

            return res.choices[0].message.content
        finally:
            loader.stop()

    def new_streaming_chat_request(self, messages: list) -> Iterator[Optional[str]]:
        stream = self.client.chat.completions.create(
            model=self.default_model,
            messages=messages,
            stream=True,
        )

        try:
            for chunk in stream:
                token = chunk.choices[0].delta.content or ''
                yield token
        except AttributeError:
            pass
        finally:
            yield None
    
    def new_json_request(self, query: str, json_schema: dict, loading_message: str = '') -> Iterator[Optional[str]]:
        loader = Loader(message=loading_message)
        loader_thread = threading.Thread(target=loader.spin)
        loader_thread.start()
        
        try:
            while True:
                try:
                    res = self.client.chat.completions.create(
                        model=self.default_model,
                        messages=[
                            {
                                'role': 'system',
                                'content': self.system_message
                            },
                            {
                                'role': 'user',
                                'content': query
                            }
                        ],
                        response_format={ 'type': 'json_object' }
                    )

                    json_obj = json.loads(res.choices[0].message.content)
                    validate(json_obj, json_schema)

                    return json_obj
                except ValidationError:
                    print('Received invalid JSON, retrying...')
        finally:
            loader.stop()
