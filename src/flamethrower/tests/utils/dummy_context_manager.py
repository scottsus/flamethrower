from typing import Any, Optional, Type

class DummyContextManager:
    def __enter__(self) -> 'DummyContextManager':
        return self

    def __exit__(self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any]
    ) -> None:
        pass
