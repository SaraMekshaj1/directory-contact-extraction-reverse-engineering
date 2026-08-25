from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Iterable, Optional

from app.abstraction.base_exporter import BaseExporter
from app.exceptions.scraper_exceptions import ExportError


class JsonlExporter(BaseExporter):
    def __init__(self, output_path: Path, logger: Optional[logging.Logger] = None) -> None:
        self.output_path = Path(output_path)
        self._file = None
        self._logger = logger or logging.getLogger(__name__)
        self._count = 0

    def open(self) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._file = self.output_path.open("w", encoding="utf-8")
        except OSError as exc:
            raise ExportError(f"Failed to open {self.output_path} for writing: {exc}") from exc

    def write_row(self, item: Any) -> None:
        if self._file is None:
            raise ExportError("JsonlExporter.write_row called before open()")
        row = item.to_row() if hasattr(item, "to_row") else dict(item)
        try:
            self._file.write(json.dumps(row, default=str, ensure_ascii=False) + "\n")
        except (TypeError, ValueError, OSError) as exc:
            raise ExportError(f"Failed to write row {row!r}: {exc}") from exc
        self._count += 1

    def write_batch(self, items: Iterable[Any]) -> None:
        for item in items:
            self.write_row(item)
        if self._file:
            self._file.flush()

    def close(self) -> None:
        if self._file:
            self._file.close()
            self._logger.info("JSONL export complete: %d record(s) -> %s", self._count, self.output_path)
        self._file = None