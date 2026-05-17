"""Download the 'Exportar em CSV' ZIP from the Facto portal detail page."""
from __future__ import annotations

import tempfile
from pathlib import Path

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from factor_lib.export.exceptions import ButtonNotFoundError, DownloadTimeoutError

_EXPORT_BUTTON_TEXT = "Exportar em CSV"


def download_csv_export(page: Page, *, timeout: int = 60_000) -> bytes:
    """Click 'Exportar em CSV', download resulting ZIP, return its bytes.

    Caller must already be on the project detail page.
    Temp dir is managed and deleted by this function regardless of outcome.
    """
    button = page.locator(f"text={_EXPORT_BUTTON_TEXT}")
    if button.count() == 0:
        raise ButtonNotFoundError(
            stage="download",
            reason=f"'{_EXPORT_BUTTON_TEXT}' button not found on current page",
        )

    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = Path(tmp_dir) / "export.zip"
        try:
            with page.expect_download(timeout=timeout) as download_info:
                button.click()
            download_info.value.save_as(zip_path)
        except PlaywrightTimeoutError as exc:
            raise DownloadTimeoutError(
                stage="download",
                reason=f"ZIP download did not complete within {timeout}ms",
            ) from exc

        return zip_path.read_bytes()
