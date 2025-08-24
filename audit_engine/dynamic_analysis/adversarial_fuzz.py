# audit_engine/dynamic_analysis/adversarial_fuzz.py

import os
import json
import uuid
from datetime import datetime
from typing import List
from audit_engine.static_analysis.base import AbstractAdapter
from audit_engine.core.schemas import Finding, ToolError

try:
    from manticore.ethereum import ManticoreEVM
    from manticore.core.smtlib import Operators
except ImportError as e:
    raise ImportError("Manticore must be installed: pip install manticore")

class AdversarialFuzz(AbstractAdapter):
    """
    AdversarialFuzz uses Manticore to perform adversarial, feedback-guided fuzzing on smart contracts.
    It generates syntactically valid but edge-case inputs, explores transactions, and reports exploitable findings.
    """

    TOOL_NAME = "AdversarialFuzz"
    TOOL_VERSION = "1.1.0"

    def run(self, contract_path: str, solc_version: str = "0.8.19", max_states: int = 100, **kwargs) -> List[Finding]:
        """
        Runs adversarial fuzzing on a Solidity contract using symbolic execution for edge-case path discovery.
        Returns a list of Finding objects upon exploitable states or assertion/require failures.
        """
        findings = []
        if not os.path.isfile(contract_path):
            raise ToolError(f"Contract file {contract_path} does not exist.")

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
        except Exception as e:
            raise ToolError(f"Contract compilation/deploy failed: {e}")

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
                elif inp["type"].startswith("uint") or inp["type"].startswith("int"):
                    val = m.make_symbolic_value(name=f"{func_name}_{inp['name']}_int")
                elif inp["type"] == "bool":
                    val = m.make_symbolic_value(name=f"{func_name}_{inp['name']}_bool")
                else:
                    val = m.make_symbolic_buffer(32, name=f"{func_name}_{inp['name']}_buf")
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
                finding = Finding(
                    finding_id=str(uuid.uuid4()),
                    swc_id="SWC-123",  # Map exception types to SWC if you have mapping logic in severity_mapping.py
                    severity="Major",
                    tool_name=self.TOOL_NAME,
                    tool_version=self.TOOL_VERSION,
                    file_path=contract_path,
                    line_span={"start": exc.get("pc", 0), "end": exc.get("pc", 0)},
                    function_name=None,  # Optional: parse from exc or runtime context
                    bytecode_offset=exc.get("pc", 0),
                    description=f"{exc.get('type', 'Exception')}: {exc.get('description', '')}",
                    reproduction_steps=json.dumps(exc),
                    proof_of_concept="Replay the transaction in the given workspace with provided symbolic input.",
                    exploit_complexity="High",
                    confidence=0.8,
                    sanitizer_present=False,
                    recommendations=["Add input validation", "Enforce require/assert checks"],
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )
                findings.append(finding)

            # Check for abnormal balance changes as signs of reentrancy, DoS, etc.
            actors = world.accounts
            for addr, account in actors.items():
                # You can extend with specific exploitation logic (e.g. checking for >10x balance increase)
                balance = account.balance
                if balance > 10 ** 22:  # Arbitrary threshold for abnormal gain
                    finding = Finding(
                        finding_id=str(uuid.uuid4()),
                        swc_id="SWC-105",  # Example: Unprotected Ether Withdrawal
                        severity="Critical",
                        tool_name=self.TOOL_NAME,
                        tool_version=self.TOOL_VERSION,
                        file_path=contract_path,
                        line_span={"start": 0, "end": 0},
                        function_name=None,
                        bytecode_offset=None,
                        description=f"Abnormal Ether transfer detected: {balance}",
                        reproduction_steps=f"Actor {addr} balance {balance}",
                        proof_of_concept="Fuzz inputs that lead to abnormal actor balance.",
                        exploit_complexity="Medium",
                        confidence=0.9,
                        sanitizer_present=False,
                        recommendations=["Add withdrawal limits", "Restrict Ether transfer access"],
                        timestamp=datetime.utcnow().isoformat() + "Z"
                    )
                    findings.append(finding)

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
