from openai import OpenAI
import flamethrower.config.constants as config

def get_api_key() -> str:
    try:
        with open(config.get_flamethrower_env_path(), 'r') as f:
            env_list = f.readlines()
            for env in env_list:
                if env.startswith('OPENAI_API_KEY'):
                    return env.split('=')[1].strip()
    except FileNotFoundError:
        with open(config.get_flamethrower_env_path(), 'w') as f:
            f.write('')
    
    return ''

def set_api_key(openai_api_key: str) -> None:
    with open(config.get_flamethrower_env_path(), 'w') as f:
        f.write(f'OPENAI_API_KEY={openai_api_key}\n')

def try_api_key(openai_api_key: str) -> bool:
    try:
        model = OpenAI(api_key=openai_api_key)
        _ = model.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{
                'role': 'user',
                'content': 'Say "Hi".'
            }]
        )
        return True
    except Exception:
        return False
    