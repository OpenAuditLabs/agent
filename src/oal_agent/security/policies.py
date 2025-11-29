"""Security policies."""

import importlib.util
import logging
import os
import sys

from oal_agent.core.config import settings
from oal_agent.tools.slither import SlitherTool

logger = logging.getLogger(__name__)


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
    """
    Loads additional security policy modules from a configurable directory.

    Security Implications:
    Dynamically loading and executing Python modules from a filesystem path
    introduces significant security risks, including arbitrary code execution.
    The 'additional_policies_path' MUST point only to trusted,
    access-controlled directories. Ensure that the directory and its contents
    are secured against unauthorized modifications.

    Deployment Guidance:
    Operators enabling this feature must verify directory ownership,
    permissions, and contents to prevent supply chain attacks or privilege
    escalation. This feature should only be used in environments where
    strict control over the policy directory can be maintained.
    """
    if not settings.additional_policies_path:
        return

    policy_dir = settings.additional_policies_path
    if not os.path.isdir(policy_dir):
        logger.warning(f"Additional policies directory not found: {policy_dir}")
        return

    logger.warning(
        f"Dynamic policy loading is enabled from: {policy_dir}. "
        "Operators must verify directory ownership, permissions, and contents "
        "to mitigate code execution risks."
    )
    logger.info(f"Loading additional policies from: {policy_dir}")
    for filename in os.listdir(policy_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"oal_agent.security.dynamic_policies.{filename[:-3]}"
            file_path = os.path.join(policy_dir, filename)
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    logger.info(f"Successfully loaded policy module: {module_name}")

                    if hasattr(module, "register_policies"):
                        try:
                            module.register_policies(SecurityPolicy)
                            logger.info(
                                f"Successfully registered policies from module: {module_name}"
                            )
                        except Exception as reg_e:
                            logger.error(
                                f"Failed to register policies from module {module_name}: {reg_e}",
                                exc_info=True,
                            )
                    else:
                        logger.warning(
                            f"Policy module {module_name} does not have a 'register_policies' function. "
                            "No policies were registered from this module."
                        )
                else:
                    logger.error(
                        f"Could not get spec or loader for module: {module_name}"
                    )
            except Exception as e:
                logger.error(
                    f"Failed to load policy module {module_name} from {file_path}: {e}",
                    exc_info=True,
                )


load_additional_policies()
