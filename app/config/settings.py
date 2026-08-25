from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    # --- target API -------------------------------------------------
    base_url: str = "https://canfieldtrainerdirectory.com/wp-json/btn-directory/v1/listings?map-search"
    request_method: str = "GET"  
    

    # Set to a non-empty Algolia filter string (e.g. 'categories: gender_male')
    # to scope every brand-crawl query; leave "" to crawl everything.
    category_filter: str = ""

    # Static headers copied from the browser's Network tab.
    headers: dict = field(default_factory=lambda: {
        "User-Agent":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        
    })

    # --- discovery + pagination -----------------------------------------
    # Algolia caps hits per single query, so we can't just page through the
    # whole index -- we discover facet values (brands) first, then page
    # through each brand's slice individually. See fetch_service.py.
    facet_field: str = "attributes.BRAND"
    brand_filter_field: str = "attributes.BRAND"
    hits_per_page: int = 100

    # --- networking / resilience --------------------------------------
    timeout_seconds: float = 30.0
    max_retries: int = 5
    backoff_factor: float = 2.0
    status_forcelist: tuple = (429, 500, 502, 503, 504)

    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_reset_seconds: float = 60.0

    requests_per_second: float | None = 5.0

    # --- run identity / storage ----------------------------------------
    run_id: str = "sunglasshut-run"
    data_dir: Path = Path("data")

    output_csv_path: Path | None = None
    output_jsonl_path: Path | None = None
    failed_items_path: Path | None = None
    dedup_state_path: Path | None = None
    log_file: Path | None = None

    log_level: str = "INFO"

    def __post_init__(self) -> None:
        if self.output_csv_path is None:
            object.__setattr__(self, "output_csv_path", self.data_dir / "products.csv")
        if self.output_jsonl_path is None:
            object.__setattr__(self, "output_jsonl_path", self.data_dir / "products.jsonl")
        if self.failed_items_path is None:
            object.__setattr__(self, "failed_items_path", self.data_dir / "failed_items.jsonl")
        if self.dedup_state_path is None:
            object.__setattr__(self, "dedup_state_path", self.data_dir / "dedup_keys.json")
        if self.log_file is None:
            object.__setattr__(self, "log_file", self.data_dir / "scraper.log")

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

