import json
import os
from typing import Optional, Dict

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trusted_sources.json")

_cache: Optional[Dict] = None


def load_sources() -> Dict:
    global _cache
    if _cache is None:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


def get_brand_info(brand: Optional[str]) -> Optional[Dict]:
    if not brand:
        return None
    sources = load_sources()
    key = brand.strip().lower().replace(" ", "_")
    return sources.get(key)


def is_domain_official(brand: Optional[str], domain: str) -> Optional[bool]:
    """Return True/False if we can verify, None if brand unknown (no claim made)."""
    info = get_brand_info(brand)
    if not info:
        return None
    official = [d.lower() for d in info.get("official_domains", [])]
    domain = domain.lower()
    return any(domain == d or domain.endswith("." + d) for d in official)
