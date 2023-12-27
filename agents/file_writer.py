from models.llm import LLM

# Given an LLM coding response, extract the code and write it to a file
llm = LLM()

# stream = llm.new_chat_request('Write python code to solve the LeetCode TwoSum problem')

# content = ''
# for token in stream:
#     print(token.choices[0].delta.content, end='', flush=True)

# print(content)

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'blah',
            'description': 'Actual code that will be written into a target file',
            'parameters': {
                'type': 'object',
                'properties': {
                    'explanation': {
                        'type': 'string'
                    },
                    'code': {
                        'type': 'string'
                    },
                    'target_file': {
                        'type': 'string'
                    }
                },
                'required': ['target_file', 'code']
            }
        }
    }
]

starting_point = """
class A():
    def greeting():
        print('hello')

class B():
    def greeting():
        print('hello')

class C():
    def greeting():
        print('hello')

class Solution():
    def twoSum():
        pass
"""

solution = """
This looks like the classic LeetCode TwoSum problem! In order to solve this in Python, use the following implementation below.

```
... existing code ...

class Solution(object):
    def twoSum(self, nums, target):
        h = {}
        for i, num in enumerate(nums):
            n = target - num
            if n not in h:
                h[num] = i
            else:
                return [h[n], i]
```
"""

res = llm.new_json_request(f'This is the starting code: {starting_point}.\n'
                           f'This is the solution provided by an expert engineer: {solution}.\n'
                           f'Your crucial task is to incorporate the solution above into the starting code, while providing a short explanation of the solution.\n'
                           'You MUST write your response to "blah.py"', tools=tools)

prev = ''
content = ''
logfile = open('logfile.txt', 'w')
for chunk in res:
    try:
        token = chunk.choices[0].delta.tool_calls[0].function.arguments
        if prev.endswith('\\'):
            if token.startswith('n'):
                token = token[1:]
                print(f'\n{token}', end='', flush=True)
                content += '\n' + token
                prev = '\n'
            # else if token is some other escape
        elif token.endswith('\\'):
            token = token[:-1]
            print(token, end='', flush=True)
            content += token
            prev = '\\'
        else:
            if token == '\\n' or token == '\\\n':
                token = '\n'
            print(token, end='', flush=True)
            content += token
            prev = token
    except TypeError:
        pass

print('\n')
print(content)


# target_file, code = res['target_file'], res['code']
# print(code)

# with open(target_file, 'w') as f:
#     f.write(code)
#     print(code)