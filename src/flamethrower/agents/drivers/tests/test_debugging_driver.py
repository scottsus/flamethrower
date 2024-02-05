from unittest.mock import patch
from flamethrower.agents.drivers.debugging_driver import DebuggingDriver
from flamethrower.test_utils.mocks.mock_prompt_generator import mock_prompt_generator

def mock_debugging_driver() -> DebuggingDriver:
    with patch('flamethrower.agents.drivers.debugging_driver.LLM') as mock_llm:
        return DebuggingDriver(
            target_dir='flamethrower/some/path',
            prompt_generator=mock_prompt_generator()
        )

def test_debugging_driver_init() -> None:
    target_dir = 'flamethrower/some/path'
    prompt_generator = mock_prompt_generator()

    with patch('flamethrower.agents.drivers.debugging_driver.LLM') as mock_llm:
        driver = DebuggingDriver(
            target_dir=target_dir,
            prompt_generator=prompt_generator
        )

        assert driver.target_dir == target_dir
        assert driver.prompt_generator == prompt_generator
        assert driver.llm == mock_llm.return_value
        
        mock_llm.assert_called_once()
        
def test_debugging_driver_respond_to() -> None:
    pass
