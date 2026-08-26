import json
from app.normalizer.field_normalizer import PhoneNormalizer

pn = PhoneNormalizer()
with open("data/products.jsonl") as f:
    for line in f:
        row = json.loads(line)
        phone = row.get("phone")
        if not phone:
            continue
        digits_count = sum(c.isdigit() for c in phone)
        normalized = pn.normalize(phone)
        # flag anything that ISN'T a clean (XXX) XXX-XXXX result
        if normalized and not normalized.startswith("(") :
            print(f"UNCHANGED/UNUSUAL: {phone!r}")