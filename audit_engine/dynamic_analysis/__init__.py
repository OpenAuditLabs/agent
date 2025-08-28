"""
Dynamic Analysis Module for OpenAudit Agent

This module implements the dynamic analysis component of the agentic AI framework
described in the research paper. It orchestrates multiple dynamic analysis tools
including Echidna fuzzing and AdversarialFuzz techniques to detect runtime
vulnerabilities in smart contracts.

Key Features:
- Multi-tool dynamic analysis orchestration
- Adversarial fuzzing capabilities (Rahman et al., 2025)
- Reinforcement learning integration for continuous improvement
- Cross-chain vulnerability detection support
- Trust-calibrated output with confidence scoring
"""

from typing import List, Dict, Any, Optional, Iterable, Union
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from .echidna_adapter import EchidnaAdapter
from .adversarial_fuzz import AdversarialFuzz

__all__ = [
    "DynamicAnalysisOrchestrator",
    "AnalysisResult", 
    "ConfidenceLevel",
    "EchidnaAdapter", 
    "AdversarialFuzz",
    "run_dynamic_analysis"
]

class ConfidenceLevel(Enum):
    """Trust calibration levels for HITL integration as per research paper Section 5.5"""
    LOW = "low"           # Requires human review
    MEDIUM = "medium"     # Automated with flagging
    HIGH = "high"         # Fully automated
    CRITICAL = "critical" # Immediate escalation

@dataclass
class AnalysisResult:
    """
    Standardized result format for dynamic analysis findings.
    Implements trust scoring and explainability features from the research.
    """
    tool_name: str
    vulnerability_type: str
    severity: str
    confidence: ConfidenceLevel
    finding_details: Dict[str, Any]
    exploit_poc: Optional[str] = None
    remediation_suggestion: Optional[str] = None
    cross_chain_impact: Optional[List[str]] = None
    timestamp: Optional[str] = None

