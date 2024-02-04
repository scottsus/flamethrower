import tiktoken
from pydantic import BaseModel
from flamethrower.models.models import (
    OPENAI_GPT_4_TURBO,
    OPENAI_GPT_3_TURBO,
)
from typing import Any, Dict

class TokenCounter(BaseModel):
    input_tokens: Dict[str, int] = {
        OPENAI_GPT_4_TURBO: 0,
        OPENAI_GPT_3_TURBO: 0,
    }
    output_tokens: Dict[str, int] = {
        OPENAI_GPT_4_TURBO: 0,
        OPENAI_GPT_3_TURBO: 0,
    }
    pricing: Dict[str, Any] = {
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
    
    def add_input_tokens(self, tokens: int, model: str) -> None:
        self.input_tokens[model] += tokens
    
    def add_output_tokens(self, tokens: int, model: str) -> None:
        self.output_tokens[model] += tokens
    
    def add_streaming_input_tokens(self, complete_input_text: str, model: str = OPENAI_GPT_4_TURBO) -> None:
        num_input_tokens = self.calc_token_usage(complete_input_text, model)

        self.add_input_tokens(num_input_tokens, model)
    
    def add_streaming_output_tokens(self, complete_output_text: str, model: str = OPENAI_GPT_4_TURBO) -> None:
        num_output_tokens = self.calc_token_usage(complete_output_text, model)

        self.add_output_tokens(num_output_tokens, model)
        
    def return_cost_analysis(self, model: str = OPENAI_GPT_4_TURBO) -> str:
        input_cost = 0
        for model in self.input_tokens:
            input_cost += (
                self.input_tokens[model] 
                * self.pricing[model]['input']['cost']
                / self.pricing[model]['input']['per']
            )
        output_cost = 0
        for model in self.output_tokens:
            output_cost += (
                self.output_tokens[model]
                * self.pricing[model]['output']['cost']
                / self.pricing[model]['output']['per']
            )
        total_cost = input_cost + output_cost

        total_input_tokens = sum(self.input_tokens.values())
        total_output_tokens = sum(self.output_tokens.values())

        return (
            'Total tokens used:\n'
            f'  Input tokens: {total_input_tokens} => ${input_cost:.2f}\n'
            f'  Output tokens: {total_output_tokens} => ${output_cost:.2f}\n'
            f'  💸 Total cost: ${total_cost:.2f}'
        )

    def calc_token_usage(self, input_message: str, model: str = OPENAI_GPT_4_TURBO) -> int:
        enc = tiktoken.encoding_for_model(model)
        num_input_tokens = len(enc.encode(input_message))

        return num_input_tokens

token_counter = TokenCounter()