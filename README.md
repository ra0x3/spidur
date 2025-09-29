# spidur 🕷️

[![PyPI version](https://img.shields.io/pypi/v/spidur.svg)](https://pypi.org/project/spidur/)
[![License](https://img.shields.io/github/license/ra0x3/spidur)](LICENSE)
[![Tests](https://github.com/ra0x3/spidur/actions/workflows/tests.yml/badge.svg)](https://github.com/ra0x3/spidur/actions)

🕷️ **spidur** is a tiny, hackable framework for running custom scrapers in parallel.

- No business logic
- Just a base class + registry + runner
- Multiprocessing + async friendly

---

## ✨ Features

- **Zero assumptions** — bring your own scraper code.
- **Base class for scrapers** — implement 2 methods and you’re done.
- **Parallel execution** — run across all CPU cores.
- **OSS-style** — small, clean, and easy to hack.

---

## 📦 Install

```bash
pip install spidur
```

Or install with poetry

```
poetry add spidur
```

### Quickstart

```python
from spidur.base import Target, Scraper
from spidur.factory import ScraperFactory
from spidur.runner import Runner

class MyScraper(Scraper):
    async def discover_urls(self, page, known, overwrite=False):
        return ["http://example.com/1", "http://example.com/2"]

    async def scrape_page(self, page, url):
        return {"url": url, "data": "demo"}

    async def fetch(self, known, overwrite=False):
        urls = await self.discover_urls(None, known)
        return [await self.scrape_page(None, u) for u in urls]

# register scraper
ScraperFactory.register("example", MyScraper)

# run
target = Target(name="example", start_url="http://example.com")
results = Runner.run([target], seen=set(), overwrite=True)

print(results)

```

### Tests

```
poetry install
poetry run pytest
```
