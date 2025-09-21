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