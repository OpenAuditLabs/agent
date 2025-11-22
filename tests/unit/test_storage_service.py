import aiofiles
import pytest
import pytest_asyncio

from src.oal_agent.core.config import reset_settings
from src.oal_agent.core.errors import DecryptionError, InvalidKey
from src.oal_agent.services.storage import StorageService


@pytest.mark.asyncio
async def test_storage_service_init_encryption_enabled_no_key(tmp_path, monkeypatch):
    # Mock settings.storage_encryption_enabled at its import path
    monkeypatch.setattr(
        "src.oal_agent.services.storage.settings", "storage_encryption_enabled", True
    )
    storage_path = tmp_path / "test_storage_enc_no_key"
    storage_path.mkdir()
    with pytest.raises(
        ValueError,
        match="Encryption key must be provided when storage encryption is enabled.",
    ):
        StorageService(str(storage_path), encryption_key=None)


@pytest_asyncio.fixture
async def unencrypted_storage_service_with_key(tmp_path, monkeypatch):
    # Mock settings.storage_encryption_enabled at its import path
    monkeypatch.setattr(
        "src.oal_agent.services.storage.settings", "storage_encryption_enabled", False
    )
    encryption_key = b"a_key_that_should_be_ignored_by_fixture"
    storage_path = tmp_path / "unencrypted_test_storage_with_key"
    storage_path.mkdir()
    service = StorageService(str(storage_path), encryption_key=encryption_key)
    yield service


@pytest_asyncio.fixture
async def encrypted_storage_service(tmp_path, monkeypatch):
    # Mock settings.storage_encryption_enabled at its import path
    monkeypatch.setattr(
        "src.oal_agent.services.storage.settings", "storage_encryption_enabled", True
    )
    encryption_key = b"a_fixture_secret_key_for_testing"
    storage_path = tmp_path / "encrypted_test_storage"
    storage_path.mkdir()
    service = StorageService(str(storage_path), encryption_key=encryption_key)
    yield service


@pytest_asyncio.fixture
async def storage_service(tmp_path):
    storage_path = tmp_path / "test_storage"
    storage_path.mkdir()
    return StorageService(str(storage_path))


@pytest.mark.asyncio
async def test_load_decryption_error_corrupted_data(encrypted_storage_service):
    service = encrypted_storage_service
    storage_path = service.storage_path

    key = "corrupted_file.txt"
    data = b"Original data to be corrupted."
    await service.save(key, data)

    # Manually corrupt the encrypted file
    file_path = storage_path / key
    async with aiofiles.open(file_path, mode="rb") as f:
        encrypted_data = await f.read()

    corrupted_data = encrypted_data[:-5] + b"CORRUPT"  # Tamper with the last few bytes
    async with aiofiles.open(file_path, mode="wb") as f:
        await f.write(corrupted_data)

    with pytest.raises(DecryptionError, match="Decryption failed."):
        await service.load(key)


@pytest.mark.asyncio
async def test_storage_service_init_encryption_disabled_with_key(
    unencrypted_storage_service_with_key,
):
    service = unencrypted_storage_service_with_key
    storage_path = service.storage_path

    key = "unencrypted_file.txt"
    data = b"This data should NOT be encrypted at rest."
    await service.save(key, data)

    # Verify that the file content is the same as the original data (i.e., unencrypted)
    file_path = storage_path / key
    async with aiofiles.open(file_path, mode="rb") as f:
        unencrypted_data = await f.read()
    assert unencrypted_data == data

    loaded_data = await service.load(key)
    assert loaded_data == data


@pytest.mark.asyncio
async def test_storage_service_init_encryption_enabled_with_key(
    encrypted_storage_service,
):
    service = encrypted_storage_service
    storage_path = service.storage_path

    key = "encrypted_file.txt"
    data = b"This data should be encrypted at rest."
    await service.save(key, data)

    # Verify that the file content is different from the original data (i.e., encrypted)
    file_path = storage_path / key
    async with aiofiles.open(file_path, mode="rb") as f:
        encrypted_data = await f.read()
    assert encrypted_data != data
    assert len(encrypted_data) > len(
        data
    )  # Encrypted data should be longer due to nonce/tag

    loaded_data = await service.load(key)
    assert loaded_data == data


@pytest.mark.asyncio
async def test_save_and_load_valid_key(storage_service):
    key = "test_dir/test_file.txt"
    data = b"Hello, world!"

    await storage_service.save(key, data)
    loaded_data = await storage_service.load(key)

    assert loaded_data == data


@pytest.mark.asyncio
async def test_save_rejects_invalid_key_dotdot(storage_service):
    key = "../invalid/key"
    data = b"sample data"
    with pytest.raises(InvalidKey, match="Key cannot contain '..' or start '/'."):
        await storage_service.save(key, data)


@pytest.mark.asyncio
async def test_save_invalid_key_absolute_path(storage_service):
    key = "/absolute/path"
    data = b"sample data"
    with pytest.raises(InvalidKey, match="Key cannot contain '..' or start '/'."):
        await storage_service.save(key, data)


@pytest.mark.asyncio
async def test_save_key_outside_storage_path(storage_service):
    key = "sub_dir/../../evil_file.txt"
    data = b"malicious content"
    with pytest.raises(InvalidKey, match="Key cannot contain '..' or start '/'."):
        await storage_service.save(key, data)


@pytest.mark.asyncio
async def test_load_invalid_key_dot_dot(storage_service):
    key = "../secret"
    with pytest.raises(InvalidKey, match="Key cannot contain '..' or start '/'."):
        await storage_service.load(key)


@pytest.mark.asyncio
async def test_load_invalid_key_absolute_path(storage_service):
    key = "/invalid/path"
    with pytest.raises(InvalidKey, match="Key cannot contain '..' or start '/'."):
        await storage_service.load(key)


@pytest.mark.asyncio
async def test_load_key_outside_storage_path(storage_service):
    key = "sub_dir/../../evil_file.txt"
    with pytest.raises(InvalidKey, match="Key cannot contain '..' or start '/'."):
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
