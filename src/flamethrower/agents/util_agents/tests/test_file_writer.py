from unittest.mock import patch
from flamethrower.agents.util_agents.file_writer import FileWriter

def mock_file_writer() -> FileWriter:
    return FileWriter(base_dir='flamethrower/some/path')

def test_file_writer_init() -> None:
    base_dir = 'flamethrower/some/path'

    with patch('flamethrower.agents.util_agents.file_writer.LLM') as mock_llm:
        file_writer = FileWriter(base_dir=base_dir)
        
        assert file_writer.base_dir == base_dir
        assert file_writer.llm == mock_llm.return_value
        mock_llm.assert_called_once()

def test_file_writer_write_code() -> None:
    pass

def test_file_writer_choose_file_path() -> None:
    pass

def test_file_writer_make_original_file_copy() -> None:
    pass

def test_file_writer_clean_backticks() -> None:
    file_writer = mock_file_writer()

    # Test case where string contains backticks
    test_string_with_backticks = """
    Here is the given code:
    ```
    public class Main {
        public static void main(String[] args) {
            System.out.println("Hello, world!");
        }
    }
    ```
    """
    expected_string_without_backticks = """
    public class Main {
        public static void main(String[] args) {
            System.out.println("Hello, world!");
        }
    }
    """
    result = file_writer.clean_backticks(test_string_with_backticks)
    assert result == expected_string_without_backticks
