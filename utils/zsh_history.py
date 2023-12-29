import config.constants as config

def get_last_user_cmd() -> str:
    with open(config.get_zsh_history_path()) as f:
        history = f.read()
        if not history:
            return ''
        
        history = history.split('\n')
        last_index = -1
        last_command = history[last_index]
        
        while last_command == '':
            last_index -= 1
            last_command = history[last_index]

        return last_command
    
def update_zsh_history(query: str) -> None:
    with open(config.get_zsh_history_path(), 'a') as f:
        f.write(query + '\n')
        