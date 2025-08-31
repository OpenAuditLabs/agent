"""
Core Audit Engine Orchestrator

Main engine that coordinates static analysis, dynamic analysis, scoring,
and agentic AI components as defined in the research paper and workflow.
Implements Phase 2-5 coordination with Phase 6+ hooks for HITL and RL.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .schemas import (
    AnalysisRequest, AnalysisResult, Finding, ToolError, 
    SeverityLevel, ConfidenceLevel, AgentTask, AgentResult
)
from .config import AuditConfig
from ..static_analysis.base import AbstractAdapter as StaticAdapter
from ..dynamic_analysis import run_dynamic_analysis, DynamicAnalysisOrchestrator
from ..scoring.scoring_engine import ScoringEngine
from ..utils.logger import get_logger
from ..utils.file_handler import ContractFileHandler


class AuditEngine:
    """
    Main orchestrator implementing the agentic AI framework architecture.
    Coordinates multi-phase analysis pipeline with consensus mechanisms.
    """
    
    def __init__(self, config: Optional[AuditConfig] = None):
        self.config = config or AuditConfig()
        self.logger = get_logger(__name__, self.config.log_level)
        
        # Initialize components
        self.file_handler = ContractFileHandler()
        self.scoring_engine = ScoringEngine(config=self.config.scoring)
        
        # Phase 2: Analysis tool adapters (lazy-loaded)
        self._static_adapters: Optional[List[StaticAdapter]] = None
        self._dynamic_orchestrator: Optional[DynamicAnalysisOrchestrator] = None
        
        # Phase 5: Agentic AI components (future integration)
        self._agent_orchestrator = None
        self.enable_agents = self.config.enable_agentic_ai
        
        # Phase 6: HITL and explainability hooks
        self.enable_hitl = self.config.enable_hitl
        self.enable_explainability = self.config.enable_explainability
        
        # Phase 7: RL feedback integration
        self.enable_rl_feedback = self.config.enable_rl_feedback
        
        self.logger.info(f"AuditEngine initialized with config: {self.config.dict()}")
    
    @property
    def static_adapters(self) -> List[StaticAdapter]:
        """Lazy-load static analysis adapters"""
        if self._static_adapters is None:
            self._static_adapters = self._initialize_static_adapters()
        return self._static_adapters
    
    @property 
    def dynamic_orchestrator(self) -> DynamicAnalysisOrchestrator:
        """Lazy-load dynamic analysis orchestrator"""
        if self._dynamic_orchestrator is None:
            self._dynamic_orchestrator = DynamicAnalysisOrchestrator(
                config=self.config.dynamic_analysis,
                logger=self.logger
            )
        return self._dynamic_orchestrator
    
    def _initialize_static_adapters(self) -> List[StaticAdapter]:
        """Initialize static analysis tool adapters"""
        adapters = []
        
        try:
            # Import adapters dynamically to avoid hard dependencies
            if self.config.static_analysis.get("enable_slither", True):
                from ..static_analysis.slither_adapter import SlitherAdapter
                adapters.append(SlitherAdapter(
                    config=self.config.static_analysis.get("slither", {}),
                    logger=self.logger
                ))
            
            if self.config.static_analysis.get("enable_mythril", True):
                from ..static_analysis.mythril_adapter import MythrilAdapter
                adapters.append(MythrilAdapter(
                    config=self.config.static_analysis.get("mythril", {}),
                    logger=self.logger
                ))
            
            if self.config.static_analysis.get("enable_manticore", False):
                from ..static_analysis.manticore_adapter import ManticoreAdapter
                adapters.append(ManticoreAdapter(
                    config=self.config.static_analysis.get("manticore", {}),
                    logger=self.logger
                ))
                
        except ImportError as e:
            self.logger.warning(f"Failed to import static analysis adapter: {e}")
        
        self.logger.info(f"Initialized {len(adapters)} static analysis adapters")
        return adapters
    
    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Main analysis entry point implementing multi-phase workflow.
        Coordinates static, dynamic, scoring, and agentic components.
        """
        self.logger.info(f"Starting analysis for {len(request.contract_paths)} contracts")
        
        # Initialize result object
        result = AnalysisResult(contract_paths=request.contract_paths)
        
        try:
            # Phase 1: File validation and preprocessing
            validated_paths = await self._validate_contracts(request.contract_paths)
            
            # Phase 2: Static and Dynamic Analysis (parallel execution)
            static_findings, dynamic_findings, tool_errors = await self._run_analysis_phase(
                validated_paths, request
            )
            
            # Combine findings
            all_findings = static_findings + dynamic_findings
            result.findings = all_findings
            result.tool_errors = tool_errors
            
            # Phase 3: Vulnerability Scoring
            if request.include_scoring:
                await self._apply_scoring(result.findings)
            
            # Phase 5: Multi-Agent Orchestration (if enabled)
            if request.enable_ai_agents and self.enable_agents:
                agent_results = await self._run_agent_orchestration(result, request)
                result.agent_consensus = agent_results.get("consensus")
                result.patch_suggestions = agent_results.get("patches")
            
            # Phase 6: Explainability Analysis (if enabled)
            if self.enable_explainability:
                result.explainability_report = await self._generate_explainability_report(result)
            
            # Phase 7: RL Feedback Collection (if enabled)
            if self.enable_rl_feedback:
                await self._collect_rl_feedback(result, request)
            
            # Finalize result statistics
            result.finalize()
            
            self.logger.info(
                f"Analysis completed: {result.total_findings} findings, "
                f"{len(result.tool_errors)} errors, {result.duration_seconds:.2f}s"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}", exc_info=True)
            result.tool_errors.append(ToolError(
                tool_name="AuditEngine",
                error_type="AnalysisError",
                error_message=str(e)
            ))
            result.finalize()
            return result
    
    async def _validate_contracts(self, contract_paths: List[str]) -> List[str]:
        """Validate and normalize contract file paths"""
        validated = []
        
        for path_str in contract_paths:
            path = Path(path_str)
            
            if not path.exists():
                raise FileNotFoundError(f"Contract file not found: {path}")
            
            if not path.is_file():
                raise ValueError(f"Path is not a file: {path}")
            
            if not self.file_handler.is_supported_contract(path):
                raise ValueError(f"Unsupported contract file type: {path}")
            
            validated.append(str(path.resolve()))
        
        self.logger.debug(f"Validated {len(validated)} contract files")
        return validated
    
    async def _run_analysis_phase(
        self, 
        contract_paths: List[str], 
        request: AnalysisRequest
    ) -> tuple[List[Finding], List[Finding], List[ToolError]]:
        """
        Run static and dynamic analysis in parallel.
        Implements Phase 2 workflow with error handling and timeout.
        """
        static_findings = []
        dynamic_findings = []
        tool_errors = []
        
        # Create analysis tasks
        tasks = []
        
        if request.include_static:
            tasks.append(self._run_static_analysis(contract_paths, request))
        
        if request.include_dynamic:
            tasks.append(self._run_dynamic_analysis(contract_paths, request))
        
        if not tasks:
            self.logger.warning("No analysis methods enabled")
            return static_findings, dynamic_findings, tool_errors
        
        # Execute analysis phases in parallel
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_source = "static" if i == 0 and request.include_static else "dynamic"
                    self.logger.error(f"{error_source} analysis failed: {result}")
                    tool_errors.append(ToolError(
                        tool_name=f"{error_source}_analysis",
                        error_type=type(result).__name__,
                        error_message=str(result)
                    ))
                else:
                    findings, errors = result
                    if i == 0 and request.include_static:
                        static_findings = findings
                    else:
                        dynamic_findings = findings
                    tool_errors.extend(errors)
        
        except Exception as e:
            self.logger.error(f"Analysis phase execution failed: {e}")
            tool_errors.append(ToolError(
                tool_name="analysis_orchestrator",
                error_type="ExecutionError",
                error_message=str(e)
            ))
        
        return static_findings, dynamic_findings, tool_errors
    
    async def _run_static_analysis(
        self, 
        contract_paths: List[str], 
        request: AnalysisRequest
    ) -> tuple[List[Finding], List[ToolError]]:
        """Execute static analysis tools with parallel execution"""
        findings = []
        errors = []
        
        if not self.static_adapters:
            self.logger.warning("No static analysis adapters available")
            return findings, errors
        
        # Run adapters in parallel with timeout
        with ThreadPoolExecutor(max_workers=len(self.static_adapters)) as executor:
            futures = []
            
            for adapter in self.static_adapters:
                for contract_path in contract_paths:
                    future = executor.submit(self._run_static_adapter, adapter, contract_path)
                    futures.append((adapter, future))
            
            # Collect results with timeout
            for adapter, future in futures:
                try:
                    adapter_findings = future.result(timeout=request.max_analysis_time)
                    findings.extend(adapter_findings)
                except Exception as e:
                    self.logger.error(f"Static adapter {adapter.__class__.__name__} failed: {e}")
                    errors.append(ToolError(
                        tool_name=adapter.__class__.__name__,
                        error_type=type(e).__name__,
                        error_message=str(e)
                    ))
        
        self.logger.info(f"Static analysis completed: {len(findings)} findings, {len(errors)} errors")
        return findings, errors
    
    def _run_static_adapter(self, adapter: StaticAdapter, contract_path: str) -> List[Finding]:
        """Run individual static analysis adapter"""
        try:
            raw_results = adapter.run(contract_path)
            return self._normalize_static_findings(adapter, raw_results)
        except Exception as e:
            self.logger.error(f"Static adapter {adapter.__class__.__name__} failed on {contract_path}: {e}")
            raise
    
    def _normalize_static_findings(self, adapter: StaticAdapter, raw_results: List[Any]) -> List[Finding]:
        """Normalize static analysis results to Finding schema"""
        findings = []
        
        for result in raw_results:
            try:
                # Convert tool-specific output to Finding schema
                finding = self._convert_to_finding(adapter.__class__.__name__, result)
                findings.append(finding)
            except Exception as e:
                self.logger.warning(f"Failed to normalize finding from {adapter.__class__.__name__}: {e}")
        
        return findings
    
    async def _run_dynamic_analysis(
        self,
        contract_paths: List[str], 
        request: AnalysisRequest
    ) -> tuple[List[Finding], List[ToolError]]:
        """Execute dynamic analysis through orchestrator"""
        try:
            analysis_results = await self.dynamic_orchestrator.analyze_contracts(
                contract_paths, 
                analysis_type=request.analysis_type
            )
            
            # Convert AnalysisResult objects to Finding objects
            findings = []
            for result in analysis_results:
                finding = Finding(
                    swc_id=result.finding_details.get("swc_id"),
                    severity=self._map_severity(result.severity),
                    tool_name=result.tool_name,
                    tool_version="1.0.0",  # TODO: Get actual version
                    file_path=contract_paths[0],  # TODO: Extract from result
                    description=result.vulnerability_type,
                    reproduction_steps=str(result.finding_details),
                    confidence=self._confidence_to_float(result.confidence),
                    recommendations=result.remediation_suggestion.split('\n') if result.remediation_suggestion else [],
                    cross_chain_impact=result.cross_chain_impact
                )
                findings.append(finding)
            
            self.logger.info(f"Dynamic analysis completed: {len(findings)} findings")
            return findings, []  # Dynamic orchestrator handles errors internally
            
        except Exception as e:
            self.logger.error(f"Dynamic analysis failed: {e}")
            return [], [ToolError(
                tool_name="dynamic_analysis",
                error_type=type(e).__name__,
                error_message=str(e)
            )]
    
    def _convert_to_finding(self, tool_name: str, raw_result: Any) -> Finding:
        """Convert tool-specific result to standardized Finding"""
        # Handle dict results (most common)
        if isinstance(raw_result, dict):
            return Finding(
                swc_id=raw_result.get("swc_id"),
                severity=self._map_severity(raw_result.get("severity", "Medium")),
                tool_name=tool_name,
                tool_version=raw_result.get("tool_version", "1.0.0"),
                file_path=raw_result.get("file_path", "unknown"),
                line_span=None,  # TODO: Parse line numbers
                function_name=raw_result.get("function_name"),
                description=raw_result.get("description", "No description"),
                reproduction_steps=raw_result.get("reproduction_steps", "No steps provided"),
                confidence=float(raw_result.get("confidence", 0.5)),
                recommendations=raw_result.get("recommendations", [])
            )
        
        # Handle object results
        return Finding(
            swc_id=getattr(raw_result, "swc_id", None),
            severity=self._map_severity(getattr(raw_result, "severity", "Medium")),
            tool_name=tool_name,
            tool_version="1.0.0",
            file_path=getattr(raw_result, "file_path", "unknown"),
            description=getattr(raw_result, "description", str(raw_result)),
            reproduction_steps=getattr(raw_result, "reproduction_steps", "No steps provided"),
            confidence=float(getattr(raw_result, "confidence", 0.5))
        )
    
    def _map_severity(self, severity: str) -> SeverityLevel:
        """Map tool severity strings to standardized SeverityLevel"""
        severity_map = {
            "critical": SeverityLevel.CRITICAL,
            "high": SeverityLevel.CRITICAL,
            "major": SeverityLevel.MAJOR,
            "medium": SeverityLevel.MEDIUM,
            "low": SeverityLevel.MINOR,
            "minor": SeverityLevel.MINOR,
            "informational": SeverityLevel.INFORMATIONAL,
            "info": SeverityLevel.INFORMATIONAL
        }
        return severity_map.get(str(severity).lower(), SeverityLevel.MEDIUM)
    
    def _confidence_to_float(self, confidence) -> float:
        """Convert confidence enum to float value"""
        if isinstance(confidence, str):
            confidence_map = {
                "critical": 0.97,
                "high": 0.9, 
                "medium": 0.7,
                "low": 0.4
            }
            return confidence_map.get(confidence.lower(), 0.5)
        return float(confidence) if confidence else 0.5
    
    async def _apply_scoring(self, findings: List[Finding]) -> None:
        """Apply CVSS-inspired scoring to findings"""
        try:
            for finding in findings:
                score = self.scoring_engine.calculate_score(finding)
                finding.explainability_trace = {"cvss_score": score}
            
            self.logger.info(f"Applied scoring to {len(findings)} findings")
        except Exception as e:
            self.logger.error(f"Scoring failed: {e}")
    
    async def _run_agent_orchestration(
        self, 
        result: AnalysisResult, 
        request: AnalysisRequest
    ) -> Dict[str, Any]:
        """Phase 5: Multi-agent orchestration (placeholder for future implementation)"""
        # TODO: Implement full agentic AI orchestration
        self.logger.info("Agent orchestration not yet implemented")
        return {
            "consensus": {"status": "not_implemented"},
            "patches": []
        }
    
    async def _generate_explainability_report(self, result: AnalysisResult) -> Dict[str, Any]:
        """Phase 6: Generate explainability report (placeholder)"""
        # TODO: Implement explainability module
        return {
            "analysis_trace": "explainability_not_implemented",
            "decision_paths": [],
            "confidence_analysis": {}
        }
    
    async def _collect_rl_feedback(self, result: AnalysisResult, request: AnalysisRequest) -> None:
        """Phase 7: Collect reinforcement learning feedback (placeholder)"""
        # TODO: Implement RL feedback collection
        self.logger.debug("RL feedback collection not yet implemented")
        return adapters
