from unittest.mock import MagicMock
from flamethrower.context.conv_manager import ConversationManager

def mock_conv_manager() -> ConversationManager:
    return MagicMock(spec=ConversationManager)
