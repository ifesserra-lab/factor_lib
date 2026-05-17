"""BasePage: shared wait helpers for all Page Object Model classes."""
from __future__ import annotations

from playwright.sync_api import ElementHandle, Page


class BasePage:
    """Base POM class with shared wait helpers."""

    DEFAULT_TIMEOUT = 30_000

    def __init__(self, page: Page, *, default_timeout: int = DEFAULT_TIMEOUT) -> None:
        self.page = page
        self.default_timeout = default_timeout

    def wait_for(self, selector: str, *, timeout: int | None = None) -> ElementHandle | None:
        return self.page.wait_for_selector(
            selector, timeout=timeout if timeout is not None else self.default_timeout
        )

    def wait_for_network_idle(self, *, timeout: int = 60_000) -> None:
        self.page.wait_for_load_state("networkidle", timeout=timeout)
