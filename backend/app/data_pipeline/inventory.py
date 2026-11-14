"""
FlameLens - NASA PSI Data Pipeline
Inventory management and local file tracking.
"""

import json
import logging

from pathlib import Path
from datetime import datetime

from .settings import (
    INVENTORY_PATH,
)

from .normalizer import utc_now


logger = logging.getLogger(__name__)


# =====================================================
# 1. DEFAULT INVENTORY STRUCTURE
# =====================================================

def empty_inventory() -> dict:
    """Return a new empty inventory structure."""

    return {
        "schema_version": 3,
        "investigations": {},
        "last_scan": None,
        "last_report": None,
    }


# =====================================================
# 2. ATOMIC JSON WRITING
# =====================================================

def atomic_write_json(
    path: Path,
    data: dict,
) -> None:
    """
    Write JSON safely using a temporary file.

    The original inventory is not replaced unless
    the temporary JSON has been written successfully.
    """

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary = path.with_name(
        path.name + ".tmp"
    )

    try:
        with temporary.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

            file.flush()

            import os
            os.fsync(file.fileno())

        # Verify generated JSON before replacing original.
        with temporary.open(
            "r",
            encoding="utf-8"
        ) as file:

            json.load(file)

        temporary.replace(path)

    except Exception:
        temporary.unlink(missing_ok=True)
        raise


# =====================================================
# 3. LOAD INVENTORY
# =====================================================

def load_inventory(
    path: Path = INVENTORY_PATH,
) -> dict:
    """
    Load existing inventory.

    If the file is corrupt, preserve it as a backup
    and stop instead of silently starting with empty data.
    """

    path = Path(path)

    if not path.exists():
        logger.info(
            "No previous inventory found. Creating a new one."
        )

        return empty_inventory()

    try:
        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "Inventory root must be a JSON object."
            )

        if not isinstance(
            data.get("investigations"),
            dict
        ):
            raise ValueError(
                "Invalid investigations structure."
            )

        data.setdefault("schema_version", 3)

        data.setdefault(
            "last_scan",
            None
        )

        data.setdefault(
            "last_report",
            None
        )

        return data

    except Exception as exc:

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup = path.with_name(
            f"inventory.corrupt.{timestamp}.json"
        )

        try:
            path.replace(backup)

        except OSError:
            logger.exception(
                "Could not preserve corrupted inventory."
            )

        raise RuntimeError(
            f"Inventory is invalid. "
            f"Original preserved at: {backup}. "
            f"Reason: {exc}"
        ) from exc


# =====================================================
# 4. SAVE INVENTORY
# =====================================================

def save_inventory(
    inventory: dict,
    path: Path = INVENTORY_PATH,
) -> None:
    """Update inventory timestamp and save safely."""

    inventory["last_scan"] = utc_now()

    atomic_write_json(
        Path(path),
        inventory
    )


# =====================================================
# 5. LOCAL FILE VALIDATION
# =====================================================

def local_file_is_valid(
    record: dict,
) -> bool:
    """
    Check whether a previously downloaded file
    still exists and has the expected size.
    """

    local_path = record.get(
        "local_path"
    )

    if not local_path:
        return False

    path = Path(local_path)

    if not path.exists() or not path.is_file():
        return False

    expected_size = record.get(
        "downloaded_size_bytes"
    )

    try:
        actual_size = path.stat().st_size

    except OSError:
        return False

    if actual_size <= 0:
        return False

    if expected_size is not None:
        return actual_size == expected_size

    return True


# =====================================================
# 6. INVESTIGATION DISK USAGE
# =====================================================

def investigation_disk_usage_bytes(
    investigation_id: str,
    download_root: Path,
) -> int:
    """
    Calculate actual disk usage for one investigation.

    Includes files not yet registered in inventory.
    Ignores temporary .part files.
    """

    folder = (
        Path(download_root)
        / investigation_id
    )

    if not folder.exists():
        return 0

    total_bytes = 0

    for file_path in folder.rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.name.endswith(".part"):
            continue

        try:
            total_bytes += file_path.stat().st_size

        except OSError as exc:
            logger.warning(
                "Could not read file size: %s | %s",
                file_path,
                exc
            )

    return total_bytes


# =====================================================
# 7. FILE STATUS COMPARISON
# =====================================================

def compare_file_record(
    new_fingerprint: str,
    old_record: dict | None,
) -> str:
    """
    Compare a newly discovered file with its old record.

    Returns:
        new
        unchanged
        changed
    """

    if not old_record:
        return "new"

    old_fingerprint = old_record.get(
        "fingerprint"
    )

    if old_fingerprint == new_fingerprint:
        return "unchanged"

    return "changed"
