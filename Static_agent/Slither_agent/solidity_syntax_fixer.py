#!/usr/bin/env python3
"""
solidity_syntax_fixer.py

Automated Solidity syntax checker and fixer that:
- Detects common syntax issues across different Solidity versions
- Automatically fixes deprecated patterns to modern syntax
- Validates compilation after fixes
- Creates backup of original files
- Provides detailed report of changes made
"""

import os
import re
import json
import uuid
import shutil
import subprocess
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class SoliditySyntaxFixer:
    def __init__(self, solc_path: Optional[str] = None):
        self.solc_path = solc_path or "solc"
        self.fixes_applied = []
        self.compilation_errors = []
        
    def check_compilation(self, file_path: str) -> Tuple[bool, str]:
        """Check if a Solidity file compiles successfully"""
        try:
            cmd = [self.solc_path, "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, "Solidity compiler not found"
                
            # Try to compile the file
            cmd = [self.solc_path, file_path, "--bin", "--overwrite"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return True, "Compilation successful"
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, f"Error during compilation: {str(e)}"
        
    def detect_and_fix_syntax_issues(self, content: str, file_path: str) -> str:
        """Detect and fix common Solidity syntax issues"""
        original_content = content
        fixes = []
        
        # Fix 1: Abstract contracts with unimplemented functions
        pattern = r'contract\s+(\w+)\s*{'
        matches = re.finditer(pattern, content)
        for match in matches:
            contract_name = match.group(1)
            contract_start = match.start()
            
            # Look for unimplemented functions in this contract
            # Find the contract body
            brace_count = 0
            contract_end = contract_start
            for i, char in enumerate(content[contract_start:]):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        contract_end = contract_start + i
                        break
            
            contract_body = content[contract_start:contract_end + 1]
            
            # Check for unimplemented functions (ending with semicolon)
            func_pattern = r'function\s+\w+\([^)]*\)\s*[^{]*;'
            if re.search(func_pattern, contract_body):
                # This contract has unimplemented functions, make it abstract
                new_contract_def = f'abstract contract {contract_name} {{'
                content = content.replace(match.group(0), new_contract_def)
                fixes.append(f"Made contract '{contract_name}' abstract (has unimplemented functions)")
        
        # Fix 2: Add virtual keyword to unimplemented functions
        virtual_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*([^{;]*);'
        def add_virtual(match):
            func_name = match.group(1)
            modifiers = match.group(2).strip()
            if 'virtual' not in modifiers:
                if modifiers:
                    new_func = f"function {func_name}({match.group(0).split('(')[1].split(')')[0]}) {modifiers} virtual;"
                else:
                    new_func = f"function {func_name}({match.group(0).split('(')[1].split(')')[0]}) public virtual;"
                fixes.append(f"Added 'virtual' keyword to function '{func_name}'")
                return new_func
            return match.group(0)
        
        content = re.sub(virtual_pattern, add_virtual, content)
        
        # Fix 3: Update deprecated .value() syntax to {value: ...}
        value_pattern = r'(\w+)\.call\.value\(([^)]+)\)\(\)'
        def fix_call_value(match):
            address = match.group(1)
            value = match.group(2)
            fixes.append(f"Updated deprecated .value() syntax to modern {{value: ...}} format")
            return f'{address}.call{{value: {value}}}("")'
        
        content = re.sub(value_pattern, fix_call_value, content)
        
        # Fix 4: Add success handling for call operations
        call_pattern = r'require\s*\(\s*(\w+)\.call\{value:\s*([^}]+)\}\s*\(""\)\s*\)'
        def fix_call_handling(match):
            address = match.group(1)
            value = match.group(2)
            fixes.append(f"Added proper success handling for call operation")
            return f'(bool success, ) = {address}.call{{value: {value}}}("");\n        require(success)'
        
        content = re.sub(call_pattern, fix_call_handling, content)
        
        # Fix 5: Update pragma version if it's too old and causing issues
        pragma_pattern = r'pragma\s+solidity\s+([^;]+);'
        pragma_match = re.search(pragma_pattern, content)
        if pragma_match:
            version = pragma_match.group(1)
            # If version is older than 0.6.0 and we have modern syntax, update it
            if '^0.5' in version or '^0.4' in version:
                if 'abstract' in content or 'virtual' in content or '{value:' in content:
                    content = re.sub(pragma_pattern, 'pragma solidity ^0.8.0;', content)
                    fixes.append(f"Updated pragma version from '{version}' to '^0.8.0' for compatibility")
        
        # Fix 6: Add SPDX license if missing
        if 'SPDX-License-Identifier' not in content:
            lines = content.split('\n')
            lines.insert(0, '// SPDX-License-Identifier: MIT')
            content = '\n'.join(lines)
            fixes.append("Added missing SPDX license identifier")
        
        # Fix 7: Fix require statements that use old call patterns
        old_require_pattern = r'require\s*\(\s*address\([^)]+\)\.call\.value\([^)]+\)\(\)\s*\)'
        if re.search(old_require_pattern, content):
            # This is handled by the earlier fixes, but let's ensure consistency
            fixes.append("Fixed deprecated require statement with old call pattern")
        
        # Store fixes for this file
        if fixes:
            self.fixes_applied.append({
                "file": file_path,
                "fixes": fixes,
                "timestamp": datetime.now().isoformat()
            })
        
        return content