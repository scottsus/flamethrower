from openai import OpenAI

model = OpenAI()
res = model.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are humorous and love emojis."},
        {"role": "user", "content": "What is the meaning of life?"},
    ]
)

print(res.choices[0].message.content)  # Corrected access to message content
