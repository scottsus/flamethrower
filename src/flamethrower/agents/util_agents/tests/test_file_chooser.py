from unittest.mock import patch, call
from flamethrower.agents.util_agents.file_chooser import FileChooser
import flamethrower.config.constants as config

def mock_file_chooser() -> FileChooser:
    with patch('flamethrower.utils.token_counter.TokenCounter'):
        return FileChooser()

def test_file_chooser_init() -> None:
    with patch('flamethrower.agents.util_agents.file_chooser.LLM') as mock_llm, \
        patch('flamethrower.utils.token_counter.TokenCounter'):
        file_chooser = FileChooser()
        
        assert file_chooser.llm == mock_llm.return_value
        mock_llm.assert_called_once()

def test_file_chooser_infer_target_paths() -> None:
    description = 'This is a test description.'
    dir_structure = 'This is a fake dir structure.'
    conv = 'This is a fake conversation.'
    test_file_paths = ['file1', 'file2', 'file3']
    test_response = { 'file_paths': test_file_paths }
    
    with patch('flamethrower.agents.util_agents.file_chooser.LLM.new_json_request',
            return_value=test_response
        ) as mock_llm, \
        patch('flamethrower.agents.util_agents.file_chooser.FileChooser.write_to_current_files'
        ) as mock_write:
        fc = mock_file_chooser()

        with patch('builtins.open') as mock_file:
            target_file_paths = fc.infer_target_file_paths(description, dir_structure, conv)

            mock_file.assert_called_once_with(config.get_dir_dict_path(), 'r')
            mock_llm.assert_called_once()
            mock_write.assert_called_once()

            assert target_file_paths == test_file_paths

def test_file_chooser_write_to_current_files() -> None:
    fc = mock_file_chooser()
    file_paths = ['file1', 'file2', 'file3']

    with patch('builtins.open') as mock_file:
        fc.write_to_current_files(file_paths)

        mock_file.assert_has_calls([
            call(config.get_current_files_path(), 'w'),
            call().__enter__(),
            call().__enter__().write(file_paths[0] + '\n'),
            call().__enter__().write(file_paths[1] + '\n'),
            call().__enter__().write(file_paths[2] + '\n'),
            call().__exit__(None, None, None)
        ])
