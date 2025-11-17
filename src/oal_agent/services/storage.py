from pathlib import Path
import aiofiles

"""Storage service."""


class StorageService:
    """Manages persistent storage."""

    def __init__(self, storage_path: str):
        """Initialize storage service."""
        self.storage_path = storage_path

    async def save(self, key: str, data: bytes):
        """Save data to storage."""
        file_path = Path(self.storage_path) / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_path, mode="wb") as f:
            await f.write(data)

    async def load(self, key: str):
        """Load data from storage."""
        file_path = Path(self.storage_path) / key
        if not file_path.exists():
            return None
        async with aiofiles.open(file_path, mode="rb") as f:
            return await f.read()
