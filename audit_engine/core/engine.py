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