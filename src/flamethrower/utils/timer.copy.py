import time
from contextlib import contextmanager
from flamethrower.shell.printer import Printer

class Timer:
    def __init__(self, printer):
        self.printer = printer

    @contextmanager
    def get_execution_time(self):
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            exec_time_message = self.format_exec_time_message(start_time, end_time)
            self.printer.print_default(exec_time_message)  # Removed the reset keyword argument

    @staticmethod
    def format_exec_time_message(start_time: float, end_time: float) -> str:
        exec_time = end_time - start_time
        num_mins, num_secs = divmod(exec_time, 60)
        time_parts = []
        if num_mins >= 1:
            time_parts.append(f'{int(num_mins)}m')
        time_parts.append(f'{num_secs:.1f}s')
        
        return f'\nThis run took {" ".join(time_parts)} 🚀'

# Example usage
if __name__ == '__main__':
    class MockPrinter:  # Updated the MockPrinter to simulate the Printer's print_default behavior
        def print_default(self, message):
            print(message)

    printer = MockPrinter()  # This should be MockPrinter when simulating behavior
    timer = Timer(printer=printer)

    with timer.get_execution_time():
        time.sleep(1.23)  # simulate some operation taking time
