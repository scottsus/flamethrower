import itertools
from unittest import mock
from unittest.mock import patch
from flamethrower.utils.loader import Loader
from flamethrower.utils.special_keys import CLEAR_FROM_START, CLEAR_TO_END, CURSOR_TO_START
from flamethrower.utils.colors import STDIN_YELLOW, STDIN_DEFAULT
from flamethrower.test_utils.mocks.mock_shell_manager import mock_shell_manager

def test_loader_init() -> None:
    pattern_cycle = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

    with patch('time.time', return_value=0.0), \
        patch('itertools.cycle', return_value=pattern_cycle), \
        patch('flamethrower.containers.container.container.shell_manager', return_value=None):
        
        loader = Loader(
            loading_message='🧠 Thinking...',
            completion_message='🎉 Done!',
            with_newline=False,
            will_report_timing=True,
        )

        assert loader.loading_message == '🧠 Thinking...'
        assert loader.completion_message == '🎉 Done!'
        assert loader.with_newline == False
        assert loader.will_report_timing == True
        assert loader.requires_cooked_mode == True
        assert loader.done == False
        assert loader.spinner == pattern_cycle
        assert loader.start_time == 0.0

def test_loader_spin() -> None:
    loading_message = '🌀 Spinning...'
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

    with patch('flamethrower.containers.container.container.shell_manager', return_value=None):
        
        loader = Loader(loading_message=loading_message)
        assert loader.done == False

        side_effect_idx = 0
        def get_side_effect(_: float) -> None:
            nonlocal side_effect_idx
            side_effect_idx += 1
            if side_effect_idx < 3:
                return None

            setattr(loader, 'done', True)
        
        with patch('sys.stdout.write') as mock_write, \
            patch('sys.stdout.flush') as mock_flush, \
            patch('time.sleep', side_effect=get_side_effect) as mock_sleep:        
            
            loader.spin()
            
            mock_write.assert_has_calls([
                mock.call('\n'),
                mock.call(f'{STDIN_YELLOW.decode("utf-8")}\r{next(spinner)} {loading_message}{STDIN_DEFAULT.decode("utf-8")}'),
                mock.call(f'{STDIN_YELLOW.decode("utf-8")}\r{next(spinner)} {loading_message}{STDIN_DEFAULT.decode("utf-8")}'),
                mock.call(f'{STDIN_YELLOW.decode("utf-8")}\r{next(spinner)} {loading_message}{STDIN_DEFAULT.decode("utf-8")}'),
            ])
            mock_flush.assert_has_calls([mock.call(), mock.call(), mock.call()])
            mock_sleep.asset_has_calls([mock.call(0.1), mock.call(0.1), mock.call(0.1)])

def test_loader_spin_and_stop() -> None:
    loading_message = '🌀 Spinning...'
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

    with patch('flamethrower.containers.container.container.shell_manager', return_value=None):
        
        loader = Loader(loading_message=loading_message)
        assert loader.done == False

        side_effect_idx = 0
        def get_side_effect(_: float) -> None:
            nonlocal side_effect_idx
            side_effect_idx += 1
            if side_effect_idx < 3:
                return None

            loader.stop()
        
        with patch('sys.stdout.write') as mock_write, \
            patch('sys.stdout.flush') as mock_flush, \
            patch('time.sleep', side_effect=get_side_effect) as mock_sleep:        
            
            loader.spin()
            assert loader.done == True
            
            mock_write.assert_has_calls([
                mock.call('\n'),
                mock.call(f'{STDIN_YELLOW.decode("utf-8")}\r{next(spinner)} {loading_message}{STDIN_DEFAULT.decode("utf-8")}'),
                mock.call(f'{STDIN_YELLOW.decode("utf-8")}\r{next(spinner)} {loading_message}{STDIN_DEFAULT.decode("utf-8")}'),
                mock.call(f'{STDIN_YELLOW.decode("utf-8")}\r{next(spinner)} {loading_message}{STDIN_DEFAULT.decode("utf-8")}'),
                mock.call((CLEAR_FROM_START + CLEAR_TO_END + CURSOR_TO_START).decode("utf-8")),
            ])
            mock_flush.assert_has_calls([mock.call(), mock.call(), mock.call(), mock.call()])
            mock_sleep.asset_has_calls([mock.call(0.1), mock.call(0.1), mock.call(0.1)])

def test_loader_managed_loader() -> None:
    loading_message = '🌀 Spinning...'
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

    with patch('flamethrower.containers.container.container.shell_manager', return_value=mock_shell_manager()):
        
        loader = Loader(loading_message=loading_message)
        assert loader.done == False

        side_effect_idx = 0
        def get_side_effect(_: float) -> None:
            nonlocal side_effect_idx
            side_effect_idx += 1
            if side_effect_idx < 3:
                return None

            loader.stop()
        
        with patch('sys.stdout.write') as mock_write, \
            patch('sys.stdout.flush') as mock_flush, \
            patch('time.sleep', side_effect=get_side_effect) as mock_sleep:        

            assert loader.done == False            
            with loader.managed_loader():
                pass
            
            assert loader.done == True
            
            mock_write.assert_has_calls([
                mock.call('\n'),
                mock.call(f'{STDIN_YELLOW.decode("utf-8")}\r{next(spinner)} {loading_message}{STDIN_DEFAULT.decode("utf-8")}'),
                mock.call(f'{STDIN_YELLOW.decode("utf-8")}\r{next(spinner)} {loading_message}{STDIN_DEFAULT.decode("utf-8")}'),
                mock.call(f'{STDIN_YELLOW.decode("utf-8")}\r{next(spinner)} {loading_message}{STDIN_DEFAULT.decode("utf-8")}'),
                mock.call((CLEAR_FROM_START + CLEAR_TO_END + CURSOR_TO_START).decode("utf-8")),
            ])
            mock_flush.assert_has_calls([mock.call(), mock.call(), mock.call(), mock.call()])
            mock_sleep.asset_has_calls([mock.call(0.1), mock.call(0.1), mock.call(0.1)])
