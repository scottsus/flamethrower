from unittest.mock import patch, mock_open
from flamethrower.context.conv_manager import ConversationManager

def test_conv_manager_init() -> None:
    with patch('builtins.open', mock_open(read_data='[]')) as mocked_file:
        conv_manager = ConversationManager()
        mocked_file.assert_called_once_with(conv_manager.conv_path, 'w')
        mocked_file().write.assert_called_once_with('[]')

def test_conv_manager_get_conv_empty() -> None:
    with patch('builtins.open', mock_open(read_data='[]')):
        conv_manager = ConversationManager()
        assert conv_manager.get_conv() == []

def test_conv_manager_save() -> None:
    with patch('builtins.open', mock_open(read_data='[]')) as mocked_file:
        conv_manager = ConversationManager()
        save_data = [{'role': 'user', 'content': 'Save 💾', 'name': 'Tester'}]

        with patch('json.dump') as mock_json_dump:
            conv_manager.save(save_data, mocked_file())
            mock_json_dump.assert_called_once_with(save_data, mocked_file(), indent=4)
            handle = mocked_file()
            handle.seek.assert_called_once_with(0)
            handle.truncate.assert_called_once_with()

def test_conv_manager_pretty_print() -> None:
    pretty_path = 'path/to/pretty_conversation_file'
    prettified = '✨ pretty conversation ✨'

    with patch('builtins.open', mock_open(read_data='[]')) as mocked_file:
        conv_manager = ConversationManager()
         
        with patch('flamethrower.utils.pretty.pretty_print', return_value=prettified), \
            patch('flamethrower.config.constants.get_pretty_conversation_path', return_value=pretty_path):
        
            conv_manager.pretty_print()
            mocked_file.assert_called_with(pretty_path, 'w')
            mocked_file().write.assert_called_with(prettified)

def test_conv_manager_append_conv() -> None:
    with patch('builtins.open', mock_open(read_data='[]')) as mocked_file:
        conv_manager = ConversationManager()

        with patch('json.dump') as mock_json_dump, \
            patch('flamethrower.utils.pretty.pretty_print'), \
            patch('flamethrower.config.constants.get_pretty_conversation_path'):
                
            conv_manager.append_conv(role='user', content='Hello Test 🧪', name='Tester')
            mock_json_dump.assert_called_once_with(
                [{'role': 'user', 'content': 'Hello Test 🧪', 'name': 'Tester'}], mocked_file(), indent=4
            )

