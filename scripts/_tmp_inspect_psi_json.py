from __future__ import annotations

import json
from pathlib import Path

src = Path("data/metadata/_tmp_psi_live")
out_lines: list[str] = []


def summarize(obj, prefix="", depth=0, max_depth=3):
    if depth > max_depth:
        return
    if isinstance(obj, dict):
        out_lines.append(f"{prefix}dict keys={list(obj.keys())[:40]} n={len(obj)}")
        for k, v in list(obj.items())[:25]:
            summarize(v, prefix + f"  {k}.", depth + 1, max_depth)
    elif isinstance(obj, list):
        out_lines.append(f"{prefix}list n={len(obj)} type0={type(obj[0]).__name__ if obj else None}")
        if obj:
            summarize(obj[0], prefix + "  [0].", depth + 1, max_depth)
    else:
        val = obj
        if isinstance(val, str) and len(val) > 160:
            val = val[:160] + "..."
        out_lines.append(f"{prefix}{type(obj).__name__}={val!r}")


for path in sorted(src.glob("PSI-*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    out_lines.append("=" * 80)
    out_lines.append(path.name)
    summarize(data, "", 0, 2)

Path("data/metadata/_tmp_psi_live/json_structure.txt").write_text(
    "\n".join(out_lines), encoding="utf-8"
)
print(f"lines={len(out_lines)}")
print("\n".join(out_lines[:120]))
