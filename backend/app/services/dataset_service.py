"""Dataset-group queries.

Dataset groups are derived by the Stage 1 audit. They are never presented as
NASA PSI dataset entities.
"""

from __future__ import annotations

from typing import Any

from app.data_pipeline.metadata_repository import store
from app.services.investigation_service import get_datasets


def list_datasets(investigation_id: str | None = None) -> dict[str, Any]:
    if investigation_id:
        return get_datasets(investigation_id)

    datasets = store.datasets_payload.get("datasets", [])
    per_investigation: dict[str, int] = {}
    for item in datasets:
        key = item.get("investigation_id", "UNKNOWN")
        per_investigation[key] = per_investigation.get(key, 0) + 1

    return {
        "investigation_id": None,
        "items": datasets,
        "total_items": len(datasets),
        "total_size_bytes": sum(int(item.get("total_size_bytes") or 0) for item in datasets),
        "per_investigation": dict(sorted(per_investigation.items())),
        "method": store.datasets_payload.get("method", {}),
    }
