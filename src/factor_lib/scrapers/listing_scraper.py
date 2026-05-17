"""ListingScraper: Strategy for extracting project listing from portal."""
from __future__ import annotations

from typing import TYPE_CHECKING

from factor_lib.models.project import ProjectListingRecord
from factor_lib.scrapers.base_scraper import AbstractScraper

if TYPE_CHECKING:
    from factor_lib.pages.portal_page import TransparencyPortalPage


class ListingScraper(AbstractScraper):
    """Scrapes the project listing table after clicking Consultar."""

    def scrape(self, portal_page: TransparencyPortalPage) -> list[ProjectListingRecord]:
        portal_page.click_consultar()
        rows = portal_page.get_listing_rows()
        records = []
        for i, row in enumerate(rows):
            proj_id = row.get("id") or str(i)
            name = row.get("name") or ""
            raw = {k: v for k, v in row.items() if k not in ("id", "name")}
            records.append(ProjectListingRecord(id=proj_id, name=name, raw_row=raw))
        return records
