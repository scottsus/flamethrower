from unittest import mock
from flamethrower.utils.token_counter import TokenCounter
from flamethrower.models.models import (
    OPENAI_GPT_4_TURBO,
    OPENAI_GPT_3_TURBO,
)

def test_token_counter_init() -> None:
    token_counter = TokenCounter()

    assert token_counter.input_tokens is not None
    assert token_counter.output_tokens is not None
    assert token_counter.pricing is not None

    for model in token_counter.input_tokens:
        assert token_counter.input_tokens[model] == 0
    
    for model in token_counter.output_tokens:
        assert token_counter.output_tokens[model] == 0

def test_token_counter_add_input_tokens() -> None:
    token_counter = TokenCounter()

    token_counter.add_input_tokens(42_069, OPENAI_GPT_4_TURBO)
    assert token_counter.input_tokens[OPENAI_GPT_4_TURBO] == 42_069

def test_token_counter_add_output_tokens() -> None:
    token_counter = TokenCounter()

    token_counter.add_output_tokens(42_069, OPENAI_GPT_4_TURBO)
    assert token_counter.output_tokens[OPENAI_GPT_4_TURBO] == 42_069

def test_token_counter_add_streaming_input_tokens() -> None:
    token_counter = TokenCounter()

    with mock.patch('flamethrower.utils.token_counter.TokenCounter.calc_token_usage', return_value=42_069):
        token_counter.add_streaming_input_tokens('Hello World', OPENAI_GPT_4_TURBO)
        assert token_counter.input_tokens[OPENAI_GPT_4_TURBO] == 42_069

def test_token_counter_add_streaming_output_tokens() -> None:
    token_counter = TokenCounter()

    with mock.patch('flamethrower.utils.token_counter.TokenCounter.calc_token_usage', return_value=42_069):
        token_counter.add_streaming_output_tokens('Hello World', OPENAI_GPT_4_TURBO)
        assert token_counter.output_tokens[OPENAI_GPT_4_TURBO] == 42_069

# TODO: per model
def test_token_counter_return_cost_analysis() -> None:
    token_counter = TokenCounter()

    token_counter.add_input_tokens(10, OPENAI_GPT_4_TURBO)
    token_counter.add_output_tokens(10, OPENAI_GPT_4_TURBO)

    assert token_counter.return_cost_analysis(OPENAI_GPT_4_TURBO) == (
        'Total tokens used:\n'
        '  Input tokens: 10 => $0.00\n'
        '  Output tokens: 10 => $0.00\n'
        '  💸 Total cost: $0.00'
    )
