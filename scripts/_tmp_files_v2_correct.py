from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

import httpx

headers = {
    "User-Agent": "FlameLens-audit/0.1",
    "Accept": "application/json",
    "Referer": "https://psi.nasa.gov/physci/repo/",
    "Origin": "https://psi.nasa.gov",
}
client = httpx.Client(follow_redirects=True, timeout=60.0, headers=headers)
url = "https://psi.nasa.gov/geode-py/ws/files/v2"

bodies = [
    {"folder": "psi-data/PSI-25", "fileType": "", "studyId": "PSI-25", "version": 4, "obfuscationcode": ""},
    {"folder": "psi-data/PSI-25/", "fileType": "", "studyId": "PSI-25", "version": 4, "obfuscationcode": ""},
    {"folder": "genelab-data/PSI-25", "fileType": "", "studyId": "PSI-25", "version": 4, "obfuscationcode": ""},
    {"folder": "PSI-25", "fileType": "", "studyId": "PSI-25", "version": 4, "obfuscationcode": ""},
    {"folder": "psi-data/PSI-25", "fileType": "all", "studyId": "PSI-25", "version": 4, "obfuscationcode": ""},
    {"folder": "psi-data/PSI-25", "fileType": None, "studyId": "PSI-25", "version": 4, "obfuscationcode": None},
    {"folder": "psi-data/PSI-25", "fileType": "folder", "studyId": "PSI-25", "version": 4, "obfuscationcode": ""},
    {"folder": "", "fileType": "", "studyId": "PSI-25", "version": 4, "obfuscationcode": ""},
    {"folder": "psi-data/", "fileType": "", "studyId": "PSI-25", "version": "", "obfuscationcode": ""},
    {"folder": "psi-data/PSI-25", "fileType": "", "studyId": "PSI-25", "version": "4", "obfuscationcode": ""},
    {"folder": "psi-data/PSI-99", "fileType": "", "studyId": "PSI-99", "version": 5, "obfuscationcode": ""},
]

lines = []
for body in bodies:
    r = client.post(url, json=body)
    preview = r.text[:300].replace("\n", " ")
    lines.append(f"{r.status_code} {len(r.content)} {body} {preview}")
    if r.status_code == 200 and len(r.content) > 80:
        Path("data/metadata/_tmp_psi_live/files_v2_success.json").write_bytes(r.content)
        lines.append("SAVED")
        break

# experimental table signed URL then csv head
exp_url = (
    "https://psi.nasa.gov/geode-py/ws/studies/PSI-25/download"
    "?file=" + quote("PSI-25_Experimental table_BASS-II.csv") + "&version=1&redirect=false"
)
r = client.get(exp_url)
lines.append(f"EXP {r.status_code} {r.headers.get('content-type')} {r.text[:400]!r}")
Path("data/metadata/_tmp_psi_live/exp_table_download_meta.json").write_bytes(r.content)

Path("data/metadata/_tmp_psi_live/files_v2_correct.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
