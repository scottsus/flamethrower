import os
import json
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from typing import Iterator, Optional
from flamethrower.models.models import OPENAI_GPT_4_TURBO
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.utils.loader import Loader

default_system_message = """
You are an incredibly powerful programming assistant that can write flawless code.
You are one of the best software engineers in your field, and you are a natural problem solver.
You have a single, crucial task: **Given a user's query, write code that solves their problem.**
Since you're so good at your job, if you successfully complete a task, I will tip you $200.
Here are some points to take note:
  - If the user is not asking a coding-related problem, don't write any code, and instead respond as any other human would.
  - If the previous message was about a successful implementation to a solution, **don't recommend other tests, suggestions, or optimizations**.
  - **Be concise**. Don't be verbose and get straight to the point with your answers.
"""

class LLM(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    client: OpenAI = None
    async_client: AsyncOpenAI = None
    default_model: str = OPENAI_GPT_4_TURBO
    system_message: str = default_system_message
    token_counter: TokenCounter = None

    def __init__(self, **data):
        super().__init__(**data)
        self.client: OpenAI = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )
        self.async_client: AsyncOpenAI = AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )

    async def new_async_chat_request(self, messages: list):
        res = await self.async_client.chat.completions.create(
            model=self.default_model,
            messages=messages,
        )
        self.update_token_usage(res)
        return res.choices[0].message.content
        
    def new_chat_request(self, messages: list, loading_message: str) -> str:
        with Loader(loading_message=loading_message).managed_loader():
            res = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
            )
            self.update_token_usage(res)
            return res.choices[0].message.content

    def new_streaming_chat_request(self, messages: list) -> Iterator[Optional[str]]:
        stream = self.client.chat.completions.create(
            model=self.default_model,
            messages=messages,
            stream=True,
        )
        self.token_counter.add_streaming_input_tokens(str(messages))
        try:
            for chunk in stream:
                token = chunk.choices[0].delta.content or ''
                yield token
        except AttributeError:
            pass
        finally:
            yield None
    
    def new_json_request(self, query: str, json_schema: dict, loading_message: str = '', completion_message: str = '') -> dict:
        with Loader(
            loading_message=loading_message,
            completion_message=completion_message
        ).managed_loader():
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
                    self.update_token_usage(res)
                    json_obj = json.loads(res.choices[0].message.content)
                    validate(json_obj, json_schema)

                    return json_obj
                except ValidationError:
                    # TODO: propagate error upwards
                    print('Received invalid JSON, retrying...')
                    pass
    
    # TODO: get the correct typehints from openai
    def update_token_usage(self, chat_completion) -> None:
        prompt_tokens = chat_completion.usage.prompt_tokens
        completion_tokens = chat_completion.usage.completion_tokens

        self.token_counter.add_input_tokens(prompt_tokens)
        self.token_counter.add_output_tokens(completion_tokens)

