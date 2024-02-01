import os
import sys
from unittest.mock import patch, Mock
from flamethrower.shell.shell import Shell
from flamethrower.test_utils.mocks.mock_container import mock_container

def todo_test_shell_run() -> None:
    base_dir = os.getcwd()          # Cannot be mocked because it is called during Shell() instantiation
    env_dict = os.environ.copy()    # Need a real env?

    with patch('sys.argv', return_value=['flamethrower']), \
        patch('flamethrower.setup.setup.setup_zsh_env', return_value=env_dict) as setup, \
        patch('subprocess.Popen', return_value=Mock()) as mock_popen, \
        patch('termios.tcgetattr', return_value=[]) as mock_tcgetattr, \
        patch('termios.tcsetattr') as mock_tcsetattr, \
        patch('tty.setraw') as mock_setraw, \
        patch('flamethrower.containers.container', return_value=mock_container), \
        patch('flamethrower.context.dir_walker.setup_dir_summary') as dir_walker, \
        patch('select.select') as mock_select, \
        patch('os.read') as mock_os_read, \
        patch('os.write') as mock_os_write, \
        patch('os.close') as mock_os_close, \
        patch('builtins.print') as mock_print:

        shell = Shell()
        shell.run()

        assert shell.base_dir == base_dir

        """
        This file is particularly problematic to test because of the pty.
        """
