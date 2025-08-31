"""
Core module for OpenAudit Agent

Main orchestration engine implementing the agentic AI framework
for smart contract vulnerability detection and mitigation.
"""

from .engine import AuditEngine
from .config import AuditConfig, StaticAnalysisConfig, ScoringConfig, AgentConfig
from ..dynamic_analysis.config import DynamicAnalysisConfig
from .schemas import (
    Finding, AnalysisRequest, AnalysisResult, ToolError,
    SeverityLevel, ConfidenceLevel, ExploitComplexity,
    AgentTask, AgentResult, LineSpan
)

__all__ = [
    # Main engine
    "AuditEngine",
    
    # Configuration
    "AuditConfig", 
    "StaticAnalysisConfig",
    "DynamicAnalysisConfig", 
    "ScoringConfig",
    "AgentConfig",
    
    # Schemas
    "Finding",
    "AnalysisRequest", 
    "AnalysisResult",
    "ToolError",
    "SeverityLevel",
    "ConfidenceLevel", 
    "ExploitComplexity",
    "AgentTask",
    "AgentResult",
    "LineSpan",
]

# Version info
__version__ = "0.1.0"
__author__ = "OpenAudit Labs"
__description__ = "Agentic AI Smart Contract Security Analysis Engine"
