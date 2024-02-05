import asyncio
from unittest.mock import patch, call, mock_open, AsyncMock
import flamethrower.config.constants as config
from flamethrower.setup.dir_walker import DirectoryWalker

def test_dir_walker_init() -> None:
    workspace_summary = '📔 Test workspace summary.'
    target_dir = 'some/test/dir'
    file_paths = {
        'src/flamethrower/file_1.py': 'This file is about this and that',
        'src/flamethrower/file_2.py': 'This file is about they and them',
        'src/flamethrower/file_3.py': 'This file is about Tom and Jerry',
    }

    with patch('flamethrower.setup.dir_walker.Summarizer') as mock_summarizer, \
        patch('flamethrower.setup.dir_walker.setup_workspace_summary', return_value=workspace_summary), \
        patch('builtins.open', mock_open(read_data='')) as mock_file, \
        patch('json.loads', return_value=file_paths) as mock_json_loads:
        
        dw = DirectoryWalker(
            workspace_summary=workspace_summary,
            target_dir=target_dir
        )
        
        assert dw.target_dir == target_dir
        assert dw._lock is not None
        assert dw._semaphore is not None
        assert dw._summarizer is not None
        assert dw._summary_manager is not None

        mock_file.assert_has_calls([
            call(config.get_dir_dict_path(), 'r'),
            call().__enter__(),
            call().read(),
            call().__exit__(None, None, None),
        ])

        mock_json_loads.assert_called_once()

        assert dw.file_paths == file_paths

def test_dir_walker_generate_directory_summary() -> None:
    workspace_summary = '📔 Test workspace summary.'
    json_dumps_return_value = '{ "test_key": "test_value" }'

    with patch('builtins.open', mock_open()) as mock_file, \
        patch('json.loads'), \
        patch('json.dumps', return_value=json_dumps_return_value), \
        patch('flamethrower.setup.dir_walker.setup_workspace_summary', return_value=workspace_summary), \
        patch('flamethrower.setup.dir_walker.Summarizer'), \
        patch('flamethrower.setup.dir_walker.DirectoryWalker.process_directory') as mock_process_directory, \
        patch('flamethrower.setup.dir_walker.DirectoryWalker.get_gitignore') as mock_get_gitignore, \
        patch('flamethrower.setup.dir_walker.SummaryManager') as mock_summary_manager, \
        patch('builtins.print') as mock_print:
        
        dw = DirectoryWalker(
            workspace_summary=workspace_summary,
            target_dir='some/test/dir'
        )

        sm = mock_summary_manager.return_value
        sm.get_summarizations_with_timeout = AsyncMock(return_value=[1, 0, 1, 1])
        asyncio.get_event_loop().run_until_complete(dw.generate_directory_summary())

        mock_file.assert_has_calls([
            call(config.get_dir_dict_path(), 'r'),
            call().__enter__(),
            call().read(),
            call().__exit__(None, None, None),

            call(config.get_dir_tree_path(), 'w'),
            call().__enter__(),
            call().__exit__(None, None, None),

            call(config.get_dir_dict_path(), 'w'),
            call().__enter__(),
            call().write(json_dumps_return_value),
            call().__exit__(None, None, None),
        ])
        mock_process_directory.assert_called_once()
        mock_get_gitignore.assert_called_once()

        sm.get_summarizations_with_timeout.assert_awaited_once()
        mock_print.assert_called_once_with('📚 Learned 3 files in the workspace.')

def test_dir_walker_process_directory() -> None:
    pass

def test_dir_walker_process_subdirectory() -> None:
    pass

def test_dir_walker_write_file_entry() -> None:
    pass

def test_dir_walker_get_directory_tree() -> None:
    pass

def test_dir_walker_get_gitignore() -> None:
    pass

def test_dir_walker_update_file_paths() -> None:
    pass

def test_dir_walker_setup_dir_summary() -> None:
    pass
