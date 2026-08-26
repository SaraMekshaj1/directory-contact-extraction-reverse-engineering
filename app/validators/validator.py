from __future__ import annotations
from typing import Iterable
from app.models.item import Item


class ItemValidator:
    def __init__(self, required_fields: Iterable[str] = ("id", "full_name", "email")):
        self._required_fields = tuple(required_fields)

    def is_valid(self, item: Item) -> bool:
        return all(getattr(item, field, None) for field in self._required_fields)