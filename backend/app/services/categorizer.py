import json
from pathlib import Path

_CATEGORIES = None

def _load_categories() -> list[dict]:
    global _CATEGORIES
    if _CATEGORIES is None:
        path = Path(__file__).parent.parent / "fixtures" / "categories.json"
        with open(path) as f:
            _CATEGORIES = json.load(f)
    return _CATEGORIES

def categorize_channel(title: str, description: str | None) -> str:
    text = f"{title} {description or ''}".lower()
    categories = _load_categories()
    for cat in categories:
        if cat["slug"] == "other":
            continue
        for keyword in cat["keywords"]:
            if keyword in text:
                return cat["slug"]
    return "other"
