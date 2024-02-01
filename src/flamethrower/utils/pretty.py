import json
from typing import Union, List, Dict

def pretty_print(conv: Union[List[Dict[str, str]], str]) -> str:
    if isinstance(conv, str):
        conv_dict: List[Dict[str, str]] = json.loads(conv)
    else:
        conv_dict = conv
    
    pretty = ''
    for message in conv_dict:
        name = ''
        try:
            name = message["name"]
        except KeyError:
            pass
        pretty += f'[[{message["role"]}|{name}]]\n{message["content"]}\n'
    return f'{pretty}\n'
