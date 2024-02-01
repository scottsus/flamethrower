import os
import pytest
from unittest import mock
from unittest.mock import patch, mock_open
import flamethrower.config.constants as config
from flamethrower.context.prompt import PromptGenerator
from flamethrower.test_utils.mocks.mock_conv_manager import mock_conv_manager
from flamethrower.test_utils.mocks.mock_token_counter import mock_token_counter
from flamethrower.test_utils.mocks.mock_printer import mock_printer

@pytest.fixture
def mock_prompt_generator() -> PromptGenerator:
    with patch('builtins.open', mock_open(read_data='flamethrower/some/path')):
        return PromptGenerator(
            conv_manager=mock_conv_manager(),
            token_counter=mock_token_counter(),
            printer=mock_printer()
        )

def test_prompt_generator_init(mock_prompt_generator: PromptGenerator) -> None:
    pg = mock_prompt_generator
    
    assert pg.greeting.startswith('Good') and pg.greeting.endswith('👋')
    assert pg.description != ''
    assert pg.dir_structure == 'flamethrower/some/path'

def test_prompt_generator_construct_greeting(mock_prompt_generator: PromptGenerator) -> None:
    pg = mock_prompt_generator
    
    greeting = pg.construct_greeting()

    # TODO: this will change
    assert 'Good' in greeting and '👋' in greeting
    assert pg.description in greeting

def test_prompt_generator_construct_messages(mock_prompt_generator: PromptGenerator) -> None:
    pg = mock_prompt_generator

    query = '🧪 Testing...'
    target_files = ['file_1', 'file_2', 'file_3']
    target_file_contents = """
    Content_1
    Content_2
    Content_3
    """
    conversation_history = [
        {
            'role': 'user',
            'content': 'User message 1'
        },
        {
            'role': 'assistant',
            'content': 'Assistant message 1'
        },
        {
            'role': 'user',
            'content': 'User message 2'
        },
        {
            'role': 'assistant',
            'content': 'Assistant message 2'
        }
    ]
    
    with patch('flamethrower.agents.file_chooser.FileChooser.infer_target_file_paths', return_value=target_files) as mock_infer_target_files, \
        patch('builtins.open', mock_open(read_data=target_file_contents)) as mock_file, \
        patch('json.loads', return_value=conversation_history) as mock_loads:
        
        messages = pg.construct_messages(query)

        assert isinstance(messages, list)
        assert len(messages) == 5
        
        about_message = messages[0]
        assert about_message['role'] == 'user'
        assert about_message['content'].startswith('This project is about')

        dir_structure_message = messages[1]
        assert dir_structure_message['role'] == 'user'
        assert dir_structure_message['content'].startswith('Here is the directory structure')

        mock_infer_target_files.assert_called_once_with(pg.description, pg.dir_structure, query)
        pg.printer.print_regular.assert_called_once_with(f'🔭 Focusing on the following files: {target_files}\n')

        mock_file.assert_has_calls([
            mock.call(os.path.join(os.getcwd(), target_files[0]), 'r'),
            mock.call().__enter__(),
            mock.call().read(),
            mock.call().__exit__(None, None, None),
            
            mock.call(os.path.join(os.getcwd(), target_files[1]), 'r'),
            mock.call().__enter__(),
            mock.call().read(),
            mock.call().__exit__(None, None, None),
            
            mock.call(os.path.join(os.getcwd(), target_files[2]), 'r'),
            mock.call().__enter__(),
            mock.call().read(),
            mock.call().__exit__(None, None, None),

            mock.call(config.get_conversation_path(), 'r'),
            mock.call().__enter__(),
            mock.call().read(),
            mock.call().__exit__(None, None, None),

            mock.call(config.get_last_prompt_path(), 'w'),
            mock.call().__enter__(),
            mock.call().write(mock.ANY),
            mock.call().__exit__(None, None, None),
        ])

        target_files_message = messages[2]
        assert target_files_message['role'] == 'user'
        assert target_files_message['content'].startswith(f'Currently you are working with these files:')

        mock_loads.assert_called_once()
        
        conv_message = messages[3]
        assert conv_message['role'] == 'user'
        assert conv_message['content'].startswith('Here are the most recent conversations between the human, stdout logs, and assistant')

        task_message = messages[4]
        assert task_message['role'] == 'user'
        assert task_message['content'].startswith('Given the context, here is your **crucial task')
