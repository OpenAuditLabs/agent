"""Queue service for job management."""

import asyncio

from oal_agent.telemetry.logging import get_logger

logger = get_logger(__name__)


class QueueFullError(Exception):
    """Custom exception for when the queue is full."""

    pass


class QueueService:
    """Manages the job queue."""

    def __init__(self, queue_url: str, max_size: int = 0):
        """Initialize queue service."""
        self.queue_url = queue_url
        self.queue = asyncio.Queue(maxsize=max_size)
        self.worker_task = None

    async def enqueue(self, job_id: str, job_data: dict):
        """Add a job to the queue."""
        try:
            self.queue.put_nowait({"job_id": job_id, "job_data": job_data})
        except asyncio.QueueFull:
            raise QueueFullError("Queue is full, cannot enqueue job.")

    async def dequeue(self):
        """Get next job from queue."""
        return await self.queue.get()

    async def _worker(self):
        """Background worker to process jobs."""
        job = None  # Initialize job to None
        try:
            while True:
                job = await self.queue.get()
                try:
                    logger.debug("Processing job: %s", job["job_id"])
                    # Process the job here. For now, just acknowledge it.
                finally:
                    if (
                        job
                    ):  # Ensure task_done is only called if a job was actually obtained
                        self.queue.task_done()
                job = None  # Reset job after task_done
        except asyncio.CancelledError:
            logger.info("Worker cancelled, exiting gracefully")
            raise

    async def start(self):
        """Start the queue worker."""
        self.worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        """Stop the queue worker and drain the queue."""
        if self.worker_task:
            self.worker_task.cancel()
            await asyncio.gather(self.worker_task, return_exceptions=True)

        # Drain remaining items in the queue
        while not self.queue.empty():
            try:
                job = self.queue.get_nowait()
                logger.debug("Draining unacknowledged job: %s", job["job_id"])
                self.queue.task_done()
            except asyncio.QueueEmpty:
                break
        await self.queue.join()  # Wait until all jobs are processed
