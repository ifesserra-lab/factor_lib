"""pytest-playwright fixtures and network mock helpers for E2E tests."""
from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page, Route

FIXTURES_DIR = Path(__file__).parent / "fixtures"

PORTAL_URL = "https://facto.conveniar.com.br/portaltransparencia/"


def _load_fixture(name: str) -> str:
    path = FIXTURES_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"E2E fixture not found: {path}\n"
            "Run `python tests/e2e/record_fixtures.py` to capture portal snapshots."
        )
    return path.read_text(encoding="utf-8")


@pytest.fixture()
def mock_portal_listing(page: Page) -> None:
    """Route portal URL to recorded listing HTML snapshot."""
    html = _load_fixture("portal_listing.html")

    def _handle(route: Route) -> None:
        route.fulfill(status=200, content_type="text/html", body=html)

    page.route(f"{PORTAL_URL}**", _handle)


@pytest.fixture()
def mock_portal_detail(page: Page) -> None:
    """Route portal URL to recorded detail HTML snapshot."""
    html = _load_fixture("portal_detail.html")

    def _handle(route: Route) -> None:
        route.fulfill(status=200, content_type="text/html", body=html)

    page.route(f"{PORTAL_URL}**", _handle)
