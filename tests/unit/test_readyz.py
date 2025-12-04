from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from starlette import status

from src.oal_agent.app.main import app, queue_service, storage_service

client = TestClient(app)


def test_readyz_healthy():
    """
    Test the /readyz endpoint when both queue and storage services are healthy.
    """
    with (
        patch.object(
            queue_service, "check_health", new_callable=MagicMock
        ) as mock_queue_health,
        patch.object(
            storage_service, "check_health", new_callable=MagicMock
        ) as mock_storage_health,
    ):
        mock_queue_health.return_value = True
        mock_storage_health.return_value = True

        response = client.get("/readyz")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ready"}
        mock_queue_health.assert_called_once()
        mock_storage_health.assert_called_once()


def test_readyz_queue_unhealthy():
    """
    Test the /readyz endpoint when the queue service is unhealthy.
    """
    with (
        patch.object(
            queue_service, "check_health", new_callable=MagicMock
        ) as mock_queue_health,
        patch.object(
            storage_service, "check_health", new_callable=MagicMock
        ) as mock_storage_health,
    ):
        mock_queue_health.return_value = False
        mock_storage_health.return_value = True

        response = client.get("/readyz")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json() == {
            "status": "not ready",
            "dependencies": {"queue": "unhealthy"},
        }
        mock_queue_health.assert_called_once()
        mock_storage_health.assert_called_once()


def test_readyz_storage_unhealthy():
    """
    Test the /readyz endpoint when the storage service is unhealthy.
    """
    with (
        patch.object(
            queue_service, "check_health", new_callable=MagicMock
        ) as mock_queue_health,
        patch.object(
            storage_service, "check_health", new_callable=MagicMock
        ) as mock_storage_health,
    ):
        mock_queue_health.return_value = True
        mock_storage_health.return_value = False

        response = client.get("/readyz")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json() == {
            "status": "not ready",
            "dependencies": {"storage": "unhealthy"},
        }
        mock_queue_health.assert_called_once()
        mock_storage_health.assert_called_once()


def test_readyz_all_unhealthy():
    """
    Test the /readyz endpoint when both queue and storage services are unhealthy.
    """
    with (
        patch.object(
            queue_service, "check_health", new_callable=MagicMock
        ) as mock_queue_health,
        patch.object(
            storage_service, "check_health", new_callable=MagicMock
        ) as mock_storage_health,
    ):
        mock_queue_health.return_value = False
        mock_storage_health.return_value = False

        response = client.get("/readyz")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json() == {
            "status": "not ready",
            "dependencies": {"queue": "unhealthy", "storage": "unhealthy"},
        }
        mock_queue_health.assert_called_once()
        mock_storage_health.assert_called_once()
