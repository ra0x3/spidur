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

    @abc.abstractmethod
    async def discover_urls(
        self, page: Any, known: Set[str], overwrite: bool = False
    ) -> List[str]:
        """Find new URLs given a page."""
        ...

    @abc.abstractmethod
    async def scrape_page(self, page: Any, url: str) -> Optional[Dict[str, Any]]:
        """Scrape structured data from a page."""
        ...

    async def fetch(self, known: Set[str], overwrite: bool = False) -> List[Dict[str, Any]]:
        """
        Override if you want to implement your own orchestration.
        By default, it's not implemented.
        """
        raise NotImplementedError("Subclasses must implement `fetch` or override this method.")
