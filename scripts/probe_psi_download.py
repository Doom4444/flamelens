#!/usr/bin/env python3
"""Probe PSI download accessibility without downloading scientific data.

For each sampled file this script requests only a single byte (HTTP Range
``bytes=0-0``) after resolving the PSI download endpoint to its short-lived
signed S3 URL. It records status codes, byte ranges and content lengths, and
never writes file content to disk.

Usage
-----
    python scripts/probe_psi_download.py --write
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "metadata" / "psi_api" / "download_probe.json"

HEADERS = {
    "User-Agent": "FlameLens-audit/0.1",
    "Referer": "https://psi.nasa.gov/physci/repo/",
    "Accept": "*/*",
    "Origin": "https://psi.nasa.gov",
}

SAMPLES = [
    ("PSI-25", "PSI-25_Experimental table_BASS-II.csv", 1),
    ("PSI-25", "PSI-25_Raw Data_BASS_GMT50_SAMPLE_147_TEST_B1.mp4", 2),
    ("PSI-25", "PSI-25_metadata_PSI_metadata_PSI-101_BASS-II.zip", 4),
    ("PSI-26", "PSI-26_Experimental table_BASS.csv", 1),
    ("PSI-98", "PSI-98_Experimental table_SAFFIRE-1.csv", 1),
    ("PSI-99", "PSI-99_Experimental table_SAFFIRE-2.csv", 1),
    ("PSI-100", "PSI-100_Experimental table_SAFFIRE-3.csv", 1),
    ("PSI-101", "PSI-101_Experimental table_SAME-R.csv", 1),
    ("PSI-102", "PSI-102_Experimental table_SAME.csv", 1),
]


def probe(client: httpx.Client, investigation_id: str, filename: str, version: int) -> dict[str, Any]:
    endpoint = (
        f"https://psi.nasa.gov/geode-py/ws/studies/{investigation_id}/download"
        f"?file={quote(filename, safe='')}&version={version}&redirect=false"
    )
    result: dict[str, Any] = {
        "investigation_id": investigation_id,
        "filename": filename,
        "version": version,
        "endpoint": endpoint,
    }
    try:
        response = client.get(endpoint)
        body = response.text.strip()
        result["endpoint_status"] = response.status_code
        result["signed_url_returned"] = response.status_code == 200 and body.startswith("http")
        if not result["signed_url_returned"]:
            result["endpoint_body_preview"] = body[:200]
            return result

        from urllib.parse import urlsplit

        result["signed_url_host"] = urlsplit(body).netloc
        result["signed_url_expires_present"] = "Expires=" in body or "X-Amz-Expires=" in body

        head = client.head(body)
        result["head_status"] = head.status_code

        ranged = client.get(body, headers={"Range": "bytes=0-0"})
        result["range_status"] = ranged.status_code
        result["range_content_range"] = ranged.headers.get("content-range")
        result["range_content_length"] = ranged.headers.get("content-length")
        result["range_supported"] = ranged.status_code == 206 and bool(ranged.headers.get("content-range"))
        content_range = ranged.headers.get("content-range") or ""
        if "/" in content_range:
            total = content_range.rsplit("/", 1)[-1]
            result["remote_size_bytes"] = int(total) if total.isdigit() else None
    except Exception as error:  # noqa: BLE001 - probe records the failure verbatim
        result["error"] = f"{type(error).__name__}: {error}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write download_probe.json")
    args = parser.parse_args()

    with httpx.Client(follow_redirects=False, timeout=60.0, headers=HEADERS) as client:
        results = [probe(client, *sample) for sample in SAMPLES]

    payload = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "method": (
            "Resolve the PSI download endpoint, then request Range: bytes=0-0 from the signed S3 URL. "
            "No file content is persisted. HEAD is recorded to document that S3 rejects it."
        ),
        "results": results,
    }

    for result in results:
        print(
            f"{result['investigation_id']:8s} "
            f"endpoint={result.get('endpoint_status')} "
            f"head={result.get('head_status')} "
            f"range={result.get('range_status')} "
            f"size={result.get('remote_size_bytes')} "
            f"host={result.get('signed_url_host')}"
        )

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nWrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
