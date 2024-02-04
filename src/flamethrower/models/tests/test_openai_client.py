import asyncio
from unittest.mock import AsyncMock, patch
from flamethrower.models.openai_client import OpenAIClient
from openai.types.completion_usage import CompletionUsage
from openai.types.chat.chat_completion import ChatCompletion, Choice as BasicChoice
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk, Choice as ChunkChoice

def test_openai_client_init() -> None:
    test_message = 'test_message'
    test_model = 'test_model'
    test_api_key = 'test_api_key'

    with patch('flamethrower.utils.key_handler.get_api_key', return_value=test_api_key):
        client = OpenAIClient(system_message=test_message, model=test_model)
        
        assert client.system_message == test_message
        assert client.model == test_model
        assert client.client.api_key == test_api_key

def test_openai_client_new_basic_chat_request() -> None:
    test_message, test_model = 'test_message', 'test_model'
    test_prompt_tokens, test_completion_tokens = 42, 69
    test_messages = [
        { 'role': 'system', 'content': 'You are OpenAI.' },
        { 'role': 'user', 'content': 'Say "This is a 🔥 flamethrower test."' }
    ]
    test_content = 'This is a 🔥 flamethrower test.'
    test_response = ChatCompletion(
            id='chatcmpl-123',
            object='chat.completion',
            created=1677652288,
            model='gpt-3.5-turbo-0613',
            system_fingerprint='fp_fingerprint',
            choices=[
                BasicChoice(
                    index=0,
                    message={
                        'role': 'assistant',
                        'content': test_content
                    },
                    logprobs=None,
                    finish_reason='stop'
                )
            ],
            usage=CompletionUsage(
                prompt_tokens=42,
                completion_tokens=69,
                total_tokens=111
            )
        )

    with patch('flamethrower.models.openai_client.OpenAI') as mock_openai, \
        patch('flamethrower.models.openai_client.OpenAIClient.get_token_usage',
            return_value=(test_prompt_tokens, test_completion_tokens)
        ):

        client = OpenAIClient(system_message=test_message, model=test_model)

        model = mock_openai.return_value
        model.chat.completions.create.return_value = test_response

        response = client.new_basic_chat_request(test_messages)

        assert response == (test_content, test_prompt_tokens, test_completion_tokens, test_model)
    
def test_openai_client_new_streaming_chat_request() -> None:
    test_message, test_model = 'test_message', 'test_model'
    test_messages = [
        { 'role': 'system', 'content': 'You are OpenAI.' },
        { 'role': 'user', 'content': 'Say "This is a 🔥 flamethrower test."' }
    ]
    test_contents = ['This', 'is', 'a', '🔥', 'flamethrower', 'test.']
    test_responses = [
        ChatCompletionChunk(
            id='chatcmpl-123',
            object='chat.completion.chunk',
            created=1677652288,
            model='gpt-3.5-turbo-0613',
            system_fingerprint='fp_fingerprint',
            choices=[
                ChunkChoice(
                    index=0,
                    delta={
                        'role': 'assistant',
                        'content': test_contents[0]
                    },
                    logprobs=None,
                    finish_reason=None
                )
            ],
        ),
        ChatCompletionChunk(
            id='chatcmpl-123',
            object='chat.completion.chunk',
            created=1677652288,
            model='gpt-3.5-turbo-0613',
            system_fingerprint='fp_fingerprint',
            choices=[
                ChunkChoice(
                    index=0,
                    delta={
                        'role': 'assistant',
                        'content': test_contents[1]
                    },
                    logprobs=None,
                    finish_reason=None
                )
            ],
        ),
        ChatCompletionChunk(
            id='chatcmpl-123',
            object='chat.completion.chunk',
            created=1677652288,
            model='gpt-3.5-turbo-0613',
            system_fingerprint='fp_fingerprint',
            choices=[
                ChunkChoice(
                    index=0,
                    delta={
                        'role': 'assistant',
                        'content': test_contents[2]
                    },
                    logprobs=None,
                    finish_reason=None
                )
            ],
        ),
        ChatCompletionChunk(
            id='chatcmpl-123',
            object='chat.completion.chunk',
            created=1677652288,
            model='gpt-3.5-turbo-0613',
            system_fingerprint='fp_fingerprint',
            choices=[
                ChunkChoice(
                    index=0,
                    delta={
                        'role': 'assistant',
                        'content': test_contents[3]
                    },
                    logprobs=None,
                    finish_reason=None
                )
            ],
        ),
        ChatCompletionChunk(
            id='chatcmpl-123',
            object='chat.completion.chunk',
            created=1677652288,
            model='gpt-3.5-turbo-0613',
            system_fingerprint='fp_fingerprint',
            choices=[
                ChunkChoice(
                    index=0,
                    delta={
                        'role': 'assistant',
                        'content': test_contents[4]
                    },
                    logprobs=None,
                    finish_reason=None
                )
            ],
        ),
        ChatCompletionChunk(
            id='chatcmpl-123',
            object='chat.completion.chunk',
            created=1677652288,
            model='gpt-3.5-turbo-0613',
            system_fingerprint='fp_fingerprint',
            choices=[
                ChunkChoice(
                    index=0,
                    delta={
                        'role': 'assistant',
                        'content': test_contents[5]
                    },
                    logprobs=None,
                    finish_reason=None
                )
            ],
        ),
        ChatCompletionChunk(
            id='chatcmpl-123',
            object='chat.completion.chunk',
            created=1677652288,
            model='gpt-3.5-turbo-0613',
            system_fingerprint='fp_fingerprint',
            choices=[
                ChunkChoice(
                    index=0,
                    delta={
                        'role': 'assistant',
                        'content': ''
                    },
                    logprobs=None,
                    finish_reason='stop'
                )
            ],
        ),
    ]
    
    with patch('flamethrower.models.openai_client.OpenAI') as mock_openai:
        client = OpenAIClient(system_message=test_message, model=test_model)

        model = mock_openai.return_value
        model.chat.completions.create.return_value = test_responses

        stream = client.new_streaming_chat_request(test_messages)
        assert stream is not None

        idx = 0
        for chunk in stream:
            assert chunk == test_contents[idx]
            idx += 1

