from unittest.mock import patch, mock_open
from flamethrower.utils.zsh_history import (
    get_last_user_cmd,
    update_zsh_history,
)
import flamethrower.config.constants as config

def test_zsh_history_get_last_user_cmd() -> None:
    mock_history = """
    command_1
    command_2
    command_3
    """

    with patch('builtins.open', mock_open(read_data=mock_history)):
        last_user_cmd = get_last_user_cmd()
        assert last_user_cmd == 'command_3', f'Expected last_user_cmd to be "command_3", got {last_user_cmd}'

def test_zsh_history_update_zsh_history() -> None:
    mock_history = """
    command_1
    command_2
    command_3
    """

    with patch('builtins.open', mock_open(read_data=mock_history)) as mock_history_file:
        new_command = 'command_4 🚀'
        update_zsh_history(new_command)
        mock_history_file.assert_called_once_with(config.get_zsh_history_path(), 'a')
        mock_history_file().write.assert_called_once_with(new_command + '\n')
