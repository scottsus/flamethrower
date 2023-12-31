import os

"""
🔥 main directory
"""

FLAMETHROWER_DIR_NAME = '.flamethrower'

FLAMETHROWER_DIR = os.path.join(
    os.getcwd(), FLAMETHROWER_DIR_NAME
)

def flamethrower_path(file_name: str) -> str:
    return os.path.join(
        FLAMETHROWER_DIR, file_name
    )

"""
🔧 zsh configs
"""

ZSH_CONFIG_FILE_NAME = '.zshrc'
ZSH_HISTORY_FILE_NAME = '.zsh_history'

def get_zsh_config_path() -> str:
    return flamethrower_path(ZSH_CONFIG_FILE_NAME)

def get_zsh_history_path() -> str:
    return flamethrower_path(ZSH_HISTORY_FILE_NAME)

"""
🪵 flamethrower logs
"""

FLAMETHROWER_LOG_DIR_NAME = 'logs'
FLAMETHROWER_LOG_DIR = flamethrower_path('logs')

def flamethrower_log_dir(file_name: str) -> str:
    return os.path.join(
        FLAMETHROWER_LOG_DIR, file_name
    )

DIR_STRUCTURE_FILE_NAME = 'tree.log'
CONVERSATION_FILE_NAME = 'conv.json'
PRETTY_CONVERSATION_FILE_NAME = 'conv.log'
LAST_PROMPT_FILE_NAME = 'last_prompt.log'
LAST_RESPONSE_FILE_NAME  = 'last_response.log'

def get_dir_structure_path() -> str:
    return flamethrower_log_dir(DIR_STRUCTURE_FILE_NAME)

def get_conversation_path() -> str:
    return flamethrower_log_dir(CONVERSATION_FILE_NAME)

def get_pretty_conversation_path() -> str:
    return flamethrower_log_dir(PRETTY_CONVERSATION_FILE_NAME)

def get_last_prompt_path() -> str:
    return flamethrower_log_dir(LAST_PROMPT_FILE_NAME)

def get_last_response_path() -> str:
    return flamethrower_log_dir(LAST_RESPONSE_FILE_NAME)
