import asyncio
import pytest
from pathlib import Path
import aiofiles
import pytest_asyncio

from src.oal_agent.services.storage import StorageService
from src.oal_agent.core.errors import InvalidKey

@pytest_asyncio.fixture
async def storage_service(tmp_path):
    storage_path = tmp_path / "test_storage"
    storage_path.mkdir()
    return StorageService(str(storage_path))

@pytest.mark.asyncio
async def test_save_and_load_valid_key(storage_service):
    key = "test_dir/test_file.txt"
    data = b"Hello, world!"

    await storage_service.save(key, data)
    loaded_data = await storage_service.load(key)

    assert loaded_data == data

@pytest.mark.asyncio
    with pytest.raises(InvalidKey, match=r"Key cannot contain '\.\.' or start with '/' "):
        await storage_service.save(key, data)

@pytest.mark.asyncio
async def test_save_invalid_key_absolute_path(storage_service):
    with pytest.raises(InvalidKey, match=r"Key cannot contain '\.\.' or start with '/' "):
        await storage_service.save(key, data)

@pytest.mark.asyncio
async def test_save_key_outside_storage_path(storage_service):
    key = "sub_dir/../../evil_file.txt"
    data = b"malicious content"

    with pytest.raises(InvalidKey, match=r"Key cannot contain '\.\.' or start with '/'"):
        await storage_service.save(key, data)

@pytest.mark.asyncio
async def test_load_invalid_key_dot_dot(storage_service):
    key = "../evil_file.txt"

    with pytest.raises(InvalidKey, match=r"Key cannot contain '\.\.' or start with '/' "):
        await storage_service.load(key)

@pytest.mark.asyncio
async def test_load_invalid_key_absolute_path(storage_service):
    with pytest.raises(InvalidKey, match=r"Key cannot contain '\.\.' or start with '/' "):
        await storage_service.load(key)

@pytest.mark.asyncio
async def test_load_key_outside_storage_path(storage_service):
    key = "sub_dir/../../evil_file.txt"

    with pytest.raises(InvalidKey, match="Key cannot contain '..' or start with '/\\.'"):
        await storage_service.load(key)

@pytest.mark.asyncio
async def test_load_non_existent_file(storage_service):
    key = "non_existent_file.txt"
    loaded_data = await storage_service.load(key)
    assert loaded_data is None

@pytest.mark.asyncio
async def test_save_nested_directory(storage_service):
    key = "level1/level2/file.txt"
    data = b"Nested content"
    await storage_service.save(key, data)
    loaded_data = await storage_service.load(key)
    assert loaded_data == data

@pytest.mark.asyncio
async def test_load_file_from_nested_directory(storage_service):
    key = "dir1/dir2/nested_file.txt"
    data = b"Nested file content"
    await storage_service.save(key, data)
    loaded_data = await storage_service.load(key)
    assert loaded_data == data

@pytest.mark.asyncio
async def test_save_empty_data(storage_service):
    key = "empty.txt"
    data = b""
    await storage_service.save(key, data)
    loaded_data = await storage_service.load(key)
    assert loaded_data == data

@pytest.mark.asyncio
async def test_overwrite_file(storage_service):
    key = "overwrite.txt"
    data1 = b"First content"
    data2 = b"Second content"

    await storage_service.save(key, data1)
    await storage_service.save(key, data2)
    loaded_data = await storage_service.load(key)
    assert loaded_data == data2

@pytest.mark.asyncio
async def test_storage_path_resolution(tmp_path):
    # Test with a relative path for storage_path during initialization
    relative_storage_path = "./my_storage"
    full_relative_path = tmp_path / relative_storage_path
    full_relative_path.mkdir()
    service = StorageService(str(full_relative_path))
    assert service.storage_path == full_relative_path.resolve()

    key = "test.txt"
    data = b"Relative path test"
    await service.save(key, data)
    loaded_data = await service.load(key)
    assert loaded_data == data

    # Test with an absolute path for storage_path during initialization
    absolute_storage_path = tmp_path / "abs_storage"
    absolute_storage_path.mkdir()
    service_abs = StorageService(str(absolute_storage_path))
    assert service_abs.storage_path == absolute_storage_path.resolve()

    key_abs = "test_abs.txt"
    data_abs = b"Absolute path test"
    await service_abs.save(key_abs, data_abs)
    loaded_data_abs = await service_abs.load(key_abs)
    assert loaded_data_abs == data_abs
