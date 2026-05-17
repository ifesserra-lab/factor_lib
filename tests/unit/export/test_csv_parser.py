"""Failing tests for parse_zip_csv (T015–T020 — RED phase)."""
from __future__ import annotations

import io
import zipfile

from factor_lib.export.csv_parser import parse_zip_csv
from factor_lib.export.models import CsvRecord


def _make_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


# T015 — single CSV → list of dicts with correct keys


def test_parse_single_csv_returns_records_with_header_keys() -> None:
    csv = "Código|Situação|Valor\rPRJ-001|Em andamento|500000\rPRJ-002|Concluído|750000\r"
    zip_bytes = _make_zip({"projetos.csv": csv.encode("utf-8")})

    records = parse_zip_csv(zip_bytes)

    assert len(records) == 2
    assert all(isinstance(r, CsvRecord) for r in records)
    assert records[0].fields["Código"] == "PRJ-001"
    assert records[0].fields["Situação"] == "Em andamento"
    assert records[1].fields["Código"] == "PRJ-002"


# T016 — multi-CSV ZIP: rows merged, each record has source_file tag


def test_parse_multi_csv_merges_rows_and_tags_source_file() -> None:
    csv1 = "Col\rA\r"
    csv2 = "Col\rB\r"
    zip_bytes = _make_zip(
        {"first.csv": csv1.encode("utf-8"), "second.csv": csv2.encode("utf-8")}
    )

    records = parse_zip_csv(zip_bytes)

    assert len(records) == 2
    source_files = {r.source_file for r in records}
    assert "first.csv" in source_files
    assert "second.csv" in source_files


# T017 — ZIP with no CSVs → empty list (no exception)


def test_parse_zip_with_no_csv_returns_empty_list() -> None:
    zip_bytes = _make_zip({"readme.txt": b"not a csv"})

    records = parse_zip_csv(zip_bytes)

    assert records == []


# T018 — Latin-1 CSV falls back from UTF-8 correctly


def test_parse_latin1_csv_falls_back_from_utf8() -> None:
    csv_latin1 = "Objeto|Exercício\rConstrução de escola|2024\r".encode("latin-1")
    zip_bytes = _make_zip({"detalhes.csv": csv_latin1})

    records = parse_zip_csv(zip_bytes)

    assert len(records) == 1
    assert records[0].fields["Objeto"] == "Construção de escola"


# T019 — empty rows skipped; short rows get "" for missing columns


def test_parse_skips_empty_rows() -> None:
    csv = "Col1|Col2\rA|B\r\r\rC|D\r"
    zip_bytes = _make_zip({"data.csv": csv.encode("utf-8")})

    records = parse_zip_csv(zip_bytes)

    assert len(records) == 2


def test_parse_short_row_defaults_missing_columns_to_empty_string() -> None:
    csv = "Col1|Col2|Col3\rA|B\r"
    zip_bytes = _make_zip({"data.csv": csv.encode("utf-8")})

    records = parse_zip_csv(zip_bytes)

    assert len(records) == 1
    assert records[0].fields["Col3"] == ""


# T020 — each record has _extracted_at (ISO 8601) and source_file


def test_parse_records_have_metadata_fields() -> None:
    csv = "Col\rVal\r"
    zip_bytes = _make_zip({"data.csv": csv.encode("utf-8")})

    records = parse_zip_csv(zip_bytes)

    assert len(records) == 1
    r = records[0]
    assert r.source_file == "data.csv"
    assert "T" in r.extracted_at  # ISO 8601 contains "T" separator
    assert len(r.extracted_at) >= 19  # at least YYYY-MM-DDTHH:MM:SS
