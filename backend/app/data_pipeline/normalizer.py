"""
FlameLens - NASA PSI Data Pipeline
File and metadata normalization utilities.
"""

import hashlib
import re

from pathlib import Path
from datetime import datetime, timezone

from .settings import (
    SUPPORTED_IMAGE_EXTENSIONS,
)


# =====================================================
# 1. DATE AND TIME
# =====================================================

def utc_now() -> str:
    """Return current UTC timestamp."""

    return datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )


def generate_timestamp() -> str:
    """Generate unique timestamp for downloaded filenames."""

    return datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )


# =====================================================
# 2. TEXT NORMALIZATION
# =====================================================

def normalize_text(value: str | None) -> str:
    """Normalize whitespace in text."""

    return re.sub(
        r"\s+",
        " ",
        value or ""
    ).strip()


# =====================================================
# 3. FILE NAME NORMALIZATION
# =====================================================

def clean_name(value: str) -> str:
    """
    Remove characters that are invalid in Windows filenames.
    """

    value = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        str(value)
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    value = value.strip(" ._")

    return value[:150] or "unnamed"


# =====================================================
# 4. FILE SIZE NORMALIZATION
# =====================================================

def parse_size_mb(value: str | None) -> float | None:
    """
    Convert a displayed file size into MB.

    Supported units:
    B, Bytes, KB, KiB, MB, MiB, GB, GiB, TB, TiB
    """

    if not value:
        return None

    match = re.search(
        r"(?<![\w.])([\d,]+(?:\.\d+)?)\s*"
        r"(B|bytes?|KB|KiB|MB|MiB|GB|GiB|TB|TiB)\b",
        value,
        re.IGNORECASE
    )

    if not match:
        return None

    number = float(
        match.group(1).replace(",", "")
    )

    unit = match.group(2).lower()

    factors = {
        "b": 1 / 1048576,
        "byte": 1 / 1048576,
        "bytes": 1 / 1048576,

        "kb": 1 / 1024,
        "kib": 1 / 1024,

        "mb": 1,
        "mib": 1,

        "gb": 1024,
        "gib": 1024,

        "tb": 1048576,
        "tib": 1048576,
    }

    return number * factors[unit]


# =====================================================
# 5. FILE TYPE DETECTION
# =====================================================

def is_image_file(filename: str) -> bool:
    """Check whether a file is an image based on its extension."""

    return (
        Path(filename).suffix.lower()
        in SUPPORTED_IMAGE_EXTENSIONS
    )


def is_raw_path(path: str) -> bool:
    """
    Identify files located inside Raw Data folders.

    Folder matching is case-insensitive.
    """

    return any(
        part.strip().casefold() in {
            "raw data",
            "rawdata"
        }
        for part in path.replace("\\", "/").split("/")
    )


# =====================================================
# 6. FILE FINGERPRINT
# =====================================================

def generate_fingerprint(file_info: dict) -> str:
    """
    Generate a metadata-based fingerprint.

    Used to detect changes between NASA scans.

    Note:
    This is not a content checksum because the remote file
    content is not downloaded at this stage.
    """

    fields = (
        "path",
        "size_mb",
        "text",
        "href",
    )

    payload = "|".join(
        str(file_info.get(field, ""))
        for field in fields
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()


# =====================================================
# 7. TREE PATH CONSTRUCTION
# =====================================================

def attach_paths(
    visible_rows: list[tuple],
) -> list[tuple]:
    """
    Build hierarchical paths from visible PSI tree rows.

    Each row must contain:
        depth
        name
        folder
        text
    """

    stack = []

    sibling_counts = {}

    output = []

    for row, original_info in visible_rows:

        info = dict(original_info)

        depth = info["depth"]

        name = info["name"]

        # Remove folders at the same or deeper level.
        while stack and stack[-1][0] >= depth:
            stack.pop()

        parent = (
            stack[-1][1]
            if stack
            else ""
        )

        # Handle duplicate filenames under same parent.
        sibling_key = (
            parent.casefold(),
            name.casefold()
        )

        sibling_counts[sibling_key] = (
            sibling_counts.get(sibling_key, 0) + 1
        )

        occurrence = sibling_counts[sibling_key]

        path_name = (
            name
            if occurrence == 1
            else f"{name} ({occurrence})"
        )

        full_path = (
            f"{parent}/{path_name}".strip("/")
        )

        info.update({
            "path": full_path,
            "parent": parent,

            "size_mb": parse_size_mb(
                info.get("text", "")
            ),

            "is_raw": is_raw_path(full_path),

            "is_image": is_image_file(name),
        })

        output.append(
            (row, info)
        )

        if info["folder"]:
            stack.append(
                (depth, full_path)
            )

    # Detect already-expanded folders.
    for index, (_, info) in enumerate(output):

        has_children = (
            info["folder"]
            and index + 1 < len(output)
            and output[index + 1][1]["depth"] > info["depth"]
        )

        info["has_visible_children"] = has_children

        info["is_expanded"] = bool(
            has_children
            or info.get("folder_open")
            or info.get("aria_expanded") == "true"
        )

    return output
