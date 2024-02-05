from unittest.mock import patch
from flamethrower.agents.util_agents.file_chooser import FileChooser

def test_file_chooser_init() -> None:
    with patch('flamethrower.agents.util_agents.file_chooser.LLM') as mock_llm:
        file_chooser = FileChooser()
        
        assert file_chooser.llm == mock_llm.return_value
        mock_llm.assert_called_once()
