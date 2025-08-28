"""
Configuration management for OpenAudit Agent

Centralized configuration with environment variable support
and validation using Pydantic settings.
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field, validator


class StaticAnalysisConfig(BaseSettings):
    """Static analysis tool configuration"""
    enable_slither: bool = Field(default=True, description="Enable Slither analyzer")
    enable_mythril: bool = Field(default=True, description="Enable Mythril analyzer") 
    enable_manticore: bool = Field(default=False, description="Enable Manticore analyzer")
    
    # Tool-specific configs
    slither: Dict[str, Any] = Field(default_factory=dict)
    mythril: Dict[str, Any] = Field(default_factory=dict)
    manticore: Dict[str, Any] = Field(default_factory=dict)
    
    # Common settings
    analysis_timeout: int = Field(default=300, description="Per-tool timeout in seconds")
    max_workers: int = Field(default=4, description="Maximum parallel workers")

    class Config:
        env_prefix = "STATIC_ANALYSIS_"


class DynamicAnalysisConfig(BaseSettings):
    """Dynamic analysis configuration"""
    enable_echidna: bool = Field(default=True, description="Enable Echidna fuzzing")
    enable_adversarial_fuzz: bool = Field(default=True, description="Enable adversarial fuzzing")
    
    # Tool configs
    echidna: Dict[str, Any] = Field(default_factory=dict)
    adversarial_fuzz: Dict[str, Any] = Field(default_factory=dict)
    
    # Analysis settings
    analysis_timeout: int = Field(default=600, description="Analysis timeout in seconds")
    max_workers: int = Field(default=2, description="Maximum parallel workers")
    reinforcement_learning: bool = Field(default=False, description="Enable RL feedback")
    cross_chain_analysis: bool = Field(default=False, description="Enable cross-chain analysis")

    class Config:
        env_prefix = "DYNAMIC_ANALYSIS_"


class ScoringConfig(BaseSettings):
    """Vulnerability scoring configuration"""
    enable_cvss_scoring: bool = Field(default=True, description="Enable CVSS-inspired scoring")
    
    # Weight factors for scoring
    financial_impact_weight: float = Field(default=0.4, ge=0.0, le=1.0)
    exploit_complexity_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    on_chain_damage_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    
    # Scoring thresholds
    critical_threshold: float = Field(default=9.0, ge=0.0, le=10.0)
    major_threshold: float = Field(default=7.0, ge=0.0, le=10.0)
    medium_threshold: float = Field(default=4.0, ge=0.0, le=10.0)

    class Config:
        env_prefix = "SCORING_"


class AgentConfig(BaseSettings):
    """Agentic AI configuration"""
    enable_detection_agent: bool = Field(default=True, description="Enable detection agent")
    enable_exploit_agent: bool = Field(default=False, description="Enable exploit simulation agent")
    enable_patch_agent: bool = Field(default=False, description="Enable patch suggestion agent")
    enable_verification_agent: bool = Field(default=False, description="Enable patch verification agent")
    
    # LLM settings
    llm_model: str = Field(default="gpt-4", description="LLM model to use")
    llm_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=2000, gt=0)
    
    # Agent coordination
    consensus_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    max_agent_retries: int = Field(default=3, ge=0)
    agent_timeout: int = Field(default=300, gt=0)

    class Config:
        env_prefix = "AGENT_"


class AuditConfig(BaseSettings):
    """Main configuration class combining all subsystems"""
    
    # Core settings
    log_level: str = Field(default="INFO", description="Logging level")
    max_analysis_time: int = Field(default=1800, description="Global analysis timeout")
    enable_parallel_execution: bool = Field(default=True, description="Enable parallel analysis")
    
    # Feature flags
    enable_agentic_ai: bool = Field(default=False, description="Enable agentic AI features")
    enable_hitl: bool = Field(default=False, description="Enable human-in-the-loop")
    enable_explainability: bool = Field(default=False, description="Enable explainability features")
    enable_rl_feedback: bool = Field(default=False, description="Enable RL feedback collection")
    
    # Subsystem configurations
    static_analysis: StaticAnalysisConfig = Field(default_factory=StaticAnalysisConfig)
    dynamic_analysis: DynamicAnalysisConfig = Field(default_factory=DynamicAnalysisConfig)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    agents: AgentConfig = Field(default_factory=AgentConfig)
    
    # Storage and output
    output_format: str = Field(default="json", description="Output format")
    save_intermediate_results: bool = Field(default=False, description="Save intermediate analysis results")
    results_directory: str = Field(default="./results", description="Results output directory")

    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()

    class Config:
        env_prefix = "AUDIT_"
        env_file = ".env"
        case_sensitive = False

    @classmethod
    def from_file(cls, config_path: str) -> 'AuditConfig':
        """Load configuration from file"""
        # TODO: Implement YAML/JSON config file loading
        return cls()

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Convert to dictionary with nested configs"""
        return super().dict(**kwargs)
