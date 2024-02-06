import os
import enum
import time
import json
import subprocess
import questionary
from pydantic import BaseModel
from openai import RateLimitError

import flamethrower.config.constants as config
from flamethrower.agents.drivers.driver_interface import Driver
from flamethrower.agents.drivers.done_driver import DoneDriver
from flamethrower.agents.drivers.feature_driver import FeatureDriver
from flamethrower.agents.drivers.debugging_driver import DebuggingDriver
from flamethrower.agents.router import Router

from flamethrower.agents.interpreter import Interpreter
from flamethrower.context.conv_manager import ConversationManager
from flamethrower.context.prompt import PromptGenerator
from flamethrower.agents.util_agents.file_writer import FileWriter
from flamethrower.utils.loader import Loader
from flamethrower.shell.printer import Printer
from flamethrower.exceptions.exceptions import *
from flamethrower.exceptions.handlers import *

from typing import Any, Dict, List, Optional

class Choice(enum.Enum):
    YES = 1
    NO = 2

class Operator(BaseModel):
    max_retries: int = 8
    base_dir: str
    conv_manager: ConversationManager
    prompt_generator: PromptGenerator
    printer: Printer
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._done_driver: DoneDriver = DoneDriver()
        self._feature_driver: FeatureDriver = FeatureDriver(
            target_dir=self.base_dir,
            prompt_generator=self.prompt_generator
        )
        self._debugging_driver: DebuggingDriver = DebuggingDriver(
            target_dir=self.base_dir,
            prompt_generator=self.prompt_generator
        )
        self._router: Router = Router()
        self._interpreter: Interpreter = Interpreter()
        self._file_writer: FileWriter = FileWriter(base_dir=self.base_dir)
    
    @property
    def done_driver(self) -> DoneDriver:
        return self._done_driver
    
    @property
    def feature_driver(self) -> FeatureDriver:
        return self._feature_driver
    
    @property
    def debugging_driver(self) -> DebuggingDriver:
        return self._debugging_driver
    
    @property
    def router(self) -> Router:
        return self._router
    
    @property
    def interpreter(self) -> Interpreter:
        return self._interpreter
    
    @property
    def file_writer(self) -> FileWriter:
        return self._file_writer
    
    
    def new_implementation_run(self) -> None:
        try:
            is_first_time_asking_for_permission = True

            for _ in range(self.max_retries):
                conv = self.get_latest_conv()
                query = conv[-1]['content']

                """
                Driver can be a:
                  - feature builder
                  - debugger
                  - done
                """
                with Loader(loading_message='🧠 Thinking...').managed_loader():
                    driver = self.get_driver(conv)
                    if not driver:
                        raise Exception('Operator.new_implementation_run: driver is None')
                
                if driver.__class__.__name__ == 'FeatureDriver':
                    mode = 'REGULAR'
                elif driver.__class__.__name__ == 'DebuggingDriver':
                    mode = 'DEBUG'
                elif driver.__class__.__name__ == 'DoneDriver':
                    mode = 'DONE'
                else:
                    mode = 'UNKNOWN'
                self.printer.print_cyan(f'Mode: {mode}', reset=True)
                
                stream = driver.respond_to(conv)
                if not stream:
                    raise Exception('Driver.respond_to: stream is empty')
                self.printer.print_llm_response(stream)
                
                action = ''
                with Loader(loading_message='🤖 Determining next step...').managed_loader():
                    last_driver_res = self.get_last_assistant_response()
                    actions = self.interpreter.make_decision_from(query, last_driver_res)
                
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
                        
                        elif action == 'need_context':
                            self.handle_action_need_context(obj)

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
                        self.printer.print_err(error_message)
                    except Exception as e:
                        self.printer.print_err(f'Error: {str(e)}\nPlease try again.')
                        return
            
            # Max retries exceeded
            self.printer.print_err('Too many iterations, need your help to debug.')
        
        except KeyboardInterrupt:
            self.printer.print_orange('^C', reset=True)
            return
        except QuotaExceededException:
            self.printer.print_err(get_quota_exceeded_message())
        except Exception:
            raise
    
    def handle_action_run(self, json: Dict[str, str]) -> None:
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

        time.sleep(1) # Give user time to read
        output = execute_action(command)
        self.printer.print_regular(output)

        self.conv_manager.append_conv(
            role='user',
            content=f'# {os.getcwd()}\n$ {command}',
            name='human',
        )
        self.conv_manager.append_conv(
            role='user',
            content=output,
            name='stdout',
        )

    def handle_action_write(self, json: Dict[str, str], driver_res: str) -> None:
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
            time.sleep(1) # Give user time to read
        
        except Exception:
            failed_message = f'Failed to update {file_paths}'
            self.conv_manager.append_conv(
                role='user',
                content=failed_message,
                name='human'
            )
            self.printer.print_err(failed_message)

            raise
    
    def handle_action_need_context(self, json: Dict[str, str]) -> None:
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
            self.printer.print_err(failed_message)

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

    def get_driver(self, messages: List[Dict[str, str]]) -> Optional[Driver]:
        driver_type = self.router.get_driver(messages)
        
        if driver_type == 'done':
            return self.done_driver
        if driver_type == 'debugging':
            return self.debugging_driver
        
        # Default to feature driver
        return self.feature_driver
    
    def get_latest_conv(self) -> List[Dict[str, str]]:
        try:
            with open(config.get_conversation_path(), 'r') as f:
                json_list = json.loads(f.read())
                if not isinstance(json_list, list):
                    return []
                
                return json_list
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def get_last_assistant_response(self) -> str:
        with open(config.get_last_response_path(), 'r') as f:
            return f.read()
