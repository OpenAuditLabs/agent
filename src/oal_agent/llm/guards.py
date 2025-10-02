"""LLM guardrails."""


class LLMGuards:
    """Implements safety guardrails for LLM interactions."""

    def __init__(self):
        """Initialize guards."""
        pass

    async def validate_input(self, prompt: str) -> bool:
        """Validate input prompt."""
        # TODO: Implement input validation
        return True

    async def validate_output(self, response: str) -> bool:
        """Validate LLM output."""
        # TODO: Implement output validation
        return True
