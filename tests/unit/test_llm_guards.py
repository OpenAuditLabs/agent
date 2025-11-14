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


def test_validate_input_valid(llm_guards):
    assert llm_guards.validate_input("This is a safe prompt.") is True
    assert llm_guards.validate_input("Another safe prompt with numbers 123.") is True


def test_validate_input_exceeds_max_length(llm_guards):
    long_prompt = "a" * 4097  # Exceeds MAX_PROMPT_LENGTH of 4096
    assert llm_guards.validate_input(long_prompt) is False


def test_validate_input_malicious_pattern(llm_guards):
    assert llm_guards.validate_input("SELECT * FROM users UNION SELECT 1,2,3") is False
    assert llm_guards.validate_input("rm -rf /") is False
    assert llm_guards.validate_input("import os; os.system('ls')") is False


def test_validate_input_harmful_keywords(llm_guards):
    assert llm_guards.validate_input("This prompt contains hate speech.") is False
    assert llm_guards.validate_input("Promoting violence is bad.") is False


def test_validate_input_caching(llm_guards):
    # Call the method multiple times with the same input
    llm_guards.validate_input("cached prompt")
    llm_guards.validate_input("cached prompt")
    llm_guards.validate_input("another cached prompt")
    llm_guards.validate_input("another cached prompt")

    # Check cache info
    cache_info = llm_guards._cached_validate_input_core.cache_info()

    # Expect 2 hits (2 calls for "cached prompt", 2 calls for "another cached prompt", but only 2 unique calls)
    assert cache_info.hits == 2
    assert cache_info.misses == 2
    assert cache_info.currsize == 2
