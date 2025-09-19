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
