import os

flamethrower_dir = os.path.join(os.getcwd(), '.flamethrower')

zshrc_contents = """# basic zshrc for pty

PS1='%B%F{red}%n:%f %F{white}%1~%f%b 🌊 '

source $ZDOTDIR/zsh-autosuggestions/zsh-autosuggestions.zsh
source $ZDOTDIR/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
"""

def setup_zsh_env():
    if not os.path.exists(flamethrower_dir):
        os.makedirs(flamethrower_dir)
    
    zshrc_path = f'{flamethrower_dir}/.zshrc'
    if not os.path.exists(zshrc_path):
        with open(zshrc_path, 'w') as f:
            f.write(zshrc_contents)
    
    zsh_autosuggestions_path = f'{flamethrower_dir}/zsh-autosuggestions'
    if not os.path.exists(zsh_autosuggestions_path):
        os.system(f'git clone git@github.com:zsh-users/zsh-autosuggestions.git {zsh_autosuggestions_path}')

    zsh_syntax_highlighting_path = f'{flamethrower_dir}/zsh-syntax-highlighting'
    if not os.path.exists(zsh_syntax_highlighting_path):
        os.system(f'git clone git@github.com:zsh-users/zsh-syntax-highlighting.git {zsh_syntax_highlighting_path}')
