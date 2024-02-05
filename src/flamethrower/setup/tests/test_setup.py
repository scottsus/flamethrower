from unittest.mock import patch, call
from flamethrower.setup.setup import setup_api_key, setup_zsh_env
from flamethrower.config.constants import *

def try_api_key_side_effect(api_key: str) -> bool:
    if api_key:
        return True
    return False

def test_setup_api_key_from_cache() -> None:
    with patch('flamethrower.setup.setup.get_api_key', return_value='valid_cached_api_key'), \
        patch('flamethrower.setup.setup.try_api_key') as mock_try_api_key, \
        patch('os.getenv', return_value=None), \
        patch('flamethrower.setup.setup.set_api_key') as mock_set_api_key:
        
        mock_try_api_key.side_effect = try_api_key_side_effect

        assert setup_api_key() == True
        mock_set_api_key.assert_not_called()

def test_setup_api_key_from_env() -> None:
    with patch('flamethrower.setup.setup.get_api_key', return_value=''), \
        patch('flamethrower.setup.setup.try_api_key') as mock_try_api_key, \
        patch('os.getenv', return_value='valid_env_api_key'), \
        patch('flamethrower.setup.setup.set_api_key') as mock_set_api_key:

        mock_try_api_key.side_effect = try_api_key_side_effect

        assert setup_api_key() == True
        mock_set_api_key.assert_called_with('valid_env_api_key')

def test_setup_zsh_env_first_time() -> None:
    with patch('builtins.open') as mock_open, \
        patch('flamethrower.setup.setup.os.path.exists', return_value=False), \
        patch('flamethrower.setup.setup.os.makedirs') as mock_makedirs, \
        patch('flamethrower.setup.setup.resources.path') as mock_resources_path, \
        patch('flamethrower.setup.setup.shutil.copy') as mock_copy, \
        patch('flamethrower.setup.setup.Repo.clone_from') as mock_clone_from, \
        patch('os.environ.copy', return_value={}) as mock_environ_copy, \
        patch('flamethrower.setup.setup.setup_api_key', return_value=True) as mock_setup_api_key, \
        patch('builtins.print') as mock_print:
        
        assert setup_zsh_env() is not None

        mock_makedirs.assert_has_calls([
            call(FLAMETHROWER_DIR, exist_ok=True),
            call(FLAMETHROWER_LOG_DIR, exist_ok=True),
            call(FLAMETHROWER_ZSH_DIR, exist_ok=True)
        ])

        mock_print.assert_called_once()

        mock_resources_path.assert_has_calls([
            call(f'{FLAMETHROWER_PACKAGE_NAME}.data', 'README.md'),
            call().__enter__(),
            call().__exit__(None, None, None),
            
            call(f'{FLAMETHROWER_PACKAGE_NAME}.data', '.sample.gitignore'),
            call().__enter__(),
            call().__exit__(None, None, None),

            call(f'{FLAMETHROWER_PACKAGE_NAME}.data', '.sample.zshrc'),
            call().__enter__(),
            call().__exit__(None, None, None)
        ])

        assert mock_copy.call_count == 3

        mock_open.assert_called_with(get_zsh_history_path(), 'w')

        mock_clone_from.assert_called_once()
        mock_environ_copy.assert_called_once()
        mock_setup_api_key.assert_called_once()

def test_setup_zsh_env_nth_time() -> None:
    with patch('flamethrower.setup.setup.os.path.exists', return_value=True), \
        patch('flamethrower.setup.setup.os.makedirs') as mock_makedirs, \
        patch('flamethrower.setup.setup.resources.path') as mock_resources_path, \
        patch('flamethrower.setup.setup.shutil.copy') as mock_copy, \
        patch('flamethrower.setup.setup.Repo.clone_from') as mock_clone_from, \
        patch('os.environ.copy', return_value={}) as mock_environ_copy, \
        patch('flamethrower.setup.setup.setup_api_key', return_value=True) as mock_setup_api_key, \
        patch('builtins.print') as mock_print:

        assert setup_zsh_env() is not None

        mock_makedirs.assert_not_called()
        mock_resources_path.assert_not_called()
        mock_copy.assert_not_called()
        mock_clone_from.assert_not_called()

        mock_environ_copy.assert_called_once()
        mock_setup_api_key.assert_called_once()

        mock_print.assert_not_called()
