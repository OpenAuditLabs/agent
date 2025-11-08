"""Sandboxing utilities."""

import resource
import sys


class Sandbox:
    """Provides sandboxed execution environment."""

    def __init__(self):
        """Initialize sandbox."""
        pass

    async def run(
        self,
        code: str,
        timeout: int = 30,
        cpu_time_limit: int | None = None,
        memory_limit: int | None = None,
    ):
        """Run code in sandbox with timeout and resource limits.

        Args:
            code: The code to execute.
            timeout: The maximum time in seconds the code is allowed to run.
            cpu_time_limit: The maximum CPU time in seconds the code is allowed to use.
            memory_limit: The maximum memory in bytes the code is allowed to use.
        """
        if sys.platform != "win32":
            if cpu_time_limit is not None:
                try:
                    resource.setrlimit(resource.RLIMIT_CPU, (cpu_time_limit, cpu_time_limit))
                except ValueError as e:
                    raise ValueError(f"Invalid CPU time limit: {e}") from e
                except Exception as e:
                    raise RuntimeError(f"Could not set CPU time limit: {e}") from e

            if memory_limit is not None:
                try:
                    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
                except ValueError as e:
                    raise ValueError(f"Invalid memory limit: {e}") from e
                except Exception as e:
                    raise RuntimeError(f"Could not set memory limit: {e}") from e
        else:
            if cpu_time_limit is not None or memory_limit is not None:
                print(
                    "Warning: CPU time and memory limits are not supported on Windows.",
                    file=sys.stderr,
                )
        # TODO: Implement sandboxed execution
        pass
