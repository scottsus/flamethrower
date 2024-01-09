import os
import shutil
from git import Repo
from importlib import resources
from flamethrower.config.constants import *

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

def setup_zsh_env() -> dict | None:
    is_first_setup = False

    if not os.path.exists(FLAMETHROWER_DIR):
        os.makedirs(FLAMETHROWER_DIR, exist_ok=True)
        os.makedirs(FLAMETHROWER_LOG_DIR, exist_ok=True)
        os.makedirs(FLAMETHROWER_ZSH_DIR, exist_ok=True)
        is_first_setup = True

    zshrc_path = get_zsh_config_path()
    if not os.path.exists(zshrc_path):
        with resources.path(f'{FLAMETHROWER_PACKAGE_NAME}.data', '.sample.zshrc') as f:
            shutil.copy(f, zshrc_path)
    
    flamethrower_gitignore_path = get_flamethrower_gitignore_path()
    if not os.path.exists(flamethrower_gitignore_path):
        with resources.path(f'{FLAMETHROWER_PACKAGE_NAME}.data', '.sample.gitignore') as f:
            shutil.copy(f, flamethrower_gitignore_path)
    
    zsh_autosuggestions_path = flamethrower_zsh_dir('zsh-autosuggestions')
    if not os.path.exists(zsh_autosuggestions_path):
        Repo.clone_from('https://github.com/zsh-users/zsh-autosuggestions.git', zsh_autosuggestions_path)

    zsh_syntax_highlighting_path = flamethrower_zsh_dir('zsh-syntax-highlighting')
    if not os.path.exists(zsh_syntax_highlighting_path):
        Repo.clone_from('https://github.com/zsh-users/zsh-syntax-highlighting.git', zsh_syntax_highlighting_path)
    
    zsh_history_path = get_zsh_history_path()
    if not os.path.exists(zsh_history_path):
        with open(zsh_history_path, 'w') as f:
            f.write('')
    
    env = os.environ.copy()
    env['ZDOTDIR'] = FLAMETHROWER_ZSH_DIR

    # Basic check to see that OpenAI API Key exists
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        print(
            f'Error: OpenAI API Key not found. Please run the following command in your shell:\n'
            '\n  `export OPENAI_API_KEY=sk-xxxx`\n\n'
            'You can find your OpenAI Api Keys at https://platform.openai.com/api-keys'
        )
        return None

    if is_first_setup:
        print(colored_welcome_screen)

    return env
