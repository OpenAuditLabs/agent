import pytest
import aiofiles
from pathlib import Path

from src.oal_agent.services.storage import StorageService

@pytest.fixture
def storage_service(tmp_path: Path) -> StorageService:
    """Fixture for StorageService with a temporary storage path."""
    return StorageService(storage_path=str(tmp_path))

@pytest.mark.asyncio
async def test_save_and_load_data(storage_service: StorageService):
    """Test saving and loading data."""
    key = "test_key"
    data = b"test_data_content"

    await storage_service.save(key, data)
    loaded_data = await storage_service.load(key)

    assert loaded_data == data

@pytest.mark.asyncio
async def test_load_non_existent_data(storage_service: StorageService):
    """Test loading non-existent data."""
    key = "non_existent_key"
    loaded_data = await storage_service.load(key)

    assert loaded_data is None

@pytest.mark.asyncio
async def test_save_to_subfolder_and_load(storage_service: StorageService):
    """Test saving data to a subfolder and loading it."""
    key = "subfolder/nested/test_key"
    data = b"data_in_subfolder"

    await storage_service.save(key, data)
    loaded_data = await storage_service.load(key)

    assert loaded_data == data
    assert (Path(storage_service.storage_path) / key).exists()
