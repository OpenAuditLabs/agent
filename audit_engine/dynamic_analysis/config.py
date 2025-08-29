"""
Configuration management for Dynamic Analysis Module
"""

from typing import Any, Dict, Optional, Set
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


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
    
    model_config = {
        "env_prefix": "AUDIT_",
        "env_file": ".env",
        "case_sensitive": False,
        "env_nested_delimiter": "__",
        "extra": "forbid",  # Prevent unexpected configuration keys
        "validate_assignment": True,  # Validate on assignment
    }
    
    @validator('analysis_timeout')
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate analysis timeout is reasonable"""
        if v <= 0:
            raise ValueError("Analysis timeout must be positive")
        if v > 3600:  # 1 hour max
            raise ValueError("Analysis timeout cannot exceed 1 hour")
        return v
    
    @validator('max_workers')
    @classmethod
    def validate_max_workers(cls, v: int) -> int:
        """Validate max workers is reasonable"""
        if v <= 0:
            raise ValueError("Max workers must be positive")
        if v > 16:  # Reasonable upper limit
            raise ValueError("Max workers cannot exceed 16")
        return v
    
    def masked_dict(self) -> Dict[str, Any]:
        """
        Return a dictionary representation with sensitive fields masked
        """
        # Use model_dump for Pydantic v2 compatibility
        config_dict = self.model_dump()
        return self._mask_sensitive_data(config_dict)
    
    def _mask_sensitive_data(self, obj: Any) -> Any:
        """
        Recursively mask sensitive data in configuration
        """
        # Define comprehensive set of sensitive key patterns
        sensitive_patterns: Set[str] = {
            "api_key", "auth_token", "password", "secret", "token", 
            "key", "credential", "auth", "pass", "pwd"
        }
        
        if isinstance(obj, dict):
            masked = {}
            for key, value in obj.items():
                key_lower = key.lower()
                # Check if key contains any sensitive pattern
                is_sensitive = any(pattern in key_lower for pattern in sensitive_patterns)
                
                if is_sensitive and value is not None:
                    # Mask with partial visibility for debugging
                    if isinstance(value, str) and len(value) > 8:
                        masked[key] = f"{value[:3]}***{value[-2:]}
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
    
    def get_tool_accuracy(self, tool_name: str) -> float:
        """
        Get accuracy setting for a specific tool
        """
        accuracy_map = {
            "echidna_adapter": self.echidna_adapter_accuracy,
            "adversarialfuzz": self.adversarial_fuzz_accuracy,
        }
        
        return accuracy_map.get(tool_name.lower(), 0.8)  # Default accuracy
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """
        Check if a specific tool is enabled
        """
        tool_map = {
            "echidna": self.enable_echidna,
            "adversarial_fuzz": self.enable_adversarial_fuzz,
        }
        
        return tool_map.get(tool_name.lower(), False)
    
    def validate_config(self) -> None:
        """
        Perform additional configuration validation
        """
        # Ensure at least one analysis tool is enabled
        if not (self.enable_echidna or self.enable_adversarial_fuzz):
            raise ValueError("At least one analysis tool must be enabled")
        
        # Validate tool-specific configurations
        if self.enable_echidna and not isinstance(self.echidna, dict):
            raise ValueError("Echidna configuration must be a dictionary")
        
        if self.enable_adversarial_fuzz and not isinstance(self.adversarial_fuzz, dict):
            raise ValueError("Adversarial fuzz configuration must be a dictionary")
