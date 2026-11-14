"""Small formatting helpers shared by the metadata API.

Sizes use binary units (1 KB = 1024 B) to match the Stage 1 audit
inventories exactly, so the API and the JSON files never disagree.
"""

from __future__ import annotations

import re

_UNITS = (
    ("TB", 1024**4),
    ("GB", 1024**3),
    ("MB", 1024**2),
    ("KB", 1024),
)


def human_bytes(size: int | float | None) -> str | None:
    """Format a byte count using binary units with three decimals."""
    if size is None:
        return None
    size = int(size)
    for unit, divisor in _UNITS:
        if size >= divisor:
            return f"{size / divisor:.3f} {unit}"
    return f"{size} B"


def normalize_space(value: str | None) -> str:
    """Collapse arbitrary whitespace into single spaces."""
    return re.sub(r"\s+", " ", value or "").strip()


def percent(part: int | float, total: int | float) -> float:
    """Return a rounded percentage, safe for a zero denominator."""
    if not total:
        return 0.0
    return round(float(part) / float(total) * 100.0, 2)
