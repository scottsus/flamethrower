import os
import subprocess
import enum
from pydantic import BaseModel
import questionary
import flamethrower.config.constants as config
from flamethrower.agents.driver import Driver
from flamethrower.agents.interpreter import Interpreter
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.agents.file_writer import FileWriter
from flamethrower.shell.printer import Printer
from flamethrower.utils.timer import Timer

class Choice(enum.Enum):
    YES = 1
    NO = 2
    REVISE = 3

class Operator(BaseModel):
    max_retries: int = 8
    driver: Driver = None
    interpreter: Interpreter = None
    file_writer: FileWriter = None
    conv_manager: ConversationManager
    printer: Printer
    
    def __init__(self, **data):
        super().__init__(**data)
        self.driver = Driver()
        self.interpreter = Interpreter()
        self.file_writer = FileWriter()

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
    
    def get_user_choice(self) -> Choice:
        user_choice = questionary.select(
            "Do you want me to implement the solution and test it for you?",
            choices=[
                "Yes",
                "Let me revise the response",
                "I'll do it myself, thank you very much"
            ]
        ).ask()

        if user_choice == "Let me revise the response":
            return Choice.REVISE

        if user_choice == "I'll do it myself, thank you very much":
            return Choice.NO
        
        return Choice.YES
    
    def new_implementation_run(self, query: str, conv: list) -> None:
        """
        To complete a debugging run, we need:
          1. An objective
          2. A starting point
          3. A series of steps to complete the objective
        """

        # Initial understanding of the problem and generation of solution
        stream = self.driver.get_new_solution(conv)
        self.printer.print_llm_response(stream)
        
        with Timer(printer=self.printer).get_execution_time():
            action = ''
            for _ in range(self.max_retries):
                last_driver_res = self.get_last_assistant_response()
                decision = self.interpreter.make_decision_from(query, last_driver_res)
                
                actions: list = decision['actions']
                for obj in actions:
                    action = obj['action']

                    if action in ['run', 'write', 'debug', 'stuck']:
                        self.printer.print_regular(with_newline=True)
                        choice = self.get_user_choice()
                        if choice == Choice.REVISE:
                            return
                        if choice == Choice.NO:
                            self.printer.print_green(b'\nVery well then. Let me know if you need further assistance.\n')
                            return
                    
                    if action == 'run':
                        command = obj['command']
                        self.printer.print_code(command)
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
                        self.printer.print_red("\nI don't know how to solve this, need your help\n", reset=True)
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
                        # diffs = Diff(printer=self.printer).get_diffs()
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
                stream = self.driver.get_next_step(conv)
                self.printer.print_llm_response(stream)
            
            # Max retries exceeded
            self.printer.print_red("\nToo many iterations, I'm going to need your help to debug this.", reset=True)
    
    def get_last_assistant_response(self) -> str:
        with open(config.get_last_response_path(), 'r') as f:
            return f.read()
