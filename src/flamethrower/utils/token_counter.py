import tiktoken
from pydantic import BaseModel
from flamethrower.models.models import (
    OPENAI_GPT_4_TURBO,
    OPENAI_GPT_3_TURBO,
)

class TokenCounter(BaseModel):
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    pricing: dict = {
        OPENAI_GPT_4_TURBO: {
            'max_input_tokens': 120_000,
            'input': {
                'cost': 0.01,
                'unit': 'tokens',
                'per': 1000
            },
            'output': {
                'cost': 0.03,
                'unit': 'tokens',
                'per': 1000
            }
        },
        OPENAI_GPT_3_TURBO: {
            'max_input_tokens': 15_000,
            'input': {
                'cost': 0.0010,
                'unit': 'tokens',
                'per': 1000
            },
            'output': {
                'cost': 0.0020,
                'unit': 'tokens',
                'per': 1000
            }
        }
    }
    
    # TODO: consider tokens of which model type
    def add_input_tokens(self, tokens: int) -> None:
        self.total_input_tokens += tokens
    
    # TODO: consider tokens of which model type
    def add_output_tokens(self, tokens: int) -> None:
        self.total_output_tokens += tokens
    
    def add_streaming_input_tokens(self, complete_input_text: str) -> None:
        # TODO: no hardcoded models
        num_input_tokens = self.calc_token_usage(complete_input_text)

        self.add_input_tokens(num_input_tokens)
    
    def add_streaming_output_tokens(self, complete_output_text: str) -> None:
        # TODO: no hardcoded models
        num_output_tokens = self.calc_token_usage(complete_output_text)

        self.add_output_tokens(num_output_tokens)
        
    def return_cost_analysis(self, model: str = OPENAI_GPT_4_TURBO) -> str:
        input_cost = (
            self.total_input_tokens 
            * self.pricing[model]['input']['cost']
            / self.pricing[model]['input']['per']
        )
        output_cost = (
            self.total_output_tokens
            * self.pricing[model]['output']['cost']
            / self.pricing[model]['output']['per']
        )
        total_cost = input_cost + output_cost

        return (
            'Total tokens used:\n'
            f'  Input tokens: {self.total_input_tokens} => ${input_cost:.2f}\n'
            f'  Output tokens: {self.total_output_tokens} => ${output_cost:.2f}\n'
            f'  💸 Total cost: ${total_cost:.2f}'
        )

    def calc_token_usage(self, input_message: str, model: str = OPENAI_GPT_4_TURBO) -> int:
        enc = tiktoken.encoding_for_model(model)
        num_input_tokens = len(enc.encode(input_message))

        return num_input_tokens

token_counter = TokenCounter()