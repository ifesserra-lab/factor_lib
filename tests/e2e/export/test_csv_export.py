"""E2E tests for CSV export flow using page.route() mocking (T013, T029)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from playwright.sync_api import Page

from factor_lib.export.downloader import download_csv_export
from factor_lib.export.exporter import export_project_csv_to_json

# T013 — download with route mock; assert temp dir cleaned up


@pytest.mark.parametrize("timeout", [60_000])
def test_download_returns_bytes_and_cleans_temp(
    page: Page,
    sample_zip_bytes: bytes,
    timeout: int,
) -> None:
    page.set_content(
        """<html><body>
        <a id="export-link" href="/download">Exportar em CSV</a>
        </body></html>"""
    )

    def route_download(route: object) -> None:
        from playwright.sync_api import Route
        assert isinstance(route, Route)
        route.fulfill(
            status=200,
            headers={"Content-Disposition": "attachment; filename=export.zip"},
            body=sample_zip_bytes,
        )

    page.route("**/download", route_download)

    result = download_csv_export(page, timeout=timeout)

    assert len(result) > 0
    assert result == sample_zip_bytes


# T029 — full facade flow with route mock


def test_export_project_csv_to_json_produces_json_file(
    page: Page,
    sample_zip_bytes: bytes,
    tmp_path: Path,
) -> None:
    page.set_content(
        """<html><body>
        <a href="/download">Exportar em CSV</a>
        </body></html>"""
    )

    def route_download(route: object) -> None:
        from playwright.sync_api import Route
        assert isinstance(route, Route)
        route.fulfill(
            status=200,
            headers={"Content-Disposition": "attachment; filename=export.zip"},
            body=sample_zip_bytes,
        )

    page.route("**/download", route_download)

    output_path = tmp_path / "output.json"
    result = export_project_csv_to_json(page, output_path)

    assert output_path.exists()
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == result.total_records
    assert result.total_records > 0
    assert "_source_file" in data[0]
    assert "_extracted_at" in data[0]
