from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Optional

@dataclass(slots=True)
class Item:
    id: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    linkedin: Optional[str] = None

    def is_valid(self) -> bool:
        return bool(self.id) and bool(self.full_name) and bool(self.email)

    def dedup_key(self) -> str:
        return self.id

    def to_row(self) -> dict[str, Any]:
        return asdict(self)