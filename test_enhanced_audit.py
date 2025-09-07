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

    # Display enhanced findings with detailed information
    for i, finding in enumerate(result.findings, 1):
        print(f"\n{'='*80}")
        print(f"Finding {i}:")
        print(f"{'='*80}")
        
        # Basic Information
        print(f"Description: {finding.description}")
        print(f"Severity: {finding.severity}")
        print(f"SWC ID: {finding.swc_id or 'N/A'}")
        print(f"Confidence: {finding.confidence:.2f}")
        
        # Location Information
        print(f"\nVulnerable File: {finding.file_path}")
        if finding.line_span:
            print(f"Lines: {finding.line_span.start}-{finding.line_span.end}")
        if finding.function_name:
            print(f"Function: {finding.function_name}")
            
        # Detection Tips
        if finding.swc_id:
            detection_tips = get_detection_tips(finding.swc_id)
            if detection_tips:
                print("\nDetection Tips:")
                for tip in detection_tips:
                    print(f"  • {tip}")
        if finding.vulnerability_details:
            print(f"\nVulnerability Details:")
            print(f"  Name: {finding.vulnerability_details.get('name')}")
            print(f"  Impact: {finding.vulnerability_details.get('impact')}")
            print(f"\nDetailed Description:")
            print(f"{finding.vulnerability_details.get('description')}")
        
        if finding.suggested_fixes:
            print(f"\nSuggested Fixes:")
            for j, fix in enumerate(finding.suggested_fixes, 1):
                print(f"\nFix {j}: {fix.get('pattern')}")
                print("-" * 40)
                print(f"Description: {fix.get('description')}")
                print("\nExample Implementation:")
                print(f"{fix.get('code_example')}")
        
        if finding.recommendations:
            print("\nRecommendations:")
            for rec in finding.recommendations:
                print(f"- {rec}")
        
        print("\n")

if __name__ == "__main__":
    asyncio.run(test_enhanced_audit())
        