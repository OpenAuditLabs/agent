import asyncio
import secrets
from pathlib import Path
from typing import Optional

import aiofiles
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from oal_agent.core.config import settings
from oal_agent.core.errors import DecryptionError, InvalidKey

"""Storage service."""


class StorageService:
    """Manages persistent storage, with optional at-rest encryption.

    To enable encryption, set `STORAGE_ENCRYPTION_ENABLED=true` in your environment
    or configuration, and provide an `encryption_key` during initialization.
    """

    def __init__(self, storage_path: str, encryption_key: Optional[bytes] = None):
        self.storage_path = Path(storage_path).resolve()
        self.encryption_key = encryption_key
        self._derived_key = None

        if settings.storage_encryption_enabled:
            if not self.encryption_key:
                raise ValueError(
                    "Encryption key must be provided when storage encryption is enabled."
                )
            salt = b"OpenAuditLabs_Storage_v1"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
                backend=default_backend(),
            )
            self._derived_key = kdf.derive(self.encryption_key)

    def _encrypt(self, data: bytes) -> bytes:
        """Encrypt data using AES-256-GCM."""
        if not self._derived_key:
            return data

        aesgcm = AESGCM(self._derived_key)
        nonce = secrets.token_bytes(12)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def _decrypt(self, data: bytes) -> bytes:
        """Decrypt data using AES-256-GCM."""
        if not self._derived_key:
            return data

        if len(data) < 12:  # 12 bytes nonce
            raise DecryptionError(message="Ciphertext too short.")

        nonce = data[:12]
        ciphertext = data[12:]

        aesgcm = AESGCM(self._derived_key)
        try:
            return aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            raise DecryptionError(message="Decryption failed.") from e

    async def save(self, key: str, data: bytes):
        """Save data to storage. If encryption is enabled, data will be encrypted at rest."""
        if ".." in key or key.startswith("/"):
            raise InvalidKey(message="Key cannot contain '..' or start '/'.")

        file_path = (self.storage_path / key).resolve()

        if not file_path.is_relative_to(self.storage_path):
            raise InvalidKey(message="Key leads to a path outside storage directory.")

        if settings.storage_encryption_enabled and self.encryption_key:
            data = self._encrypt(data)

        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_path, mode="wb") as f:
            await f.write(data)

    async def load(self, key: str):
        """Load data from storage. If encryption is enabled, data will be decrypted after loading."""
        if ".." in key or key.startswith("/"):
            raise InvalidKey(message="Key cannot contain '..' or start '/'.")

        file_path = (self.storage_path / key).resolve()

        if not file_path.is_relative_to(self.storage_path):
            raise InvalidKey(message="Key leads to a path outside storage directory.")

        if not await asyncio.to_thread(file_path.exists):
            return None
        async with aiofiles.open(file_path, mode="rb") as f:
            data = await f.read()

        if settings.storage_encryption_enabled and self.encryption_key:
            data = self._decrypt(data)

        return data
