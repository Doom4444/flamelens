"""Create JSON and HTML reports for FlameLens pipeline runs."""

import html
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import settings

logger = logging.getLogger(__name__)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_html(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def format_number(value: Any, decimals: int = 2) -> str:
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "0"


def get_report_id(summary: dict) -> str:
    return str(
        summary.get("run_id")
        or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    )


def atomic_write(path: Path, content: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(path.name + ".tmp")

    try:
        with temp_path.open("w", encoding="utf-8", newline="") as file:
            file.write(content)
            file.flush()

        temp_path.replace(path)

    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def generate_json_report(summary: dict, output_path: Path) -> Path:
    output_path = Path(output_path)

    data = {
        "report_generated_at": utc_now(),
        **summary,
    }

    serialized = json.dumps(
        data,
        indent=4,
        ensure_ascii=False,
        default=str,
    )

    json.loads(serialized)

    atomic_write(output_path, serialized + "\n")

    logger.info("JSON report saved: %s", output_path)

    return output_path


def status_badge(status: str) -> str:
    status = str(status or "unknown").lower()

    allowed = {
        "completed",
        "completed_with_errors",
        "partial",
        "failed",
        "running",
        "dry_run_completed",
        "started",
    }

    if status not in allowed:
        status = "unknown"

    return (
        f'<span class="badge {safe_html(status)}">'
        f'{safe_html(status.replace("_", " ").title())}</span>'
    )


def summary_cards(summary: dict) -> str:
    items = [
        ("Investigations Discovered", summary.get("investigations_discovered", 0)),
        ("Investigations Scanned", summary.get("investigations_scanned", 0)),
        ("Investigations Completed", summary.get("investigations_completed", 0)),
        ("Investigations Partial", summary.get("investigations_partial", 0)),
        ("Investigations Failed", summary.get("investigations_failed", 0)),
        ("Files Found", summary.get("files_found", 0)),
        ("Files Downloaded", summary.get("files_downloaded", 0)),
        ("Unchanged Files", summary.get("unchanged_files", 0)),
        ("Downloaded MB", format_number(summary.get("downloaded_mb", 0))),
        ("Pending Approval", len(summary.get("pending_approval", []) or [])),
        ("Errors", len(summary.get("errors", []) or [])),
    ]

    return "\n".join(
        f'<div class="card"><div class="label">{safe_html(k)}</div>'
        f'<div class="value">{safe_html(v)}</div></div>'
        for k, v in items
    )


def investigation_table(summary: dict) -> str:
    items = summary.get("investigations", []) or []

    if not items:
        return "<p>No investigation results available.</p>"

    rows = []

    for item in items:
        budget = json.dumps(
            item.get("budget", {}) or {},
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        rows.append(
            "<tr>"
            f"<td>{safe_html(item.get('investigation_id'))}</td>"
            f"<td>{safe_html(item.get('name'))}</td>"
            f"<td>{status_badge(item.get('status'))}</td>"
            f"<td>{safe_html(item.get('files_found', 0))}</td>"
            f"<td>{safe_html(item.get('downloaded_files', 0))}</td>"
            f"<td>{safe_html(item.get('unchanged_files', 0))}</td>"
            f"<td>{safe_html(format_number(item.get('downloaded_mb', 0)))}</td>"
            f"<td><details><summary>Budget</summary><pre>{safe_html(budget)}</pre></details></td>"
            "</tr>"
        )

    return (
        "<div class='scroll'><table><thead><tr>"
        "<th>Investigation ID</th><th>Name</th><th>Status</th>"
        "<th>Files Found</th><th>Downloaded</th><th>Unchanged</th>"
        "<th>Downloaded MB</th><th>Budget Details</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def pending_table(summary: dict) -> str:
    items = summary.get("pending_approval", []) or []

    if not items:
        return "<p>No files pending approval.</p>"

    rows = []

    for item in items:
        rows.append(
            "<tr>"
            f"<td>{safe_html(item.get('investigation_id'))}</td>"
            f"<td>{safe_html(item.get('name'))}</td>"
            f"<td>{safe_html(item.get('path'))}</td>"
            f"<td>{safe_html(item.get('size_mb', 'Unknown'))}</td>"
            f"<td>{safe_html(item.get('reason', 'Requires approval'))}</td>"
            "</tr>"
        )

    return (
        "<div class='scroll'><table><thead><tr>"
        "<th>Investigation</th><th>File Name</th><th>Path</th>"
        "<th>Size MB</th><th>Reason</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def errors_section(summary: dict) -> str:
    errors = summary.get("errors", []) or []

    if not errors:
        return "<p>No errors reported.</p>"

    return "\n".join(
        "<div class='error'><pre>"
        + safe_html(
            json.dumps(
                err,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
        + "</pre></div>"
        for err in errors
    )


def generate_html_report(summary: dict, output_path: Path) -> Path:
    output_path = Path(output_path)

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlameLens Pipeline Report</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;padding:28px;font-family:Arial,sans-serif;background:#f4f6f9;color:#263238}}
main{{max-width:1400px;margin:auto}}
header{{background:#172554;color:white;padding:28px;border-radius:12px;margin-bottom:22px}}
.meta{{line-height:1.9;font-size:14px}}
section{{background:white;padding:22px;border-radius:12px;margin-bottom:22px;box-shadow:0 2px 8px #0000000d}}
h2{{margin-top:0;color:#172554}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:14px}}
.card{{background:#f8fafc;padding:18px;border-radius:9px;border-left:4px solid #2563eb}}
.label{{font-size:13px;color:#64748b;margin-bottom:10px}}
.value{{font-size:24px;font-weight:bold;color:#172554}}
.scroll{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;min-width:760px}}
th,td{{padding:12px;border-bottom:1px solid #e2e8f0;text-align:left;vertical-align:top;font-size:13px}}
th{{background:#f1f5f9}}
.badge{{display:inline-block;padding:5px 9px;border-radius:20px;font-size:11px;font-weight:bold}}
.completed{{background:#dcfce7;color:#166534}}
.completed_with_errors,.partial{{background:#fef3c7;color:#92400e}}
.failed{{background:#fee2e2;color:#991b1b}}
.running,.started{{background:#dbeafe;color:#1e40af}}
.dry_run_completed{{background:#ede9fe;color:#5b21b6}}
.unknown{{background:#e2e8f0;color:#334155}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}}
.error{{background:#fff1f2;border-left:4px solid #dc2626;padding:12px;margin:10px 0}}
footer{{text-align:center;color:#64748b;font-size:12px;padding:18px}}
@media print{{body{{background:white;padding:8px}}section{{box-shadow:none;border:1px solid #ddd}}}}
</style>
</head>
<body>
<main>
<header>
<h1>FlameLens Pipeline Report</h1>
<div class="meta">
<div><b>Run ID:</b> {safe_html(summary.get("run_id", "unknown"))}</div>
<div><b>Mode:</b> {safe_html(summary.get("mode", "unknown"))}</div>
<div><b>Status:</b> {status_badge(summary.get("status"))}</div>
<div><b>Dry Run:</b> {safe_html(summary.get("dry_run", False))}</div>
<div><b>Started:</b> {safe_html(summary.get("started_at", "Unknown"))}</div>
<div><b>Finished:</b> {safe_html(summary.get("finished_at", "Unknown"))}</div>
<div><b>Generated:</b> {safe_html(utc_now())}</div>
</div>
</header>

<section>
<h2>Run Overview</h2>
<div class="cards">{summary_cards(summary)}</div>
</section>

<section>
<h2>Investigation Results</h2>
{investigation_table(summary)}
</section>

<section>
<h2>Pending Approval</h2>
{pending_table(summary)}
</section>

<section>
<h2>Errors and Warnings</h2>
{errors_section(summary)}
</section>

<footer>FlameLens | NASA PSI Combustion Data Pipeline</footer>
</main>
</body>
</html>"""

    atomic_write(output_path, document)

    logger.info("HTML report saved: %s", output_path)

    return output_path


def save_run_reports(summary: dict, report_root: Path = None) -> dict:
    if report_root is None:
        report_root = settings.REPORT_ROOT

    report_root = Path(report_root)
    report_root.mkdir(parents=True, exist_ok=True)

    report_id = get_report_id(summary)

    json_path = report_root / f"run_{report_id}.json"
    html_path = report_root / f"run_{report_id}.html"

    generate_json_report(summary, json_path)
    generate_html_report(summary, html_path)

    logger.info("Run reports generated successfully.")

    return {
        "json": json_path,
        "html": html_path,
    }