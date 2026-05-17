"""Scraper data models for portal project listing and detail records."""
from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class ProjectListingRecord:
    """One row from the portal's project listing table."""

    id: str
    name: str
    raw_row: dict[str, str]


@dataclasses.dataclass(frozen=True)
class ProjectDetailRecord:
    """All scraped fields from a project's detail view."""

    id: str
    name: str
    fields: dict[str, str]
    _source_url: str
    _scraped_at: str
    _error: str | None = None
