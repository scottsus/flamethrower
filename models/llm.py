import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
)

def ask(query: str):
    stream = client.chat.completions.create(
        model='gpt-3.5-turbo',
        # model='gpt-4',
        messages=[{
            'role': 'user',
            # 'content': 'Write typescript code for the LeetCode TwoSum problem'
            'content': query,
        }],
        stream=True,
    )

    return stream
