import os
import openai
from openai import OpenAI, AsyncOpenAI
import backoff
import json
import jsonschema
from typing import Iterator, Optional
from flamethrower.models.llm import LLM
from flamethrower.models.models import OPENAI_GPT_4_TURBO
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.utils.loader import Loader
from flamethrower.exceptions.exceptions import *
from flamethrower.utils.colors import STDIN_RED, STDIN_DEFAULT

class OpenAIClient(LLM):
    system_message: str
    client: OpenAI = None
    async_client: AsyncOpenAI = None
    token_counter: TokenCounter = None
    model: str = OPENAI_GPT_4_TURBO

    def __init__(self, **data):
        super().__init__(**data)
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.async_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        from flamethrower.containers.container import container
        self.token_counter = container.token_counter()

    def new_chat_request(self, messages: list, loading_message: str) -> Optional[str]:
        with Loader(loading_message=loading_message).managed_loader():
            try:
                res = self.new_basic_chat_request(messages)                
                self.update_token_usage(res)

                return res.choices[0].message.content
            except KeyboardInterrupt:
                raise
            except Exception:
                raise
    
    async def new_async_chat_request(self, messages: list) -> Optional[str]:
        try:
            res = await self.new_basic_async_chat_request(messages)
            self.update_token_usage(res)

            return res.choices[0].message.content
        except KeyboardInterrupt:
            raise
        except Exception:
            raise
    
    def new_streaming_chat_request(self, messages: list) -> Iterator[Optional[str]]:
        interrupted = None
        try:
            stream = self.new_basic_chat_request(messages, is_streaming=True)
            self.token_counter.add_streaming_input_tokens(str(messages))
            
            for chunk in stream:
                token = chunk.choices[0].delta.content or ''
                yield token
        except AttributeError:
            # End of stream
            pass
        except KeyboardInterrupt as e:
            interrupted = e
        except QuotaExceededException as e:
            interrupted = e
        except Exception:
            yield f'\n\n{STDIN_RED.decode("utf-8")}Encountered some error{STDIN_DEFAULT.decode("utf-8")}'
        finally:
            if interrupted:
                raise interrupted
            yield None
    
    def new_json_request(self, query: str, json_schema: dict, loading_message: str, completion_message: str = '') -> Optional[dict]:
        messages = [
            {
                'role': 'system',
                'content': self.system_message
            },
            {
                'role': 'user',
                'content': query
            }
        ]
        
        with Loader(
            loading_message=loading_message,
            completion_message=completion_message
        ).managed_loader():
            max_retries = 3
            for _ in range(max_retries):
                try:
                    res = self.new_basic_chat_request(messages, is_json=True)
                    self.update_token_usage(res)

                    json_obj = json.loads(res.choices[0].message.content)
                    jsonschema.validate(json_obj, json_schema)
                    
                    return json_obj
                except jsonschema.exceptions.ValidationError:
                    # Just retry and hope for the best
                    pass
                except KeyboardInterrupt:
                    raise
                except Exception:
                    raise
    
    @backoff.on_exception(
        backoff.expo,
        (
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.RateLimitError,
            openai.InternalServerError,
            openai.UnprocessableEntityError
        ),
        max_tries=3
    )
    def new_basic_chat_request(
        self,
        messages: list,
        is_json: bool = False,
        is_streaming: bool = False
    ) -> Optional[dict] | Iterator[Optional[dict]]:
        try:
            return self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    'role': 'system',
                    'content': self.system_message
                }] + messages,
                stream=is_streaming,
                response_format={ 'type': 'json_object' if is_json else 'text' }
            )
        
        # TODO: Proper handling of each one
        except KeyboardInterrupt:
            raise
        except openai.RateLimitError as e:
            if e.code == 'insufficient_quota':
                raise QuotaExceededException()
            raise
        except (
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.InternalServerError,
            openai.UnprocessableEntityError
        ):
            # These are OpenAI server/API issues
            raise
        except (
            openai.AuthenticationError,
            openai.PermissionDeniedError
        ):
            # These should have been handled during setup
            raise
        except (
            openai.BadRequestError,
            openai.ConflictError,
            openai.NotFoundError
        ):
            # These should not happen
            raise

    @backoff.on_exception(backoff.expo,
                          (
                            openai.APIConnectionError,
                            openai.APITimeoutError,
                            openai.RateLimitError,
                            openai.InternalServerError,
                            openai.UnprocessableEntityError
                          ),
                          max_tries=3)
    async def new_basic_async_chat_request(self, messages: list) -> Optional[dict]:
        try:
            return await self.async_client.chat.completions.create(
                model=self.model,
                messages=[{
                    'role': 'system',
                    'content': self.system_message
                }] + messages,
                stream=False
            )
        
        # TODO: Proper handling of each one
        except KeyboardInterrupt:
            raise
        except openai.RateLimitError as e:
            if e.code == 'insufficient_quota':
                raise QuotaExceededException()
            raise
        except (
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.InternalServerError,
            openai.UnprocessableEntityError
        ):
            # These are OpenAI server/API issues
            raise
        except (
            openai.AuthenticationError,
            openai.PermissionDeniedError
        ):
            # These should have been handled during setup
            raise
        except (
            openai.BadRequestError,
            openai.ConflictError,
            openai.NotFoundError
        ):
            # These should not happen
            raise
    
    # TODO: get the correct typehints from openai
    def update_token_usage(self, chat_completion) -> None:
        prompt_tokens = chat_completion.usage.prompt_tokens
        completion_tokens = chat_completion.usage.completion_tokens

        self.token_counter.add_input_tokens(prompt_tokens)
        self.token_counter.add_output_tokens(completion_tokens)
