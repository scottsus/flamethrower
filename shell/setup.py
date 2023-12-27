import os
from context.prompt import Prompt
from config.constants import *

zshrc_contents = """# basic zshrc for pty

PS1='%B%F{red}%n:%f %F{white}%1~%f%b 🌊 '

source $ZDOTDIR/zsh-autosuggestions/zsh-autosuggestions.zsh
source $ZDOTDIR/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

setopt INC_APPEND_HISTORY
"""

original_welcome_screen = """
    ______                     __  __
   / __/ /___ _____ ___  ___  / /_/ /_  _________ _      _____  _____
  / /_/ / __ `/ __ `__ \/ _ \/ __/ __ \/ ___/ __ \ | /| / / _ \/ ___/
 / __/ / /_/ / / / / / /  __/ /_/ / / / /  / /_/ / |/ |/ /  __/ /
/_/ /_/\__,_/_/ /_/ /_/\___/\__/_/ /_/_/   \____/|__/|__/\___/_/

    Major credits to pyfiglet to make this possible 🚀
"""

colored_welcome_screen = (
    "\033[31m    ______                     __  __\n"
    "   / __/ /___ _____ ___  ___  / /_/ /_  _________ _      _____  _____\033[0m\n"
    "\033[35m  / /_/ / __ `/ __ `__ \\/ _ \\/ __/ __ \\/ ___/ __ \\ | /| / / _ \\/ ___/\n"
    " / __/ / /_/ / / / / / /  __/ /_/ / / / /  / /_/ / |/ |/ /  __/ /\033[0m\n"
    "\033[34m/_/ /_/\\__,_/_/ /_/ /_/\\___/\\__/_/ /_/_/   \\____/|__/|__/\\___/_/\033[0m"
    "\n"
)

def setup_zsh_env() -> Prompt:
    if not os.path.exists(FLAMETHROWER_DIR):
        os.makedirs(FLAMETHROWER_DIR)
    
    zshrc_path = get_zsh_config_path()
    if not os.path.exists(zshrc_path):
        with open(zshrc_path, 'w') as f:
            f.write(zshrc_contents)
    
    zsh_autosuggestions_path = flamethrower_path('zsh-autosuggestions')
    if not os.path.exists(zsh_autosuggestions_path):
        os.system(f'git clone git@github.com:zsh-users/zsh-autosuggestions.git {zsh_autosuggestions_path}')

    zsh_syntax_highlighting_path = flamethrower_path('zsh-syntax-highlighting')
    if not os.path.exists(zsh_syntax_highlighting_path):
        os.system(f'git clone git@github.com:zsh-users/zsh-syntax-highlighting.git {zsh_syntax_highlighting_path}')
    
    zsh_history_path = get_zsh_history_path()
    if not os.path.exists(zsh_history_path):
        with open(zsh_history_path, 'w') as f:
            f.write('')
    
    if not os.path.exists(FLAMETHROWER_LOG_DIR):
        os.makedirs(FLAMETHROWER_LOG_DIR)

    prompt = Prompt()
    # TODO: use printer API
    print(prompt.generate_initial_prompt())

    return prompt
    
