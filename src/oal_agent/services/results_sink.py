"""Results sink service."""

import json
import asyncio
import aiofiles
from pathlib import Path


class ResultsSink:
    """Collects and stores analysis results."""

    RESULTS_DIR = Path("data/datasets")  # Using existing data/datasets for now

    def __init__(self):
        """Initialize results sink."""
        self.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    async def store(self, job_id: str, results: dict):
        """Store analysis results asynchronously."""
        file_path = self.RESULTS_DIR / f"{job_id}.json"
        async with aiofiles.open(file_path, mode="w") as f:
            await f.write(json.dumps(results, indent=4))

    async def retrieve(self, job_id: str) -> dict:
        """Retrieve analysis results asynchronously."""
        file_path = self.RESULTS_DIR / f"{job_id}.json"
        if not file_path.exists():
            return {}
        async with aiofiles.open(file_path, mode="r") as f:
            content = await f.read()
            return json.loads(content)

    def store_sync(self, job_id: str, results: dict):
        """Store analysis results synchronously."""
        asyncio.run(self.store(job_id, results))

    def retrieve_sync(self, job_id: str) -> dict:
        """Retrieve analysis results synchronously."""
        return asyncio.run(self.retrieve(job_id))
