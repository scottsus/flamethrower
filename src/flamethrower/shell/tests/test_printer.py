import sys
import pytest
from unittest.mock import patch, call

from flamethrower.shell.printer import Printer
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.shell.shell_manager import ShellManager
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.utils.colors import *

from flamethrower.test_utils.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.test_utils.mocks.mock_shell_manager import mock_shell_manager
from flamethrower.test_utils.mocks.mock_token_counter import mock_token_counter

@pytest.fixture
def mock_printer() -> Printer:
    return Printer(
        leader_fd=sys.stdout.fileno(),
        stdout_fd=sys.stdout.fileno(),
        conv_manager=mock_conv_manager(),
        shell_manager=mock_shell_manager(),
        token_counter=mock_token_counter(),
    )

def test_printer_init(mock_printer: Printer) -> None:
    printer = mock_printer

    assert printer.leader_fd == sys.stdout.fileno()
    assert printer.stdout_fd == sys.stdout.fileno()
    assert isinstance(printer.conv_manager, ConversationManager)
    assert isinstance(printer.shell_manager, ShellManager)
    assert isinstance(printer.token_counter, TokenCounter)

def test_printer_write_leader(mock_printer: Printer) -> None:
    printer = mock_printer

    with patch('os.write') as mock_os_write:
        printer.write_leader(b'hello')
        mock_os_write.assert_called_once_with(printer.leader_fd, b'hello')
    
def test_printer_print_stdout(mock_printer: Printer) -> None:
    printer = mock_printer

    with patch('os.write') as mock_os_write:
        byte_message = b'bytes'
        printer.print_stdout(byte_message)
        mock_os_write.assert_called_once_with(printer.stdout_fd, byte_message)

        str_message = 'string'
        printer.print_stdout(str_message)
        mock_os_write.assert_called_with(printer.stdout_fd, str_message.encode('utf-8'))

def test_printer_print_color(mock_printer: Printer) -> None:
    printer = mock_printer

    with patch('os.write') as mock_os_write:
        bytes_message = b'bytes'
        printer.print_color(bytes_message, STDIN_RED)
        mock_os_write.assert_has_calls([
            call(printer.stdout_fd, STDIN_RED),
            call(printer.stdout_fd, bytes_message),
        ])

"""
TODO: Test other functions
"""
