from __future__ import annotations
import re
from typing import Any
from app.abstraction.base_hit_parser import BaseHitParser
from app.exceptions.scraper_exceptions import ParseError
from app.models.item import Item
from app.normalizer.field_normalizer import PhoneNormalizer, TextNormalizer, EmailNormalizer

ALLOWED_COUNTRIES = {"US", "CA"}
def _strip_html(value):
    if not value:
        return value
    return re.sub(r"<[^>]+>", "", value).strip()

class ItemParser(BaseHitParser):
    def __init__(self):
        self._phone_normalizer = PhoneNormalizer()
        self._text_normalizer = TextNormalizer()
        self._email_normalizer= EmailNormalizer()

    def parse(self, raw_record: dict[str, Any]) -> Item:
        try:
            trainer_id = str(raw_record.get("id", ""))
            name = raw_record.get("display_name", "")
            if not trainer_id or not name:
                raise ParseError("Missing id/display_name")

            return Item(
                id=trainer_id,
                full_name=self._text_normalizer.normalize(name),
                email=self._email_normalizer.normalize(raw_record.get("user_email")) or self._email_normalizer.normalize(raw_record.get("user_email2")),
                phone=self._phone_normalizer.normalize(raw_record.get("phone_number")),
                company=self._text_normalizer.normalize(raw_record.get("company")),
                job_title=self._text_normalizer.normalize(raw_record.get("job_title")),
                address=raw_record.get("address"),
                city=raw_record.get("city"),
                state=raw_record.get("state"),
                country=raw_record.get("country"),
                postcode=raw_record.get("postcode"),
                website=raw_record.get("website"),
                facebook=raw_record.get("facebook"),
                linkedin=raw_record.get("linkedin"),
            )
        except ParseError:
            raise
        except Exception as exc:
            raise ParseError(f"Failed to parse hit: {exc}") from exc