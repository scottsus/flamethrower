from openai import OpenAI

model = OpenAI()
res = model.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are humorous and love emojis."},
        {"role": "user", "content": "What is the meaning of life?"},  # Changed 'human' to 'user'
    ]
)

# I assume the correct attribute names to access the message should be 'choices[0].message.content' rather than 'choices.message.content'
print(res.choices[0].message.content)  # Modified the line to correctly index into the response
