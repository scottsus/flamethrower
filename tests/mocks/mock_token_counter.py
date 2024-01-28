import pytest
from flamethrower.utils.token_counter import TokenCounter

@pytest.fixture
def mock_token_counter() -> TokenCounter:
    token_counter = TokenCounter()
    token_counter.add_token(token='Hello')
    token_counter.add_token(token='World')
    return token_counter