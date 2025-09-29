import abc
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set


@dataclass
class Target:
    """A generic scrape target: define your own attributes as needed."""

    name: str
    start_url: str
    meta: dict[str, Any] = None


class Scraper(abc.ABC):
    """
    Base class to extend. Subclass this for your own scraper.
    """

    def __init__(self, target: Target):
        self.target = target
        self._discovered: List[str] = []
        self._scraped: List[Dict[str, Any]] = []

    @abc.abstractmethod
    async def discover_urls(self, page: Any, known: Set[str], overwrite: bool = False) -> List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    async def scrape_page(self, page: Any, url: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    async def fetch(self, known: Set[str], overwrite: bool = False) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_discovered(self) -> List[str]:
        return self._discovered

    def get_scraped(self) -> List[Dict[str, Any]]:
        return self._scraped
