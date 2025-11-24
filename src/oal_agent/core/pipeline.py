"""Pipeline definitions."""

from typing import Any, Awaitable, Callable, List

from oal_agent.app.schemas.jobs import PipelineArtifactsSummary
from oal_agent.telemetry.logging import logger
from oal_agent.utils.timing import timestamp


class Pipeline:
    """Analysis pipeline."""

    def __init__(
        self, name: str, steps: List[Callable[[dict[str, Any]], Awaitable[Any]]]
    ):
        """
        Initializes a pipeline.

        Args:
            name: The name of the pipeline.
            steps: A list of callable functions representing the pipeline steps.
        """
        self.name: str = name
        self.steps: List[Callable[[dict[str, Any]], Awaitable[Any]]] = steps

    async def execute(self, context: dict[str, Any]) -> PipelineArtifactsSummary:
        """Execute the pipeline.

        Args:
            context: The context dictionary to pass through the pipeline.
        """
        logger.debug("Pipeline '%s' started at %s", self.name, timestamp())
        artifacts_summary = PipelineArtifactsSummary()
        for i, step in enumerate(self.steps):
            step_name = step.__name__ if hasattr(step, "__name__") else f"step_{i}"
            start_time = timestamp()
            logger.debug(
                "Pipeline '%s' step '%s' started at %s",
                self.name,
                step_name,
                start_time,
            )
            await step(context)
            end_time = timestamp()
            elapsed_time = end_time - start_time
            logger.debug(
                "Pipeline '%s' step '%s' finished at %s, took %.2f seconds",
                self.name,
                step_name,
                end_time,
                elapsed_time,
            )
            # Collect artifacts from context
            if "logs" in context:
                artifacts_summary.logs.extend(context["logs"])
                del context["logs"]
            if "reports" in context:
                artifacts_summary.reports.extend(context["reports"])
                del context["reports"]

        logger.debug("Pipeline '%s' finished at %s", self.name, timestamp())
        return artifacts_summary
