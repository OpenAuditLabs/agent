from typing import Any
from unittest.mock import AsyncMock

import pytest

from oal_agent.app.schemas.jobs import PipelineArtifactsSummary
from oal_agent.core.pipeline import Pipeline


@pytest.mark.asyncio
async def test_pipeline_executes_steps_and_returns_summary():
    """Test that the pipeline executes all steps and returns an artifact summary."""
    mock_step1 = AsyncMock(return_value=None)
    mock_step2 = AsyncMock(return_value=None)

    pipeline = Pipeline(name="test_pipeline", steps=[mock_step1, mock_step2])
    context = {}
    summary = await pipeline.execute(context)

    mock_step1.assert_called_once_with(context)
    mock_step2.assert_called_once_with(context)
    assert isinstance(summary, PipelineArtifactsSummary)
    assert summary.logs == []
    assert summary.reports == []


@pytest.mark.asyncio
async def test_pipeline_collects_artifacts_from_context():
    """Test that the pipeline correctly collects logs and reports from the context."""

    async def step_with_logs(context: dict[str, Any]) -> None:
        context.setdefault("logs", []).append("log_entry_1")
        context.setdefault("logs", []).append("log_entry_2")

    async def step_with_reports(context: dict[str, Any]) -> None:
        context.setdefault("reports", []).append("report_path_1.json")

    async def step_with_mixed_artifacts(context: dict[str, Any]) -> None:
        context.setdefault("logs", []).append("log_entry_3")
        context.setdefault("reports", []).append("report_path_2.pdf")

    pipeline = Pipeline(
        name="artifact_pipeline",
        steps=[step_with_logs, step_with_reports, step_with_mixed_artifacts],
    )
    context = {}
    summary = await pipeline.execute(context)

    assert isinstance(summary, PipelineArtifactsSummary)
    assert summary.logs == ["log_entry_1", "log_entry_2", "log_entry_3"]
    assert summary.reports == ["report_path_1.json", "report_path_2.pdf"]
    assert "logs" not in context  # Ensure artifacts are cleared from context
    assert "reports" not in context  # Ensure artifacts are cleared from context


@pytest.mark.asyncio
async def test_pipeline_handles_empty_artifacts():
    """Test that the pipeline returns an empty summary if no artifacts are produced."""

    async def empty_step(context: dict[str, Any]) -> None:
        pass

    pipeline = Pipeline(name="empty_artifact_pipeline", steps=[empty_step])
    context = {}
    summary = await pipeline.execute(context)

    assert isinstance(summary, PipelineArtifactsSummary)
    assert summary.logs == []
    assert summary.reports == []
    assert "logs" not in context
    assert "reports" not in context
