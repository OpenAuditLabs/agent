"""
Configuration management for Dynamic Analysis Module
"""

from typing import Any, Dict, Optional, Set
from pydantic import Field

try:
    # Pydantic v2
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
    from pydantic import model_validator  # type: ignore[attr-defined]
    _PYDANTIC_V2 = True
except Exception:  # pragma: no cover
    # Pydantic v1 fallback
    from pydantic import BaseSettings, root_validator  # type: ignore
    _PYDANTIC_V2 = False


class DynamicAnalysisConfig(BaseSettings):
    """
    Configuration for Dynamic Analysis with secure environment variable handling
    """
    
    # Analysis configuration
    enable_echidna: bool = Field(True, description="Enable Echidna fuzzing")
    enable_adversarial_fuzz: bool = Field(True, description="Enable adversarial fuzzing")
    analysis_timeout: int = Field(600, ge=1, le=3600, description="Analysis timeout in seconds")
    max_workers: int = Field(4, ge=1, le=16, description="Maximum worker threads")
    
    # Trust and RL configuration
    reinforcement_learning: bool = Field(False, description="Enable RL feedback")
    cross_chain_analysis: bool = Field(False, description="Enable cross-chain analysis")
    
    # Tool-specific configurations
    echidna: Dict[str, Any] = Field(default_factory=dict, description="Echidna configuration")
    adversarial_fuzz: Dict[str, Any] = Field(default_factory=dict, description="Adversarial fuzz configuration")
    
    # Tool accuracy settings for trust calibration
    echidna_adapter_accuracy: float = Field(
        0.8, 
        ge=0.0, 
        le=1.0, 
        description="EchidnaAdapter accuracy weight"
    )
    adversarial_fuzz_accuracy: float = Field(
        0.85, 
        ge=0.0, 
        le=1.0, 
        description="AdversarialFuzz accuracy weight"
    )
    
    # API keys and sensitive data (will be masked in logs)
    api_key: Optional[str] = Field(None, description="API key for external services")
    auth_token: Optional[str] = Field(None, description="Authentication token")
    
    if _PYDANTIC_V2:
        model_config = SettingsConfigDict(
            env_prefix="DYNAMIC_ANALYSIS_",
            env_file=".env",
            case_sensitive=False,
            env_nested_delimiter="__",
            extra="forbid",
            validate_assignment=True,
        )
    else:
        class Config:
            env_prefix = "DYNAMIC_ANALYSIS_"
            env_file = ".env"
            case_sensitive = False
            env_nested_delimiter = "__"
            extra = "forbid"
            validate_assignment = True
    
    # Validation (v2 instance "after" validator; v1 class-level root validator)
    if _PYDANTIC_V2:
        @model_validator(mode="after")
        def _validate_after(self) -> "DynamicAnalysisConfig":
            if not (self.enable_echidna or self.enable_adversarial_fuzz):
                raise ValueError("At least one analysis tool must be enabled")
            if self.enable_echidna and not isinstance(self.echidna, dict):
                raise ValueError("Echidna configuration must be a dictionary")
            if self.enable_adversarial_fuzz and not isinstance(self.adversarial_fuzz, dict):
                raise ValueError("Adversarial fuzz configuration must be a dictionary")
            return self
    else:
        @root_validator
        def _validate_v1(cls, values: Dict[str, Any]) -> Dict[str, Any]:
            if not (values.get("enable_echidna") or values.get("enable_adversarial_fuzz")):
                raise ValueError("At least one analysis tool must be enabled")
            if values.get("enable_echidna") and not isinstance(values.get("echidna"), dict):
                raise ValueError("Echidna configuration must be a dictionary")
            if values.get("enable_adversarial_fuzz") and not isinstance(values.get("adversarial_fuzz"), dict):
                raise ValueError("Adversarial fuzz configuration must be a dictionary")
            return values
    
    def masked_dict(self) -> Dict[str, Any]:
        """
        Return a dictionary representation with sensitive fields masked
        """
        # Use model_dump for Pydantic v2 compatibility, dict() for v1
        config_dict = self.model_dump() if hasattr(self, "model_dump") else self.dict()
        return self._mask_sensitive_data(config_dict)
    
    def _mask_sensitive_data(self, obj: Any) -> Any:
        """
        Recursively mask sensitive data in configuration
        """
        # Define comprehensive set of sensitive key patterns as class constant
        if not hasattr(self, '_sensitive_patterns'):
            self._sensitive_patterns: Set[str] = {
                "api_key", "access_key", "secret_key", "private_key", "client_secret",
                "password", "pass", "pwd",
                "secret", "token", "auth_token", "bearer_token", "refresh_token",
                "authorization", "x-api-key", "x_api_key",
            }
        
        if isinstance(obj, dict):
            masked = {}
            for key, value in obj.items():
                key_lower = str(key).lower()
                # Narrow match: exact known keys or common suffixes
                is_sensitive = (
                    key_lower in self._sensitive_patterns
                    or key_lower.endswith(("_key", "_secret", "_token", "-key", "-secret", "-token"))
                )
                
                if is_sensitive and value is not None:
                    # Mask with partial visibility for debugging
                    if isinstance(value, str) and len(value) > 8:
                        masked[key] = f"{value[:3]}***{value[-2:]}"
                    else:
                        masked[key] = "***"
                else:
                    masked[key] = self._mask_sensitive_data(value)
            return masked
        elif isinstance(obj, (list, tuple)):
            return [self._mask_sensitive_data(item) for item in obj]
        else:
            return obj
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific tool with fallback to defaults
        """
        tool_configs = {
            "echidna": self.echidna,
            "adversarial_fuzz": self.adversarial_fuzz,
        }
        
        return tool_configs.get(tool_name.lower(), {})
    