from flamethrower.containers.lm_container import LMContainer
from flamethrower.utils.token_counter import TokenCounter

def mock_lm_container() -> LMContainer:
    return LMContainer()

def test_lm_container_init() -> None:
    container = mock_lm_container()
    assert isinstance(container.token_counter(), TokenCounter)
