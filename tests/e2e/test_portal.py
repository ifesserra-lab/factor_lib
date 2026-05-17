"""E2E tests for portal scraper using recorded HTML fixtures (T023, T031)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from playwright.sync_api import Page

from factor_lib.models import ProjectListingRecord, ScrapeResult

PORTAL_URL = "https://facto.conveniar.com.br/portaltransparencia/"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> str:
    path = FIXTURES_DIR / name
    if not path.exists():
        pytest.skip(f"Fixture not found: {path} — run record_fixtures.py first")
    return path.read_text(encoding="utf-8")


# T023 — list_projects E2E with mocked HTML

class TestListProjectsE2E:
    def test_list_projects_returns_non_empty_list(self, page: Page) -> None:
        html = _load_fixture("portal_listing.html")

        page.route(f"{PORTAL_URL}**", lambda route: route.fulfill(
            status=200, content_type="text/html; charset=utf-8", body=html
        ))

        from factor_lib.api import list_projects

        with patch("factor_lib.api.BrowserFactory") as mock_factory_cls:
            mock_factory_cls.return_value.__enter__.return_value.new_page.return_value = page
            result = list_projects(url=PORTAL_URL)

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(r, ProjectListingRecord) for r in result)

    def test_list_projects_records_have_id_and_name(self, page: Page) -> None:
        html = _load_fixture("portal_listing.html")

        page.route(f"{PORTAL_URL}**", lambda route: route.fulfill(
            status=200, content_type="text/html; charset=utf-8", body=html
        ))

        from factor_lib.api import list_projects

        with patch("factor_lib.api.BrowserFactory") as mock_factory_cls:
            mock_factory_cls.return_value.__enter__.return_value.new_page.return_value = page
            result = list_projects(url=PORTAL_URL)

        for r in result:
            assert r.id
            assert r.name


# T031 — scrape_all_projects E2E with mocked listing + detail HTML

class TestScrapeAllProjectsE2E:
    def test_scrape_all_projects_returns_scrape_result(self, page: Page) -> None:
        listing_html = _load_fixture("portal_listing.html")
        detail_html = _load_fixture("portal_detail.html")

        call_count = [0]

        def _router(route):  # type: ignore[no-untyped-def]
            call_count[0] += 1
            html = detail_html if call_count[0] > 1 else listing_html
            route.fulfill(status=200, content_type="text/html; charset=utf-8", body=html)

        page.route(f"{PORTAL_URL}**", _router)

        from factor_lib.api import scrape_all_projects

        with patch("factor_lib.api.BrowserFactory") as mock_factory_cls:
            mock_factory_cls.return_value.__enter__.return_value.new_page.return_value = page
            result = scrape_all_projects(url=PORTAL_URL)

        assert isinstance(result, ScrapeResult)
        assert result.total > 0
        assert result.success_count + result.error_count == result.total
