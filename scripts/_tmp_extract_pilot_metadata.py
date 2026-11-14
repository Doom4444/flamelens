import json
from pathlib import Path

pilots = [
    "PSI-25",
    "PSI-26",
    "PSI-98",
    "PSI-99",
    "PSI-100",
    "PSI-101",
    "PSI-102",
]
records = [
    json.loads(line)
    for line in Path("data/metadata/psi_descriptions.jsonl").open(encoding="utf-8")
]
by: dict[str, list] = {}
for rec in records:
    by.setdefault(rec["investigation_id"], []).append(rec)

out = Path("data/metadata/_tmp_pilot_extract.txt")
lines: list[str] = []
for pid in pilots:
    recs = by.get(pid, [])
    lines.append("=" * 70)
    lines.append(f"{pid} copies={len(recs)}")
    if not recs:
        continue
    rec = recs[0]
    lines.append(rec["source_url"])
    for item in rec["data"]["project"]:
        lines.append(f"  PROJECT {item['field']}: {item['value']}")
    for sec in rec["data"]["sections"]:
        title = sec.get("title")
        if sec.get("contacts"):
            lines.append(f"  SECTION {title}:")
            for contact in sec["contacts"]:
                lines.append(
                    f"    CONTACT name={contact.get('name')} details={contact.get('details')}"
                )
        else:
            content = (sec.get("content") or "").replace("\n", " / ")
            snippet = content[:800]
            suffix = "..." if len(content) > 800 else ""
            lines.append(f"  SECTION {title}: {snippet}{suffix}")

out.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size} bytes)")
