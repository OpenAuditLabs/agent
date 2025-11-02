import asyncio
from unittest import mock

import pytest

from src.oal_agent.core.config import settings
from src.oal_agent.services.queue import QueueFullError, QueueService


@pytest.mark.asyncio
async def test_enqueue_dequeue():
    """Test basic enqueue and dequeue functionality."""
    queue_service = QueueService(queue_url="test_url", max_size=2)
    await queue_service.enqueue("job1", {"data": "test1"})
    await queue_service.enqueue("job2", {"data": "test2"})

    job = await queue_service.dequeue()
    assert job["job_id"] == "job1"
    assert job["job_data"] == {"data": "test1"}

    job = await queue_service.dequeue()
    assert job["job_id"] == "job2"
    assert job["job_data"] == {"data": "test2"}


@pytest.mark.asyncio
async def test_queue_full_error():
    """Test that QueueFullError is raised when queue is full."""
    queue_service = QueueService(queue_url="test_url", max_size=1)
    await queue_service.enqueue("job1", {"data": "test1"})

    with pytest.raises(QueueFullError):
        await queue_service.enqueue("job2", {"data": "test2"})


@pytest.mark.asyncio
async def test_queue_max_size_from_config():
    """Test that max_size is correctly picked up from config."""
    # Temporarily override the setting for this test
    original_max_size = settings.queue_max_size
    settings.queue_max_size = 1

    queue_service = QueueService(queue_url="test_url", max_size=settings.queue_max_size)
    await queue_service.enqueue("job1", {"data": "test1"})

    with pytest.raises(QueueFullError):
        await queue_service.enqueue("job2", {"data": "test2"})

    # Restore original setting
    settings.queue_max_size = original_max_size


@pytest.mark.asyncio
async def test_stop_with_cancellation_and_draining():
    """Test that stop() gracefully cancels worker, drains queue, and calls task_done."""
    queue_service = QueueService(queue_url="test_url", max_size=5)
    await queue_service.start()

    # Enqueue some jobs
    for i in range(3):
        await queue_service.enqueue(f"job{i}", {"data": f"test{i}"})

    # Allow worker to pick up some jobs (but not necessarily process all)
    await asyncio.sleep(0.01)

    # Stop the queue service
    await queue_service.stop()

    # Assert that the queue is empty and all tasks are done
    assert queue_service.queue.empty()
    assert queue_service.queue.qsize() == 0

    # Verify that the worker task is cancelled and finished
    assert queue_service.worker_task.done()
    with pytest.raises(asyncio.CancelledError):
        await queue_service.worker_task


@pytest.mark.asyncio
async def test_queue_processing_time_metric():
    """Test that queue processing time metric is recorded."""
    with mock.patch("src.oal_agent.services.queue.metrics") as mock_metrics:
        queue_service = QueueService(queue_url="test_url", max_size=1)
        await queue_service.start()

        await queue_service.enqueue("job1", {"data": "test1"})
        await queue_service.queue.join()  # Wait for the job to be processed

        await queue_service.stop()

        mock_metrics.gauge.assert_called_once()
        assert mock_metrics.gauge.call_args[0][0] == "queue_processing_time_seconds"
        assert mock_metrics.gauge.call_args[0][1] > 0


@pytest.mark.asyncio
async def test_queue_processing_error_metric():
    """Test that queue processing error metric is recorded."""
    with mock.patch("src.oal_agent.services.queue.metrics") as mock_metrics:
        queue_service = QueueService(queue_url="test_url", max_size=1)

        # Mock the internal processing to raise an exception
        def mock_process_job(*args, **kwargs):
            raise ValueError("Simulated processing error")

        # Patch the logger.debug call within the _worker to simulate an error
        with mock.patch(
            "src.oal_agent.services.queue.logger.debug", side_effect=mock_process_job
        ):
            await queue_service.start()
            await queue_service.enqueue("job1", {"data": "test1"})
            await queue_service.queue.join()  # Wait for the job to be processed
            await queue_service.stop()

        mock_metrics.increment.assert_called_once_with("queue_processing_errors_total")
