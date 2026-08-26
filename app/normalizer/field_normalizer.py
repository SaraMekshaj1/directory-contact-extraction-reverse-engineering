from __future__ import annotations
import re
from typing import Optional


class PhoneNormalizer:
    def normalize(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return value

        digits = re.sub(r"\D", "", value)

        # Junk detection: if there aren't enough digits to be any kind of
        # real phone number, this isn't a phone number at all (e.g. someone
        # typed a note like "contact via email" into the field).
        if len(digits) < 7:
            return None

        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]

        if len(digits) == 10:
            return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"

        # Longer than 10 digits and not a recognized +1 US/CA number ->
        # likely an international number. Leave it as the source gave it.
        return value.strip()


class TextNormalizer:
    """Default normalizer for plain text fields — strips whitespace and
    collapses repeated spaces. Also handles any leftover HTML tags."""

    _tag_re = re.compile(r"<[^>]+>")

    def normalize(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        value = self._tag_re.sub("", value)
        return re.sub(r"\s+", " ", value).strip()