"""Security policies."""

import logging
import os
import importlib.util
import sys

from oal_agent.tools.slither import SlitherTool
from oal_agent.core.config import settings


class SecurityPolicy:
    """Defines security policies."""

    ALLOWED_ACTIONS = ["read", "write", "execute", "analyze"]  # Example allowed actions

    def __init__(self):
        """Initialize security policy."""
        self.slither_tool = SlitherTool()
        self.logger = logging.getLogger(__name__)

    def check_permission(self, action: str, resource: str) -> bool:
        """Check if action is permitted on resource."""
        if action not in self.ALLOWED_ACTIONS:
            return False
        # TODO: Implement more granular permission checks based on resource
        return True

    async def check_static_analysis_misconfigurations(self, contract_path: str) -> bool:
        """
        Check for common security misconfigurations using static analysis (Slither).
        Returns True if misconfigurations are found. Returns False if no issues were found,
        or if input validation fails or static analysis encounters an error (errors are logged).
        """
        if not isinstance(contract_path, str) or not contract_path.strip():
            self.logger.error("Invalid contract_path: must be a non-empty string")
            return False

        if not os.path.exists(contract_path) or not os.path.isfile(contract_path):
            self.logger.error(
                "contract_path does not exist or is not a file: %s", contract_path
            )
            return False

        try:
            analysis_results = await self.slither_tool.analyze(contract_path)
        except Exception as e:
            self.logger.error(
                "Static analysis failed for %s: %s", contract_path, e, exc_info=True
            )
            return False

        # For now, assuming if analysis_results is not empty, then misconfigurations were found.
        # This logic will need to be refined once SlitherTool.analyze is fully implemented.
        return bool(analysis_results)

def load_additional_policies():
    """Loads additional security policy modules from a configurable directory."""
    if not settings.additional_policies_path:
        return

    policy_dir = settings.additional_policies_path
    if not os.path.isdir(policy_dir):
        logging.warning(f"Additional policies directory not found: {policy_dir}")
        return

    logging.info(f"Loading additional policies from: {policy_dir}")
    for filename in os.listdir(policy_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            file_path = os.path.join(policy_dir, filename)
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    logging.info(f"Successfully loaded policy module: {module_name}")
                    # Here, you would typically call a registration function within the loaded module
                    # For example: module.register_policies(SecurityPolicy)
                else:
                    logging.error(f"Could not get spec or loader for module: {module_name}")
            except Exception as e:
                logging.error(f"Failed to load policy module {module_name} from {file_path}: {e}", exc_info=True)

load_additional_policies()
