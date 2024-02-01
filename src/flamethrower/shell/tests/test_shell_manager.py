import sys
import termios
import pytest
from unittest.mock import patch
from flamethrower.shell.shell_manager import ShellManager

@pytest.fixture
def mock_shell_manager() -> ShellManager:
    return ShellManager(
        old_settings=[],
        in_cooked_mode=False,
    )

def test_shell_manager_init(mock_shell_manager: ShellManager) -> None:
    sm = mock_shell_manager

    assert sm.old_settings == []
    assert sm.in_cooked_mode == False

def test_shell_manager_cooked_mode(mock_shell_manager: ShellManager) -> None:
    sm = mock_shell_manager
    sm.in_cooked_mode = False

    with patch('termios.tcsetattr') as mock_termios, \
        patch('tty.setraw') as mock_setraw:
        with sm.cooked_mode():
            pass
    
        assert mock_termios.called_once_with(sys.stdin, termios.TCSADRAIN, sm.old_settings)
        assert mock_setraw.called_once_with(sys.stdin)
        assert sm.in_cooked_mode == False
