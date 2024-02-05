import os
import shutil
from git import Repo
from importlib import resources
from flamethrower.config.constants import *
from flamethrower.utils.key_handler import (
    get_api_key, set_api_key, try_api_key
)
from typing import Dict

original_welcome_screen = """
    ______                     __  __
   / __/ /___ _____ ___  ___  / /_/ /_  _________ _      _____  _____
  / /_/ / __ `/ __ `__ \/ _ \/ __/ __ \/ ___/ __ \ | /| / / _ \/ ___/
 / __/ / /_/ / / / / / /  __/ /_/ / / / /  / /_/ / |/ |/ /  __/ /
/_/ /_/\__,_/_/ /_/ /_/\___/\__/_/ /_/_/   \____/|__/|__/\___/_/

    Major credits to `pyfiglet` for making this possible 🚀
"""

colored_welcome_screen = (
    "\033[31m    ______                     __  __\n"
    "   / __/ /___ _____ ___  ___  / /_/ /_  _________ _      _____  _____\033[0m\n"
    "\033[35m  / /_/ / __ `/ __ `__ \\/ _ \\/ __/ __ \\/ ___/ __ \\ | /| / / _ \\/ ___/\n"
    " / __/ / /_/ / / / / / /  __/ /_/ / / / /  / /_/ / |/ |/ /  __/ /\033[0m\n"
    "\033[34m/_/ /_/\\__,_/_/ /_/ /_/\\___/\\__/_/ /_/_/   \\____/|__/|__/\\___/_/\033[0m"
)

def setup_zsh_env() -> Dict[str, str]:
    if not os.path.exists(FLAMETHROWER_DIR):
        os.makedirs(FLAMETHROWER_DIR, exist_ok=True)
        os.makedirs(FLAMETHROWER_LOG_DIR, exist_ok=True)
        os.makedirs(FLAMETHROWER_ZSH_DIR, exist_ok=True)
        print(colored_welcome_screen)

    flamethrower_readme_path = get_flamethrower_readme_path()
    if not os.path.exists(flamethrower_readme_path):
        with resources.path(f'{FLAMETHROWER_PACKAGE_NAME}.data', 'README.md') as f:
            shutil.copy(f, flamethrower_readme_path)
    
    flamethrower_gitignore_path = get_flamethrower_gitignore_path()
    if not os.path.exists(flamethrower_gitignore_path):
        with resources.path(f'{FLAMETHROWER_PACKAGE_NAME}.data', '.sample.gitignore') as f:
            shutil.copy(f, flamethrower_gitignore_path)
    
    zshrc_path = get_zsh_config_path()
    if not os.path.exists(zshrc_path):
        with resources.path(f'{FLAMETHROWER_PACKAGE_NAME}.data', '.sample.zshrc') as f:
            shutil.copy(f, zshrc_path)

    zsh_history_path = get_zsh_history_path()
    if not os.path.exists(zsh_history_path):
        with open(zsh_history_path, 'w') as f:
            f.write('')

    zsh_syntax_highlighting_path = flamethrower_zsh_dir('zsh-syntax-highlighting')
    if not os.path.exists(zsh_syntax_highlighting_path):
        Repo.clone_from('https://github.com/zsh-users/zsh-syntax-highlighting.git', zsh_syntax_highlighting_path)
    
    env = os.environ.copy()
    env['ZDOTDIR'] = FLAMETHROWER_ZSH_DIR

    if not setup_api_key():
        return {}

    return env

def setup_api_key() -> bool:
    # Check for cached/current OpenAI API Key
    old_openai_api_key = get_api_key()
    old_key_works = try_api_key(old_openai_api_key)
    
    new_openai_api_key = os.getenv('OPENAI_API_KEY')
    new_key_works = try_api_key(new_openai_api_key)
    
    if not old_key_works and not new_key_works:
        print(
            f'Error: OpenAI API Key not found or malfunctioning.\n'
            '\nMaybe this is a new project, so you need to set up your OpenAI API Key again.\n'
            '\nYou can find your OpenAI Api Keys at https://platform.openai.com/api-keys.\n'
        )
        try:
            new_openai_key = input('OPENAI_API_KEY=')
            while try_api_key(new_openai_key) == False:
                print('\nOpenAI API Key still invalid. Please try again.')
                new_openai_key = input('OPENAI_API_KEY=')
            set_api_key(new_openai_key)
        except KeyboardInterrupt:
            return False
    
    if not old_key_works and new_key_works:
        set_api_key(new_openai_api_key)
    
    return True
