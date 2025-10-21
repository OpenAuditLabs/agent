"""Mythril tool integration."""

import asyncio
import logging
import os
import tempfile

from oal_agent.tools.sandbox import execute_external_command

logger = logging.getLogger(__name__)


class MythrilTool:
    """Integration with Mythril symbolic analyzer."""

    def __init__(self):
        """Initialize Mythril tool."""
        pass

    async def analyze(self, contract_code: str):
        """Run Mythril analysis."""
        temp_file = None
        temp_path = None
        try:
            # Create a temporary file for the Solidity contract
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False)
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
                    logger.warning("Error cleaning up temporary file %s: %s", temp_path, e)

