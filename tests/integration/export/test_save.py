"""Integration tests for save_to_json with CsvRecord (T022–T025)."""
from __future__ import annotations

import json
from pathlib import Path

from factor_lib.export.models import CsvRecord
from factor_lib.serializers import save_to_json


def _make_record(code: str = "PRJ-001") -> CsvRecord:
    return CsvRecord(
        fields={"Código": code, "Situação": "Em andamento"},
        source_file="projetos.csv",
        extracted_at="2026-05-16T14:35:00",
    )


# T022 — save_to_json creates valid JSON file from CsvRecord list


def test_save_to_json_creates_valid_json_file(tmp_path: Path) -> None:
    records = [_make_record("PRJ-001"), _make_record("PRJ-002")]
    output = tmp_path / "output.json"

    save_to_json(records, output)

    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 2


# T022 (continued) — fields merged at root level, not nested under "fields"


def test_save_to_json_merges_csv_fields_at_root(tmp_path: Path) -> None:
    records = [_make_record("PRJ-001")]
    output = tmp_path / "output.json"

    save_to_json(records, output)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert "Código" in data[0]
    assert data[0]["Código"] == "PRJ-001"
    assert "_source_file" in data[0]
    assert "_extracted_at" in data[0]
    assert "fields" not in data[0]


# T023 — save_to_json overwrites existing file


def test_save_to_json_overwrites_existing_file(tmp_path: Path) -> None:
    output = tmp_path / "output.json"
    output.write_text("old content", encoding="utf-8")

    save_to_json([_make_record()], output)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 1


# T024 — save_to_json creates missing parent directories


def test_save_to_json_creates_parent_directories(tmp_path: Path) -> None:
    output = tmp_path / "deep" / "nested" / "dir" / "output.json"

    save_to_json([_make_record()], output)

    assert output.exists()


# T025 — CsvRecord serializes correctly via to_dict (no dataclasses.asdict nesting)


def test_csv_record_serializes_without_fields_nesting(tmp_path: Path) -> None:
    record = CsvRecord(
        fields={"Código": "PRJ-001", "Valor": "500000"},
        source_file="projetos.csv",
        extracted_at="2026-05-16T14:35:00",
    )
    output = tmp_path / "out.json"

    save_to_json([record], output)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data[0]["Código"] == "PRJ-001"
    assert data[0]["Valor"] == "500000"
    assert data[0]["_source_file"] == "projetos.csv"
    assert data[0]["_extracted_at"] == "2026-05-16T14:35:00"
    assert "fields" not in data[0]
    assert "source_file" not in data[0]
