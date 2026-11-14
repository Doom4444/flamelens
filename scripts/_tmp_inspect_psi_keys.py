from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

src = Path("data/metadata/_tmp_psi_live")
lines: list[str] = []

for path in sorted(src.glob("PSI-*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    lines.append("=" * 80)
    lines.append(path.name)
    lines.append("ALL KEYS: " + ", ".join(sorted(data.keys())))
    for k in sorted(data.keys()):
        v = data[k]
        if isinstance(v, list):
            lines.append(f"  {k}: list n={len(v)}")
            if v and isinstance(v[0], dict):
                lines.append(f"    item_keys={sorted(v[0].keys())}")
                if "file_name" in v[0]:
                    names = [str(x.get("file_name")) for x in v[:8]]
                    lines.append(f"    sample_files={names}")
            elif v and not isinstance(v[0], (dict, list)):
                lines.append(f"    sample={v[:5]!r}")
        elif isinstance(v, dict):
            lines.append(f"  {k}: dict keys={sorted(v.keys())[:30]} n={len(v)}")
        elif isinstance(v, str):
            snippet = v.replace("\n", " ")[:140]
            lines.append(f"  {k}: str len={len(v)} {snippet!r}")
        else:
            lines.append(f"  {k}: {type(v).__name__}={v!r}")

    # file-like collections
    file_like = {}
    for k, v in data.items():
        if isinstance(v, list) and v and isinstance(v[0], dict) and (
            "file_name" in v[0] or "filename" in v[0] or "s3_path" in v[0]
        ):
            file_like[k] = len(v)
    lines.append(f"FILE-LIKE FIELDS: {file_like}")

    # research area
    for key in [
        "researchArea",
        "research_area",
        "researchAreas",
        "title",
        "investigationTitle",
        "relatedInvestigations",
        "related",
        "publications",
        "readme",
        "studyFiles",
        "files",
        "fileTree",
        "currentFiles",
        "version",
        "versionNumber",
        "currentVersion",
        "totalSize",
        "size",
        "subResearchArea",
        "impacts",
        "benefits",
        "earthBenefits",
        "researchImpacts",
    ]:
        if key in data:
            val = data[key]
            if isinstance(val, str):
                lines.append(f"SPECIAL {key}: {val[:200]!r}")
            else:
                lines.append(f"SPECIAL {key}: {type(val).__name__} {val if not isinstance(val, (dict,list)) else (len(val) if hasattr(val,'__len__') else '')}")

Path("data/metadata/_tmp_psi_live/json_keys.txt").write_text("\n".join(lines), encoding="utf-8")
print("wrote json_keys.txt", len(lines))
