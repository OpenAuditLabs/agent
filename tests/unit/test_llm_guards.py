import pytest

from oal_agent.llm.guards import LLMGuards


@pytest.fixture
def llm_guards():
    return LLMGuards()


def test_validate_retry_attempts_valid(llm_guards):
    assert llm_guards.validate_retry_attempts(1) is True
    assert llm_guards.validate_retry_attempts(3) is True
    assert llm_guards.validate_retry_attempts(5) is True


def test_validate_retry_attempts_invalid(llm_guards):
    assert llm_guards.validate_retry_attempts(0) is False
    assert llm_guards.validate_retry_attempts(6) is False
    assert llm_guards.validate_retry_attempts("abc") is False
    assert llm_guards.validate_retry_attempts(1.5) is False


def test_validate_timeout_valid(llm_guards):
    assert llm_guards.validate_timeout(10) is True
    assert llm_guards.validate_timeout(60) is True
    assert llm_guards.validate_timeout(120) is True


def test_validate_timeout_invalid(llm_guards):
    assert llm_guards.validate_timeout(9) is False
    assert llm_guards.validate_timeout(121) is False
    assert llm_guards.validate_timeout("abc") is False
    assert llm_guards.validate_timeout(59.9) is False
