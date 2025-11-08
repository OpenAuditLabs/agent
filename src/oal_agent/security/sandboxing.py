"""Sandboxing utilities."""

import sys
import subprocess
import os

try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False


class Sandbox:
    """Provides sandboxed execution environment."""

    def __init__(self):
        """Initialize sandbox."""
        pass

    def run(
        self,
        code: str,
        timeout: int = 30,
        cpu_time_limit: int | None = None,
        memory_limit: int | None = None,
    ) -> tuple[str, str]:
        """Run code in sandbox with timeout and resource limits.

        Args:
            code: The code to execute.
            timeout: The maximum time in seconds the code is allowed to run.
            cpu_time_limit: The maximum CPU time in seconds the code is allowed to use.
            memory_limit: The maximum memory in bytes the code is allowed to use.
        """
        if sys.platform == "win32":
            if cpu_time_limit is not None or memory_limit is not None:
                print(
                    "Warning: CPU time and memory limits are not supported on Windows.",
                    file=sys.stderr,
                )


        env = os.environ.copy()
        if cpu_time_limit is not None:
            env["OAL_CPU_TIME_LIMIT"] = str(cpu_time_limit)
        if memory_limit is not None:
            env["OAL_MEMORY_LIMIT"] = str(memory_limit)

        child_script = f"""
import sys
import os
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

if HAS_RESOURCE:
    cpu_limit_str = os.getenv("OAL_CPU_TIME_LIMIT")
    if cpu_limit_str:
        cpu_limit = int(cpu_limit_str)
        if cpu_limit < 0:
            print(f"Error: Invalid CPU time limit in child process: {{cpu_limit}} is negative", file=sys.stderr)
            sys.exit(1)
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
        except Exception as e:
            print(f"Error: Could not set CPU time limit in child process: {{e}}", file=sys.stderr)
            sys.exit(1)

    mem_limit_str = os.getenv("OAL_MEMORY_LIMIT")
    if mem_limit_str:
        mem_limit = int(mem_limit_str)
        if mem_limit < 0:
            print(f"Error: Invalid memory limit in child process: {{mem_limit}} is negative", file=sys.stderr)
            sys.exit(1)
        try:
            resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))
        except Exception as e:
            print(f"Error: Could not set memory limit in child process: {{e}}", file=sys.stderr)
            sys.exit(1)

exec({repr(code)})
"""

        process = subprocess.Popen(
            [sys.executable, "-c", child_script],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return (
                "",
                f"Error: Sandbox process timed out after {timeout} seconds.\n"
                f"Stdout: {stdout.decode()}\nStderr: {stderr.decode()}",
            )

        stdout_decoded = stdout.decode()
        stderr_decoded = stderr.decode()

        if process.returncode != 0:
            return (
                "",
                f"Error: Sandbox process exited with non-zero code {process.returncode}.\n"
                f"Stdout: {stdout_decoded}\nStderr: {stderr_decoded}",
            )

        return stdout_decoded, stderr_decoded
