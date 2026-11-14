from __future__ import annotations

import json
from pathlib import Path

import httpx

ids = ["PSI-25", "PSI-26", "PSI-98", "PSI-99", "PSI-100", "PSI-101", "PSI-102"]
out_dir = Path("data/metadata/_tmp_psi_live")
out_dir.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "FlameLens-audit/0.1",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://psi.nasa.gov/physci/repo/",
}

client = httpx.Client(follow_redirects=True, timeout=60.0, headers=headers)
summary: list[str] = []

for pid in ids:
    urls = [
        f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{pid}",
        f"https://psi.nasa.gov/geode-py/ws/repo/investigations/{pid}/files",
        f"https://psi.nasa.gov/geode-py/ws/files/v2?investigation={pid}",
        f"https://psi.nasa.gov/geode-py/ws/files/v2?accession={pid}",
        f"https://psi.nasa.gov/geode-py/ws/files/v2?id={pid}",
    ]
    for url in urls:
        try:
            resp = client.get(url)
        except Exception as exc:
            summary.append(f"ERR GET {url} {exc}")
            continue
        ctype = resp.headers.get("content-type", "")
        summary.append(f"{resp.status_code} {len(resp.content):8d} {ctype[:40]} GET {url}")
        if resp.status_code == 200 and "json" in ctype:
            name = url.replace("https://", "").replace("/", "_")
            path = out_dir / f"{pid}_{name[-80:]}.json"
            path.write_bytes(resp.content)
            summary.append(f"    saved {path.name}")

# POST files/v2 variants
post_bodies = [
    {"investigation": "PSI-25"},
    {"accession": "PSI-25"},
    {"id": "PSI-25"},
    {"study": "PSI-25"},
    {"path": "PSI-25"},
    {"filePath": "PSI-25"},
]
for body in post_bodies:
    url = "https://psi.nasa.gov/geode-py/ws/files/v2"
    try:
        resp = client.post(url, json=body)
        summary.append(
            f"{resp.status_code} {len(resp.content):8d} POST {url} {json.dumps(body)} {resp.text[:180]!r}"
        )
    except Exception as exc:
        summary.append(f"ERR POST {body} {exc}")

(out_dir / "probe_summary.txt").write_text("\n".join(summary), encoding="utf-8")
print("\n".join(summary[:80]))
print(f"wrote {out_dir / 'probe_summary.txt'}")
