"""Storage service."""


class StorageService:
    """Manages persistent storage."""

    def __init__(self, storage_path: str):
        """Initialize storage service."""
        self.storage_path = storage_path

    async def save(self, key: str, data: bytes):
        """Save data to storage."""
        # TODO: Implement storage save
        pass

    async def load(self, key: str):
        """Load data from storage."""
        # TODO: Implement storage load
        pass
