import json
import jsonschema
from pydantic import BaseModel
from flamethrower.models.client_interface import LLMClient
from flamethrower.models.openai_client import OpenAIClient
from flamethrower.models.models import OPENAI_GPT_4_TURBO
from flamethrower.containers.lm_container import lm_container
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.exceptions.exceptions import *
from flamethrower.utils.colors import *
from typing import Any, Dict, List, Union, Iterator, Optional

class LLM(BaseModel):
    system_message: str
    model: str = OPENAI_GPT_4_TURBO

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._llm_client: LLMClient = OpenAIClient(system_message=self.system_message)
        self._token_counter = lm_container.token_counter()

    @property
    def llm_client(self) -> LLMClient:
        return self._llm_client
    
    @property
    def token_counter(self) -> TokenCounter:
        return self._token_counter
    
    def new_chat_request(self, messages: List[Dict[str, str]]) -> str:
        try:
            (content, prompt_tokens, completion_tokens, model) = self.llm_client.new_basic_chat_request(messages)

            self.token_counter.add_input_tokens(prompt_tokens, model)
            self.token_counter.add_output_tokens(completion_tokens, model)

            return content
        except KeyboardInterrupt:
            raise
        except Exception:
            raise

    def new_streaming_chat_request(self, messages: List[Dict[str, str]]) -> Optional[Iterator[str]]:
        interrupted = None
        try:
            stream = self.llm_client.new_streaming_chat_request(messages)
            if stream is None:
                raise Exception('LLM.new_streaming_chat_request: stream is None')
            
            self.token_counter.add_streaming_input_tokens(str(messages))
            
            for token in stream:
                yield token
            
            """
            We explicitly yield None to indicate to `Printer.print_llm_response` that the stream has ended.
            """
            yield None
        except KeyboardInterrupt as e:
            interrupted = e
        except QuotaExceededException as e:
            interrupted = e
        except Exception as e:
            yield f'\n\n{STDIN_RED.decode("utf-8")}Error: {e}{STDIN_DEFAULT.decode("utf-8")}\n'
        finally:
            if interrupted:
                raise interrupted
    
    async def new_async_chat_request(self, messages: List[Dict[str, str]]) -> str:
        try:
            (content, prompt_tokens, completion_tokens, model) = await self.llm_client.new_basic_async_chat_request(messages)
            
            self.token_counter.add_input_tokens(prompt_tokens, model)
            self.token_counter.add_output_tokens(completion_tokens, model)

            return content
        except KeyboardInterrupt:
            raise
        except Exception:
            raise

    def new_json_request(self, query: str, json_schema: Dict[str, Any]) -> Union[Dict[Any, Any], List[Dict[Any, Any]]]:
        messages = [{
            'role': 'user',
            'content': query
        }] #TODO: make this list

        max_retries = 3
        for _ in range(max_retries):
            try:
                (content, prompt_tokens, completion_tokens, model) = self.llm_client.new_json_request(messages)
                
                self.token_counter.add_input_tokens(prompt_tokens, model)
                self.token_counter.add_output_tokens(completion_tokens, model)

                loaded_json_obj = json.loads(content)
                if not isinstance(loaded_json_obj, (dict, list)):
                    raise Exception(f'LLM.new_json_request: loaded_json_obj not type dict or list, got {type(loaded_json_obj)}')
                
                jsonschema.validate(loaded_json_obj, json_schema)
                
                return loaded_json_obj
            except jsonschema.exceptions.ValidationError:
                # Just retry and hope for the best
                pass
            except KeyboardInterrupt:
                raise
            except Exception:
                raise
        
        return []
    