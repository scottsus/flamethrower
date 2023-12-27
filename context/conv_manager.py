import json
from io import TextIOWrapper
from pydantic import BaseModel
import config.constants as config
from utils import (
    sequence_parser as sp,
    zsh_history as zh,
    pretty as pr
)

class ConversationManager(BaseModel):
    """
    Manages a conv.json file that stores the conversation history
    """
    conv_path: str = config.get_conversation_path()
    
    def __init__(self, **data):
        super().__init__(**data)
        with open(self.conv_path, 'w') as f:
            json.dump([], f)
    
    def get_conv(self) -> list:
        try:
            with open(self.conv_path, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def append_message(self, role: str, content: str, name: str = '') -> None:
        new_message = { 'role': role, 'content': content }
        if name:
            new_message['name'] = name
        
        with open(self.conv_path, 'r+') as f:
            try:
                conv = json.load(f)
                conv.append(new_message)
                self.save(conv, f)
                self.pretty_print()
            except Exception:
                pass

    def update_conv_from_stdout(self, data: bytes) -> None:
        """
        This function is special because we're employing a unique way to capture stdout responses.
          1. Store stdout chunks in a buffer.log file until the next prompt newline regex
          2. When that is found, read the buffer.log file
          3. Right before appending the stdout log, we inject the last known user command
        """

        buffer_file = config.flamethrower_log_dir('buffer.log')
        
        def write_buffer(data: bytes) -> None:
            with open(buffer_file, 'ab') as f:
                f.write(sp.get_cleaned_data(data))
        
        def read_buffer():
            with open(buffer_file, 'rb') as f:
                return f.read()
        
        if sp.is_prompt_newline(data):
            user_cmd = zh.get_last_user_cmd()
            if user_cmd == '' or user_cmd.lower() == 'exit':
                return
            
            stdout_log = read_buffer()
            if stdout_log == b'':
                return
            
            self.append_message(
                role='user',
                content=user_cmd,
                name='human'
            )
            self.append_message(
                role='user',
                content=stdout_log.decode('utf-8'),
                name='stdout'
            )

            # Clear the buffer
            with open(buffer_file, 'w') as f:
                f.write('')

        else:
            write_buffer(data)

    def save(self, conv: list, f: TextIOWrapper) -> None:
        f.seek(0)
        json.dump(conv, f, indent=4)
        f.truncate()
    
    def pretty_print(self) -> None:
        conv = self.get_conv()
        with open(config.get_pretty_conversation_path(), 'w') as f:
            pretty = pr.pretty_print(conv)
            f.write(pretty)
