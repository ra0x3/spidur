import asyncio
import multiprocessing
import logging
from typing import List, Dict, Any, Set
from .core import Target
from .factory import ScraperFactory

log = logging.getLogger("scrape-runner")


def _run_batch(batch: List[Target], out: Any, seen: Set[str], overwrite: bool):
    async def _inner():
        for t in batch:
            log.info(f"Running scraper: {t.name}")
            scraper = ScraperFactory.create(t)
            results = await scraper.fetch(seen, overwrite)
            out[t.name] = results or []

    asyncio.run(_inner())


class Runner:
    """Parallel runner across multiple scrapers."""

    @classmethod
    def run(cls, targets: List[Target], seen: Set[str], overwrite: bool) -> Dict[str, List[Dict]]:
        if not targets:
            return {}

        batch_size = max(1, len(targets) // multiprocessing.cpu_count())
        batches = [targets[i : i + batch_size] for i in range(0, len(targets), batch_size)]

        with multiprocessing.Manager() as manager:
            out = manager.dict()
            jobs = [multiprocessing.Process(target=_run_batch, args=(b, out, seen, overwrite)) for b in batches]

            for j in jobs:
                j.start()
            for j in jobs:
                j.join()

            return dict(out)
