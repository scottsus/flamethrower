import asyncio
from unittest.mock import AsyncMock, patch
from flamethrower.models.llm import LLM

def test_llm_init() -> None:
    test_system_message = 'test system message'

    llm = LLM(system_message=test_system_message)
    
    assert llm.system_message == test_system_message
    assert llm.model != ''
    assert llm.llm_client is not None
    
    assert llm.llm_client.system_message == test_system_message
    assert llm.token_counter is not None

def test_llm_new_chat_request() -> None:
    test_system_message = '🤖 You are OpenAI'
    test_messages = [
        { 'role': 'system', 'content': test_system_message },
        { 'role': 'user', 'content': 'Say "This is a 🔥 flamethrower test."' }
    ]
    (test_content, test_prompt_tokens, test_completion_tokens, test_model) = ('This is a 🔥 flamethrower test.', 42, 69, 'Test model')
    test_result = (test_content, test_prompt_tokens, test_completion_tokens, test_model)

    with patch('flamethrower.models.llm.OpenAIClient.new_basic_chat_request',
              return_value=test_result
        ) as mock_new_basic_chat_request, \
        patch('flamethrower.models.llm.TokenCounter.add_input_tokens') as mock_add_input_tokens, \
        patch('flamethrower.models.llm.TokenCounter.add_output_tokens') as mock_add_output_tokens:
            llm = LLM(system_message=test_system_message)

            result = llm.new_chat_request(test_messages)
            assert result == test_content

            mock_new_basic_chat_request.assert_called_once_with(test_messages)

            mock_add_input_tokens.assert_called_once_with(test_prompt_tokens, test_model)
            mock_add_output_tokens.assert_called_once_with(test_completion_tokens, test_model)

def test_llm_new_streaming_chat_request() -> None:
     test_system_message = '🤖 You are OpenAI'
     test_messages = [
         { 'role': 'system', 'content': test_system_message },
         { 'role': 'user', 'content': 'Say "This is a 🔥 flamethrower test."' }
     ]
     test_chunks = [
        'This', 'is', 'a', '🔥', 'flamethrower', 'test.'
     ]

     with patch('flamethrower.models.llm.OpenAIClient.new_streaming_chat_request',
              return_value=iter(test_chunks)
        ) as mock_new_streaming_chat_request, \
        patch('flamethrower.models.llm.TokenCounter.add_streaming_input_tokens') as mock_add_streaming_input_tokens:
            llm = LLM(system_message=test_system_message)

            stream = llm.new_streaming_chat_request(test_messages)
            assert stream is not None

            idx = 0
            for chunk in stream:
                if chunk is None:
                      break
                assert chunk == test_chunks[idx]
                idx += 1

            mock_new_streaming_chat_request.assert_called_once_with(test_messages)
            mock_add_streaming_input_tokens.assert_called_once_with(str(test_messages))

def test_llm_new_async_chat_request() -> None:
    test_system_message = '🤖 You are OpenAI'
    test_messages = [
        { 'role': 'system', 'content': test_system_message },
        { 'role': 'user', 'content': 'This is a 🔥 flamethrower test.' }
    ]
    (test_content, test_prompt_tokens, test_completion_tokens, test_model) = ('Test content', 42, 69, 'Test model')
    test_result = (test_content, test_prompt_tokens, test_completion_tokens, test_model)

    with patch('flamethrower.models.llm.OpenAIClient') as mock_openai, \
        patch('flamethrower.models.llm.TokenCounter.add_input_tokens') as mock_add_input_tokens, \
        patch('flamethrower.models.llm.TokenCounter.add_output_tokens') as mock_add_output_tokens:
            llm = LLM(system_message=test_system_message)

            llm_client = mock_openai.return_value
            llm_client.new_basic_async_chat_request = AsyncMock(return_value=test_result)

            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(llm.new_async_chat_request(test_messages))

            mock_add_input_tokens.assert_called_once_with(test_prompt_tokens, test_model)
            mock_add_output_tokens.assert_called_once_with(test_completion_tokens, test_model)

            assert result == test_content

def test_llm_new_json_request() -> None:
    test_system_message = '🤖 You are OpenAI'
    test_messages = [
        { 'role': 'system', 'content': test_system_message },
        { 'role': 'user', 'content': 'Return a json of a random Person with a name and age.' }
    ]
    (test_content, test_prompt_tokens, test_completion_tokens, test_model) = ('{ person: { name: "Ragnaros the Firelord", age: 9000 } }', 42, 69, 'Test model')
    test_result = (test_content, test_prompt_tokens, test_completion_tokens, test_model)

    with patch('flamethrower.models.llm.OpenAIClient.new_basic_chat_request',
              return_value=test_result
        ) as mock_new_basic_chat_request, \
        patch('flamethrower.models.llm.TokenCounter.add_input_tokens') as mock_add_input_tokens, \
        patch('flamethrower.models.llm.TokenCounter.add_output_tokens') as mock_add_output_tokens:
            llm = LLM(system_message=test_system_message)

            result = llm.new_chat_request(test_messages)
            assert result == test_content

            mock_new_basic_chat_request.assert_called_once_with(test_messages)

            mock_add_input_tokens.assert_called_once_with(test_prompt_tokens, test_model)
            mock_add_output_tokens.assert_called_once_with(test_completion_tokens, test_model)
