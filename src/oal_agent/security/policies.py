"""Security policies."""

import logging
import os

from oal_agent.tools.slither import SlitherTool


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
