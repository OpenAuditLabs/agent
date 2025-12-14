"""Queue service for job management."""

import asyncio
import time
from typing import Any, Dict, Optional

from oal_agent.app.schemas.results import AnalysisStatus
from oal_agent.services.results_sink import ResultsSink
from oal_agent.core.orchestrator import Orchestrator
from oal_agent.telemetry.logging import get_logger
from oal_agent.telemetry.metrics import metrics

logger = get_logger(__name__)


class QueueFullError(Exception):
    """Custom exception for when the queue is full."""

    pass


class JobNotFoundError(Exception):
    """Custom exception for when a job is not found in the queue."""

    pass


class QueueService:
    """Manages the job queue."""

    def __init__(self, queue_url: str, max_size: int = 0):
        """Initialize queue service."""
        self.queue_url = queue_url
        self.queue: asyncio.PriorityQueue[tuple[int, Dict[str, Any]]] = asyncio.PriorityQueue(maxsize=max_size)
        self.worker_task = None
        self.orchestrator = Orchestrator()
        self.processing_jobs: Dict[str, asyncio.Task] = {}
        self._pending_jobs: set[str] = set()
        self.results_sink = ResultsSink()

    async def enqueue(self, job_id: str, job_data: dict, priority: int = 0):
        """Add a job to the queue with a given priority. Lower numbers mean higher priority."""
        try:
            self.queue.put_nowait((priority, {"job_id": job_id, "job_data": job_data}))
            self._pending_jobs.add(job_id)
            metrics.gauge("queue_depth", self.queue.qsize())
        except asyncio.QueueFull:
            raise QueueFullError("Queue is full, cannot enqueue job.")

    async def dequeue(self) -> Dict[str, Any]:
        """Get next job from queue, returning only the job data."""
        priority, job = await self.queue.get()
        self._pending_jobs.discard(job["job_id"])
        return job

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job by its ID."""
        logger.info("Attempting to cancel job: %s", job_id)
        if job_id in self.processing_jobs:
            # Job is currently being processed
            task = self.processing_jobs.pop(job_id)
            task.cancel()
            logger.info("Cancelled currently processing job: %s", job_id)
            await self.results_sink.update_status(job_id, AnalysisStatus.CANCELLED)
            return True
        elif job_id in self._pending_jobs:
            # Job is in the queue, remove it
            # Create a new queue without the cancelled job
            new_queue: asyncio.PriorityQueue[tuple[int, Dict[str, Any]]] = asyncio.PriorityQueue(maxsize=self.queue.maxsize)
            found = False
            while not self.queue.empty():
                priority, job = await self.queue.get()
                if job["job_id"] == job_id:
                    found = True
                    self._pending_jobs.discard(job_id)
                    logger.info("Removed pending job from queue: %s", job_id)
                else:
                    await new_queue.put((priority, job))
            self.queue = new_queue
            if found:
                await self.results_sink.update_status(job_id, AnalysisStatus.CANCELLED)
                metrics.gauge("queue_depth", self.queue.qsize())
                return True
        logger.warning("Job %s not found for cancellation.", job_id)
        return False

    async def _worker(self):
        """Background worker to process jobs."""
        while True:
            job_item: Optional[tuple[int, Dict[str, Any]]] = None
            job_id: Optional[str] = None
            processing_task: Optional[asyncio.Task] = None
            try:
                metrics.gauge("queue_depth", self.queue.qsize())
                job_item = await self.queue.get()
                _priority, job = job_item
                job_id = job["job_id"]

                # Create a task for processing this specific job
                async def process_single_job():
                    start_time = time.time()
                    try:
                        logger.debug("Processing job: %s", job_id)
                        await self.results_sink.update_status(job_id, AnalysisStatus.RUNNING)
                        await self.orchestrator.orchestrate(job_id, job["job_data"])
                        await self.results_sink.update_status(job_id, AnalysisStatus.COMPLETED)
                    except asyncio.CancelledError:
                        logger.info("Job %s was cancelled during processing.", job_id)
                        await self.results_sink.update_status(job_id, AnalysisStatus.CANCELLED)
                    except Exception:
                        metrics.increment("queue_processing_errors_total")
                        logger.exception("Error processing job: %s", job_id)
                        await self.results_sink.update_status(job_id, AnalysisStatus.FAILED)
                    finally:
                        self.queue.task_done()
                        metrics.gauge("queue_depth", self.queue.qsize())
                        processing_time = time.time() - start_time
                        metrics.gauge("queue_processing_time_seconds", processing_time)

                processing_task = asyncio.create_task(process_single_job())
                self.processing_jobs[job_id] = processing_task
                await processing_task  # Wait for the single job to complete or be cancelled
            except asyncio.CancelledError:
                logger.info("Worker cancelled, exiting gracefully")
                # If the worker itself is cancelled, ensure any currently processing job is also cleaned up
                if job_id and job_id in self.processing_jobs:
                    task_to_cancel = self.processing_jobs.pop(job_id)
                    task_to_cancel.cancel()
                    # No need to await, as we are exiting
                raise
            except Exception:
                logger.exception("Error in queue worker loop.")
            finally:
                if job_id and job_id in self.processing_jobs:
                    # Clean up if the job completed normally and was still in processing_jobs
                    self.processing_jobs.pop(job_id, None)

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
                _priority, job = self.queue.get_nowait()
                logger.debug("Draining unacknowledged job: %s", job["job_id"])
                self.queue.task_done()
                metrics.gauge("queue_depth", self.queue.qsize())
            except asyncio.QueueEmpty:
                break
        await self.queue.join()  # Wait until all jobs are processed

    def check_health(self) -> bool:
        """Checks the health of the queue service.

        This method should never raise an exception. Instead, it should return `False`
        if the queue service is unhealthy, and `True` otherwise.
        For an in-memory queue, this simply returns True if the queue is initialized.
        For an external queue (e.g., Redis), this would involve pinging the external service.
        """
        logger.debug("Checking queue service health...")
        # In a real-world scenario with an external queue (e.g., Redis), you'd ping it here.
        # For an in-memory asyncio.Queue, we assume it's healthy if the app is running.
        return True
