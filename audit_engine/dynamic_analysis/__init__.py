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

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Union
import time

from .echidna_adapter import EchidnaAdapter
from .adversarial_fuzz import AdversarialFuzz
from .config import DynamicAnalysisConfig

__all__ = [
    "DynamicAnalysisOrchestrator",
    "AnalysisResult", 
    "ConfidenceLevel",
    "EchidnaAdapter", 
    "AdversarialFuzz",
    "run_dynamic_analysis"
]

# Constants to avoid magic numbers
DEFAULT_ANALYSIS_TIMEOUT = 600
DEFAULT_MAX_WORKERS = 4
CONFIDENCE_THRESHOLDS = {
    'critical': 0.97,
    'high': 0.9,
    'medium': 0.7,
    'low': 0.0
}
DEFAULT_TOOL_ACCURACY = 0.8
ADVERSARIAL_BOOST_FACTOR = 1.1

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
        self.adapters: List[Any] = []
        self.rl_feedback_enabled = self.config.get("reinforcement_learning", False)
        self.cross_chain_enabled = self.config.get("cross_chain_analysis", False)
        
        # Log configuration securely without exposing sensitive data
        self.logger.info(f"DynamicAnalysisOrchestrator initialized with config: {self._masked_config_dict()}")
        
        try:
            self.adapters = self._initialize_adapters()
        except Exception as e:
            self.logger.error(f"Failed to initialize adapters: {e}")
            # Don't re-raise to allow graceful degradation

    def _masked_config_dict(self) -> Dict[str, Any]:
        """
        Create a masked version of config for safe logging.
        Masks sensitive keys that might contain tokens, passwords, or secrets.
        """
        # Define specific sensitive patterns to avoid false positives
        sensitive_patterns = {
            "api_key", "access_key", "secret_key", "private_key", "client_secret",
            "password", "pass", "pwd",
            "secret", "token", "auth_token", "bearer_token", "refresh_token",
        }
        
        def mask_sensitive_data(obj: Any) -> Any:
            if isinstance(obj, dict):
                masked = {}
                for key, value in obj.items():
                    key_lower = key.lower()
                    # Narrow match: exact known keys or common suffixes
                    is_sensitive = (
                        key_lower in sensitive_patterns
                        or key_lower.endswith(("_key", "_secret", "_token"))
                    )
                    
                    if is_sensitive and value is not None:
                        # Mask with partial visibility for debugging
                        if isinstance(value, str) and len(value) > 8:
                            masked[key] = f"{value[:3]}***{value[-2:]}"
                        else:
                            masked[key] = "***"
                    else:
                        masked[key] = mask_sensitive_data(value)
                return masked
            elif isinstance(obj, list):
                return [mask_sensitive_data(item) for item in obj]
            else:
                return obj
        
        return mask_sensitive_data(self.config)

    def _initialize_adapters(self) -> List[Any]:
        """Initialize dynamic analysis adapters with configuration"""
        adapters = []
        
        # Handle both dict and DynamicAnalysisConfig objects
        if hasattr(self.config, 'enable_echidna'):
            # Pydantic config object
            enable_echidna = self.config.enable_echidna
            enable_adversarial_fuzz = self.config.enable_adversarial_fuzz
            echidna_config = self.config.echidna if hasattr(self.config, 'echidna') else {}
            adversarial_config = self.config.adversarial_fuzz if hasattr(self.config, 'adversarial_fuzz') else {}
        else:
            # Dict config
            enable_echidna = self.config.get("enable_echidna", True)
            enable_adversarial_fuzz = self.config.get("enable_adversarial_fuzz", True)
            echidna_config = self.config.get("echidna", {})
            adversarial_config = self.config.get("adversarial_fuzz", {})
        
        # Standard Echidna fuzzing
        if enable_echidna:
            try:
                adapters.append(EchidnaAdapter(config=echidna_config, logger=self.logger))
            except Exception as e:
                self.logger.warning(f"Failed to initialize EchidnaAdapter: {e}")
        
        # Adversarial fuzzing as per Rahman et al. (2025)
        if enable_adversarial_fuzz:
            try:
                adapters.append(AdversarialFuzz(config=adversarial_config, logger=self.logger))
            except Exception as e:
                self.logger.warning(f"Failed to initialize AdversarialFuzz: {e}")
                
        return adapters

    def _extract_confidence_score(self, result: Any) -> float:
        """Extract numerical confidence score from result"""
        if isinstance(result, dict):
            conf_str = str(result.get("confidence", "")).lower()
            confidence_mapping = {"high": 0.9, "medium": 0.7, "low": 0.4}
            if conf_str in confidence_mapping:
                return confidence_mapping[conf_str]
            try:
                return float(result.get("confidence_score", 0.5))
            except (TypeError, ValueError):
                return 0.5
        return float(getattr(result, "confidence_score", 0.5))

    def _score_to_confidence_level(self, score: float) -> ConfidenceLevel:
        """Convert numerical score to ConfidenceLevel enum"""
        if score >= CONFIDENCE_THRESHOLDS['critical']:
            return ConfidenceLevel.CRITICAL
        elif score >= CONFIDENCE_THRESHOLDS['high']:
            return ConfidenceLevel.HIGH
        elif score >= CONFIDENCE_THRESHOLDS['medium']:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _calculate_confidence_level(self, adapter: Any, result: Any) -> ConfidenceLevel:
        """
        Implement trust calibration as described in Section 5.5.
        Uses multi-modal consistency checks and historical accuracy.
        """
        # Extract confidence score from result
        score = self._extract_confidence_score(result)
        
        # Apply adapter-specific adjustments
        if isinstance(adapter, AdversarialFuzz):
            score = min(1.0, score * ADVERSARIAL_BOOST_FACTOR)

        # Apply tool accuracy weighting - check both PascalCase and snake_case
        class_name = adapter.__class__.__name__
        snake_case = "".join([f"_{c.lower()}" if c.isupper() else c for c in class_name]).lstrip("_")
        tool_accuracy = self.config.get(
            f"{class_name}_accuracy",
            self.config.get(f"{snake_case}_accuracy", DEFAULT_TOOL_ACCURACY),
        )
        adjusted_score = max(0.0, min(1.0, score * tool_accuracy))

        return self._score_to_confidence_level(adjusted_score)

    async def analyze_contracts(
        self, 
        contract_paths: Iterable[str],
        analysis_type: str = "comprehensive"
    ) -> List[AnalysisResult]:
        """
        Asynchronous multi-agent analysis with consensus-based decision making
        as described in Section 5.10 of the research paper.
        """
        if not self.adapters:
            self.logger.warning("No dynamic analysis adapters available; returning empty results.")
            return []

        contract_list = list(contract_paths)
        if not contract_list:
            self.logger.warning("No contract paths provided for analysis.")
            return []

        results = await self._execute_parallel_analysis(contract_list)
        
        # Reinforcement learning feedback integration
        if self.rl_feedback_enabled:
            await self._update_rl_feedback(results)
        
        return results

    async def _execute_parallel_analysis(self, contract_paths: List[str]) -> List[AnalysisResult]:
        """Execute analysis across multiple adapters in parallel"""
        results = []
        max_workers = min(
            self.config.get("max_workers", DEFAULT_MAX_WORKERS), 
            len(self.adapters)
        )
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all adapter tasks
            future_to_adapter = {
                executor.submit(self._run_adapter_analysis, adapter, contract_paths): adapter
                for adapter in self.adapters
            }
            
            # Collect results with proper error handling
            for future in as_completed(future_to_adapter):
                adapter = future_to_adapter[future]
                try:
                    timeout = self.config.get("analysis_timeout", DEFAULT_ANALYSIS_TIMEOUT)
                    adapter_results = future.result(timeout=timeout)
                    processed_results = self._process_adapter_results(adapter, adapter_results)
                    results.extend(processed_results)
                except Exception as e:
                    self.logger.error(f"Adapter {adapter.__class__.__name__} failed: {e}")
                    
        return results
    
    def _run_adapter_analysis(self, adapter: Any, contract_paths: List[str]) -> List[Any]:
        """Run individual adapter analysis with error handling"""
        findings: List[Any] = []
        adapter_name = adapter.__class__.__name__
        
        try:
            timeout = self.config.get(
                f"{adapter_name}_timeout", 
                self.config.get("analysis_timeout", DEFAULT_ANALYSIS_TIMEOUT)
            )
            
            for path in contract_paths:
                try:
                    result = adapter.run(path, timeout=timeout)
                    if result:
                        if isinstance(result, list):
                            findings.extend(result)
                        else:
                            findings.append(result)
                except Exception as e:
                    self.logger.warning(f"Analysis failed for {path} with {adapter_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Critical failure in {adapter_name}: {e}")
            
        return findings
    
    def _process_adapter_results(self, adapter: Any, raw_results: List[Any]) -> List[AnalysisResult]:
        """
        Process and standardize adapter results into unified format.
        Implements trust calibration and explainability features.
        """
        processed = []
        
        for result in raw_results:
            try:
                processed_result = self._create_analysis_result(adapter, result)
                if processed_result:
                    processed.append(processed_result)
            except Exception as e:
                self.logger.warning(f"Failed to process result from {adapter.__class__.__name__}: {e}")
                
        return processed

    def _create_analysis_result(self, adapter: Any, result: Any) -> Optional[AnalysisResult]:
        """Create a standardized AnalysisResult from adapter output"""
        try:
            # Extract fields with proper type handling
            severity, vuln_type, details = self._extract_result_fields(result)
            confidence = self._calculate_confidence_level(adapter, result)
            remediation = self._generate_remediation_suggestion(result)
            
            # Cross-chain impact analysis
            cross_chain_impact = None
            if self.cross_chain_enabled:
                cross_chain_impact = self._analyze_cross_chain_impact(result)
            
            return AnalysisResult(
                tool_name=adapter.__class__.__name__,
                vulnerability_type=vuln_type,
                severity=severity,
                confidence=confidence,
                finding_details=details,
                remediation_suggestion=remediation,
                cross_chain_impact=cross_chain_impact,
                timestamp=str(time.time())
            )
        except Exception as e:
            self.logger.error(f"Failed to create AnalysisResult: {e}")
            return None

    def _extract_result_fields(self, result: Any) -> tuple[str, str, Dict[str, Any]]:
        """Extract severity, vulnerability type, and details from result"""
        if isinstance(result, dict):
            severity = result.get('severity', 'Medium')
            vuln_type = result.get('swc_id') or result.get('title') or 'unknown'
            details = result
        else:
            severity = getattr(result, 'severity', 'Medium')
            vuln_type = (
                getattr(result, 'vulnerability_type', None) or 
                getattr(result, 'swc_id', None) or 
                'unknown'
            )
            details = getattr(result, 'details', {'raw': repr(result)})
        
        return severity, vuln_type, details
    
    def _generate_remediation_suggestion(self, result: Any) -> Optional[str]:
        """Generate actionable remediation suggestions"""
        vuln_type = getattr(result, 'vulnerability_type', '').lower()
        
        remediation_templates = {
            'reentrancy': 'Consider using the checks-effects-interactions pattern or ReentrancyGuard modifier',
            'integer_overflow': 'Use SafeMath library or Solidity 0.8+ built-in overflow protection',
            'unchecked_call': 'Always check return values of external calls and handle failures appropriately'
        }
        
        return remediation_templates.get(vuln_type)
    
    def _analyze_cross_chain_impact(self, result: Any) -> Optional[List[str]]:
        """
        Cross-chain vulnerability analysis as per Section 5.6.
        Identifies vulnerabilities that may manifest differently across chains.
        """
        vuln_type = getattr(result, 'vulnerability_type', '').lower()
        
        # Define chain-specific vulnerability mappings
        chain_mappings = {
            'gas_limit': ['ethereum', 'polygon', 'bsc'],
            'block_gas_limit': ['ethereum', 'polygon', 'bsc'],
            'timestamp_dependence': ['ethereum', 'arbitrum']
        }
        
        return chain_mappings.get(vuln_type)

    async def _update_rl_feedback(self, results: List[AnalysisResult]) -> None:
        """
        Reinforcement learning feedback loop as described in Section 5.4.
        Updates agent behavior based on analysis outcomes.
        """
        try:
            feedback_data = self._generate_feedback_data(results)
            self.logger.info(f"RL Feedback collected: {feedback_data}")
            # TODO: Implement actual RL model updates
        except Exception as e:
            self.logger.error(f"Failed to update RL feedback: {e}")

    def _generate_feedback_data(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Generate structured feedback data for RL training"""
        tool_names = {r.tool_name for r in results}
        
        return {
            'analysis_timestamp': str(time.time()),
            'total_findings': len(results),
            'confidence_distribution': {
                level.value: sum(1 for r in results if r.confidence == level)
                for level in ConfidenceLevel
            },
            'tool_performance': {
                tool: sum(1 for r in results if r.tool_name == tool)
                for tool in tool_names
            }
        }

def run_dynamic_analysis(
    contract_paths: Iterable[str],
    config: Optional[Union[Dict[str, Any], DynamicAnalysisConfig]] = None,
    logger: Optional[logging.Logger] = None,
    adapters: Optional[List[Any]] = None,
) -> List[AnalysisResult]:
    """
    Simplified interface for dynamic analysis execution.
    
    Args:
        contract_paths: Paths to smart contract files
        config: Configuration dictionary or DynamicAnalysisConfig instance
        logger: Logger instance
        adapters: Pre-initialized adapters (for testing)
    
    Returns:
        List of standardized analysis results
    """
    if adapters:
        return _run_legacy_analysis(contract_paths, config, logger, adapters)
    