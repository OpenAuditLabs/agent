"""Static analysis agent."""

from src.oal_agent.core.config import settings


class StaticAgent:
    """Performs static analysis on smart contracts."""

    def __init__(self, evaluation_mode: bool = settings.evaluation_mode):
        """Initialize the static agent."""
        self.evaluation_mode = evaluation_mode

    async def analyze(self, contract_code: str):
        """Perform static analysis."""
        # TODO: Implement static analysis
        pass
