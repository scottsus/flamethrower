from rich.console import Console
from rich.syntax import Syntax

def test():
    my_code = '''
    def iter_first_last(values: Iterable[T]) -> Iterable[Tuple[bool, bool, T]]:
        """Iterate and generate a tuple with a flag for first and last value."""
        iter_values = iter(values)
        try:
            previous_value = next(iter_values)
        except StopIteration:
            return
        first = True
        for value in iter_values:
            yield first, False, previous_value
            first = False
            previous_value = value
        yield first, True, previous_value
    '''
    syntax = Syntax(my_code, "python", theme="monokai", line_numbers=True)
    console = Console()
    console.print(syntax)
