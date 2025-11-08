"""LLM guardrails."""

import re


class LLMGuards:
    """Implements safety guardrails for LLM interactions."""

    def __init__(self):
        """Initialize guards."""
        pass

    async def validate_input(self, prompt: str) -> bool:
        """Validate input prompt for safety, appropriateness, and well-formedness.

        Args:
            prompt: The input string to validate.

        Returns:
            True if the prompt is valid, False otherwise.
        """

        MAX_PROMPT_LENGTH = 4096
        if len(prompt) > MAX_PROMPT_LENGTH:
            print(
                f"Input validation failed: Prompt exceeds maximum length of {MAX_PROMPT_LENGTH} characters."
            )
            return False

        malicious_patterns = [
            # SQL Injection
            r"('|%27)\s*(OR|AND)\s*(\d+=\d+|'[^']+'='[^']+')",
            r"UNION\s+SELECT",
            r"SLEEP\(",
            # Command Injection
            r"&&\s*\w+",
            r"||\s*\w+",
            r";\s*\w+",
            r"`\s*\w+\s*`",
            r"\$\(",
            # Code Injection (Python examples)
            r"import\s+os",
            r"subprocess\.run",
            r"eval\(",
            r"exec\(",
        ]

        for pattern in malicious_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                print(f"Input validation failed: Malicious pattern detected: {pattern}")
                return False

        harmful_keywords = [
            r"hate\s+speech",
            r"violence\s+promotion",
            r"illegal\s+activity",
            r"offensive\s+term_x",
            r"offensive\s+term_y",
        ]

        for keyword in harmful_keywords:
            if re.search(keyword, prompt, re.IGNORECASE):
                print(
                    f"Input validation failed: Harmful/offensive language detected: {keyword}"
                )
                return False

        return True

    def validate_retry_attempts(self, attempts: int) -> bool:
        """Validate retry attempts for LLM calls.

        Args:
            attempts: The number of retry attempts.

        Returns:
            True if the attempts are valid, False otherwise.
        """
        if not isinstance(attempts, int) or not (1 <= attempts <= 5):
            print(f"Input validation failed: Retry attempts must be an integer between 1 and 5. Got {attempts}.")
            return False
        return True

    def validate_timeout(self, timeout: int) -> bool:
        """Validate timeout for LLM calls.

        Args:
            timeout: The timeout in seconds.

        Returns:
            True if the timeout is valid, False otherwise.
        """
        if not isinstance(timeout, int) or not (10 <= timeout <= 120):
            print(f"Input validation failed: Timeout must be an integer between 10 and 120 seconds. Got {timeout}.")
            return False
        return True

    async def validate_output(self, response: str) -> bool:
        """Validate LLM output."""
        # TODO: Implement output validation
        return True
