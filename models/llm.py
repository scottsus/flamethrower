import os
import json
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

    def new_json_request(self, query: str, tools: list[str], model: str = 'gpt-3.5-turbo'):
        tool_calls = None
        while tool_calls is None:
            res = self.client.chat.completions.create(
                model=model,
                messages=[{
                    'role': 'user',
                    'content': query
                }],
                tools=tools,
            )
            tool_calls = res.choices[0].message.tool_calls
        
        return json.loads(tool_calls[0].function.arguments)
    
