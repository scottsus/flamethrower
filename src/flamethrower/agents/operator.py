import os
import subprocess
import enum
import questionary
from pydantic import BaseModel
from openai import RateLimitError
import flamethrower.config.constants as config
from flamethrower.agents.driver import Driver
from flamethrower.agents.interpreter import Interpreter
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.context.prompt import PromptGenerator
from flamethrower.agents.file_writer import FileWriter
from flamethrower.shell.printer import Printer
from flamethrower.exceptions.exceptions import *
from flamethrower.exceptions.handlers import *

class Choice(enum.Enum):
    YES = 1
    NO = 2

class Operator(BaseModel):
    max_retries: int = 8
    base_dir: str
    driver: Driver = None
    interpreter: Interpreter = None
    file_writer: FileWriter = None
    conv_manager: ConversationManager
    prompt_generator: PromptGenerator
    printer: Printer
    
    def __init__(self, **data):
        super().__init__(**data)
        self.driver = Driver(base_dir=self.base_dir)
        self.interpreter = Interpreter()
        self.file_writer = FileWriter(base_dir=self.base_dir)
    
    def new_implementation_run(self, query: str, conv: list) -> None:
        """
        To complete a debugging run, we need:
          1. An objective
          2. A starting point
          3. A series of steps to complete the objective
        """

        try:
            # Initial understanding of the problem and generation of solution
            stream = self.driver.get_new_solution(conv)
            self.printer.print_llm_response(stream)
            
            action = ''
            is_first_time_asking_for_permission = True
            
            for _ in range(self.max_retries):
                last_driver_res = self.get_last_assistant_response()
                decision = self.interpreter.make_decision_from(query, last_driver_res)
                if decision is None:
                    self.printer.print_err('Interpreter unable to make decision. Marking as complete.')
                    return
                
                actions: list = decision['actions']
                for i in range (len(actions)):
                    obj = actions[i]
                    action = obj['action']
                    self.printer.print_actions(actions[i:])
                    
                    if is_first_time_asking_for_permission and action in ['run', 'write', 'debug']:
                        self.printer.print_regular(with_newline=True)

                        choice = self.get_user_choice()
                        if choice == Choice.NO:
                            return
                        
                        is_first_time_asking_for_permission = False
                    
                    try:
                        if action == 'run':
                            self.handle_action_run(obj)
                        
                        elif action == 'write':
                            self.handle_action_write(obj, last_driver_res)
                        
                        elif action == 'debug':
                            self.handle_action_debug(obj, last_driver_res)
                        
                        elif action == 'need_context':
                            self.handle_action_need_context(obj)
                        
                        elif action == 'stuck':
                            self.handle_action_stuck()
                            return

                        elif action == 'cleanup':
                            self.handle_action_cleanup(obj, last_driver_res)

                        elif action == 'completed':
                            # diffs = Diff(printer=self.printer).get_diffs()
                            # TODO: diffs for just that 1 file?
                            # self.printer.print_diffs(diffs)
                            return
                        
                        else:
                            # Impossible, since obj is validated by json schema, but just in case
                            raise ValueError('Foreign JSON')
                    
                    except RateLimitError:
                        error_message = (
                            'You might have exceeded your current quota for OpenAI.\n'
                            "We're working hard to setup a 🔥 flamethrower LLM server for your usage\n"
                            'Please try again soon!\n'
                        )
                        self.printer.print_err(error_message.encode('utf-8'))
                    except Exception as e:
                        self.printer.print_err(f'Error: {str(e)}\nPlease try again.')
                        return

                # Subsequent iterations of implementation
                messages = self.prompt_generator.construct_messages(query)
                stream = self.driver.get_next_step(messages)
                self.printer.print_llm_response(stream)
            
            # Max retries exceeded
            self.printer.print_err(b'Too many iterations, need your help to debug.', reset=True)
        
        except KeyboardInterrupt:
            self.printer.print_orange('^C', reset=True)
            return
        except QuotaExceededException:
            self.printer.print_err(get_quota_exceeded_message())
        except Exception:
            raise
    
    def handle_action_run(self, json: dict) -> None:
        command = json['command']
        self.printer.print_code(command)

        def execute_action(command: str) -> str:
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

        output = execute_action(command)
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

    def handle_action_write(self, json: dict, driver_res: str) -> None:
        try:
            file_paths = json['file_paths']
            self.file_writer.write_code(file_paths, driver_res)

            success_message = f'Successfully updated {file_paths}\n'
            self.conv_manager.append_conv(
                role='user',
                content=success_message,
                name='human',
            )
            self.printer.print_green(success_message, reset=True)
        
        except Exception:
            failed_message = f'Failed to update {file_paths}'
            self.conv_manager.append_conv(
                role='user',
                content=failed_message,
                name='human'
            )
            self.printer.print_err(failed_message, reset=True)

            raise
    
    def handle_action_debug(self, json: dict, driver_res: str) -> None:
        try:
            file_paths = json['file_paths']
            self.file_writer.write_code(file_paths, driver_res)

            debug_message = f'Wrote debugging statements for future testing in file: {file_paths}\n'
            self.conv_manager.append_conv(
                role='user',
                content=debug_message,
                name='human'
            )
            self.printer.print_yellow(debug_message, reset=True)
        
        except Exception:
            failed_message = f'Failed to update {file_paths}'
            self.conv_manager.append_conv(
                role='user',
                content=failed_message,
                name='human'
            )
            self.printer.print_err(failed_message, reset=True)

            raise
    
    def handle_action_need_context(self, json: dict) -> None:
        try:
            file_paths = json['file_paths']
            complete_target_path = os.path.join(os.getcwd(), file_paths)

            try:
                with open(complete_target_path, 'r') as f:
                    file_contents = f.read()
                    new_message = (
                        f'# {file_paths}:\n'
                        f'```\n{file_contents}\n```\n'
                    )
                    self.conv_manager.append_conv(
                        role='user',
                        content=new_message,
                        name='human'
                    )
                    self.printer.print_green(f'Context obtained for {file_paths}')
            except FileNotFoundError:
                not_found_message = f'Unable to locate {file_paths}'
                self.conv_manager.append_conv(
                    role='user',
                    content=not_found_message,
                    name='human'
                )
                self.printer.print_err(not_found_message)
            
        except Exception:
            failed_message = f'Failed to draw context for {file_paths}'
            self.conv_manager.append_conv(
                role='user',
                content=failed_message,
                name='human'
            )
            self.printer.print_err(failed_message, reset=True)

            raise

    
    def handle_action_stuck(self) -> None:
        self.printer.print_err(b"I don't know how to solve this, need your help", reset=True)
    
    def handle_action_cleanup(self, json: dict, driver_res: str) -> None:
        try:
            file_paths = json['file_paths']
            self.file_writer.write_code(file_paths, driver_res)

            cleanup_message = f'✨ Cleaned up files: {file_paths}\n'
            self.conv_manager.append_conv(
                role='user',
                content=cleanup_message,
                name='human'
            )
            self.printer.print_green(cleanup_message, reset=True)
        
        except Exception:
            failed_message = f'Failed to cleanup {file_paths}'
            self.conv_manager.append_conv(
                role='user',
                content=failed_message,
                name='human'
            )
            self.printer.print_err(failed_message, reset=True)

            raise
    
    def get_user_choice(self) -> Choice:
        user_choice = questionary.select(
            "Do you want me to implement the solution and test it for you?",
            choices=[
                "Yes",
                "No",
            ]
        ).ask()

        if user_choice == "No":
            return Choice.NO
        
        return Choice.YES

    def get_last_assistant_response(self) -> str:
        with open(config.get_last_response_path(), 'r') as f:
            return f.read()
