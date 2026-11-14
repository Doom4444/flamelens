from pathlib import Path

import httpx

js = httpx.get(
    "https://psi.nasa.gov/physci/repo/main.5216219a85b99359.js",
    timeout=60.0,
    headers={"User-Agent": "FlameLens-audit/0.1"},
).text

needles = [
    "fileType",
    "FileType",
    "Invalid File Type",
    "startingFilePath",
    "obfuscationcode",
    "postFileCustomEndpoint",
]
out = []
for needle in needles:
    out.append(f"==== {needle} count={js.count(needle)}")
    idx = 0
    n = 0
    while n < 4:
        i = js.find(needle, idx)
        if i < 0:
            break
        out.append(js[max(0, i - 180) : i + 220])
        out.append("----")
        idx = i + len(needle)
        n += 1

Path("data/metadata/_tmp_psi_live/js_filetypes.txt").write_text("\n".join(out), encoding="utf-8")
print("wrote", len(out))
