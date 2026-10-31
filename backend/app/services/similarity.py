"""Topic-based channel similarity using keyword overlap (Jaccard on token bags)."""

import re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    """Split text into lowercase word tokens (3+ chars)."""
    return [w for w in re.findall(r"\w+", text.lower()) if len(w) >= 3]


def compute_topic_similarity(
    title_a: str,
    desc_a: str | None,
    title_b: str,
    desc_b: str | None,
) -> float:
    """Return Jaccard-like similarity score (0-1) between two channels.

    Compares token bags from title + description. Title tokens are weighted 2x.
    """
    raw_a = _tokenize(f"{title_a} {title_a} {desc_a or ''}")
    raw_b = _tokenize(f"{title_b} {title_b} {desc_b or ''}")

    tokens_a = Counter(raw_a)
    tokens_b = Counter(raw_b)

    intersection = sum((tokens_a & tokens_b).values())
    union = sum((tokens_a | tokens_b).values())

    if union == 0:
        return 0.0
    return round(intersection / union, 3)
