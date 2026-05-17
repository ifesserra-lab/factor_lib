"""Unit tests for BasePage (T011 — RED)."""
from __future__ import annotations

from unittest.mock import MagicMock

from factor_lib.pages.base_page import BasePage


class TestBasePage:
    def test_stores_page_reference(self) -> None:
        mock_page = MagicMock()
        bp = BasePage(mock_page)
        assert bp.page is mock_page

    def test_wait_for_selector_delegates_to_page(self) -> None:
        mock_page = MagicMock()
        bp = BasePage(mock_page)
        bp.wait_for(selector="#someId", timeout=5_000)
        mock_page.wait_for_selector.assert_called_once_with("#someId", timeout=5_000)

    def test_wait_for_selector_uses_default_timeout_from_page_attribute(self) -> None:
        mock_page = MagicMock()
        bp = BasePage(mock_page, default_timeout=10_000)
        bp.wait_for("#myEl")
        mock_page.wait_for_selector.assert_called_once_with("#myEl", timeout=10_000)

    def test_wait_for_network_idle_delegates_to_page(self) -> None:
        mock_page = MagicMock()
        bp = BasePage(mock_page)
        bp.wait_for_network_idle()
        args, kwargs = mock_page.wait_for_load_state.call_args
        assert args[0] == "networkidle"
