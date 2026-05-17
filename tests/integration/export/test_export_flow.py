"""Integration test: full export flow with mocked download (T026)."""
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from unittest.mock import patch

from factor_lib.export.exporter import export_project_csv_to_json
from factor_lib.export.models import ExportResult


def _make_zip_bytes() -> bytes:
    csv = "Código|Situação\rPRJ-001|Em andamento\rPRJ-002|Concluído\r"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("projetos.csv", csv.encode("utf-8"))
    return buf.getvalue()


# T026 — facade produces valid JSON with all records from fixture ZIP


def test_export_flow_produces_valid_json_with_all_records(tmp_path: Path) -> None:
    from unittest.mock import MagicMock

    page = MagicMock()
    output = tmp_path / "output.json"
    zip_bytes = _make_zip_bytes()

    with patch(
        "factor_lib.export.exporter.download_csv_export",
        return_value=zip_bytes,
    ):
        result = export_project_csv_to_json(page, output)

    assert isinstance(result, ExportResult)
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 2
    assert result.total_records == 2
    assert result.files_processed == 1
    assert result.errors == ()
    assert "Código" in data[0]
    assert "_source_file" in data[0]
    assert "_extracted_at" in data[0]
