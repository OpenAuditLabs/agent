"""FastAPI dependencies."""

import time
from typing import AsyncGenerator, Generator, Annotated, Optional

from fastapi import Request, Header, Depends
from pydantic import BaseModel

from oal_agent.telemetry.logging import logger


def get_db() -> Generator:
    """Database dependency."""
    # TODO: Implement database session
    yield None


def get_queue() -> Generator:
    """Queue dependency."""
    # TODO: Implement queue connection
    yield None


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
        logger.info("Request duration: %.4f seconds", duration)


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
    """
    return RequestMetadata(
        request_id=request_id,
        user_agent=user_agent,
        x_forwarded_for=x_forwarded_for,
    )
