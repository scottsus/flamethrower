import pytest
from flamethrower.context.conv_manager import ConversationManager

@pytest.fixture
def mock_conv_manager() -> ConversationManager:
    conv_manager = ConversationManager()
    conv_manager.append_conv(role='user', content='Hello World')
    return conv_manager
