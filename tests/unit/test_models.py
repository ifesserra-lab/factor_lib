"""Unit tests for scraper models (T007–T009 — RED)."""
from __future__ import annotations

import pytest

from factor_lib.models import ProjectDetailRecord, ProjectListingRecord, ScrapeResult

# T007 — ProjectListingRecord

class TestProjectListingRecord:
    def test_is_frozen_dataclass(self) -> None:
        rec = ProjectListingRecord(id="12", name="Projeto X", raw_row={"col": "val"})
        with pytest.raises((AttributeError, TypeError)):
            rec.id = "other"  # type: ignore[misc]

    def test_required_fields(self) -> None:
        rec = ProjectListingRecord(id="12", name="Projeto X", raw_row={})
        assert rec.id == "12"
        assert rec.name == "Projeto X"
        assert rec.raw_row == {}

    def test_raw_row_can_have_entries(self) -> None:
        rec = ProjectListingRecord(id="1", name="N", raw_row={"Situação": "Em andamento"})
        assert rec.raw_row["Situação"] == "Em andamento"


# T008 — ProjectDetailRecord

class TestProjectDetailRecord:
    def test_is_frozen_dataclass(self) -> None:
        rec = ProjectDetailRecord(
            id="12", name="N", fields={}, _source_url="u", _scraped_at="2026-01-01T00:00:00"
        )
        with pytest.raises((AttributeError, TypeError)):
            rec.id = "other"  # type: ignore[misc]

    def test_error_defaults_to_none(self) -> None:
        rec = ProjectDetailRecord(
            id="1", name="N", fields={}, _source_url="u", _scraped_at="2026-01-01T00:00:00"
        )
        assert rec._error is None

    def test_error_can_be_set(self) -> None:
        rec = ProjectDetailRecord(
            id="1", name="N", fields={}, _source_url="u",
            _scraped_at="2026-01-01T00:00:00", _error="timeout"
        )
        assert rec._error == "timeout"

    def test_fields_stores_key_value_pairs(self) -> None:
        rec = ProjectDetailRecord(
            id="1", name="N",
            fields={"Coordenador": "João", "Valor": "100"},
            _source_url="u", _scraped_at="2026-01-01T00:00:00"
        )
        assert rec.fields["Coordenador"] == "João"

    def test_scraped_at_is_iso8601(self) -> None:
        ts = "2026-05-16T14:30:00"
        rec = ProjectDetailRecord(id="1", name="N", fields={}, _source_url="u", _scraped_at=ts)
        assert rec._scraped_at == ts


# T009 — ScrapeResult

class TestScrapeResult:
    def _make_records(self, n: int) -> tuple[ProjectDetailRecord, ...]:
        return tuple(
            ProjectDetailRecord(
                id=str(i), name=f"P{i}", fields={},
                _source_url="u", _scraped_at="2026-01-01T00:00:00"
            )
            for i in range(n)
        )

    def test_is_frozen_dataclass(self) -> None:
        r = ScrapeResult(
            records=(), total=0, success_count=0, error_count=0,
            started_at="2026-01-01T00:00:00", completed_at="2026-01-01T00:01:00"
        )
        with pytest.raises((AttributeError, TypeError)):
            r.total = 5  # type: ignore[misc]

    def test_total_equals_success_plus_error(self) -> None:
        recs = self._make_records(3)
        r = ScrapeResult(
            records=recs, total=3, success_count=2, error_count=1,
            started_at="2026-01-01T00:00:00", completed_at="2026-01-01T00:01:00"
        )
        assert r.total == r.success_count + r.error_count

    def test_records_length_equals_total(self) -> None:
        recs = self._make_records(5)
        r = ScrapeResult(
            records=recs, total=5, success_count=5, error_count=0,
            started_at="2026-01-01T00:00:00", completed_at="2026-01-01T00:01:00"
        )
        assert len(r.records) == r.total

    def test_empty_result(self) -> None:
        r = ScrapeResult(
            records=(), total=0, success_count=0, error_count=0,
            started_at="2026-01-01T00:00:00", completed_at="2026-01-01T00:00:00"
        )
        assert r.total == 0
