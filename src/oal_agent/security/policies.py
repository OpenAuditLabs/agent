"""Security policies."""


from oal_agent.tools.slither import SlitherTool


class SecurityPolicy:
    """Defines security policies."""

    ALLOWED_ACTIONS = ["read", "write", "execute", "analyze"]  # Example allowed actions

    def __init__(self):
        """Initialize security policy."""
        self.slither_tool = SlitherTool()

    def check_permission(self, action: str, resource: str) -> bool:
        """Check if action is permitted on resource."""
        if action not in self.ALLOWED_ACTIONS:
            return False
        # TODO: Implement more granular permission checks based on resource
        return True

    async def check_static_analysis_misconfigurations(self, contract_path: str) -> bool:
        """
        Check for common security misconfigurations using static analysis (Slither).
        Returns True if misconfigurations are found, False otherwise.
        """
        analysis_results = await self.slither_tool.analyze(contract_path)
        # For now, assuming if analysis_results is not empty, then misconfigurations were found.
        # This logic will need to be refined once SlitherTool.analyze is fully implemented.
        return bool(analysis_results)
