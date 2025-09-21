#!/usr/bin/env python3
"""
slither_to_json_with_diagnostics.py

Improved Slither runner that:
 - automatically validates and fixes contract syntax before analysis
 - collects detector results
 - captures detector exceptions
 - records timing
 - falls back to CLI and Docker if Python API yields no findings
 - emits JSON report to stdout
"""

import sys
import os
import json
import uuid
import time
import re
from datetime import datetime
import logging

# Import our pre-validator
try:
    from pre_slither_validator import validate_contract_before_slither
    PRE_VALIDATION_AVAILABLE = True
except ImportError:
    PRE_VALIDATION_AVAILABLE = False

# === configurable ===
CONTRACT = sys.argv[1] if len(sys.argv) > 1 else "VulnerableBank.sol"
SOLC_PATH = sys.argv[2] if len(sys.argv) > 2 else None
DETECTORS_CLI = "all"  # Use all detectors for comprehensive analysis
DOCKER_IMAGE = "trailofbits/slither:latest"
AUTO_FIX_SYNTAX = True  # Enable automatic syntax fixing
# ====================

def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def parse_slither_cli_output(stdout, stderr, contract_path):
    """Extract findings from Slither CLI output"""
    findings = []
    
    # Look for detector findings in stderr (where Slither outputs results)
    output_text = stderr + stdout
    
    # Enhanced patterns to match different Slither output formats
    
    # 1. Pattern for "uses delegatecall to a input-controlled function id" (Controlled Delegatecall)
    controlled_delegatecall_pattern = r'([^\n]+)\s+uses delegatecall to a input-controlled function id\n\t- ([^\n]+)'
    controlled_delegatecall_matches = re.findall(controlled_delegatecall_pattern, output_text)
    
    for func_sig, call_location in controlled_delegatecall_matches:
        # Extract function name and file info
        func_match = re.search(r'([^(]+)\(([^)]*)\)\s+\(([^#]+)#(\d+)-(\d+)\)', func_sig.strip())
        if func_match:
            contract_func = func_match.group(1).strip()
            file_path = func_match.group(3).strip()
            start_line = func_match.group(4)
            end_line = func_match.group(5)
            
            findings.append({
                "finding_id": str(uuid.uuid4()),
                "swc_id": None,
                "severity": "High",  # Controlled delegatecall is high severity
                "tool_name": "slither-cli",
                "tool_version": "unknown",
                "file_path": file_path,
                "function_name": contract_func,
                "description": "Controlled Delegatecall",
                "elements": [
                    f"Controlled delegatecall in {func_sig.strip()}:",
                    f"\t- {call_location.strip()}"
                ],
                "detector": "controlleddelegatecall",
                "timestamp": now_iso(),
                "line_range": f"{start_line}-{end_line}",
                "reference": "https://github.com/crytic/slither/wiki/Detector-Documentation#controlled-delegatecall"
            })
    
    # 2. Pattern for "ignores return value by" (Unchecked Low Level)
    unchecked_pattern = r'([^\n]+)\s+ignores return value by ([^\n]+)'
    unchecked_matches = re.findall(unchecked_pattern, output_text)
    
    for func_sig, call_info in unchecked_matches:
        func_match = re.search(r'([^(]+)\(([^)]*)\)\s+\(([^#]+)#(\d+)-(\d+)\)', func_sig.strip())
        if func_match:
            contract_func = func_match.group(1).strip()
            file_path = func_match.group(3).strip()
            start_line = func_match.group(4)
            end_line = func_match.group(5)
            
            findings.append({
                "finding_id": str(uuid.uuid4()),
                "swc_id": None,
                "severity": "Medium",
                "tool_name": "slither-cli",
                "tool_version": "unknown",
                "file_path": file_path,
                "function_name": contract_func,
                "description": "Unchecked Low Level Call",
                "elements": [
                    f"Unchecked low level call in {func_sig.strip()}:",
                    f"\t- ignores return value by {call_info.strip()}"
                ],
                "detector": "uncheckedlowlevel",
                "timestamp": now_iso(),
                "line_range": f"{start_line}-{end_line}",
                "reference": "https://github.com/crytic/slither/wiki/Detector-Documentation#unchecked-low-level-calls"
            })
    
    # 3. Pattern for "lacks a zero-check on" (Missing Zero Address Validation)
    zero_check_pattern = r'([^\n]+)\s+lacks a zero-check on :\n\t\t- ([^\n]+)'
    zero_check_matches = re.findall(zero_check_pattern, output_text)
    
    for param_info, call_info in zero_check_matches:
        # Extract function info from parameter
        param_match = re.search(r'([^.]+)\.([^.]+)\(([^)]*)\)\.([^(]+)\s+\(([^#]+)#(\d+)\)', param_info.strip())
        if param_match:
            contract_name = param_match.group(1).strip()
            func_name = param_match.group(2).strip()
            param_name = param_match.group(4).strip()
            file_path = param_match.group(5).strip()
            line_num = param_match.group(6)
            
            findings.append({
                "finding_id": str(uuid.uuid4()),
                "swc_id": None,
                "severity": "Low",
                "tool_name": "slither-cli",
                "tool_version": "unknown",
                "file_path": file_path,
                "function_name": f"{contract_name}.{func_name}",
                "description": "Missing Zero Address Validation",
                "elements": [
                    f"Missing zero-check in {contract_name}.{func_name}:",
                    f"\t- Parameter {param_name} lacks zero-check on: {call_info.strip()}"
                ],
                "detector": "missingzeroaddressvalidation",
                "timestamp": now_iso(),
                "line_range": line_num,
                "reference": "https://github.com/crytic/slither/wiki/Detector-Documentation#missing-zero-address-validation"
            })
    
    # 4. Fallback pattern for other detectors (legacy support)
    finding_pattern = r'INFO:Detectors:\n(.*?)(?=INFO:|$)'
    matches = re.findall(finding_pattern, output_text, re.DOTALL)
    
    for match in matches:
        lines = match.strip().split('\n')
        current_finding = None
        
        for line in lines:
            line = line.strip()
            if not line or any(pattern in line for pattern in [
                'uses delegatecall to a input-controlled function id',
                'ignores return value by',
                'lacks a zero-check on'
            ]):
                continue  # Skip lines we've already processed above
                
            # Look for other vulnerability patterns
            if ' in ' in line and '(' in line and ')' in line:
                parts = line.split(' in ')
                if len(parts) >= 2:
                    vuln_type = parts[0].strip()
                    location_part = parts[1]
                    
                    func_match = re.search(r'([^(]+)\(([^)]*)\)', location_part)
                    file_match = re.search(r'\(([^#]+)#(\d+)-(\d+)\)', location_part)
                    
                    function_name = func_match.group(1).strip() if func_match else None
                    file_info = file_match.groups() if file_match else (contract_path, None, None)
                    
                    # Determine severity based on vulnerability type
                    severity = "Medium"  # default
                    if any(keyword in vuln_type.lower() for keyword in ["reentrancy", "controlled", "delegatecall"]):
                        severity = "High"
                    elif any(keyword in vuln_type.lower() for keyword in ["low level", "unchecked", "missing"]):
                        severity = "Medium"
                    elif any(keyword in vuln_type.lower() for keyword in ["naming", "convention", "style"]):
                        severity = "Low"
                    
                    current_finding = {
                        "finding_id": str(uuid.uuid4()),
                        "swc_id": None,
                        "severity": severity,
                        "tool_name": "slither-cli",
                        "tool_version": "unknown",
                        "file_path": file_info[0] if file_info[0] else contract_path,
                        "function_name": function_name,
                        "description": vuln_type,
                        "elements": [line],
                        "detector": vuln_type.replace(' ', '').lower(),
                        "timestamp": now_iso(),
                        "line_range": f"{file_info[1]}-{file_info[2]}" if file_info[1] and file_info[2] else None
                    }
                    findings.append(current_finding)
            
            elif current_finding and (line.startswith('\t') or line.startswith('Reference:')):
                if 'elements' not in current_finding:
                    current_finding['elements'] = []
                current_finding['elements'].append(line)
                
                if line.startswith('Reference:'):
                    current_finding['reference'] = line.replace('Reference:', '').strip()
    
    return findings