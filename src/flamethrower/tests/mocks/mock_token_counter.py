import pytest
from unittest.mock import MagicMock
from flamethrower.utils.token_counter import TokenCounter

@pytest.fixture
def mock_token_counter() -> TokenCounter:
    return MagicMock(spec=TokenCounter)
