from openai import OpenAI

model = OpenAI()
res = model.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are humorous and love emojis."},
        {"role": "human", "content": "What is the meaning of life?"},
    ]
)

print(res.choice.message.content)
