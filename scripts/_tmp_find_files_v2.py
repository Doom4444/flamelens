from __future__ import annotations

import json
from pathlib import Path

import httpx

headers = {
    "User-Agent": "FlameLens-audit/0.1",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://psi.nasa.gov/physci/repo/",
    "Origin": "https://psi.nasa.gov",
}

js_url = "https://psi.nasa.gov/physci/repo/main.5216219a85b99359.js"
client = httpx.Client(follow_redirects=True, timeout=60.0, headers=headers)
js = client.get(js_url).text
Path("data/metadata/_tmp_psi_live/main.js_snip.txt").write_text(
    "files/v2 count=" + str(js.count("files/v2")) + "\n", encoding="utf-8"
)

idx = 0
snippets = []
while True:
    i = js.find("files/v2", idx)
    if i < 0:
        break
    snippets.append(js[max(0, i - 250) : i + 250])
    idx = i + 8
    if len(snippets) >= 8:
        break

Path("data/metadata/_tmp_psi_live/files_v2_js_snippets.txt").write_text(
    "\n\n----\n\n".join(snippets), encoding="utf-8"
)

# also search related strings
for needle in ["fileTree", "currentFiles", "studyFiles", "datamanager", "psi-data", "listFiles"]:
    Path("data/metadata/_tmp_psi_live/files_v2_js_snippets.txt").write_text(
        Path("data/metadata/_tmp_psi_live/files_v2_js_snippets.txt").read_text(encoding="utf-8")
        + f"\n\nNEEDLE {needle} count={js.count(needle)}\n",
        encoding="utf-8",
    )

# POST variants for files/v2
bodies = [
    {"source": "datamanager", "accession": "PSI-25"},
    {"source": "datamanager", "id": "PSI-25"},
    {"source": "datamanager", "path": "PSI-25"},
    {"source": "datamanager", "file": "PSI-25"},
    {"accession": "PSI-25", "source": "psi"},
    {"study_id": "PSI-25"},
    {"studyId": "PSI-25"},
    {"investigationId": "PSI-25"},
    {"investigation_id": "PSI-25"},
    {"prefix": "psi-data/PSI-25"},
    {"prefix": "PSI-25"},
    {"s3_path": "psi-data/PSI-25"},
    {"bucket": "psi-repo-prod", "prefix": "psi-data/PSI-25"},
    {"path": "psi-data/PSI-25"},
    {"remote_path": "psi-data/PSI-25"},
    "PSI-25",
]
lines = []
for body in bodies:
    try:
        if isinstance(body, str):
            r = client.post(
                "https://psi.nasa.gov/geode-py/ws/files/v2",
                content=body,
                headers={**headers, "Content-Type": "application/json"},
            )
        else:
            r = client.post("https://psi.nasa.gov/geode-py/ws/files/v2", json=body)
        preview = r.text[:220].replace("\n", " ")
        lines.append(f"{r.status_code} {len(r.content)} {body} {preview}")
        if r.status_code == 200 and len(r.content) > 100:
            Path("data/metadata/_tmp_psi_live/files_v2_PSI-25.json").write_bytes(r.content)
            lines.append("SAVED files_v2_PSI-25.json")
            break
    except Exception as e:
        lines.append(f"ERR {body} {e}")

# search term=combustion save accessions
r = client.get(
    "https://psi.nasa.gov/geode-py/ws/repo/search",
    params={"term": "combustion", "size": 100},
)
Path("data/metadata/_tmp_psi_live/search_combustion.json").write_bytes(r.content)
data = r.json()
hits = data.get("hits", {}).get("hits", [])
accessions = []
for h in hits:
    src = h.get("_source", {})
    accessions.append(
        {
            "accession": src.get("accession") or src.get("Accession") or src.get("id"),
            "title": src.get("title") or src.get("Title"),
            "acronym": src.get("investigationAcronym") or src.get("acronym"),
            "keys": sorted(src.keys())[:40],
        }
    )
Path("data/metadata/_tmp_psi_live/search_accessions.json").write_text(
    json.dumps({"total": data.get("hits", {}).get("total"), "n_hits": len(hits), "items": accessions}, indent=2),
    encoding="utf-8",
)
lines.append(f"search total={data.get('hits', {}).get('total')} hits={len(hits)}")

Path("data/metadata/_tmp_psi_live/files_v2_probe.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[-30:]))
print("wrote probes")
