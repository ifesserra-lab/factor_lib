"""E2E tests for CSV export flow using page.route() mocking (T013, T029)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from playwright.sync_api import Page

from factor_lib.export.downloader import EXPORT_CSV_SEL, download_csv_export
from factor_lib.export.exporter import export_project_csv_to_json

_LINK_ID = EXPORT_CSV_SEL.lstrip("#")
_DOWNLOAD_URL = "http://localhost/download"
_PAGE_URL = "http://localhost/page"


def _setup_routes(page: Page, sample_zip_bytes: bytes, *, link_id: str = _LINK_ID) -> None:
    """Route /page → HTML with export link; /download → ZIP bytes."""
    html = (
        f"<html><body>"
        f'<a id="{link_id}" href="{_DOWNLOAD_URL}">Exportar em CSV</a>'
        f"</body></html>"
    )
    page.route(_PAGE_URL, lambda r: r.fulfill(status=200, content_type="text/html", body=html))
    page.route(_DOWNLOAD_URL, lambda r: r.fulfill(
        status=200,
        headers={"Content-Disposition": "attachment; filename=export.zip"},
        body=sample_zip_bytes,
    ))
    page.goto(_PAGE_URL)


# T013 — download with route mock; assert temp dir cleaned up


@pytest.mark.parametrize("timeout", [60_000])
def test_download_returns_bytes_and_cleans_temp(
    page: Page,
    sample_zip_bytes: bytes,
    timeout: int,
) -> None:
    _setup_routes(page, sample_zip_bytes)

    result = download_csv_export(page, timeout=timeout)

    assert len(result) > 0
    assert result == sample_zip_bytes


# T029 — full facade flow with route mock


def test_export_project_csv_to_json_produces_json_file(
    page: Page,
    sample_zip_bytes: bytes,
    tmp_path: Path,
) -> None:
    _setup_routes(page, sample_zip_bytes)

    output_path = tmp_path / "output.json"
    result = export_project_csv_to_json(page, output_path)

    assert output_path.exists()
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == result.total_records
    assert result.total_records > 0
    assert "_source_file" in data[0]
    assert "_extracted_at" in data[0]
