import asyncio
import pytest

from scrape_runner.base import Target, Scraper
from scrape_runner.factory import ScraperFactory
from scrape_runner.runner import Runner


class DummyScraper(Scraper):
    """Minimal fake scraper for testing."""

    async def discover_urls(self, page, known, overwrite=False):
        # Pretend to find 2 URLs
        urls = ["http://test/1", "http://test/2"]
        self._discovered.extend(urls)
        return urls

    async def scrape_page(self, page, url):
        # Pretend to return a dict
        item = {"url": url, "content": f"data-from-{url}"}
        self._scraped.append(item)
        return item

    async def fetch(self, known, overwrite=False):
        # A trivial orchestrator for test purposes
        urls = await self.discover_urls(page=None, known=known, overwrite=overwrite)
        results = []
        for u in urls:
            item = await self.scrape_page(page=None, url=u)
            results.append(item)
        return results


def test_factory_and_scraper_registration(monkeypatch):
    target = Target(name="dummy", start_url="http://test")
    ScraperFactory.register("dummy", DummyScraper)

    scraper = ScraperFactory.create(target)
    assert isinstance(scraper, DummyScraper)


@pytest.mark.asyncio
async def test_scraper_fetch_collects_urls_and_data():
    scraper = DummyScraper(Target(name="dummy", start_url="http://test"))

    results = await scraper.fetch(known=set(), overwrite=True)

    assert len(scraper.get_discovered()) == 2
    assert all(r in scraper.get_discovered() for r in ["http://test/1", "http://test/2"])
    assert len(scraper.get_scraped()) == 2
    assert all("content" in r for r in results)


def test_runner_parallel_executes(monkeypatch):
    target = Target(name="dummy", start_url="http://test")
    ScraperFactory.register("dummy", DummyScraper)

    results = Runner.run([target], seen=set(), overwrite=True)

    assert "dummy" in results
    assert isinstance(results["dummy"], list)
    assert all("url" in r for r in results["dummy"])
