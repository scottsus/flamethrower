import os
import json
from pydantic import BaseModel
from openai import OpenAI

class LLM(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    client: OpenAI = None

    def __init__(self, **data):
        super().__init__(**data)
        self.client: OpenAI = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )

    def new_chat_request(self, messages, model: str ='gpt-4'):
        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )

        return stream

    def new_json_request(self, query: str, tools: list[str], model: str = 'gpt-4'):
        tool_calls = None
        while tool_calls is None:
            try:
                res = self.client.chat.completions.create(
                    model=model,
                    messages=[{
                        'role': 'user',
                        'content': query
                    }],
                    tools=tools,
                    # stream=True,
                )
                tool_calls = res.choices[0].message.tool_calls
                # return stream
            except json.decoder.JSONDecodeError:
                pass
        
        return json.loads(tool_calls[0].function.arguments)
    