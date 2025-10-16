"""Queue service for job management."""

import asyncio

class QueueFullError(Exception):
    """Custom exception for when the queue is full."""
    pass

class QueueService:
    """Manages the job queue."""

    def __init__(self, queue_url: str, max_size: int = 0):
        """Initialize queue service."""
        self.queue_url = queue_url
        self.queue = asyncio.Queue(maxsize=max_size)

    async def enqueue(self, job_id: str, job_data: dict):
        """Add a job to the queue."""
        try:
            self.queue.put_nowait({"job_id": job_id, "job_data": job_data})
        except asyncio.QueueFull:
            raise QueueFullError("Queue is full, cannot enqueue job.")

    async def dequeue(self):
        """Get next job from queue."""
        return await self.queue.get()