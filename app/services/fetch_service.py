from __future__ import annotations
import logging
from typing import Any, Iterator

from app.abstraction.base_api_client import BaseApiClient
from app.abstraction.base_hit_parser import BaseHitParser
from app.config.settings import Settings
from app.exceptions.scraper_exceptions import ParseError
from app.monitoring.scrape_statistics import ScrapeStatistics
from app.storage.failed_item_store import FailedItemStore

ALLOWED_COUNTRIES = {"US", "CA"}


class FetchService:
    def __init__(
        self,
        api_client: BaseApiClient,
        hit_parser: BaseHitParser,
        failed_item_store: FailedItemStore,
        statistics: ScrapeStatistics,
        settings: Settings,
        logger: logging.Logger | None = None,
    ) -> None:
        self.api_client = api_client
        self.hit_parser = hit_parser
        self.failed_item_store = failed_item_store
        self.statistics = statistics
        self.settings = settings
        self.run_id = settings.run_id
        self.logger = logger or logging.getLogger("scraper")
        self._all_records: list[dict] | None = None  # cached so get_total_expected() doesn't re-fetch

    def fetch_all(self) -> Iterator[Any]:
        records = self._fetch_raw()
        self.statistics.requests_sent += 1
        self.logger.info("Fetched %d total records from API", len(records))

        for raw_record in records:
            if raw_record.get("country") not in ALLOWED_COUNTRIES:
                continue
            try:
                item = self.hit_parser.parse(raw_record)
            except ParseError as exc:
                self.logger.warning("Parse failed id=%s: %s", raw_record.get("id"), exc)
                self.failed_item_store.record(stage="parse", reason=str(exc), raw=raw_record, run_id=self.run_id)
                self.statistics.items_failed += 1
                continue

            if not item.is_valid():
                self.failed_item_store.record(stage="validate", reason="is_valid() False", raw=raw_record, run_id=self.run_id)
                self.statistics.items_failed += 1
                continue

            yield item

    def get_total_expected(self) -> int:
        """US+CA count — used by RunMonitor for the coverage report."""
        records = self._fetch_raw()
        return sum(1 for r in records if r.get("country") in ALLOWED_COUNTRIES)

    def _fetch_raw(self) -> list[dict]:
        if self._all_records is None:
            self._all_records = self.api_client.get(self.settings.base_url)
        return self._all_records