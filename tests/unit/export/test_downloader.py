"""Failing tests for download_csv_export (T010–T012 — RED phase)."""
from __future__ import annotations

import io
import zipfile
from unittest.mock import MagicMock

import pytest

from factor_lib.export.downloader import download_csv_export
from factor_lib.export.exceptions import ButtonNotFoundError, DownloadTimeoutError


def _make_zip_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("data.csv", "col\nval\n")
    return buf.getvalue()


# T010 — button not found


def test_download_raises_button_not_found_when_no_button() -> None:
    page = MagicMock()
    page.locator.return_value.count.return_value = 0

    with pytest.raises(ButtonNotFoundError) as exc_info:
        download_csv_export(page)

    assert exc_info.value.stage == "download"


# T011 — timeout


def test_download_raises_timeout_on_slow_download() -> None:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

    page = MagicMock()
    page.locator.return_value.count.return_value = 1

    ctx_manager = MagicMock()
    ctx_manager.__enter__ = MagicMock(side_effect=PlaywrightTimeoutError("timeout"))
    ctx_manager.__exit__ = MagicMock(return_value=False)
    page.expect_download.return_value = ctx_manager

    with pytest.raises(DownloadTimeoutError) as exc_info:
        download_csv_export(page, timeout=100)

    assert exc_info.value.stage == "download"


# T012 — redirect follow (Playwright handles automatically; test that bytes returned)


def test_download_returns_bytes_on_success() -> None:
    zip_bytes = _make_zip_bytes()

    page = MagicMock()
    page.locator.return_value.count.return_value = 1

    def fake_save_as(dest_path: object) -> None:
        from pathlib import Path as PathType
        assert isinstance(dest_path, PathType)
        dest_path.write_bytes(zip_bytes)

    download_mock = MagicMock()
    download_mock.save_as.side_effect = fake_save_as

    ctx_manager = MagicMock()
    ctx_manager.__enter__ = MagicMock(return_value=ctx_manager)
    ctx_manager.__exit__ = MagicMock(return_value=False)
    ctx_manager.value = download_mock
    page.expect_download.return_value = ctx_manager

    result = download_csv_export(page)

    assert result == zip_bytes
