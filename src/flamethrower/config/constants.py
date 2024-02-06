import os

"""
🔥 main directory
"""

FLAMETHROWER_PACKAGE_NAME = 'flamethrower'

FLAMETHROWER_DIR_NAME = '.flamethrower'

FLAMETHROWER_DIR = os.path.join(
    os.getcwd(), FLAMETHROWER_DIR_NAME
)

def flamethrower_path(file_name: str) -> str:
    return os.path.join(
        FLAMETHROWER_DIR, file_name
    )

FLAMETHROWER_README_FILE_NAME = 'README.md'
FLAMETHROWER_GITIGNORE_FILE_NAME = '.gitignore'
FLAMETHROWER_ENV_FILE_NAME = '.env'

def get_flamethrower_readme_path() -> str:
    return flamethrower_path(FLAMETHROWER_README_FILE_NAME)

def get_flamethrower_gitignore_path() -> str:
    return flamethrower_path(FLAMETHROWER_GITIGNORE_FILE_NAME)

def get_flamethrower_env_path() -> str:
    return flamethrower_path(FLAMETHROWER_ENV_FILE_NAME)

"""
🔧 zsh configs
"""

FLAMETHROWER_ZSH_DIR_NAME = 'zsh'
FLAMETHROWER_ZSH_DIR = flamethrower_path(FLAMETHROWER_ZSH_DIR_NAME)

def flamethrower_zsh_dir(file_name: str) -> str:
    return os.path.join(
        FLAMETHROWER_ZSH_DIR, file_name
    )

ZSH_CONFIG_FILE_NAME = '.zshrc'
ZSH_HISTORY_FILE_NAME = '.zsh_history'

def get_zsh_config_path() -> str:
    return flamethrower_zsh_dir(ZSH_CONFIG_FILE_NAME)

def get_zsh_history_path() -> str:
    return flamethrower_zsh_dir(ZSH_HISTORY_FILE_NAME)

"""
🪵 flamethrower logs
"""

FLAMETHROWER_LOG_DIR_NAME = 'logs'
FLAMETHROWER_LOG_DIR = flamethrower_path(FLAMETHROWER_LOG_DIR_NAME)

def flamethrower_log_dir(file_name: str) -> str:
    return os.path.join(
        FLAMETHROWER_LOG_DIR, file_name
    )

SUMMARY_FILE_NAME = 'workspace_summary.log'
DIR_TREE_FILE_NAME = 'dir_tree.log'
DIR_LIST_FILE_NAME = 'dir_dict.json'
CONVERSATION_FILE_NAME = 'conv.json'
PRETTY_CONVERSATION_FILE_NAME = 'conv.log'
CURRENT_FILES_FILE_NAME = 'current_files.log'
LAST_PROMPT_FILE_NAME = 'last_prompt.log'
LAST_RESPONSE_FILE_NAME  = 'last_response.log'
PATCH_FILE_NAME = 'update.patch'

def get_workspace_summary_path() -> str:
    return flamethrower_log_dir(SUMMARY_FILE_NAME)

def get_dir_tree_path() -> str:
    return flamethrower_log_dir(DIR_TREE_FILE_NAME)

def get_dir_dict_path() -> str:
    return flamethrower_log_dir(DIR_LIST_FILE_NAME)

def get_current_files_path() -> str:
    return flamethrower_log_dir(CURRENT_FILES_FILE_NAME)

def get_conversation_path() -> str:
    return flamethrower_log_dir(CONVERSATION_FILE_NAME)

def get_pretty_conversation_path() -> str:
    return flamethrower_log_dir(PRETTY_CONVERSATION_FILE_NAME)

def get_last_prompt_path() -> str:
    return flamethrower_log_dir(LAST_PROMPT_FILE_NAME)

def get_last_response_path() -> str:
    return flamethrower_log_dir(LAST_RESPONSE_FILE_NAME)

def get_patch_path() -> str:
    return flamethrower_log_dir(PATCH_FILE_NAME)