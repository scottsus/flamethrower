from unittest.mock import patch, mock_open, call
from flamethrower.utils.key_handler import (
    get_api_key, set_api_key, try_api_key
)

def test_try_api_key() -> None:
    with patch('flamethrower.utils.key_handler.OpenAI') as mock_openai:
        model = mock_openai.return_value
        model.chat.completions.create.return_value = {
            'dummy_response': 'I am a dummy response.'
        }
        assert try_api_key('sk-valid_api_key') == True
    
    with patch('flamethrower.utils.key_handler.OpenAI') as mock_openai:
        model = mock_openai.return_value
        model.chat.completions.create.side_effect = Exception('Invalid API Key')
        assert try_api_key('sk-invalid_api_key') == False

def test_get_api_key() -> None:
    with patch('builtins.open', mock_open(read_data='OPENAI_API_KEY=1234\n')):
        assert get_api_key() == '1234'

def test_set_api_key() -> None:
    with patch('builtins.open', mock_open()) as mock_file:
        set_api_key('1234')
        mock_file().assert_has_calls([
            call.__enter__(),
            call.write('OPENAI_API_KEY=1234\n'),
            call.__exit__(None, None, None)
        ])
