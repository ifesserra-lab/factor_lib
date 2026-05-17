"""DetailScraper: Strategy for extracting project detail fields from portal."""
from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING

from factor_lib.models.project import ProjectDetailRecord, ProjectListingRecord
from factor_lib.scrapers.base_scraper import AbstractScraper

if TYPE_CHECKING:
    from factor_lib.pages.portal_page import TransparencyPortalPage

logger = logging.getLogger(__name__)

_PORTAL_URL = "https://facto.conveniar.com.br/portaltransparencia/"


class DetailScraper(AbstractScraper):
    """Scrapes the detail view for each project by clicking its lupa icon."""

    def __init__(self, *, source_url: str = _PORTAL_URL) -> None:
        self.source_url = source_url

    def scrape(
        self,
        portal_page: TransparencyPortalPage,
        listing: list[ProjectListingRecord],
    ) -> list[ProjectDetailRecord]:
        records = []
        for i, item in enumerate(listing):
            scraped_at = datetime.datetime.now().isoformat(timespec="seconds")
            try:
                portal_page.click_detail_icon(i)
                fields = portal_page.get_detail_fields()
                records.append(
                    ProjectDetailRecord(
                        id=item.id,
                        name=item.name,
                        fields=fields,
                        _source_url=self.source_url,
                        _scraped_at=scraped_at,
                    )
                )
            except Exception as exc:
                logger.warning("Detail scraping failed for project %s: %s", item.id, exc)
                records.append(
                    ProjectDetailRecord(
                        id=item.id,
                        name=item.name,
                        fields={},
                        _source_url=self.source_url,
                        _scraped_at=scraped_at,
                        _error=str(exc),
                    )
                )
        return records
