import asyncio
import os
import secrets
from pathlib import Path
from typing import Optional

import aiofiles
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from oal_agent.core.config import settings
from oal_agent.core.errors import InvalidKey, DecryptionError

"""Storage service."""


class StorageService:
    """Manages persistent storage, with optional at-rest encryption.

    To enable encryption, set `STORAGE_ENCRYPTION_ENABLED=true` in your environment
    or configuration, and provide an `encryption_key` during initialization.
    """

    def __init__(self, storage_path: str, encryption_key: Optional[bytes] = None):
        """Initialize storage service.

        Args:
            storage_path: The base path for storing files.
            encryption_key: An optional key for at-rest encryption. Required if encryption is enabled.
        """
        self.storage_path = Path(storage_path).resolve()
        self.encryption_key = encryption_key

        if settings.storage_encryption_enabled and not self.encryption_key:
            raise ValueError("Encryption key must be provided when storage encryption is enabled.")

    def _derive_key(self, key: bytes, salt: bytes) -> bytes:
        """Derive a fixed-size key from the provided encryption key using PBKDF2HMAC."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=default_backend()
        )
        return kdf.derive(key)

    def _encrypt(self, data: bytes) -> bytes:
        """Encrypt data using AES-256-GCM."""
        if not self.encryption_key:
            return data

        salt = os.urandom(16)
        derived_key = self._derive_key(self.encryption_key, salt)
        aesgcm = AESGCM(derived_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return salt + nonce + ciphertext

    def _decrypt(self, data: bytes) -> bytes:
        """Decrypt data using AES-256-GCM."""
        if not self.encryption_key:
            return data

        if len(data) < 28:  # 16 bytes salt + 12 bytes nonce
            raise DecryptionError("Ciphertext too short for decryption.")

        salt = data[:16]
        nonce = data[16:28]
        ciphertext = data[28:]

        derived_key = self._derive_key(self.encryption_key, salt)
        aesgcm = AESGCM(derived_key)
        try:
            return aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            raise DecryptionError("Decryption failed: Invalid key or corrupted data.") from e

    async def save(self, key: str, data: bytes):
        """Save data to storage. If encryption is enabled, data will be encrypted at rest."""
        if ".." in key or key.startswith("/"):
            raise InvalidKey("Key cannot contain '..' or start '/'.")

        file_path = (self.storage_path / key).resolve()

        if not file_path.is_relative_to(self.storage_path):
            raise InvalidKey("Key leads to a path outside storage directory.")

        if settings.storage_encryption_enabled and self.encryption_key:
            data = self._encrypt(data)

        await asyncio.to_thread(file_path.parent.mkdir, parents=True, exist_ok=True)
        async with aiofiles.open(file_path, mode="wb") as f:
            await f.write(data)

    async def load(self, key: str):
        """Load data from storage. If encryption is enabled, data will be decrypted after loading."""
        if ".." in key or key.startswith("/"):
            raise InvalidKey("Key cannot contain '..' or start '/'.")

        file_path = (self.storage_path / key).resolve()

        if not file_path.is_relative_to(self.storage_path):
            raise InvalidKey("Key leads to a path outside storage directory.")

        if not await asyncio.to_thread(file_path.exists):
            return None
        async with aiofiles.open(file_path, mode="rb") as f:
            data = await f.read()

        if settings.storage_encryption_enabled and self.encryption_key:
            data = self._decrypt(data)

        return data
