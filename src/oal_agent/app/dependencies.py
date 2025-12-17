"""FastAPI dependencies."""

import contextvars
import time
import uuid
from typing import AsyncGenerator, Generator, Optional

from fastapi import Header
from pydantic import BaseModel

from oal_agent.telemetry.logging import logger
from oal_agent.services.queue import QueueService


def get_db() -> Generator:
    """Database dependency."""
    # TODO: Implement database session
    yield None



_queue_service: Optional[QueueService] = None

_request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)

def get_queue_service() -> QueueService:
    """Dependency that provides the QueueService instance."""
    if _queue_service is None:
        raise ValueError("QueueService has not been initialized.")
    return _queue_service



async def get_request_duration() -> AsyncGenerator[None, None]:
    """
    Dependency that records the duration of a request.
    Yields control (None) and logs the request duration as a side effect.
    """
    start_time = time.monotonic()
    try:
        yield
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        request_id = _request_id_ctx.get()
        logger.info("Request ID: %s, duration: %.4f seconds", request_id, duration)


class RequestMetadata(BaseModel):
    """
    Pydantic model to hold request ID and client metadata.
    """

    request_id: Optional[str] = None
    user_agent: Optional[str] = None
    x_forwarded_for: Optional[str] = None

    @property
    def client_ip(self) -> str | None:
        """
        Returns the client IP address, prioritizing X-Forwarded-For header.
        """
        if self.x_forwarded_for:
            return self.x_forwarded_for.split(",")[0].strip()
        return None


def get_request_metadata(
    request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    user_agent: Optional[str] = Header(None, alias="User-Agent"),
    x_forwarded_for: Optional[str] = Header(None, alias="X-Forwarded-For"),
) -> RequestMetadata:
    """
    Dependency that provides RequestMetadata to other dependencies and routers.
    Extracts or generates a request ID and propagates it to all downstream calls and logs.
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    _request_id_ctx.set(request_id)
    metadata = RequestMetadata(
        request_id=request_id,
        user_agent=user_agent,
        x_forwarded_for=x_forwarded_for,
    )
    logger.info(
        "Request ID: %s, Client IP: %s, User-Agent: %s",
        metadata.request_id,
        metadata.client_ip,
        metadata.user_agent,
    )
    return metadata
