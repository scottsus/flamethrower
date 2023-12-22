import os
import re
import time
import hashlib
from pydantic import BaseModel
from openai import OpenAI

class LLM(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    client: OpenAI = None
    cache_dir: str = os.path.join(
        os.path.dirname(__file__),
        'response_cache'
    )

    def __init__(self, **data):
        super().__init__(**data)
        self.client: OpenAI = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )

    def new_chat_request(self, query: str, model: str ='gpt-3.5-turbo'):
        stream = self.client.chat.completions.create(
            model=model,
            messages=[{
                'role': 'user',
                'content': query or 'Write typescript code for the LeetCode TwoSum problem',
            }],
            stream=True,
        )

        return stream

    def ask(self, query: str):
        key = self.generate_cache_key(query)
        cache_path = os.path.join(self.cache_dir, key)

        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cached_response = f.read()
                # this splits ```, ' ', and '\n' into separate tokens
                tokens = re.findall(r'```|\S+|\s+', cached_response)
                for token in tokens:
                    nice_delay = 0.03
                    time.sleep(nice_delay)
                    yield token
                yield None
        
        else:
            stream = self.new_chat_request(query)
            response = ''

            try:
                for chunk in stream:
                    token = chunk.choices[0].delta.content or ''
                    response += token
                    yield token
            except AttributeError:
                pass
            finally:
                with open(cache_path, 'w') as f:
                    f.write(response)

                yield None
        

    def generate_cache_key(self, query: str):
        return hashlib.md5(query.encode()).hexdigest() + '.txt'
