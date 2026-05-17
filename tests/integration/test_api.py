"""Integration tests for save_to_json and scrape_and_save (T039, T040)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from factor_lib.models import ProjectDetailRecord, ScrapeResult


def _make_detail(idx: int) -> ProjectDetailRecord:
    return ProjectDetailRecord(
        id=str(idx),
        name=f"Projeto {idx}",
        fields={"Coordenador": f"Person {idx}"},
        _source_url="https://portal.example",
        _scraped_at="2026-05-16T14:00:00",
    )


def _make_result(n: int = 3) -> ScrapeResult:
    recs = tuple(_make_detail(i) for i in range(n))
    return ScrapeResult(
        records=recs, total=n, success_count=n, error_count=0,
        started_at="2026-05-16T14:00:00", completed_at="2026-05-16T14:01:00"
    )


class TestSaveToJsonIntegration:
    def test_file_exists_after_save(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        out = tmp_path / "out.json"
        save_to_json([_make_detail(0)], out)
        assert out.exists()

    def test_output_is_valid_json(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        out = tmp_path / "out.json"
        save_to_json([_make_detail(0), _make_detail(1)], out)
        data = json.loads(out.read_text())
        assert isinstance(data, list)

    def test_record_count_matches(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        records = [_make_detail(i) for i in range(5)]
        out = tmp_path / "out.json"
        save_to_json(records, out)
        data = json.loads(out.read_text())
        assert len(data) == 5

    def test_overwrite_behavior(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        out = tmp_path / "out.json"
        save_to_json([_make_detail(0)], out)
        save_to_json([_make_detail(1), _make_detail(2)], out)
        data = json.loads(out.read_text())
        assert len(data) == 2


class TestScrapeAndSaveIntegration:
    def test_scrape_and_save_writes_file_and_returns_result(self, tmp_path: Path) -> None:
        from factor_lib.api import scrape_and_save
        mock_result = _make_result(3)

        with patch("factor_lib.api.scrape_all_projects", return_value=mock_result), \
             patch("factor_lib.api._save_result_to_json") as mock_save:
            out = tmp_path / "projects.json"
            result = scrape_and_save(out)

        assert result is mock_result
        mock_save.assert_called_once()

    def test_scrape_and_save_propagates_portal_error(self, tmp_path: Path) -> None:
        from factor_lib.api import scrape_and_save
        from factor_lib.exceptions import PortalNavigationError

        with patch("factor_lib.api.scrape_all_projects", side_effect=PortalNavigationError("fail")):
            with pytest.raises(PortalNavigationError):
                scrape_and_save(tmp_path / "out.json")
