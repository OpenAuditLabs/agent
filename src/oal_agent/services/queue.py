"""Queue service for job management."""

import asyncio
import time
from typing import Any, Dict, Optional

from oal_agent.core.orchestrator import Orchestrator
from oal_agent.telemetry.logging import get_logger
from oal_agent.telemetry.metrics import metrics

logger = get_logger(__name__)


class QueueFullError(Exception):
    """Custom exception for when the queue is full."""

    pass


class QueueService:
    """Manages the job queue."""

    def __init__(self, queue_url: str, max_size: int = 0):
        """Initialize queue service."""
        self.queue_url = queue_url
        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=max_size)
        self.worker_task = None
        self.orchestrator = Orchestrator()

    async def enqueue(self, job_id: str, job_data: dict):
        """Add a job to the queue."""
        try:
            self.queue.put_nowait({"job_id": job_id, "job_data": job_data})
            metrics.gauge("queue_depth", self.queue.qsize())
        except asyncio.QueueFull:
            raise QueueFullError("Queue is full, cannot enqueue job.")

    async def dequeue(self):
        """Get next job from queue."""
        return await self.queue.get()

    async def _worker(self):
        """Background worker to process jobs."""
        job: Optional[Dict[str, Any]] = None  # Initialize job to None
        try:
            while True:
                metrics.gauge("queue_depth", self.queue.qsize())
                job = await self.queue.get()
                start_time = time.time()
                try:
                    logger.debug("Processing job: %s", job["job_id"])
                    await self.orchestrator.orchestrate(job["job_id"], job["job_data"])
                except Exception:
                    metrics.increment("queue_processing_errors_total")
                    logger.exception("Error processing job: %s", job["job_id"])
                finally:
                    if (
                        job
                    ):  # Ensure task_done is only called if a job was actually obtained
                        self.queue.task_done()
                        metrics.gauge("queue_depth", self.queue.qsize())
                        processing_time = time.time() - start_time
                        metrics.gauge("queue_processing_time_seconds", processing_time)
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
                metrics.gauge("queue_depth", self.queue.qsize())
            except asyncio.QueueEmpty:
                break
        await self.queue.join()  # Wait until all jobs are processed

    async def check_health(self) -> bool:
        """Checks the health of the queue service.

        For an in-memory queue, this simply returns True if the queue is initialized.
        For an external queue (e.g., Redis), this would involve pinging the external service.
        """
        logger.debug("Checking queue service health...")
        # In a real-world scenario with an external queue (e.g., Redis), you'd ping it here.
        # For an in-memory asyncio.Queue, we assume it's healthy if the app is running.
        return True

