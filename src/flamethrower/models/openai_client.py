import openai
from openai import OpenAI, AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import backoff

from flamethrower.models.client_interface import LLMClient
from flamethrower.models.models import OPENAI_GPT_4_TURBO
from flamethrower.utils import key_handler as kh
from flamethrower.exceptions.exceptions import *

from typing import cast, Any, Dict, List, Iterator, Tuple

class OpenAIClient(LLMClient):
    system_message: str
    model: str = OPENAI_GPT_4_TURBO

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client: OpenAI = OpenAI(api_key=kh.get_api_key())
        self._async_client: AsyncOpenAI = AsyncOpenAI(api_key=kh.get_api_key())
    
    @property
    def client(self) -> OpenAI:
        return self._client
    
    @property
    def async_client(self) -> AsyncOpenAI:
        return self._async_client
    
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
    def new_basic_chat_request(self, messages: List[Dict[str, str]]) -> Tuple[str, int, int, str]:
        try:
            chat_completion_messages = cast(
                List[ChatCompletionMessageParam],
                [{'role': 'system', 'content': self.system_message }] + messages
            )

            res = self.client.chat.completions.create(
                model=self.model,
                messages=chat_completion_messages,
                response_format={ 'type': 'text' }
            )

            content = res.choices[0].message.content or ''
            prompt_tokens, completion_tokens = self.get_token_usage(res)
            
            return (content, prompt_tokens, completion_tokens, self.model)
        
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
    def new_streaming_chat_request(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        try:
            chat_completion_messages = cast(
                List[ChatCompletionMessageParam],
                [{'role': 'system', 'content': self.system_message }] + messages
            )
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=chat_completion_messages,
                stream=True,
                response_format={ 'type': 'text' }
            )

            for chunk in stream:
                choice = chunk.choices[0]
                if choice.finish_reason == 'stop':
                    return
                
                yield choice.delta.content or ''
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
    async def new_basic_async_chat_request(self, messages: List[Dict[str, str]]) -> Tuple[str, int, int, str]:
        try:
            chat_completion_messages = cast(
                List[ChatCompletionMessageParam],
                [{'role': 'system', 'content': self.system_message }] + messages
            )

            res = await self.async_client.chat.completions.create(
                model=self.model,
                messages=chat_completion_messages,
            )

            content = res.choices[0].message.content or ''
            (prompt_tokens, completion_tokens) = self.get_token_usage(res)

            return (content, prompt_tokens, completion_tokens, self.model)
        
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
    def new_json_request(self, messages: List[Dict[str, str]]) -> Tuple[str, int, int, str]:
        try:
            chat_completion_messages = cast(
                List[ChatCompletionMessageParam],
                [{'role': 'system', 'content': self.system_message }] + messages
            )

            res = self.client.chat.completions.create(
                model=self.model,
                messages=chat_completion_messages,
                response_format={ 'type': 'json_object' }
            )

            content = res.choices[0].message.content or ''
            (prompt_tokens, completion_tokens) = self.get_token_usage(res)

            return (content, prompt_tokens, completion_tokens, self.model)
        
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
    
    def get_token_usage(self, chat_completion: ChatCompletion) -> Tuple[int, int]:
        if not chat_completion.usage:
            raise Exception('openai_client.update_token_usage: chat_completion.usage is None')

        prompt_tokens = chat_completion.usage.prompt_tokens
        completion_tokens = chat_completion.usage.completion_tokens

        return (prompt_tokens, completion_tokens)
