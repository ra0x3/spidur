import pytest

from spidur.core import Target, Scraper
from spidur.factory import ScraperFactory
from spidur.runner import Runner

import multiprocessing

multiprocessing.set_start_method("fork", force=True)


class DummyScraper(Scraper):
    """Minimal fake scraper for testing."""

    def is_valid_url(self, url: str) -> bool:
        return url.startswith("http://test/")

    async def discover_urls(self, page, known):
        # Pretend to find 2 URLs
        urls = ["http://test/1", "http://test/2"]
        self._discovered_urls.extend(urls)
        return urls

    async def scrape_page(self, page, url):
        # Pretend to return a dict
        item = {"url": url, "content": f"data-from-{url}"}
        self._scraped_data.append(item)
        return item

    async def fetch_round(self, known):
        # A trivial orchestrator for test purposes
        urls = await self.discover_urls(page=None, known=known)
        results = []
        for u in urls:
            item = await self.scrape_page(page=None, url=u)
            results.append(item)
        return results


def test_factory_and_scraper_registration():
    target = Target(name="dummy", start_url="http://test")
    ScraperFactory.register("dummy", DummyScraper)

    scraper = ScraperFactory.create(target)
    assert isinstance(scraper, DummyScraper)


@pytest.mark.asyncio
async def test_scraper_fetch_round_collects_urls_and_data():
    scraper = DummyScraper(Target(name="dummy", start_url="http://test"))

    results = await scraper.fetch_round(known=set())

    discovered = scraper.get_discovered_urls()
    scraped = scraper.get_scraped_data()

    assert len(discovered) == 2
    assert all(url in discovered for url in ["http://test/1", "http://test/2"])
    assert len(scraped) == 2
    assert all("content" in r for r in results)


def test_runner_parallel_executes(monkeypatch):
    target = Target(name="dummy", start_url="http://test")
    ScraperFactory.register("dummy", DummyScraper)

    import spidur.runner as runner

    old_run_batch = runner._run_batch

    def patched_run_batch(batch, out, seen):
        # Re-register in each subprocess before running
        from spidur.factory import ScraperFactory
        from tests.test_lib import DummyScraper

        ScraperFactory.register("dummy", DummyScraper)
        return old_run_batch(batch, out, seen)

    monkeypatch.setattr(runner, "_run_batch", patched_run_batch)

    results = Runner.run([target], seen=set())

    assert "dummy" in results
    assert isinstance(results["dummy"], list)
    assert all("url" in r for r in results["dummy"])
