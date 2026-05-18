"""Portal scraper Strategy implementations."""
from factor_lib.scrapers.base_scraper import AbstractScraper
from factor_lib.scrapers.detail_scraper import DetailScraper
from factor_lib.scrapers.listing_scraper import ListingScraper
from factor_lib.scrapers.parallel_detail_scraper import ParallelDetailScraper

__all__ = ["AbstractScraper", "DetailScraper", "ListingScraper", "ParallelDetailScraper"]
