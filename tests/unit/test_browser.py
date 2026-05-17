"""Unit tests for BrowserFactory (T010 — RED)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from factor_lib.browser import BrowserFactory


class TestBrowserFactory:
    def test_factory_creates_context_with_headless_flag(self) -> None:
        with patch("factor_lib.browser.sync_playwright") as mock_pw:
            mock_browser = MagicMock()
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = (
                mock_browser
            )
            factory = BrowserFactory(headless=True, timeout=30_000)
            with factory as _:
                pass
            mock_pw.return_value.__enter__.return_value.chromium.launch.assert_called_once_with(
                headless=True
            )

    def test_factory_creates_context_with_headless_false(self) -> None:
        with patch("factor_lib.browser.sync_playwright") as mock_pw:
            mock_browser = MagicMock()
            mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = (
                mock_browser
            )
            factory = BrowserFactory(headless=False, timeout=15_000)
            with factory as _:
                pass
            mock_pw.return_value.__enter__.return_value.chromium.launch.assert_called_once_with(
                headless=False
            )

    def test_factory_exposes_timeout(self) -> None:
        factory = BrowserFactory(headless=True, timeout=45_000)
        assert factory.timeout == 45_000

    def test_factory_supports_context_manager_protocol(self) -> None:
        factory = BrowserFactory(headless=True, timeout=30_000)
        assert hasattr(factory, "__enter__")
        assert hasattr(factory, "__exit__")
