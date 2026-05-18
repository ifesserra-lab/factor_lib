"""ParallelDetailScraper: concurrent detail extraction via CSV download, one browser per worker."""
from __future__ import annotations

import datetime
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING

from factor_lib.browser import BrowserFactory
from factor_lib.export.csv_parser import parse_zip_csv
from factor_lib.export.downloader import download_csv_export
from factor_lib.models.project import ProjectDetailRecord, ProjectListingRecord
from factor_lib.pages.portal_page import TransparencyPortalPage
from factor_lib.scrapers.base_scraper import AbstractScraper

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

_PORTAL_URL = "https://facto.conveniar.com.br/portaltransparencia/"


def _scrape_one(
    row_index: int,
    item: ProjectListingRecord,
    url: str,
    headless: bool,
    timeout: int,
) -> ProjectDetailRecord:
    """Worker: own browser instance per thread. Downloads CSV export for each project."""
    scraped_at = datetime.datetime.now().isoformat(timespec="seconds")
    try:
        with BrowserFactory(headless=headless, timeout=timeout) as factory:
            page = factory.new_page()
            portal = TransparencyPortalPage(page, url=url, default_timeout=timeout)
            portal.navigate()
            portal.click_consultar()
            portal.click_detail_icon(row_index)

            # Download and parse CSV export — primary data source
            zip_bytes = download_csv_export(page, timeout=timeout)
            csv_records = parse_zip_csv(zip_bytes)

        # Group rows by source CSV file → store as JSON strings per section
        sections: dict[str, str] = {}
        groups: dict[str, list[dict[str, str]]] = {}
        for rec in csv_records:
            groups.setdefault(rec.source_file, []).append(rec.fields)
        for filename, rows in groups.items():
            sections[filename] = json.dumps(rows, ensure_ascii=False)

        return ProjectDetailRecord(
            id=item.id,
            name=item.name,
            fields=sections,
            _source_url=url,
            _scraped_at=scraped_at,
        )
    except Exception as exc:
        logger.warning("Detail scraping failed for project %s: %s", item.id, exc)
        return ProjectDetailRecord(
            id=item.id,
            name=item.name,
            fields={},
            _source_url=url,
            _scraped_at=scraped_at,
            _error=str(exc),
        )


class ParallelDetailScraper(AbstractScraper):
    """Scrapes project details concurrently using a thread pool."""

    def __init__(
        self,
        *,
        source_url: str = _PORTAL_URL,
        workers: int = 4,
        headless: bool = True,
        timeout: int = 30_000,
    ) -> None:
        self.source_url = source_url
        self.workers = workers
        self.headless = headless
        self.timeout = timeout

    def scrape(
        self,
        portal_page: object,  # unused — each worker opens its own browser
        listing: list[ProjectListingRecord],
    ) -> list[ProjectDetailRecord]:
        total = len(listing)
        results: list[ProjectDetailRecord | None] = [None] * total
        done = 0

        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {
                pool.submit(
                    _scrape_one,
                    i,
                    item,
                    self.source_url,
                    self.headless,
                    self.timeout,
                ): i
                for i, item in enumerate(listing)
            }
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()
                done += 1
                rec = results[idx]
                assert rec is not None
                status = "ERR" if rec._error else "OK"
                logger.info(
                    "[%d/%d] [%s] project %s — %d fields",
                    done, total, status, rec.id, len(rec.fields),
                )

        return [r for r in results if r is not None]
