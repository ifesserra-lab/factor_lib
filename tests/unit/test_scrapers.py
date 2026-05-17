"""Unit tests for scraper Strategy classes (T021, T022, T030, T031, T032 — RED)."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from factor_lib.models import ProjectDetailRecord, ProjectListingRecord

# T021 — AbstractScraper protocol

class TestAbstractScraper:
    def test_abstract_scraper_has_scrape_method(self) -> None:
        from factor_lib.scrapers.base_scraper import AbstractScraper
        assert hasattr(AbstractScraper, "scrape")

    def test_abstract_scraper_cannot_be_instantiated(self) -> None:
        from factor_lib.scrapers.base_scraper import AbstractScraper
        with pytest.raises(TypeError):
            AbstractScraper()  # type: ignore[abstract]


# T022 — ListingScraper

class TestListingScraper:
    def _make_page(self, rows: list[dict[str, str]] | None = None) -> MagicMock:
        mock_page = MagicMock()
        return mock_page

    def test_listing_scraper_returns_list_of_project_listing_records(self) -> None:
        from factor_lib.scrapers.listing_scraper import ListingScraper

        mock_portal_page = MagicMock()
        mock_portal_page.click_consultar.return_value = None
        mock_portal_page.get_listing_rows.return_value = [
            {"id": "12", "name": "Projeto 12 - Apoio", "raw": "Apoio e Fortalecimento"},
            {"id": "24", "name": "Projeto 24 - Plano", "raw": "Plano de pesquisa"},
        ]

        scraper = ListingScraper()
        result = scraper.scrape(mock_portal_page)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(r, ProjectListingRecord) for r in result)

    def test_listing_scraper_populates_id_and_name(self) -> None:
        from factor_lib.scrapers.listing_scraper import ListingScraper

        mock_portal_page = MagicMock()
        mock_portal_page.get_listing_rows.return_value = [
            {"id": "12", "name": "Projeto 12", "raw": "something"},
        ]

        scraper = ListingScraper()
        result = scraper.scrape(mock_portal_page)

        assert result[0].id == "12"
        assert result[0].name == "Projeto 12"

    def test_listing_scraper_handles_empty_table(self) -> None:
        from factor_lib.scrapers.listing_scraper import ListingScraper

        mock_portal_page = MagicMock()
        mock_portal_page.get_listing_rows.return_value = []

        scraper = ListingScraper()
        result = scraper.scrape(mock_portal_page)

        assert result == []

    def test_listing_scraper_assigns_sequential_id_when_missing(self) -> None:
        from factor_lib.scrapers.listing_scraper import ListingScraper

        mock_portal_page = MagicMock()
        mock_portal_page.get_listing_rows.return_value = [
            {"id": "", "name": "Sem ID", "raw": "x"},
        ]

        scraper = ListingScraper()
        result = scraper.scrape(mock_portal_page)

        assert result[0].id == "0"


# T030 — DetailScraper

class TestDetailScraper:
    def _make_listing_record(self, idx: int = 0) -> ProjectListingRecord:
        return ProjectListingRecord(
            id=str(idx), name=f"Projeto {idx}", raw_row={"col": "val"}
        )

    def test_detail_scraper_returns_list_of_project_detail_records(self) -> None:
        from factor_lib.scrapers.detail_scraper import DetailScraper

        mock_portal_page = MagicMock()
        mock_portal_page.click_detail_icon.return_value = None
        mock_portal_page.get_detail_fields.return_value = {"Coordenador": "João"}

        listing = [self._make_listing_record(0), self._make_listing_record(1)]
        scraper = DetailScraper()
        result = scraper.scrape(mock_portal_page, listing)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(r, ProjectDetailRecord) for r in result)

    def test_detail_scraper_captures_fields(self) -> None:
        from factor_lib.scrapers.detail_scraper import DetailScraper

        mock_portal_page = MagicMock()
        mock_portal_page.get_detail_fields.return_value = {"Coordenador": "João", "Valor": "100"}

        listing = [self._make_listing_record(0)]
        scraper = DetailScraper(source_url="https://example.com")
        result = scraper.scrape(mock_portal_page, listing)

        assert result[0].fields["Coordenador"] == "João"
        assert result[0].fields["Valor"] == "100"

    def test_detail_scraper_adds_scraped_at_metadata(self) -> None:
        from factor_lib.scrapers.detail_scraper import DetailScraper

        mock_portal_page = MagicMock()
        mock_portal_page.get_detail_fields.return_value = {}

        listing = [self._make_listing_record(0)]
        scraper = DetailScraper()
        result = scraper.scrape(mock_portal_page, listing)

        assert "T" in result[0]._scraped_at

    def test_detail_scraper_adds_source_url(self) -> None:
        from factor_lib.scrapers.detail_scraper import DetailScraper

        mock_portal_page = MagicMock()
        mock_portal_page.get_detail_fields.return_value = {}

        listing = [self._make_listing_record(0)]
        scraper = DetailScraper(source_url="https://myportal.example")
        result = scraper.scrape(mock_portal_page, listing)

        assert result[0]._source_url == "https://myportal.example"


# T032 — Error tolerance

class TestDetailScraperErrorTolerance:
    def test_on_click_failure_sets_error_and_continues(self) -> None:
        from factor_lib.scrapers.detail_scraper import DetailScraper

        mock_portal_page = MagicMock()
        mock_portal_page.click_detail_icon.side_effect = [
            Exception("lupa not clickable"),
            None,
        ]
        mock_portal_page.get_detail_fields.return_value = {"Coordenador": "Ana"}

        listing = [
            ProjectListingRecord(id="0", name="P0", raw_row={}),
            ProjectListingRecord(id="1", name="P1", raw_row={}),
        ]
        scraper = DetailScraper()
        result = scraper.scrape(mock_portal_page, listing)

        assert len(result) == 2
        assert result[0]._error is not None
        assert result[1]._error is None
        assert result[1].fields["Coordenador"] == "Ana"

    def test_failed_record_has_empty_fields(self) -> None:
        from factor_lib.scrapers.detail_scraper import DetailScraper

        mock_portal_page = MagicMock()
        mock_portal_page.click_detail_icon.side_effect = Exception("timeout")

        listing = [ProjectListingRecord(id="0", name="P0", raw_row={})]
        scraper = DetailScraper()
        result = scraper.scrape(mock_portal_page, listing)

        assert result[0].fields == {}
