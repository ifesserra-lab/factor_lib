"""DetailScraper: Strategy for extracting project detail fields from portal."""
from __future__ import annotations

import datetime
import logging
import re
from typing import TYPE_CHECKING

from factor_lib.models.project import ProjectDetailRecord, ProjectListingRecord
from factor_lib.scrapers.base_scraper import AbstractScraper

if TYPE_CHECKING:
    from factor_lib.pages.portal_page import TransparencyPortalPage

logger = logging.getLogger(__name__)

_PORTAL_URL = "https://facto.conveniar.com.br/portaltransparencia/"

_TITLE_RE = re.compile(r"projeto\s+\d+\s*-\s*(.+)", re.IGNORECASE | re.DOTALL)
_MAX_FILTER_LEN = 40


def _name_filter(listing_name: str) -> str:
    """Extract the project title from a listing link text for use as a search filter.

    "Visualizar os detalhes do projeto 278 - Estudos da fluidodinâmica..." →
    "Estudos da fluidodinâmica...". Returns "" (no filter) when the text does
    not follow the expected pattern.
    """
    m = _TITLE_RE.search(listing_name)
    if not m:
        return ""
    title = m.group(1).strip().rstrip(".")
    return title[:_MAX_FILTER_LEN].strip()


_REF_ID_RE = re.compile(r"^\s*(\d+)\s*-")


def _reference_mismatch(project_id: str, fields: dict[str, str]) -> str | None:
    """Describe a mismatch when the detail view belongs to another project.

    The portal sometimes opens a different record from a project's lupa (e.g.
    project 259 shows "393 - Fundo rescisório ... (259)"). The fields are kept,
    but the record is flagged so consumers do not take them as project_id's.
    """
    m = _REF_ID_RE.match(fields.get("Referência do projeto", ""))
    if m and m.group(1) != project_id:
        return (
            f"Portal returned project {m.group(1)} for project {project_id} "
            f"(Referência: {fields['Referência do projeto'][:120]!r})"
        )
    return None


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
        for item in listing:
            scraped_at = datetime.datetime.now().isoformat(timespec="seconds")
            try:
                portal_page.open_project_detail(item.id, name_filter=_name_filter(item.name))
                fields = portal_page.get_detail_fields()
                mismatch = _reference_mismatch(item.id, fields)
                if mismatch:
                    logger.warning("Project %s: %s", item.id, mismatch)
                records.append(
                    ProjectDetailRecord(
                        id=item.id,
                        name=item.name,
                        fields=fields,
                        _source_url=self.source_url,
                        _scraped_at=scraped_at,
                        _error=mismatch,
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
