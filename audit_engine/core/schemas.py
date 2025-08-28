"""
Unified Pydantic schemas for OpenAudit Agent

Implements the standardized JSON schema from Workflow.md Section 3.1
for consistent data contracts across all analysis phases.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator


class SeverityLevel(str, Enum):
    """Severity classification as per Workflow.md interim calibration"""
    CRITICAL = "Critical"      # Direct fund loss, contract takeover
    MAJOR = "Major"           # Service disruption, governance bypass  
    MEDIUM = "Medium"         # Logic errors, privilege escalation
    MINOR = "Minor"           # Best practice violations
    INFORMATIONAL = "Informational"  # Code quality issues


class ExploitComplexity(str, Enum):
    """Exploit complexity classification"""
    LOW = "Low"
    MEDIUM = "Medium" 
    HIGH = "High"


class ConfidenceLevel(str, Enum):
    """Trust calibration levels for HITL integration"""
    LOW = "low"           # Requires human review
    MEDIUM = "medium"     # Automated with flagging
    HIGH = "high"         # Fully automated
    CRITICAL = "critical" # Immediate escalation


class LineSpan(BaseModel):
    """Source code line span for vulnerability location"""
    start: int = Field(..., description="Starting line number (1-indexed)")
    end: int = Field(..., description="Ending line number (1-indexed)")
    
    @validator('end')
    def end_must_be_gte_start(cls, v, values):
        if 'start' in values and v < values['start']:
            raise ValueError('end line must be >= start line')
        return v


class Finding(BaseModel):
    """
    Standardized vulnerability finding schema implementing Workflow.md requirements.
    Used across all analysis phases for consistent data exchange.
    """
    finding_id: UUID = Field(default_factory=uuid4, description="Unique finding identifier")
    swc_id: Optional[str] = Field(None, regex=r"SWC-\d{3}", description="SWC registry ID (SWC-XXX format)")
    severity: SeverityLevel = Field(..., description="Vulnerability severity level")
    tool_name: str = Field(..., description="Analysis tool that generated finding")
    tool_version: str = Field(..., description="Version of analysis tool")
    file_path: str = Field(..., description="Path to vulnerable source file")
    line_span: Optional[LineSpan] = Field(None, description="Source code line range")
    function_name: Optional[str] = Field(None, description="Function containing vulnerability")
    bytecode_offset: Optional[int] = Field(None, description="Bytecode offset for EVM-level findings")
    description: str = Field(..., description="Human-readable vulnerability description")
    reproduction_steps: str = Field(..., description="Steps to reproduce the vulnerability")
    proof_of_concept: Optional[str] = Field(None, description="Executable proof of concept code")
    exploit_complexity: ExploitComplexity = Field(default=ExploitComplexity.MEDIUM, description="Difficulty of exploitation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Tool confidence in finding (0.0-1.0)")
    sanitizer_present: bool = Field(default=False, description="Whether security controls are present")
    recommendations: List[str] = Field(default_factory=list, description="Remediation recommendations")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Finding generation timestamp")
    
    # Extended fields for agentic AI integration
    cross_chain_impact: Optional[List[str]] = Field(None, description="Affected blockchain networks")
    remediation_suggestion: Optional[str] = Field(None, description="AI-generated patch suggestion")
    explainability_trace: Optional[Dict[str, Any]] = Field(None, description="Decision trace for explainability")
    rl_feedback_score: Optional[float] = Field(None, description="Reinforcement learning feedback score")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ToolError(BaseModel):
    """Error information when analysis tools fail"""
    tool_name: str
    error_type: str
    error_message: str
    stderr_output: Optional[str] = None
    exit_code: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AnalysisRequest(BaseModel):
    """Request schema for audit analysis"""
    contract_paths: List[str] = Field(..., description="Paths to smart contract files")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis to perform")
    include_static: bool = Field(default=True, description="Enable static analysis")
    include_dynamic: bool = Field(default=True, description="Enable dynamic analysis") 
    include_scoring: bool = Field(default=True, description="Enable vulnerability scoring")
    enable_ai_agents: bool = Field(default=False, description="Enable agentic AI features")
    cross_chain_analysis: bool = Field(default=False, description="Enable cross-chain vulnerability detection")
    max_analysis_time: int = Field(default=600, description="Maximum analysis time in seconds")
    
    # Configuration overrides
    tool_config: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific configuration")
    agent_config: Dict[str, Any] = Field(default_factory=dict, description="AI agent configuration")


class AnalysisResult(BaseModel):
    """Complete analysis result with findings and metadata"""
    request_id: UUID = Field(default_factory=uuid4, description="Analysis request identifier")
    contract_paths: List[str] = Field(..., description="Analyzed contract files")
    findings: List[Finding] = Field(default_factory=list, description="Detected vulnerabilities")
    tool_errors: List[ToolError] = Field(default_factory=list, description="Tool execution errors")
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict, description="Analysis execution metadata")
    
    # Summary statistics
    total_findings: int = Field(default=0, description="Total number of findings")
    severity_distribution: Dict[SeverityLevel, int] = Field(default_factory=dict, description="Findings by severity")
    confidence_distribution: Dict[ConfidenceLevel, int] = Field(default_factory=dict, description="Findings by confidence")
    
    # Timing information
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Analysis start time")
    end_time: Optional[datetime] = Field(None, description="Analysis completion time")
    duration_seconds: Optional[float] = Field(None, description="Total analysis duration")
    
    # Agentic AI results
    agent_consensus: Optional[Dict[str, Any]] = Field(None, description="Multi-agent consensus results")
    patch_suggestions: Optional[List[Dict[str, Any]]] = Field(None, description="AI-generated patches")
    explainability_report: Optional[Dict[str, Any]] = Field(None, description="Explainability analysis")

    def finalize(self):
        """Compute derived fields after analysis completion"""
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        self.total_findings = len(self.findings)
        
        # Compute severity distribution
        self.severity_distribution = {}
        for severity in SeverityLevel:
            count = sum(1 for f in self.findings if f.severity == severity)
            if count > 0:
                self.severity_distribution[severity] = count

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class AgentTask(BaseModel):
    """Task specification for agentic AI agents"""
    task_id: UUID = Field(default_factory=uuid4)
    agent_type: str = Field(..., description="Type of agent (detection, exploit, patch, verification)")
    input_data: Dict[str, Any] = Field(..., description="Input data for agent")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific configuration")
    priority: int = Field(default=5, ge=1, le=10, description="Task priority (1=highest, 10=lowest)")
    timeout_seconds: int = Field(default=300, description="Task timeout")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")


class AgentResult(BaseModel):
    """Result from agentic AI agent execution"""
    task_id: UUID = Field(..., description="Reference to original task")
    agent_type: str = Field(..., description="Agent that produced result")
    success: bool = Field(..., description="Whether task completed successfully")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Agent output")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Agent confidence in result")
    execution_time: float = Field(..., description="Task execution time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if task failed")
    explainability_trace: Optional[List[str]] = Field(None, description="Decision trace for explainability")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Utility type aliases for cleaner code
FindingList = List[Finding]
ToolErrorList = List[ToolError]
AnalysisConfig = Dict[str, Any]