class DynamicAnalysisOrchestrator:
    """
    Main orchestrator for dynamic analysis tools implementing the agentic AI
    framework from the research paper. Coordinates multiple analysis agents
    with reinforcement learning feedback loops.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, logger: Optional[logging.Logger] = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.adapters = self._initialize_adapters()
        self.rl_feedback_enabled = self.config.get("reinforcement_learning", False)
        self.cross_chain_enabled = self.config.get("cross_chain_analysis", False)
        
    def _initialize_adapters(self) -> List[Any]:
        """Initialize dynamic analysis adapters with configuration"""
        adapters = []
        
        try:
            # Standard Echidna fuzzing
            if self.config.get("enable_echidna", True):
                echidna_config = self.config.get("echidna", {})
                adapters.append(EchidnaAdapter(config=echidna_config, logger=self.logger))
            
            # Adversarial fuzzing as per Rahman et al. (2025)
            if self.config.get("enable_adversarial_fuzz", True):
                adversarial_config = self.config.get("adversarial_fuzz", {})
                adapters.append(AdversarialFuzz(config=adversarial_config, logger=self.logger))
                
        except Exception as e:
            self.logger.error(f"Failed to initialize dynamic analysis adapters: {e}")
            raise
            
        return adapters
    
    async def analyze_contracts(
        self, 
        contract_paths: Iterable[str],
        analysis_type: str = "comprehensive"
    ) -> List[AnalysisResult]:
        """
        Asynchronous multi-agent analysis with consensus-based decision making
        as described in Section 5.10 of the research paper.
        """
        results = []
        
        # Parallel execution of multiple analysis agents
        with ThreadPoolExecutor(max_workers=len(self.adapters)) as executor:
            futures = []
            
            for adapter in self.adapters:
                future = executor.submit(self._run_adapter_analysis, adapter, contract_paths)
                futures.append((adapter, future))
            
            # Collect results with timeout handling
            for adapter, future in futures:
                try:
                    adapter_results = future.result(timeout=self.config.get("analysis_timeout", 600))
                    processed_results = self._process_adapter_results(adapter, adapter_results)
                    results.extend(processed_results)
                except Exception as e:
                    self.logger.error(f"Adapter {adapter.__class__.__name__} failed: {e}")
                    continue
        
        # Apply consensus scoring and multi-agent coordination
        consensus_results = self._apply_consensus_scoring(results)
        
        # Reinforcement learning feedback integration
        if self.rl_feedback_enabled:
            await self._update_rl_feedback(consensus_results)
        
        return consensus_results
    
    def _run_adapter_analysis(self, adapter: Any, contract_paths: Iterable[str]) -> List[Any]:
        """Run individual adapter analysis with error handling"""
        try:
            return adapter.run(contract_paths)
        except Exception as e:
            self.logger.error(f"Analysis failed for {adapter.__class__.__name__}: {e}")
            return []
    
    def _process_adapter_results(self, adapter: Any, raw_results: List[Any]) -> List[AnalysisResult]:
        """
        Process and standardize adapter results into unified format.
        Implements trust calibration and explainability features.
        """
        processed = []
        
        for result in raw_results:
            try:
                # Extract standard fields
                vuln_type = getattr(result, 'vulnerability_type', 'unknown')
                severity = getattr(result, 'severity', 'medium')
                details = getattr(result, 'details', {})
                
                # Calculate confidence level using trust calibration
                confidence = self._calculate_confidence_level(adapter, result)
                
                # Generate remediation suggestions if applicable
                remediation = self._generate_remediation_suggestion(result)
                
                # Cross-chain impact analysis (Section 5.6)
                cross_chain_impact = None
                if self.cross_chain_enabled:
                    cross_chain_impact = self._analyze_cross_chain_impact(result)
                
                analysis_result = AnalysisResult(
                    tool_name=adapter.__class__.__name__,
                    vulnerability_type=vuln_type,
                    severity=severity,
                    confidence=confidence,
                    finding_details=details,
                    remediation_suggestion=remediation,
                    cross_chain_impact=cross_chain_impact
                )
                
                processed.append(analysis_result)
                
            except Exception as e:
                self.logger.warning(f"Failed to process result from {adapter.__class__.__name__}: {e}")
                continue
                
        return processed
    
    def _calculate_confidence_level(self, adapter: Any, result: Any) -> ConfidenceLevel:
        """
        Implement trust calibration as described in Section 5.5.
        Uses multi-modal consistency checks and historical accuracy.
        """
        # Default confidence scoring logic
        confidence_score = getattr(result, 'confidence_score', 0.5)
        
        # Adjust based on tool reliability
        if isinstance(adapter, AdversarialFuzz):
            confidence_score *= 1.2  # Higher weight for adversarial findings
        
        # Historical accuracy adjustment (would be loaded from training data)
        tool_accuracy = self.config.get(f"{adapter.__class__.__name__}_accuracy", 0.8)
        adjusted_score = confidence_score * tool_accuracy
        
        # Map to confidence levels
        if adjusted_score >= 0.9:
            return ConfidenceLevel.HIGH
        elif adjusted_score >= 0.7:
            return ConfidenceLevel.MEDIUM
        elif adjusted_score >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.CRITICAL
    
    def _generate_remediation_suggestion(self, result: Any) -> Optional[str]:
        """Generate actionable remediation suggestions"""
        # Placeholder for LLM-based remediation generation
        # Would integrate with GPT-4 or fine-tuned models as per research
        vuln_type = getattr(result, 'vulnerability_type', '')
        
        remediation_templates = {
            'reentrancy': 'Consider using the checks-effects-interactions pattern or ReentrancyGuard modifier',
            'integer_overflow': 'Use SafeMath library or Solidity 0.8+ built-in overflow protection',
            'unchecked_call': 'Always check return values of external calls and handle failures appropriately'
        }
        
        return remediation_templates.get(vuln_type.lower())
    
    def _analyze_cross_chain_impact(self, result: Any) -> Optional[List[str]]:
        """
        Cross-chain vulnerability analysis as per Section 5.6.
        Identifies vulnerabilities that may manifest differently across chains.
        """
        if not self.cross_chain_enabled:
            return None
        
        # Placeholder for cross-chain differential analysis
        # Would implement semantic diffing across EVM-compatible chains
        affected_chains = []
        
        vuln_type = getattr(result, 'vulnerability_type', '')
        if vuln_type in ['gas_limit', 'block_gas_limit']:
            affected_chains = ['ethereum', 'polygon', 'bsc']  # Different gas limits
        elif vuln_type in ['timestamp_dependence']:
            affected_chains = ['ethereum', 'arbitrum']  # Different block times
        
        return affected_chains if affected_chains else None
    
    def _apply_consensus_scoring(self, results: List[AnalysisResult]) -> List[AnalysisResult]:
        """
        Multi-agent consensus mechanism as described in Section 5.10.
        Aggregates findings from multiple tools to reduce false positives.
        """
        # Group results by vulnerability type and location
        grouped_results = {}
        
        for result in results:
            key = f"{result.vulnerability_type}_{hash(str(result.finding_details))}"
            if key not in grouped_results:
                grouped_results[key] = []
            grouped_results[key].append(result)
        
        consensus_results = []
        
        for group in grouped_results.values():
            if len(group) == 1:
                # Single detection - adjust confidence
                result = group[0]
                if result.confidence == ConfidenceLevel.HIGH:
                    result.confidence = ConfidenceLevel.MEDIUM
                consensus_results.append(result)
            else:
                # Multiple detections - increase confidence
                primary_result = max(group, key=lambda r: self._confidence_weight(r.confidence))
                primary_result.confidence = min(
                    ConfidenceLevel.HIGH, 
                    ConfidenceLevel(list(ConfidenceLevel)[
                        min(len(ConfidenceLevel) - 1, 
                            list(ConfidenceLevel).index(primary_result.confidence) + 1)
                    ])
                )
                
                # Merge finding details from all tools
                merged_details = primary_result.finding_details.copy()
                merged_details['consensus_tools'] = [r.tool_name for r in group]
                primary_result.finding_details = merged_details
                
                consensus_results.append(primary_result)
        
        return consensus_results
    
    def _confidence_weight(self, confidence: ConfidenceLevel) -> int:
        """Convert confidence level to numeric weight for comparison"""
        weights = {
            ConfidenceLevel.CRITICAL: 0,
            ConfidenceLevel.LOW: 1,
            ConfidenceLevel.MEDIUM: 2,
            ConfidenceLevel.HIGH: 3
        }
        return weights.get(confidence, 1)
    
    async def _update_rl_feedback(self, results: List[AnalysisResult]) -> None:
        """
        Reinforcement learning feedback loop as described in Section 5.4.
        Updates agent behavior based on analysis outcomes.
        """
        if not self.rl_feedback_enabled:
            return
        
        # Placeholder for RL feedback implementation
        # Would integrate with policy gradient methods or PPO
        feedback_data = {
            'analysis_timestamp': str(asyncio.get_event_loop().time()),
            'total_findings': len(results),
            'confidence_distribution': {
                level.value: sum(1 for r in results if r.confidence == level)
                for level in ConfidenceLevel
            },
            'tool_performance': {
                tool: sum(1 for r in results if r.tool_name == tool)
                for tool in set(r.tool_name for r in results)
            }
        }
        
        self.logger.info(f"RL Feedback collected: {feedback_data}")
        # TODO: Implement actual RL model updates

# Convenience function for backward compatibility and simple usage
def run_dynamic_analysis(
    contract_paths: Iterable[str],
    config: Optional[Dict[str, Any]] = None,
    logger: Optional[logging.Logger] = None,
    adapters: Optional[List[Any]] = None,
) -> List[AnalysisResult]:
    """
    Simplified interface for dynamic analysis execution.
    
    Args:
        contract_paths: Paths to smart contract files
        config: Configuration dictionary
        logger: Logger instance
        adapters: Pre-initialized adapters (for testing)
    
    Returns:
        List of standardized analysis results
    """
    if adapters:
        # Legacy mode for backward compatibility
        findings = []
        for adapter in adapters:
            try:
                result = adapter.run(contract_paths)
                if result:
                    findings.extend(result if isinstance(result, list) else [result])
            except Exception as e:
                if logger:
                    logger.error(f"Adapter {adapter.__class__.__name__} failed: {e}")
        return [
            AnalysisResult(
                tool_name="unknown",
                vulnerability_type="unknown", 
                severity="medium",
                confidence=ConfidenceLevel.MEDIUM,
                finding_details={"raw_finding": finding}
            ) for finding in findings
        ]
    
    # Modern agentic AI orchestration
    orchestrator = DynamicAnalysisOrchestrator(config=config, logger=logger)
    
    # Run synchronously for backward compatibility
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(orchestrator.analyze_contracts(contract_paths))
    except RuntimeError:
        # No event loop running
        return asyncio.run(orchestrator.analyze_contracts(contract_paths))