def test_openai_client_new_basic_async_chat_request() -> None:
    test_message, test_model = 'test_message', 'test_model'
    test_prompt_tokens, test_completion_tokens = 42, 69
    test_messages = [
        { 'role': 'system', 'content': 'You are OpenAI.' },
        { 'role': 'user', 'content': 'Say "This is a 🔥 flamethrower test."' }
    ]
    test_content = 'This is a 🔥 flamethrower test.'
    test_response = ChatCompletion(
            id='chatcmpl-123',
            object='chat.completion',
            created=1677652288,
            model='gpt-3.5-turbo-0613',
            system_fingerprint='fp_fingerprint',
            choices=[
                BasicChoice(
                    index=0,
                    message={
                        'role': 'assistant',
                        'content': test_content
                    },
                    logprobs=None,
                    finish_reason='stop'
                )
            ],
            usage=CompletionUsage(
                prompt_tokens=42,
                completion_tokens=69,
                total_tokens=111
            )
        )

    with patch('flamethrower.models.openai_client.AsyncOpenAI') as mock_openai, \
        patch('flamethrower.models.openai_client.OpenAIClient.get_token_usage',
            return_value=(test_prompt_tokens, test_completion_tokens)
        ):

        client = OpenAIClient(system_message=test_message, model=test_model)

        model = mock_openai.return_value
        model.chat.completions.create = AsyncMock(return_value=test_response)

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(client.new_basic_async_chat_request(test_messages))

        assert response == (test_content, test_prompt_tokens, test_completion_tokens, test_model)

def test_openai_client_new_json_request() -> None:
    """
    Basically the same as `basic_chat_request`
    """

    test_message, test_model = 'test_message', 'test_model'
    test_prompt_tokens, test_completion_tokens = 42, 69
    test_messages = [
        { 'role': 'system', 'content': 'You are OpenAI.' },
        { 'role': 'user', 'content': 'Return a json of a random Person with a name and age.' }
    ]
    test_content = '{ person: { name: "Ragnaros the Firelord", age: 9000 } }'
    test_response = ChatCompletion(
            id='chatcmpl-123',
            object='chat.completion',
            created=1677652288,
            model='gpt-3.5-turbo-0613',
            system_fingerprint='fp_fingerprint',
            choices=[
                BasicChoice(
                    index=0,
                    message={
                        'role': 'assistant',
                        'content': test_content
                    },
                    logprobs=None,
                    finish_reason='stop'
                )
            ],
            usage=CompletionUsage(
                prompt_tokens=42,
                completion_tokens=69,
                total_tokens=111
            )
        )

    with patch('flamethrower.models.openai_client.OpenAI') as mock_openai, \
        patch('flamethrower.models.openai_client.OpenAIClient.get_token_usage',
              return_value=(test_prompt_tokens, test_completion_tokens)
        ):

        client = OpenAIClient(system_message=test_message, model=test_model)

        model = mock_openai.return_value
        model.chat.completions.create.return_value = test_response

        response = client.new_json_request(test_messages)

        assert response == (test_content, test_prompt_tokens, test_completion_tokens, test_model)
