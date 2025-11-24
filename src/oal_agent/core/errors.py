"""Custom error classes."""


class ErrorCodes:
    """Centralized error codes for the OAL Agent."""

    # General Errors
    UNKNOWN_ERROR = "OAL-0000"
    INVALID_INPUT = "OAL-0001"
    CONFIGURATION_ERROR = "OAL-0002"

    # Analysis Errors
    ANALYSIS_FAILED = "OAL-1000"
    LLM_TIMEOUT = "OAL-1001"

    # Security Errors
    INVALID_KEY = "OAL-2000"
    DECRYPTION_FAILED = "OAL-2001"
    VALIDATION_FAILED = "OAL-2002"

    # Orchestration Errors
    ORCHESTRATION_FAILED = "OAL-3000"


class OALAgentError(Exception):
    """Base exception for OAL Agent."""

    def __init__(self, message: str, error_code: str = ErrorCodes.UNKNOWN_ERROR):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class AnalysisError(OALAgentError):
    """Error during analysis."""

    def __init__(self, message: str = "Analysis failed.", error_code: str = ErrorCodes.ANALYSIS_FAILED):
        super().__init__(message, error_code)


class ValidationError(OALAgentError):
    """Validation error."""

    def __init__(self, message: str = "Validation failed.", error_code: str = ErrorCodes.VALIDATION_FAILED):
        super().__init__(message, error_code)


class ConfigurationError(OALAgentError):
    """Configuration error."""

    def __init__(self, message: str = "Configuration error.", error_code: str = ErrorCodes.CONFIGURATION_ERROR):
        super().__init__(message, error_code)


class LLMTimeoutError(OALAgentError):
    """LLM timeout error."""

    def __init__(self, message: str = "LLM timed out.", error_code: str = ErrorCodes.LLM_TIMEOUT):
        super().__init__(message, error_code)


class OrchestrationError(OALAgentError):
    """Error during orchestration."""

    def __init__(self, message: str = "Orchestration failed.", error_code: str = ErrorCodes.ORCHESTRATION_FAILED):
        super().__init__(message, error_code)


class InvalidKey(OALAgentError):
    """Invalid key error."""

    def __init__(self, message: str = "Invalid key provided.", error_code: str = ErrorCodes.INVALID_KEY):
        super().__init__(message, error_code)


class DecryptionError(OALAgentError):
    """Decryption error."""

    def __init__(self, message: str = "Decryption failed.", error_code: str = ErrorCodes.DECRYPTION_FAILED):
        super().__init__(message, error_code)
