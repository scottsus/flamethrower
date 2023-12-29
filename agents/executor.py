import subprocess
from pydantic import BaseModel
from models.llm import LLM
from context.conv_manager import ConversationManager
from shell.printer import Printer
from .file_writer import FileWriter
import config.constants as config

json_schema = {
    'type': 'object',
    'properties': {
        'action': {
            'type': 'string',
            'enum': ['run', 'write', 'completed']
        },
        'command': { 'type': 'string' },
        'file_paths': { 'type': 'string' },
    },
    'required': ['action'],
    'allOf': [
        {
        'if': { 'properties': { 'action': { 'const': 'run' } } },
        'then': { 'required': ['command'] },
        },
        {
        'if': { 'properties': { 'action': { 'const': 'write' } } },
        'then': { 'required': ['file_paths'] },
        },
    ]
}

system_message = f"""
You are an extremely powerful programming assistant that lives inside the unix terminal.
You have a single, crucial task: to categorize LLM responses into 3 possible actions:
  1. Run a command on the terminal and observe its output
  2. Rewrite code in a given target file
  3. Indicate that your job has been completed. If so, don't recommend other suggestions or optimizations.
It is crucial that you return a JSON object with the following JSON Schema:
    {json_schema}
"""

class Executor(BaseModel):
    max_retries: int = 4
    llm: LLM = None
    json_schema: dict = json_schema
    conv_manager: ConversationManager = None
    file_writer: FileWriter = None
    printer: Printer = None

    def __init__(self, **data):
        super().__init__(**data)
        self.llm = LLM(system_message=system_message)
        self.file_writer = FileWriter()

    def execute_action(self, command):
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
    
    def new_debugging_run(self, query: str, conv: list) -> None:
        """
        To complete a debugging run, we need:
          1. An objective
          2. A starting point
          3. A series of steps to complete the objective
        """

        # Initial understanding of the problem and generation of solution
        stream = self.llm.new_streaming_chat_request(messages=conv)
        self.printer.print_llm_response(stream)
        
        action = ''
        for _ in range(self.max_retries):
            last_driver_res = self.get_last_assistant_response()
            decision = self.make_decision_from(query, last_driver_res)

            action = decision['action']
            if action == 'run':
                command = decision['command']
                output = self.execute_action(command)
                self.conv_manager.append_conv(
                    role='user',
                    content=command,
                    name='human',
                )
                self.conv_manager.append_conv(
                    role='user',
                    content=output,
                    name='stdout',
                )
            elif action == 'write':
                file_paths = decision['file_paths']
                self.file_writer.write_code(file_paths, last_driver_res)
                self.conv_manager.append_conv(
                    role='user',
                    content=f'Done with updating file: `{file_paths}`.',
                    name='human',
                )
            elif action == 'completed':
                return
            else:
                raise Exception('Invalid action')

            # Subsequent implementations of the solution
            conv = self.conv_manager.get_conv()
            stream = self.llm.new_streaming_chat_request(messages=conv)
            self.printer.print_llm_response(stream)
        
        # Max retries exceeded
        self.printer.print_red("Something is wrong, I'm going to need your help to debug this.")
        self.printer.print_default()

    def get_last_assistant_response(self) -> str:
        with open(config.get_last_response_path(), 'r') as f:
            return f.read()

    def make_decision_from(self, objective: str, latest_response: str) -> None:
        query = (
            f'This is the objective:\n{objective}'
            f'This is the latest response:\n{latest_response}'
            'Given this objective and response, choose a possible action.'
        )
        res = self.llm.new_json_request(
            query=query,
            json_schema=self.json_schema,
            loading_message='🤖 Determining next step...'
        )

        return res
    