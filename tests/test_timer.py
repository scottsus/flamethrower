import pytest
from unittest.mock import Mock
from flamethrower.utils.timer import Timer

@pytest.fixture

def mock_printer():
    printer = Mock()
    printer.print_light_green = Mock()
    return printer

def test_timer_context_manager(mock_printer):
    timer = Timer(printer=mock_printer)

    with timer.get_execution_time() as timer_context:
        pass  # Simulate a quick execution

    assert mock_printer.print_light_green.called, "The print_light_green method should be called."

def test_format_exec_time_message_short_duration(mock_printer):
    timer = Timer(printer=mock_printer)
    message = timer.format_exec_time_message(start_time=0, end_time=1)
    assert '1.0s' in message, "Short duration should be formatted in seconds."

def test_format_exec_time_message_long_duration(mock_printer):
    timer = Timer(printer=mock_printer)
    message = timer.format_exec_time_message(start_time=0, end_time=65)
    assert '1m 5s' in message, "Long duration should be formatted in minutes and seconds."