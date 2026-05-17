"""Failing tests for CsvRecord, ExportResult, ExportError (T004–T006 — RED phase)."""
import dataclasses

import pytest

from factor_lib.exceptions import FactoLibError
from factor_lib.export.exceptions import (
    ButtonNotFoundError,
    DownloadTimeoutError,
    ExportError,
    ParseError,
)
from factor_lib.export.models import CsvRecord, ExportResult

# T004 — CsvRecord


class TestCsvRecord:
    def test_fields_stored(self) -> None:
        record = CsvRecord(
            fields={"Código": "PRJ-001", "Situação": "Em andamento"},
            source_file="projetos.csv",
            extracted_at="2026-05-16T14:35:00",
        )
        assert record.fields == {"Código": "PRJ-001", "Situação": "Em andamento"}

    def test_metadata_stored(self) -> None:
        record = CsvRecord(
            fields={},
            source_file="projetos.csv",
            extracted_at="2026-05-16T14:35:00",
        )
        assert record.source_file == "projetos.csv"
        assert record.extracted_at == "2026-05-16T14:35:00"

    def test_frozen_immutability(self) -> None:
        record = CsvRecord(fields={}, source_file="f.csv", extracted_at="2026-01-01T00:00:00")
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            record.source_file = "other.csv"  # type: ignore[misc]

    def test_is_dataclass(self) -> None:
        assert dataclasses.is_dataclass(CsvRecord)

    def test_to_dict_merges_fields_at_root(self) -> None:
        record = CsvRecord(
            fields={"Código": "PRJ-001", "Valor": "500000"},
            source_file="projetos.csv",
            extracted_at="2026-05-16T14:35:00",
        )
        d = record.to_dict()
        assert d["Código"] == "PRJ-001"
        assert d["Valor"] == "500000"
        assert d["_source_file"] == "projetos.csv"
        assert d["_extracted_at"] == "2026-05-16T14:35:00"
        assert "fields" not in d


# T005 — ExportResult


class TestExportResult:
    def _make_record(self) -> CsvRecord:
        return CsvRecord(fields={"a": "b"}, source_file="f.csv", extracted_at="2026-01-01T00:00:00")

    def test_fields_stored(self) -> None:
        r = self._make_record()
        result = ExportResult(
            records=(r,),
            total_records=1,
            files_processed=1,
            errors=(),
            exported_at="2026-05-16T14:35:00",
        )
        assert result.total_records == 1
        assert result.files_processed == 1
        assert result.errors == ()
        assert len(result.records) == 1

    def test_invariant_total_equals_records_len(self) -> None:
        r = self._make_record()
        result = ExportResult(
            records=(r, r),
            total_records=2,
            files_processed=1,
            errors=(),
            exported_at="2026-05-16T14:35:00",
        )
        assert result.total_records == len(result.records)

    def test_frozen_immutability(self) -> None:
        result = ExportResult(
            records=(),
            total_records=0,
            files_processed=0,
            errors=(),
            exported_at="2026-05-16T00:00:00",
        )
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            result.total_records = 99  # type: ignore[misc]


# T006 — ExportError hierarchy


class TestExportErrorHierarchy:
    def test_export_error_inherits_facto_lib_error(self) -> None:
        exc = ExportError(stage="download", reason="test")
        assert isinstance(exc, FactoLibError)

    def test_export_error_has_stage_and_reason(self) -> None:
        exc = ExportError(stage="parse", reason="bad zip")
        assert exc.stage == "parse"
        assert exc.reason == "bad zip"

    def test_export_error_message_includes_stage(self) -> None:
        exc = ExportError(stage="download", reason="timeout")
        assert "download" in str(exc)

    def test_download_timeout_error_is_export_error(self) -> None:
        exc = DownloadTimeoutError(stage="download", reason="60s exceeded")
        assert isinstance(exc, ExportError)

    def test_button_not_found_error_is_export_error(self) -> None:
        exc = ButtonNotFoundError(stage="download", reason="no button")
        assert isinstance(exc, ExportError)

    def test_parse_error_is_export_error(self) -> None:
        exc = ParseError(stage="parse", reason="corrupt zip")
        assert isinstance(exc, ExportError)
