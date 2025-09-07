#!/usr/bin/env python3
"""
Example script showing how to feed vulnerable smart contracts to the audit engine.
This demonstrates the proper way to use the AuditEngine with the smart_contracts folder.
"""

import asyncio
import os
from pathlib import Path
from audit_engine.core.engine import AuditEngine
from audit_engine.core.schemas import AnalysisRequest
from audit_engine.core.config import AuditConfig, StaticAnalysisConfig
from audit_engine.dynamic_analysis.config import DynamicAnalysisConfig

def get_contract_paths():
    """Get all .sol files from the smart_contracts folder"""
    base_path = Path("audit_engine/smart_contracts")
    contract_paths = []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.sol'):
                full_path = os.path.join(root, file)
                contract_paths.append(full_path)
    
    return contract_paths

def get_contracts_by_vulnerability_type():
    """Get contracts organized by vulnerability type"""
    base_path = Path("audit_engine/smart_contracts")
    contracts_by_type = {}
    
    for vuln_type in ['reentrancy', 'integer_overflow', 'timestamp']:
        vuln_path = base_path / vuln_type
        if vuln_path.exists():
            contracts_by_type[vuln_type] = [
                str(vuln_path / file) for file in os.listdir(vuln_path) 
                if file.endswith('.sol') 
                #checks if there is any file available inside each type
            ]
    
    return contracts_by_type

async def run_audit_example():
    """Main function to demonstrate audit engine usage"""
    
    print("🔍 OpenAudit Agent - Smart Contract Vulnerability Detection")
    print("=" * 60)
    
    # Initialize the audit engine with configuration
    config = AuditConfig(
        log_level="INFO",
        enable_parallel_execution=True,
        # Enable static analysis tools
        static_analysis=StaticAnalysisConfig(
            enable_mythril=False,
            enable_manticore=True,
            enable_slither=False
        ),
        # Enable dynamic analysis tools  
        dynamic_analysis=DynamicAnalysisConfig(
            enable_echidna=True,
            enable_adversarial_fuzz=False
        )
    )
    
    engine = AuditEngine(config=config)
    
    # Example 1: Analyze all contracts at once
    print("\n📁 Example 1: Analyzing ALL vulnerable contracts")
    print("-" * 50)
    
    all_contracts = get_contract_paths()
    print(f"Found {len(all_contracts)} contract files")
    
    if all_contracts:
        # Create analysis request
        request = AnalysisRequest(
            contract_paths=all_contracts[:30],  # Limit to first 5 for demo
            analysis_type="comprehensive",
            include_static=True,
            include_dynamic=True,
            include_scoring=True,
            enable_ai_agents=False,  # Not implemented yet
            max_analysis_time=300  # 5 minutes
        )
        
        print(f"Analyzing {len(request.contract_paths)} contracts...")
        result = await engine.analyze(request)
        
        print(f"\n✅ Analysis completed in {result.duration_seconds:.2f} seconds")
        print(f"📊 Found {result.total_findings} vulnerabilities")
        
        # Show severity breakdown
        if result.severity_distribution:
            print("\n📈 Severity Distribution:")
            for severity, count in result.severity_distribution.items():
                print(f"  {severity}: {count}")
        
        # Show sample findings
        if result.findings:
            print(f"\n🔍 Sample Findings (showing first 30):")
            for i, finding in enumerate(result.findings[:30]):
                print(f"\n  Finding {i+1}:")
                print(f"    Tool: {finding.tool_name}")
                print(f"    Severity: {finding.severity}")
                print(f"    SWC ID: {finding.swc_id or 'N/A'}")
                print(f"    File: {finding.file_path}")
                print(f"    Description: {finding.description[:]}...")
                print(f"    Confidence: {finding.confidence:.2f}")
    
    # Example 2: Analyze by vulnerability type
    print("\n\n📁 Example 2: Analyzing by vulnerability type")
    print("-" * 50)
    
    contracts_by_type = get_contracts_by_vulnerability_type()
    
    for vuln_type, contracts in contracts_by_type.items():
        if contracts:
            print(f"\n🔍 Analyzing {vuln_type} contracts ({len(contracts)} files)")
            
            # Analyze just 2 contracts per type for demo
            sample_contracts = contracts[:2]
            
            request = AnalysisRequest(
                contract_paths=sample_contracts,
                analysis_type="comprehensive",
                include_static=True,
                include_dynamic=False,  # Skip dynamic for faster demo
                include_scoring=True,
                max_analysis_time=120
            )
            
            result = await engine.analyze(request)
            print(f"  Found {result.total_findings} vulnerabilities")
            
            # Show specific findings for this vulnerability type
            for finding in result.findings:
                if vuln_type.lower() in finding.description.lower() or vuln_type.lower() in finding.swc_id.lower():
                    print(f"    ⚠️  {finding.severity}: {finding.description[:80]}...")
    
    # Example 3: Single contract analysis
    print("\n\n📁 Example 3: Single contract deep analysis")
    print("-" * 50)
    
    # Pick a specific reentrancy contract
    reentrancy_contracts = contracts_by_type.get('reentrancy', [])
    if reentrancy_contracts:
        single_contract = reentrancy_contracts[0]
        print(f"🔍 Deep analysis of: {single_contract}")
        
        request = AnalysisRequest(
            contract_paths=[single_contract],
            analysis_type="comprehensive",
            include_static=True,
            include_dynamic=True,
            include_scoring=True,
            max_analysis_time=180
        )
        
        result = await engine.analyze(request)
        
        print(f"\n📊 Detailed Results:")
        print(f"  Total findings: {result.total_findings}")
        print(f"  Analysis time: {result.duration_seconds:.2f}s")
        
        if result.findings:
            print(f"\n🔍 All Findings:")
            for i, finding in enumerate(result.findings, 1):
                print(f"\n  {i}. {finding.severity} - {finding.tool_name}")
                print(f"     SWC: {finding.swc_id or 'N/A'}")
                print(f"     File: {os.path.basename(finding.file_path)}")
                print(f"     Description: {finding.description}")
                print(f"     Confidence: {finding.confidence:.2f}")
                if finding.recommendations:
                    print(f"     Recommendations: {finding.recommendations[0]}")
        
        if result.tool_errors:
            print(f"\n⚠️  Tool Errors ({len(result.tool_errors)}):")
            for error in result.tool_errors:
                print(f"  - {error.tool_name}: {error.error_message}")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(run_audit_example())