import random
import string
from datetime import datetime, timezone


def generate_complaint_number(category_code: str) -> str:
    prefix = "".join(ch for ch in category_code if ch.isalpha())[:4].upper() or "GEN"
    stamp = datetime.now(timezone.utc).strftime("%y%m%d")
    suffix = "".join(random.choices(string.digits, k=4))
    return f"NGC-{prefix}-{stamp}-{suffix}"
