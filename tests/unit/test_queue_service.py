import pytest
import asyncio
from src.oal_agent.services.queue import QueueService, QueueFullError
from src.oal_agent.core.config import settings

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
