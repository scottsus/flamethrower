from unittest.mock import patch
from flamethrower.agents.util_agents.file_writer import FileWriter

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

def test_file_writer_clean_backticks() -> None:
    pass
