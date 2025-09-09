"""
Minimal scoring engine used by AuditEngine._apply_scoring.

Provides a calculate_score(Finding) API with robust severity mapping.
"""

from __future__ import annotations

from typing import Any

try:
    from audit_engine.core.schemas import SeverityLevel  # type: ignore
except Exception:  # pragma: no cover
    # Fallback enum values if core is unavailable at import time
    class SeverityLevel:  # type: ignore
        CRITICAL = "Critical"
        MAJOR = "Major"
        MEDIUM = "Medium"
        MINOR = "Minor"
        INFORMATIONAL = "Informational"


class ScoringEngine:
    def __init__(self, config: Any | None = None):
        self.config = config or {}

    def calculate_score(self, finding: Any) -> float:
        sev_value = getattr(finding, "severity", None)
        sev_key = str(getattr(sev_value, "value", sev_value) or "medium").strip().lower()
        score_map = {
            "critical": 9.5,
            "high": 8.0,
            "major": 8.0,
            "medium": 6.0,
            "low": 3.0,
            "minor": 3.0,
            "informational": 1.0,
            "info": 1.0,
        }
        base = score_map.get(sev_key, 5.0)
        confidence = float(getattr(finding, "confidence", 0.5) or 0.5)
        return round(base * (0.6 + 0.4 * confidence), 2)




