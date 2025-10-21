"""Pipeline definitions."""

from typing import Callable, List


class Pipeline:
    """Analysis pipeline."""

    def __init__(self, name: str, steps: List[Callable[[dict, ...], None]]):
        """
        Initializes a pipeline.

        Args:
            name: The name of the pipeline.
            steps: A list of callable functions representing the pipeline steps.
        """
        self.name: str = name
        self.steps: List[Callable[[dict, ...], None]] = steps

    async def execute(self, context: dict[str, any]) -> None:
        """Execute the pipeline.

        Args:
            context: The context dictionary to pass through the pipeline.
        """
        # TODO: Implement pipeline execution
        pass
