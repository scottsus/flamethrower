from unittest.mock import patch
from flamethrower.agents.drivers.feature_driver import FeatureDriver
from flamethrower.test_utils.mocks.mock_prompt_generator import mock_prompt_generator

def mock_feature_driver() -> FeatureDriver:
    with patch('flamethrower.agents.drivers.feature_driver.LLM') as mock_llm:
        return FeatureDriver(
            target_dir='flamethrower/some/path',
            prompt_generator=mock_prompt_generator()
        )

def test_feature_driver_init() -> None:
    target_dir = 'flamethrower/some/path'
    prompt_generator = mock_prompt_generator()

    with patch('flamethrower.agents.drivers.feature_driver.LLM') as mock_llm:
        driver = FeatureDriver(
            target_dir=target_dir,
            prompt_generator=prompt_generator
        )

        assert driver.target_dir == target_dir
        assert driver.prompt_generator == prompt_generator
        assert driver.llm == mock_llm.return_value
        
        mock_llm.assert_called_once()
        
def test_feature_driver_respond_to() -> None:
    pass
