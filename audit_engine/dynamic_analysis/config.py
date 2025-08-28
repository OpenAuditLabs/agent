"""
Configuration management for Dynamic Analysis Module
"""

from typing import Any, Dict, Optional
from pydantic import BaseSettings, Field


class DynamicAnalysisConfig(BaseSettings):
    """
    Configuration for Dynamic Analysis with secure environment variable handling
    """
    
    # Analysis configuration
    enable_echidna: bool = Field(True, description="Enable Echidna fuzzing")
    enable_adversarial_fuzz: bool = Field(True, description="Enable adversarial fuzzing")
    analysis_timeout: int = Field(600, description="Analysis timeout in seconds")
    max_workers: int = Field(4, description="Maximum worker threads")
    
    # Trust and RL configuration
    reinforcement_learning: bool = Field(False, description="Enable RL feedback")
    cross_chain_analysis: bool = Field(False, description="Enable cross-chain analysis")
    
    # Tool-specific configurations
    echidna: Dict[str, Any] = Field(default_factory=dict, description="Echidna configuration")
    adversarial_fuzz: Dict[str, Any] = Field(default_factory=dict, description="Adversarial fuzz configuration")
    
    # Tool accuracy settings for trust calibration
    echidna_adapter_accuracy: float = Field(0.8, description="EchidnaAdapter accuracy weight")
    adversarial_fuzz_accuracy: float = Field(0.85, description="AdversarialFuzz accuracy weight")
    
    # API keys and sensitive data (will be masked in logs)
    api_key: Optional[str] = Field(None, description="API key for external services")
    auth_token: Optional[str] = Field(None, description="Authentication token")
    
    class Config:
        env_prefix = "AUDIT_"
        env_file = ".env"
        case_sensitive = False
        # Allow AUDIT_STATIC_ANALYSIS__ENABLE_SLITHER, etc.
        env_nested_delimiter = "__"
        
    def masked_dict(self) -> Dict[str, Any]:
        """
        Return a dictionary representation with sensitive fields masked
        """
        config_dict = self.dict()
        sensitive_keys = {"api_key", "auth_token", "password", "secret"}
        
        def mask_recursive(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {
                    k: "***" if k.lower() in sensitive_keys or 
                       any(sensitive in k.lower() for sensitive in sensitive_keys)
                    else mask_recursive(v)
                    for k, v in obj.items()
                }
            return obj
            
        return mask_recursive(config_dict)
