"""Public Facade API for factor_lib scraper."""
from __future__ import annotations

import datetime
import os

from factor_lib.browser import BrowserFactory
from factor_lib.exceptions import PortalNavigationError
from factor_lib.models.project import ProjectListingRecord
from factor_lib.models.result import ScrapeResult
from factor_lib.pages.portal_page import TransparencyPortalPage
from factor_lib.scrapers.detail_scraper import DetailScraper
from factor_lib.scrapers.listing_scraper import ListingScraper
from factor_lib.serializers import save_to_json

_DEFAULT_URL = "https://facto.conveniar.com.br/portaltransparencia/"


def list_projects(
    url: str = _DEFAULT_URL,
    *,
    headless: bool = True,
    timeout: int = 30_000,
) -> list[ProjectListingRecord]:
    """Navigate to portal, click Consultar, return all project listing records."""
    with BrowserFactory(headless=headless, timeout=timeout) as factory:
        page = factory.new_page()
        portal = TransparencyPortalPage(page, url=url, default_timeout=timeout)
        try:
            portal.navigate()
            scraper = ListingScraper()
            return scraper.scrape(portal)
        except Exception as exc:
            raise PortalNavigationError(str(exc)) from exc


def scrape_all_projects(
    url: str = _DEFAULT_URL,
    *,
    headless: bool = True,
    timeout: int = 30_000,
) -> ScrapeResult:
    """List all projects then scrape details for each; return ScrapeResult."""
    started_at = datetime.datetime.now().isoformat(timespec="seconds")

    with BrowserFactory(headless=headless, timeout=timeout) as factory:
        page = factory.new_page()
        portal = TransparencyPortalPage(page, url=url, default_timeout=timeout)

        try:
            portal.navigate()
            listing = ListingScraper().scrape(portal)
        except Exception as exc:
            raise PortalNavigationError(str(exc)) from exc

        detail_records = DetailScraper(source_url=url).scrape(portal, listing)

    completed_at = datetime.datetime.now().isoformat(timespec="seconds")
    success_count = sum(1 for r in detail_records if r._error is None)
    error_count = sum(1 for r in detail_records if r._error is not None)

    return ScrapeResult(
        records=tuple(detail_records),
        total=len(detail_records),
        success_count=success_count,
        error_count=error_count,
        started_at=started_at,
        completed_at=completed_at,
    )


def scrape_and_save(
    output_path: str | os.PathLike[str],
    url: str = _DEFAULT_URL,
    *,
    headless: bool = True,
    timeout: int = 30_000,
    indent: int = 2,
) -> ScrapeResult:
    """Full flow: scrape all projects and save to JSON. Returns ScrapeResult."""
    result = scrape_all_projects(url=url, headless=headless, timeout=timeout)
    _save_result_to_json(result, output_path, indent=indent)
    return result


def _save_result_to_json(
    result: ScrapeResult,
    path: str | os.PathLike[str],
    *,
    indent: int = 2,
) -> None:
    """Serialize ScrapeResult records to JSON file with fields merged at root."""
    serialized = []
    for rec in result.records:
        flat: dict[str, object] = {**rec.fields}
        flat["id"] = rec.id
        flat["name"] = rec.name
        flat["_source_url"] = rec._source_url
        flat["_scraped_at"] = rec._scraped_at
        flat["_error"] = rec._error
        serialized.append(flat)
    save_to_json(serialized, path, indent=indent)
