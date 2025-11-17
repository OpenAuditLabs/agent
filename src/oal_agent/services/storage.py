import asyncio
from pathlib import Path

import aiofiles

from oal_agent.core.errors import InvalidKey

"""Storage service."""


class StorageService:
    """Manages persistent storage."""

    def __init__(self, storage_path: str):
        """Initialize storage service."""
        self.storage_path = Path(storage_path).resolve()

    async def save(self, key: str, data: bytes):
        """Save data to storage."""
        if ".." in key or key.startswith("/"):
            raise InvalidKey("Key cannot contain '..' or start with '/'.")

        file_path = (self.storage_path / key).resolve()

        if not file_path.is_relative_to(self.storage_path):
            raise InvalidKey("Key leads to a path outside storage directory.")

        await asyncio.to_thread(file_path.parent.mkdir, parents=True, exist_ok=True)
        async with aiofiles.open(file_path, mode="wb") as f:
            await f.write(data)

    async def load(self, key: str):
        """Load data from storage."""
        if ".." in key or key.startswith("/"):
            raise InvalidKey("Key cannot contain '..' or start with '/'.")

        file_path = (self.storage_path / key).resolve()

        if not file_path.is_relative_to(self.storage_path):
            return None

        if not await asyncio.to_thread(file_path.exists):
            return None
        async with aiofiles.open(file_path, mode="rb") as f:
            return await f.read()
