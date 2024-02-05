from unittest.mock import patch
from flamethrower.agents.drivers.general_driver import GeneralDriver

def mock_general_driver() -> GeneralDriver:
    with patch('flamethrower.agents.drivers.general_driver.LLM'):
        return GeneralDriver()

def test_general_driver_init() -> None:
    with patch('flamethrower.agents.drivers.general_driver.LLM') as mock_llm:
        driver = GeneralDriver()

        assert driver.llm == mock_llm.return_value
        
        mock_llm.assert_called_once()
        
def test_general_driver_respond_to() -> None:
    pass
