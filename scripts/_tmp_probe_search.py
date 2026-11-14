from __future__ import annotations

import httpx
from pathlib import Path

headers = {
    "User-Agent": "FlameLens-audit/0.1",
    "Accept": "application/json",
    "Referer": "https://psi.nasa.gov/physci/repo/",
}
urls = [
    "https://psi.nasa.gov/geode-py/ws/repo/search?q=combustion&data_source=psi&data_type=investigation",
    "https://psi.nasa.gov/geode-py/ws/repo/search?term=combustion",
    "https://psi.nasa.gov/geode-py/ws/repo/investigations?q=combustion",
    "https://psi.nasa.gov/geode-py/ws/repo/investigations",
    "https://psi.nasa.gov/geode-py/ws/repo/search",
]
client = httpx.Client(follow_redirects=True, timeout=40.0, headers=headers)
lines = []
for url in urls:
    try:
        r = client.get(url)
        lines.append(f"{r.status_code} {len(r.content)} {r.headers.get('content-type')} {url}")
        lines.append(r.text[:250].replace("\n", " "))
        if r.status_code == 200 and "json" in (r.headers.get("content-type") or ""):
            Path("data/metadata/_tmp_psi_live/search_sample.json").write_bytes(r.content)
    except Exception as e:
        lines.append(f"ERR {url} {e}")

# POST search
for body in [
    {"q": "combustion", "data_source": "psi", "data_type": "investigation"},
    {"term": "combustion", "type": "investigation"},
]:
    url = "https://psi.nasa.gov/geode-py/ws/repo/search"
    try:
        r = client.post(url, json=body)
        lines.append(f"{r.status_code} {len(r.content)} POST {url} {body} {r.text[:180]!r}")
    except Exception as e:
        lines.append(f"ERR POST {e}")

Path("data/metadata/_tmp_psi_live/search_probe.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
