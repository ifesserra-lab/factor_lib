"""Unit tests for json_serializer with scraper models (T038 — RED)."""
from __future__ import annotations

import json
from pathlib import Path

from factor_lib.models import ProjectDetailRecord, ScrapeResult


def _make_record(
    idx: int = 0, *, error: str | None = None, fields: dict | None = None
) -> ProjectDetailRecord:
    return ProjectDetailRecord(
        id=str(idx),
        name=f"Projeto {idx}",
        fields=fields or {"Coordenador": "João", "Valor": "100"},
        _source_url="https://portal.example",
        _scraped_at="2026-05-16T14:00:00",
        _error=error,
    )


def _make_result(n: int = 2) -> ScrapeResult:
    recs = tuple(_make_record(i) for i in range(n))
    return ScrapeResult(
        records=recs, total=n, success_count=n, error_count=0,
        started_at="2026-05-16T14:00:00", completed_at="2026-05-16T14:01:00"
    )


class TestSaveToJson:
    def test_accepts_list_of_project_detail_records(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        records = [_make_record(0), _make_record(1)]
        out = tmp_path / "out.json"
        save_to_json(records, out)
        data = json.loads(out.read_text())
        assert len(data) == 2

    def test_fields_merged_to_root(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        records = [_make_record(0, fields={"Coordenador": "Maria", "Valor": "500"})]
        out = tmp_path / "out.json"
        save_to_json(records, out)
        data = json.loads(out.read_text())
        # Fields should be present when using dataclasses.asdict
        assert data[0].get("fields", {}).get("Coordenador") == "Maria" or \
               data[0].get("Coordenador") == "Maria"

    def test_source_url_present(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        records = [_make_record(0)]
        out = tmp_path / "out.json"
        save_to_json(records, out)
        data = json.loads(out.read_text())
        assert "_source_url" in data[0]

    def test_scraped_at_present(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        records = [_make_record(0)]
        out = tmp_path / "out.json"
        save_to_json(records, out)
        data = json.loads(out.read_text())
        assert "_scraped_at" in data[0]

    def test_accepts_scrape_result_and_extracts_records(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        result = _make_result(3)
        out = tmp_path / "out.json"
        save_to_json(result, out)
        data = json.loads(out.read_text())
        assert len(data) == 3

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        out = tmp_path / "out.json"
        save_to_json([_make_record(0)], out)
        save_to_json([_make_record(1), _make_record(2)], out)
        data = json.loads(out.read_text())
        assert len(data) == 2

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        from factor_lib.serializers import save_to_json
        out = tmp_path / "deep" / "nested" / "out.json"
        save_to_json([_make_record(0)], out)
        assert out.exists()
