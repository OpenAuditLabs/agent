#!/usr/bin/env python3
"""
Test script for enhanced vulnerability detection with detailed fixes
"""

import asyncio
import os
from pathlib import Path
from audit_engine.core.engine import AuditEngine
from audit_engine.core.schemas import AnalysisRequest
from audit_engine.core.config import AuditConfig, StaticAnalysisConfig
from audit_engine.core.vulnerability_patterns import get_detection_tips, get_vulnerability_info, get_fix_suggestions
from pprint import pprint

async def test_enhanced_audit():
    """Test the enhanced vulnerability detection"""
    
    print("🔍 Enhanced Vulnerability Detection Test")
    print("=" * 60)
    
    # Initialize the audit engine with configuration
    config = AuditConfig(
        log_level="INFO",
        enable_parallel_execution=False,  # Sequential for clearer output
        static_analysis=StaticAnalysisConfig(
            enable_mythril=False,
            enable_manticore=True,
            enable_slither=False
        )
    )
    
    engine = AuditEngine(config=config)
    
    # Test contracts with different vulnerability types
    test_contracts = [
        "audit_engine/smart_contracts/reentrancy/16925.sol",
        "audit_engine/smart_contracts/integer_overflow/io1.sol",
        "audit_engine/smart_contracts/timestamp/ts1.sol"
    ]
    
    print(f"\n📁 Testing enhanced detection on {len(test_contracts)} contracts")
    
    request = AnalysisRequest(
        contract_paths=test_contracts,
        analysis_type="comprehensive",
        include_static=True,
        include_dynamic=False,
        include_scoring=True,
        max_analysis_time=120
    )
    
    result = await engine.analyze(request)
    
    print(f"\n✅ Analysis completed in {result.duration_seconds:.2f} seconds")
    print(f"📊 Found {result.total_findings} vulnerabilities\n")
