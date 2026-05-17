"""Failing unit tests for export_project_csv_to_json facade (T027–T028 — RED)."""
from __future__ import annotations

import io
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from factor_lib.export.exceptions import ExportError
from factor_lib.export.exporter import export_project_csv_to_json


def _make_zip_bytes() -> bytes:
    csv = "Col\nVal\n"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("data.csv", csv.encode("utf-8"))
    return buf.getvalue()


# T027 — download failure raises ExportError with "download" stage


def test_facade_raises_export_error_on_download_failure(tmp_path: Path) -> None:
    page = MagicMock()
    output = tmp_path / "out.json"

    with patch(
        "factor_lib.export.exporter.download_csv_export",
        side_effect=ExportError(stage="download", reason="network error"),
    ):
        with pytest.raises(ExportError) as exc_info:
            export_project_csv_to_json(page, output)

    assert exc_info.value.stage == "download"


# T028 — parse failure raises ExportError with "parse" stage


def test_facade_raises_export_error_on_parse_failure(tmp_path: Path) -> None:
    page = MagicMock()
    output = tmp_path / "out.json"

    with patch(
        "factor_lib.export.exporter.download_csv_export",
        return_value=b"not a zip",
    ):
        with pytest.raises(ExportError) as exc_info:
            export_project_csv_to_json(page, output)

    assert exc_info.value.stage == "parse"
