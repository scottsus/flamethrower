from flamethrower.setup.summary_manager import SummaryManager

def test_summary_manager_init() -> None:
    sm = SummaryManager()

    assert sm.max_summarization_tasks == 100
    assert sm.summarization_tasks == []
    assert sm.summarization_tasks_copy == []
    assert sm.instant_timeout == 0.5
    assert sm.summarization_timeout == 75
    assert sm._lock is not None

def test_summary_manager_get_summarizations_with_timeout() -> None:
    pass

def test_summary_manager_perform_async_task() -> None:
    pass

def test_summary_manager_add_summarization_task() -> None:
    pass

def test_summary_manager_cancel_summarization_task() -> None:
    pass

def test_summary_manager_safe_gather() -> None:
    pass
