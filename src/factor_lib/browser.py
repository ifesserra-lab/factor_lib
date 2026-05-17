"""BrowserFactory: creates and manages Playwright browser contexts."""
from __future__ import annotations

from types import TracebackType

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright


class BrowserFactory:
    """Factory for Playwright sync browser contexts."""

    def __init__(self, *, headless: bool = True, timeout: int = 30_000) -> None:
        self.headless = headless
        self.timeout = timeout
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    def __enter__(self) -> BrowserFactory:
        self._playwright = sync_playwright().__enter__()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._context = self._browser.new_context()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def new_page(self) -> Page:
        assert self._context is not None, "BrowserFactory must be used as context manager"
        page = self._context.new_page()
        page.set_default_timeout(self.timeout)
        return page
