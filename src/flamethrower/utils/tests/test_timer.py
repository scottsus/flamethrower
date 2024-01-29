from flamethrower.utils.timer import Timer
from flamethrower.shell.printer import Printer
from flamethrower.tests.mocks.mock_printer import mock_printer
from flamethrower.tests.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.tests.mocks.mock_shell_manager import mock_shell_manager
from flamethrower.tests.mocks.mock_token_counter import mock_token_counter

def test_timer_context_manager(mock_printer: Printer):
    timer = Timer(printer=mock_printer)

    with timer.get_execution_time():
        pass  # Simulate a quick execution

    assert timer.printer.print_light_green.called, 'print_light_green() should have been called.'

def test_format_exec_time_message_short_duration(mock_printer: Printer):
    timer = Timer(printer=mock_printer)
    message = timer.format_exec_time_message(start_time=0, end_time=1)
    assert '1.0s' in message, 'Short duration should be formatted in seconds.'

def test_format_exec_time_message_long_duration(mock_printer):
    timer = Timer(printer=mock_printer)
    message = timer.format_exec_time_message(start_time=0, end_time=65)
    assert '1m 5s' in message, 'Long duration should be formatted in minutes and seconds.'
