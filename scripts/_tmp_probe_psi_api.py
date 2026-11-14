from __future__ import annotations

import json
from pathlib import Path

import httpx

ids = ["PSI-25", "PSI-26", "PSI-98", "PSI-99", "PSI-100", "PSI-101", "PSI-102"]
numeric = [pid.split("-")[1] for pid in ids]

candidates = []
for pid, num in zip(ids, numeric):
    candidates.extend(
        [
            f"https://psi.nasa.gov/geode-py/ws/studies/{pid}",
            f"https://psi.nasa.gov/geode-py/ws/investigations/{pid}",
            f"https://psi.nasa.gov/geode-py/ws/studies/{pid}/files",
            f"https://psi.nasa.gov/geode-py/ws/investigations/{pid}/files",
            f"https://psi.nasa.gov/osdr/data/osd/files/{num}",
            f"https://psi.nasa.gov/osdr/data/osd/meta/{num}",
            f"https://osdr.nasa.gov/osdr/data/osd/files/{num}",
            f"https://osdr.nasa.gov/osdr/data/osd/meta/{num}",
            f"https://psi.nasa.gov/physci/ws/investigations/{pid}",
            f"https://psi.nasa.gov/physci/api/investigations/{pid}",
        ]
    )

# Generic search/list endpoints
candidates.extend(
    [
        "https://psi.nasa.gov/geode-py/ws/search",
        "https://psi.nasa.gov/osdr/data/search",
        "https://osdr.nasa.gov/osdr/data/search?term=PSI-25&type=cgene",
        "https://osdr.nasa.gov/osdr/data/search?term=BASS-II",
        "https://psi.nasa.gov/physci/repo/search?q=combustion&data_source=psi&data_type=investigation",
        "https://nasa-psi.s3.us-west-2.amazonaws.com/?list-type=2&prefix=PSI-25&max-keys=20",
        "https://nasa-psi.s3.us-west-2.amazonaws.com/?prefix=PSI-25",
        "https://psi.nasa.gov/geode-py/ws/investigations/PSI-25/image",
    ]
)

out_lines: list[str] = []
client = httpx.Client(follow_redirects=True, timeout=20.0, headers={"User-Agent": "FlameLens-audit/0.1"})
seen: set[str] = set()
for url in candidates:
    if url in seen:
        continue
    seen.add(url)
    try:
        resp = client.get(url)
        ctype = resp.headers.get("content-type", "")
        snippet = resp.text[:300].replace("\n", " ")
        out_lines.append(f"{resp.status_code} {len(resp.content):8d} {ctype[:40]:40s} {url}")
        out_lines.append(f"    {snippet}")
    except Exception as exc:
        out_lines.append(f"ERR {url} {exc}")

path = Path("data/metadata/_tmp_psi_api_probe.txt")
path.write_text("\n".join(out_lines), encoding="utf-8")
print(f"wrote {path} ({path.stat().st_size} bytes, {len(seen)} urls)")
