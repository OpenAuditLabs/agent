"""Mythril tool integration."""

import asyncio
import logging
import os
import tempfile
import re
import shutil
import subprocess

from oal_agent.tools.sandbox import execute_external_command, SandboxResult

logger = logging.getLogger(__name__)

SUPPORTED_MYTHRIL_VERSION_PREFIX = "0.24"


class MythrilTool:
    """Integration with Mythril symbolic analyzer."""

    def __init__(self):
        """Initialize Mythril tool."""
        self._check_mythril_version()

    def _check_mythril_version(self):
        """Check Mythril version and warn if unsupported."""
        myth_path = shutil.which("myth")
        if not myth_path:
            logger.error(
                "Mythril command not found. Please ensure Mythril is installed and in your PATH."
            )
            raise RuntimeError("Mythril executable not found.")

        try:
            result = subprocess.run(
                [myth_path, "--version"], capture_output=True, text=True, check=True
            )
            version_output = result.stdout.strip()
            match = re.search(r"Mythril version (\d+\.\d+\.\d+)", version_output)
            if match:
                version = match.group(1)
                if not version.startswith(SUPPORTED_MYTHRIL_VERSION_PREFIX):
                    logger.warning(
                        "Unsupported Mythril version detected: %s. Expected version starting with %s.",
                        version,
                        SUPPORTED_MYTHRIL_VERSION_PREFIX,
                    )
                else:
                    logger.info("Mythril version %s detected (supported).", version)
            else:
                logger.warning(
                    "Could not parse Mythril version from output: %s", version_output
                )
        except subprocess.CalledProcessError as e:
            logger.exception(
                "Error checking Mythril version: %s - %s", e, e.stderr.strip()
            )
            raise RuntimeError("Failed to check Mythril version.") from e
        except Exception as e:
            logger.exception("An unexpected error occurred during Mythril version check.")
            raise RuntimeError("An unexpected error occurred during Mythril version check.") from e

    async def analyze(self, contract_code: str) -> SandboxResult:
        """Run Mythril analysis."""
        temp_file = None
        temp_path = None
        try:
            # Create a temporary file for the Solidity contract
            temp_file = tempfile.NamedTemporaryFile(
                mode="w", suffix=".sol", delete=False
            )
            temp_path = temp_file.name

            # Write contract_code into the temporary file
            await asyncio.to_thread(temp_file.write, contract_code)
            temp_file.close()  # Close the file so Mythril can read it

            # Set restrictive file permissions
            os.chmod(temp_path, 0o600)

            # Call execute_external_command with the temporary file path
            result = await execute_external_command("myth", "analyze", temp_path)
            return result
        except Exception as e:
            # Propagate or wrap exceptions with informative messages
            raise RuntimeError(f"Mythril analysis failed: {e}") from e
        finally:
            # Ensure the temporary file is removed
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError as e:
                    # Log the error if cleanup fails, but do not swallow the original exception
                    logger.warning(
                        "Error cleaning up temporary file %s: %s", temp_path, e
                    )
