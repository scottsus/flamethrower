import json

def pretty_print(conv: list|str) -> str:
    if isinstance(conv, str):
        conv = json.loads(conv)
    
    pretty = ''
    for message in conv:
        name = ''
        try:
            name = message["name"]
        except KeyError:
            pass
        pretty += f'[[{message["role"]}|{name}]]\n{message["content"]}\n'
    return f'{pretty}\n'