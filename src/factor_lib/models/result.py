"""Aggregate scrape result model."""
from __future__ import annotations

import dataclasses

from factor_lib.models.project import ProjectDetailRecord


@dataclasses.dataclass(frozen=True)
class ScrapeResult:
    """Aggregate output of a full scraping run."""

    records: tuple[ProjectDetailRecord, ...]
    total: int
    success_count: int
    error_count: int
    started_at: str
    completed_at: str
