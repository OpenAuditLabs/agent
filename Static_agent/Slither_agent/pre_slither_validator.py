#!/usr/bin/env python3
"""
pre_slither_validator.py

A pre-processing validator that runs before Slither analysis to:
- Check and fix common syntax issues
- Ensure contracts compile before vulnerability analysis
- Integrate seamlessly with existing slither_to_json_with_diagnostics.py
"""

import os
import re
import shutil
import subprocess
from datetime import datetime
from typing import Tuple, List, Dict

class PreSlitherValidator:
    def __init__(self):
        self.fixes_applied = []
        
    def validate_and_fix_contract(self, file_path: str) -> Tuple[bool, str, List[str]]:
        """
        Validate a contract and apply fixes if needed.
        Returns: (success, fixed_content_or_error, fixes_applied)
        """
        fixes = []
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply systematic fixes
            content, file_fixes = self._apply_all_fixes(content, file_path)
            fixes.extend(file_fixes)
            
            # If changes were made, create backup and update file
            if content != original_content:
                backup_path = f"{file_path}.pre_slither_backup"
                shutil.copy2(file_path, backup_path)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixes.append(f"Backup created: {backup_path}")
            
            return True, content, fixes
            
        except Exception as e:
            return False, str(e), fixes
    
    def _apply_all_fixes(self, content: str, file_path: str) -> Tuple[str, List[str]]:
        """Apply all known fixes to the content"""
        fixes = []
        
        # Fix 1: Add SPDX license if missing
        if not re.search(r'//\s*SPDX-License-Identifier:', content):
            content = '// SPDX-License-Identifier: MIT\n' + content
            fixes.append("Added SPDX license identifier")
        
        # Fix 2: Abstract contracts
        content, abstract_fixes = self._fix_abstract_contracts(content)
        fixes.extend(abstract_fixes)
        
        # Fix 3: Virtual functions
        content, virtual_fixes = self._fix_virtual_functions(content)
        fixes.extend(virtual_fixes)
        
        # Fix 4: Deprecated .value() syntax
        content, value_fixes = self._fix_value_syntax(content)
        fixes.extend(value_fixes)
        
        # Fix 5: Call return handling
        content, call_fixes = self._fix_call_handling(content)
        fixes.extend(call_fixes)
        
        # Fix 6: Pragma version alignment
        content, pragma_fixes = self._fix_pragma_version(content)
        fixes.extend(pragma_fixes)
        
        return content, fixes
    

        def _fix_abstract_contracts(self, content: str) -> Tuple[str, List[str]]:
        """Fix contracts that should be abstract"""
        fixes = []
        
        # Find contracts with unimplemented functions
        contract_pattern = r'contract\s+(\w+)([^{]*)\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        
        def fix_contract(match):
            contract_name = match.group(1)
            inheritance = match.group(2)
            body = match.group(3)
            
            # Check for unimplemented functions (ending with semicolon)
            if re.search(r'function\s+\w+[^{]*;', body):
                fixes.append(f"Made contract '{contract_name}' abstract")
                return f'abstract contract {contract_name}{inheritance}{{{body}}}'
            
            return match.group(0)
        
        content = re.sub(contract_pattern, fix_contract, content, flags=re.DOTALL)
        return content, fixes
    
    def _fix_virtual_functions(self, content: str) -> Tuple[str, List[str]]:
        """Add virtual keyword to unimplemented functions"""
        fixes = []
        
        # Pattern for unimplemented functions
        pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*([^{;]*);'
        
        def add_virtual(match):
            func_name = match.group(1)
            params = match.group(2)
            modifiers = match.group(3).strip()
            
            if 'virtual' not in modifiers:
                if modifiers:
                    new_func = f"function {func_name}({params}) {modifiers} virtual;"
                else:
                    new_func = f"function {func_name}({params}) public virtual;"
                
                fixes.append(f"Added 'virtual' to function '{func_name}'")
                return new_func
            
            return match.group(0)
        
        content = re.sub(pattern, add_virtual, content)

        return content, fixes
    