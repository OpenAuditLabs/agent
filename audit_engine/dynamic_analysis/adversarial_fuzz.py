# audit_engine/dynamic_analysis/adversarial_fuzz.py

import os
import json
import uuid
from datetime import datetime
from typing import List
from audit_engine.static_analysis.base import AbstractAdapter
from audit_engine.core.schemas import Finding, ToolError

# Manticore is imported lazily in run() to avoid a hard import-time dependency.

# Manticore is imported lazily inside run() to avoid a hard dependency.

def run(self, contract_path: str, solc_version: str = "0.8.19", max_states: int = 100, **kwargs) -> List[Finding]:
    """
    Runs adversarial fuzzing on a Solidity contract using symbolic execution for edge-case path discovery.
    Returns a list of Finding objects upon exploitable states or assertion/require failures.
    """
    findings = []
    try:
        from manticore.ethereum import ManticoreEVM
        from manticore.core.smtlib import Operators
    except ImportError:
        return [self.standardize_finding({
            "title": "AdversarialFuzz Error",
            "description": "Manticore must be installed: pip install manticore",
            "severity": "Low",
            "swc_id": "",
            "line_numbers": [],
            "confidence": "Low",
            "tool": getattr(self, "tool_name", self.__class__.__name__),
        })]


class AdversarialFuzz(AbstractAdapter):
    """
    AdversarialFuzz uses Manticore to perform adversarial, feedback-guided fuzzing on smart contracts.
    It generates syntactically valid but edge-case inputs, explores transactions, and reports exploitable findings.
    """

    tool_name = "AdversarialFuzz"
    tool_version = "1.1.0"

    def run(self, contract_path: str, solc_version: str = "0.8.19", max_states: int = 100, **kwargs) -> List[Finding]:
        """
        Runs adversarial fuzzing on a Solidity contract using symbolic execution for edge-case path discovery.
        Returns a list of Finding objects upon exploitable states or assertion/require failures.
        """
        findings = []
        if not os.path.isfile(contract_path):
            return [self.standardize_finding({
                "title": "AdversarialFuzz Error",
                "description": f"Contract file {contract_path} does not exist.",
                "severity": "Low",
                "swc_id": "",
                "line_numbers": [],
                "confidence": "Low",
                "tool": getattr(self, "tool_name", self.__class__.__name__),
            })]

        with open(contract_path, "r") as f:
            source = f.read()

        m = ManticoreEVM()
        user_account = m.create_account(balance=10 ** 20)

        try:
            contract_account = m.solidity_create_contract(
                source_code=source,
                owner=user_account,
                solc_version=solc_version
            )
        except Exception as err:
            return [self.standardize_finding({
                "title": "AdversarialFuzz Error",
                "description": f"Contract compilation/deploy failed: {err}",
                "severity": "Low",
                "swc_id": "",
                "line_numbers": [],
                "confidence": "Low",
                "tool": getattr(self, "tool_name", self.__class__.__name__),
            })]

        # Extract ABI to fuzz all public/external and payable functions
        abi = getattr(contract_account, "abi", [])
        for func in abi:
            if func.get("type") != "function":
                continue
            if func.get("stateMutability") == "view":
                continue

            func_name = func["name"]
            inputs = func.get("inputs", [])
            symbolic_args = []
            for inp in inputs:
                # Use type info if available to generate appropriate symbolic values
                if inp["type"] == "address":
                    val = m.make_symbolic_value(name=f"{func_name}_{inp['name']}_address")
                    # 160-bit EVM address space
                    m.constrain(Operators.ULT(val, 2**160))
                elif inp["type"].startswith("uint") or inp["type"].startswith("int"):
                    val = m.make_symbolic_value(name=f"{func_name}_{inp['name']}_int")
                    bits_str = "".join(ch for ch in inp["type"] if ch.isdigit()) or "256"
                    bits = int(bits_str)
                    if inp["type"].startswith("uint"):
                        m.constrain(Operators.ULE(val, 2**bits - 1))
                    else:
                        m.constrain(Operators.SGE(val, -(2**(bits - 1))))
                        m.constrain(Operators.SLE(val, 2**(bits - 1) - 1))
                elif inp["type"] == "bool":
                    val = m.make_symbolic_value(name=f"{func_name}_{inp['name']}_bool")
                    # Constrain to {0,1}
                    m.constrain(Operators.Or(val == 0, val == 1))
                else:
                    # Fallback: treat as 256-bit value
                    val = m.make_symbolic_value(name=f"{func_name}_{inp['name']}_any")
                    m.constrain(Operators.ULE(val, 2**256 - 1))
                symbolic_args.append(val)


            try:
                m.transaction(
                    caller=user_account,
                    address=contract_account.address,
                    value=0,
                    function_name=func_name,
                    args=symbolic_args,
                    data=None,
                    gas=10000000
                )
            except Exception as e:
                # Continue fuzzing after failed transaction
                continue

        # Fuzzing exploration
        m.run(max_states=max_states)
        # Look for interesting states: assertion failures, exceptions, abnormal balances, etc.
        for state in m.final_states:
            world = state.platform
            # Check for exception
            for exc in getattr(world, "_exceptions", []):
                finding = {
                    "title": f"Runtime exception: {exc.get('type', 'Exception')}",
                    "description": exc.get("description", ""),
                    "severity": "High",
                    "swc_id": "SWC-123",
                    "line_numbers": [],
                    "confidence": "High",
                    "tool": getattr(self, "tool_name", self.__class__.__name__),
                }
                findings.append(self.standardize_finding(finding))


            # Check for abnormal balance changes as signs of reentrancy, DoS, etc.
            actors = world.accounts
            for addr, account in actors.items():
                # You can extend with specific exploitation logic (e.g. checking for >10x balance increase)
                balance = account.balance
                cond = Operators.UGT(balance, 10 ** 22)
                if state.can_be_true(cond):

                    finding = {
                        "title": "Abnormal Ether transfer detected",
                        "description": f"Actor {hex(addr) if isinstance(addr, int) else addr} balance: {balance}",
                        "severity": "High",
                        "swc_id": "SWC-105",
                        "line_numbers": [],
                        "confidence": "High",
                        "tool": getattr(self, "tool_name", self.__class__.__name__),
                    }
                    findings.append(self.standardize_finding(finding))


        return findings

    def parse_output(self, output: str) -> List[Finding]:
        """
        This remains as a fallback for any custom output parsing you want to add if needed.
        """
        try:
            raw = json.loads(output)
            findings: List[Finding] = []
            for item in raw:
                finding = Finding(**item)
                findings.append(finding)
            return findings
        except Exception as e:
            raise ToolError(f"Failed to parse output: {e}")
