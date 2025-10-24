"""Custom error classes."""


class OALAgentError(Exception):
    """Base exception for OAL Agent."""

    pass


class AnalysisError(OALAgentError):
    """Error during analysis."""

    pass


class ValidationError(OALAgentError):
    """Validation error."""

    pass


class ConfigurationError(OALAgentError):
    """Configuration error."""

    pass


class LLMTimeoutError(OALAgentError):
    """LLM timeout error."""

    pass
