"""AbstractScraper: Strategy interface for portal scrapers."""
from __future__ import annotations

import abc
from typing import Any


class AbstractScraper(abc.ABC):
    """Strategy interface — all concrete scrapers implement scrape()."""

    @abc.abstractmethod
    def scrape(self, *args: Any, **kwargs: Any) -> Any:
        ...
