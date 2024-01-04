import os
import subprocess
from pydantic import BaseModel
import flamethrower.config.constants as config
from flamethrower.models.llm import LLM
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.agents.file_writer import FileWriter
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.utils.diff import Diff
from flamethrower.shell.printer import Printer

json_schema = {
    'type': 'object',
    'properties': {
        'actions': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'action': {
                        'type': 'string',
                        'enum': ['run', 'write', 'debug', 'stuck', 'cleanup', 'completed']
                    },
                    'command': { 'type': 'string' },
                    'file_paths': { 'type': 'string' }
                },
                'required': ['action'],
                'allOf': [
                    {
                        'if': { 'properties': { 'action': { 'const': 'run' } } },
                        'then': { 'required': ['command'] }
                    },
                    {
                        'if': { 'properties': { 'action': { 'const': 'write' } } },
                        'then': { 'required': ['file_paths'] }
                    },
                    {
                        'if': { 'properties': { 'action': { 'const': 'debug' } } },
                        'then': { 'required': ['file_paths'] }
                    },
                    {
                        'if': { 'properties': { 'action': { 'const': 'cleanup' } } },
                        'then': { 'required': ['file_paths'] }
                    }
                ]
            }
        },
    },
    'required': ['actions']
}

system_message = f"""
You are an extremely powerful programming assistant that lives inside the unix terminal.
You have a single, crucial task: to categorize LLM responses into a list of 5 possible actions:
  1. Run a command on the terminal and observe its output
  2. Rewrite code in a given target file
  3. If you encountered an error, write print statements to the target file to debug for the next iteration.
  4. Indicate that you are stuck and need help.
  5. As best as possible, be extremely concise in code, and clean the file of print statements
  6. Indicate that your job has been completed. **If so, don't recommend other tests or suggestions.**
You **should choose multiple actions to perform**. For example:
  - If you are writing to a file, you **must also return a `run` action to test what you wrote.**
  - If you are debugging, you **must also follow it up with a `run` action and further `write` actions to identify the issue.**
    - Once you tested the new code and realized you got a positive output, indicate your job is completed.
It is crucial that you return a JSON object with the following JSON Schema:
    {json_schema}
"""

class Executor(BaseModel):
    max_retries: int = 8
    nl_llm: LLM = None
    json_llm: LLM = None
    json_schema: dict = json_schema
    conv_manager: ConversationManager = None
    file_writer: FileWriter = None
    token_counter: TokenCounter = None
    printer: Printer = None

    def __init__(self, **data):
        super().__init__(**data)
        self.nl_llm = LLM(
            token_counter=self.token_counter
        )
        self.json_llm = LLM(
            system_message=system_message,
            token_counter=self.token_counter
        )
        self.file_writer = FileWriter(
            token_counter=self.token_counter
        )

    def execute_action(self, command: str) -> str:
        output = ''
        try:
            completed_process = subprocess.run(
                command, 
                shell=True,
                check=True,
                text=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT
            )
            output = completed_process.stdout
        except subprocess.CalledProcessError as e:
            output = f'Error: {e.output}'

        return output
    
    def new_implementation_run(self, query: str, conv: list) -> None:
        """
        To complete a debugging run, we need:
          1. An objective
          2. A starting point
          3. A series of steps to complete the objective
        """

        # Initial understanding of the problem and generation of solution
        stream = self.nl_llm.new_streaming_chat_request(messages=conv)
        self.printer.print_llm_response(stream)
        
        action = ''
        for _ in range(self.max_retries):
            last_driver_res = self.get_last_assistant_response()
            decision = self.make_decision_from(query, last_driver_res)
            
            actions: list = decision['actions']
            for obj in actions:
                action = obj['action']
                
                if action == 'run':
                    command = obj['command']
                    self.printer.print_regular(command)
                    output = self.execute_action(command)
                    self.printer.print_regular(output)
                    self.conv_manager.append_conv(
                        role='user',
                        content=f'{os.getcwd()} $ {command}',
                        name='human',
                    )
                    self.conv_manager.append_conv(
                        role='user',
                        content=output,
                        name='stdout',
                    )
                
                elif action == 'write':
                    file_paths = obj['file_paths']
                    self.file_writer.write_code(file_paths, last_driver_res)
                    
                    success_message = f'Successfully updated {file_paths}\n'
                    self.conv_manager.append_conv(
                        role='user',
                        content=success_message,
                        name='human',
                    )
                    self.printer.print_green(success_message, reset=True)
                
                elif action == 'debug':
                    file_paths = obj['file_paths']
                    self.file_writer.write_code(file_paths, last_driver_res)

                    success_message = f'Wrote debugging statements for future testing in file: {file_paths}\n'
                    self.conv_manager.append_conv(
                        role='user',
                        content=success_message,
                        name='human'
                    )
                    self.printer.print_yellow(success_message, reset=True)
                
                elif action == 'stuck':
                    self.printer.print_red("\nI don't know how to solve this, need your help", reset=True)
                    return

                elif action == 'cleanup':
                    file_paths = obj['file_paths']
                    self.file_writer.write_code(file_paths, last_driver_res)

                    success_message = f'Cleaned up file: {file_paths}\n'
                    self.conv_manager.append_conv(
                        role='user',
                        content=success_message,
                        name='human'
                    )
                    self.printer.print_green(success_message, reset=True)

                elif action == 'completed':
                    diffs = Diff(printer=self.printer).get_diffs()
                    # TODO: diffs for just that 1 file?
                    # self.printer.print_diffs(diffs)
                    return
                
                else:
                    raise Exception('Invalid action')

            # Subsequent implementations of the solution
            conv = self.conv_manager.get_conv()
            conv.append({
                'role': 'user',
                'content': f'Remember to work towards the initial objective: [{query}]!',
                'name': 'human'
            })
            stream = self.nl_llm.new_streaming_chat_request(messages=conv)
            self.printer.print_llm_response(stream)
        
        # Max retries exceeded
        self.printer.print_red("\nToo many iterations, I'm going to need your help to debug this.", reset=True)

    def make_decision_from(self, objective: str, latest_response: str) -> dict:
        target_files = ''
        try:
            with open(config.get_current_files_path(), 'r') as f:
                target_files = f.read().split('\n')
        except FileNotFoundError:
            pass
        if target_files:
            target_files = f'Currently you are working with the following files: {target_files}'
        
        query = (
            f'This is the objective:\n{objective}'
            f'This is the latest response:\n{latest_response}'
            f'{target_files}'
            'Given this objective and response, choose a possible action.'
        )
        self.printer.print_default('\n')
        decision = self.json_llm.new_json_request(
            query=query,
            json_schema=self.json_schema,
            loading_message='🤖 Determining next step...'
        )

        return decision
    
    def get_last_assistant_response(self) -> str:
        with open(config.get_last_response_path(), 'r') as f:
            return f.read()
    