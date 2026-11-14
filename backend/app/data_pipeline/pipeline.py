"""Main orchestration for the NASA PSI FlameLens data pipeline."""

import argparse
import asyncio
import logging

from datetime import datetime, timezone
from typing import Optional

from . import settings
from .psi_client import PSIClient
from .scraper import PSIScraper
from .downloader import download_investigation_files

from .inventory import (
    empty_inventory,
    load_inventory,
    save_inventory,
)

from .normalizer import generate_fingerprint
from .reports import save_run_reports


logger = logging.getLogger(__name__)


# ============================================================
# 1. GENERAL HELPERS
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_key(node: dict) -> str:
    return (
        str(node.get("path", ""))
        .replace("\\\\", "/")
        .strip("/")
        .casefold()
    )


def create_run_summary(
    mode: str,
    dry_run: bool,
) -> dict:

    return {
        "run_id": datetime.now(timezone.utc).strftime(
            "%Y%m%d_%H%M%S_%f"
        ),

        "mode": mode,
        "dry_run": dry_run,
        "status": "running",

        "started_at": utc_now(),
        "finished_at": None,

        "investigations_discovered": 0,
        "investigations_scanned": 0,
        "investigations_completed": 0,
        "investigations_partial": 0,
        "investigations_failed": 0,

        "files_found": 0,
        "files_downloaded": 0,
        "unchanged_files": 0,

        "downloaded_mb": 0.0,

        "pending_approval": [],
        "errors": [],
        "investigations": [],
    }


# ============================================================
# 2. INVENTORY HELPERS
# ============================================================

def get_previous_files(
    inventory: dict,
    investigation_id: str,
) -> dict:

    return (
        inventory.get("investigations", {})
        .get(investigation_id, {})
        .get("files", {})
    )


def merge_investigation_inventory(
    scrape_result: dict,
    download_result: dict,
    previous_files: dict,
) -> dict:

    """
    Merge a fully completed scan.

    - Preserve downloaded file metadata.
    - Preserve previous records for files not downloaded.
    - Record all discovered files.
    - Mark missing files only after a completed scan.
    """

    download_records = download_result.get(
        "file_records",
        {},
    )

    pending_keys = {
        file_key(item)
        for item in download_result.get(
            "pending_approval",
            [],
        )
    }

    budget_skipped_keys = {
        file_key(item)
        for item in download_result.get(
            "budget_skipped_files",
            [],
        )
    }

    raw_skipped_keys = {
        file_key(item)
        for item in download_result.get(
            "skipped_raw_files",
            [],
        )
    }

    merged = {}
    current_keys = set()

    for node in scrape_result.get("files", []):

        key = file_key(node)

        if not key:
            continue

        current_keys.add(key)

        old = previous_files.get(
            key,
            {},
        )

        downloaded = download_records.get(
            key,
            {},
        )

        fingerprint = generate_fingerprint(node)

        if downloaded:

            record = {
                **old,
                **node,
                **downloaded,
            }

        elif old:

            record = {
                **old,
                **node,
            }

        else:

            status = "not_downloaded"

            if key in pending_keys:
                status = "pending_approval"

            elif (
                key in budget_skipped_keys
                or key in raw_skipped_keys
            ):
                status = "not_selected_budget"

            record = {
                **node,
                "download_status": status,
            }

        record.update({
            "fingerprint": fingerprint,
            "last_seen": utc_now(),
            "presence_status": "present",
        })

        merged[key] = record

    # This function is called only after a completed tree scan.

    for old_key, old_record in previous_files.items():

        if old_key not in current_keys:

            merged[old_key] = {
                **old_record,
                "presence_status": "missing",
                "last_seen": old_record.get("last_seen"),
            }

    return merged


def update_inventory_for_investigation(
    inventory: dict,
    investigation: dict,
    scrape_result: dict,
    download_result: dict,
    previous_files: dict,
) -> None:

    investigation_id = investigation["investigation_id"]

    inventory.setdefault(
        "investigations",
        {},
    )

    inventory["investigations"][investigation_id] = {

        "id": investigation_id,

        "name": investigation.get(
            "name",
            investigation_id,
        ),

        "url": (
            scrape_result.get("url")
            or investigation.get("url")
        ),

        "last_scan": utc_now(),

        "scan_status": download_result.get(
            "status",
            "completed",
        ),

        "files": merge_investigation_inventory(
            scrape_result,
            download_result,
            previous_files,
        ),
    }


# ============================================================
# 3. INVESTIGATION PROCESSING
# ============================================================

async def process_investigation(
    client: PSIClient,
    scraper: PSIScraper,
    investigation: dict,
    inventory: dict,
    dry_run: bool = False,
) -> dict:

    investigation_id = investigation.get(
        "investigation_id"
    )

    result = {

        "investigation_id": investigation_id,

        "name": investigation.get(
            "name",
            investigation_id,
        ),

        "status": "started",

        "files_found": 0,

        "downloaded_files": 0,

        "unchanged_files": 0,

        "downloaded_mb": 0.0,

        "pending_approval": [],

        "errors": [],

        "budget": {},

        "started_at": utc_now(),

        "finished_at": None,
    }

    try:

        logger.info(
            "Processing investigation %s",
            investigation_id,
        )

        # STEP 1: SCRAPE

        scrape = await scraper.scrape_investigation(
            investigation
        )

        result["scrape_status"] = scrape.get("status")

        result["files_found"] = len(
            scrape.get("files", [])
        )

        result["errors"].extend(
            {
                "stage": "scraping",
                **error,
            }
            for error in scrape.get("errors", [])
        )

        # STEP 2: CHECK SCRAPE COMPLETENESS

        # An incomplete tree must never alter inventory
        # or imply that files are missing.

        if scrape.get("status") != "completed":

            result["status"] = scrape.get(
                "status",
                "failed",
            )

            logger.warning(
                "Skipping download/inventory for incomplete scan %s",
                investigation_id,
            )

            return result

        # STEP 3: GET PREVIOUS INVENTORY

        previous = get_previous_files(
            inventory,
            investigation_id,
        )

        # STEP 4: DOWNLOAD

        download = await download_investigation_files(
            page=client.page,
            scraper=scraper,
            investigation_result=scrape,
            previous_files=previous,
            dry_run=dry_run,
        )

        result["download_status"] = download.get(
            "status"
        )

        for field in (
            "downloaded_files",
            "unchanged_files",
            "downloaded_mb",
            "budget",
        ):

            result[field] = download.get(
                field,
                result[field],
            )

        result["pending_approval"] = [
            {
                "investigation_id": investigation_id,
                **item,
            }
            for item in download.get(
                "pending_approval",
                [],
            )
        ]

        result["errors"].extend(
            {
                "investigation_id": investigation_id,
                **error,
            }
            for error in download.get(
                "errors",
                [],
            )
        )

        # STEP 5: UPDATE INVENTORY

        if not dry_run:

            update_inventory_for_investigation(
                inventory=inventory,
                investigation=investigation,
                scrape_result=scrape,
                download_result=download,
                previous_files=previous,
            )

            # Save after each completed investigation.
            # Earlier successful work remains safe if a later
            # investigation fails.

            save_inventory(
                inventory,
                settings.INVENTORY_PATH,
            )

        result["status"] = download.get(
            "status",
            "completed",
        )

    except Exception as exc:

        logger.exception(
            "Investigation processing failed: %s",
            investigation_id,
        )

        result["status"] = "failed"

        result["errors"].append({

            "stage": "investigation_processing",

            "error": str(exc),

        })

    finally:

        result["finished_at"] = utc_now()

    return result


# ============================================================
# 4. RUN AGGREGATION
# ============================================================

def add_investigation_result(
    summary: dict,
    result: dict,
) -> None:

    summary["investigations_scanned"] += 1

    summary["files_found"] += result.get(
        "files_found",
        0,
    )

    summary["files_downloaded"] += result.get(
        "downloaded_files",
        0,
    )

    summary["unchanged_files"] += result.get(
        "unchanged_files",
        0,
    )

    summary["downloaded_mb"] += result.get(
        "downloaded_mb",
        0.0,
    )

    summary["pending_approval"].extend(
        result.get("pending_approval", [])
    )

    summary["errors"].extend(
        result.get("errors", [])
    )

    status = result.get("status")

    if status in (
        "completed",
        "completed_with_errors",
        "dry_run_completed",
    ):

        summary["investigations_completed"] += 1

    elif status == "partial":

        summary["investigations_partial"] += 1

    else:

        summary["investigations_failed"] += 1

    summary["investigations"].append(
        result
    )


# ============================================================
# 5. MAIN PIPELINE
# ============================================================

async def run_pipeline(
    mode: str = "initial",
    dry_run: bool = False,
    selected_investigations: Optional[list[str]] = None,
) -> dict:

    """
    Run the complete NASA PSI pipeline.

    mode:
        initial
        update

    dry_run:
        Discover and plan without downloading or
        modifying inventory.

    selected_investigations:
        Optional list of investigation IDs.
    """

    mode = mode.strip().lower()

    if mode not in ("initial", "update"):

        raise ValueError(
            "mode must be either 'initial' or 'update'."
        )

    settings.initialize_directories()

    summary = create_run_summary(
        mode,
        dry_run,
    )

    # STEP 1: LOAD INVENTORY

    inventory = load_inventory()

    if not isinstance(inventory, dict):

        inventory = empty_inventory()

    inventory.setdefault(
        "investigations",
        {},
    )

    logger.info(
        "Starting FlameLens pipeline | mode=%s | dry_run=%s",
        mode,
        dry_run,
    )

    try:

        # STEP 2: START PSI CLIENT

        async with PSIClient() as client:

            scraper = PSIScraper(
                client
            )

            # STEP 3: DISCOVER INVESTIGATIONS

            logger.info(
                "Discovering NASA PSI investigations..."
            )

            investigations = await client.discover_investigations(
                search_term="combustion"
            )

            if not investigations:

                raise RuntimeError(
                    "NASA PSI discovery returned no investigations. "
                    "Inventory was not modified."
                )

            # Filter selected investigation IDs if supplied.

            if selected_investigations:

                selected_ids = {
                    item.strip().upper()
                    for item in selected_investigations
                }

                investigations = [
                    item
                    for item in investigations
                    if str(
                        item.get("investigation_id", "")
                    ).upper() in selected_ids
                ]

                if not investigations:

                    raise RuntimeError(
                        "None of the selected investigation IDs "
                        "were found."
                    )

            summary["investigations_discovered"] = len(
                investigations
            )

            logger.info(
                "Discovered %s investigations.",
                len(investigations),
            )

            # STEP 4: PROCESS EACH INVESTIGATION

            for index, investigation in enumerate(
                investigations,
                start=1,
            ):

                investigation_id = investigation.get(
                    "investigation_id"
                )

                logger.info(
                    "[%s/%s] Processing %s",
                    index,
                    len(investigations),
                    investigation_id,
                )

                one_result = await process_investigation(
                    client=client,
                    scraper=scraper,
                    investigation=investigation,
                    inventory=inventory,
                    dry_run=dry_run,
                )

                add_investigation_result(
                    summary,
                    one_result,
                )

                await asyncio.sleep(0)

        # STEP 5: FINALIZE RUN

        if (
            summary["investigations_failed"] == 0
            and summary["investigations_partial"] == 0
        ):

            if summary["errors"]:

                summary["status"] = "completed_with_errors"

            else:

                summary["status"] = "completed"

        elif summary["investigations_completed"] > 0:

            summary["status"] = "partial"

        else:

            summary["status"] = "failed"

        # Inventory is saved after each successfully completed
        # investigation. Dry runs never modify inventory.

    except asyncio.CancelledError:

        # Handle cancellation separately.
        # Do not report a manually stopped run as "running".

        summary["status"] = "cancelled"

        summary["errors"].append({

            "stage": "pipeline",

            "error": "Pipeline was cancelled by the user.",

        })

        logger.warning(
            "Pipeline cancelled by user."
        )

    except Exception as exc:

        logger.exception(
            "Pipeline execution failed."
        )

        summary["status"] = "failed"

        summary["errors"].append({

            "stage": "pipeline",

            "error": str(exc),

        })

    finally:

        summary["finished_at"] = utc_now()

        summary["downloaded_mb"] = round(
            summary["downloaded_mb"],
            3,
        )

        logger.info(
            "Pipeline finished | status=%s | scanned=%s | "
            "downloaded=%s | MB=%.3f",
            summary["status"],
            summary["investigations_scanned"],
            summary["files_downloaded"],
            summary["downloaded_mb"],
        )

        # Save reports for successful, partial, failed, and dry runs.

        try:

            report_paths = save_run_reports(summary)

            summary["report_paths"] = {

                "json": str(report_paths["json"]),

                "html": str(report_paths["html"]),

            }

            logger.info(
                "Reports saved | JSON: %s | HTML: %s",
                report_paths["json"],
                report_paths["html"],
            )

        except Exception as report_exc:

            logger.exception(
                "Failed to generate pipeline reports."
            )

            summary.setdefault("errors", []).append({

                "stage": "report_generation",

                "error": str(report_exc),

            })

    return summary


# ============================================================
# 6. CONVENIENCE ENTRY POINTS
# ============================================================

async def run_initial_pipeline(
    dry_run: bool = False,
) -> dict:

    return await run_pipeline(
        mode="initial",
        dry_run=dry_run,
    )


async def run_incremental_pipeline(
    dry_run: bool = False,
) -> dict:

    return await run_pipeline(
        mode="update",
        dry_run=dry_run,
    )


# ============================================================
# 7. COMMAND LINE ENTRY POINT
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="NASA PSI FlameLens Data Pipeline"
    )

    parser.add_argument(
        "mode",
        choices=["initial", "update"],
        help="Pipeline mode: initial or update",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Discover and plan without downloading "
            "or modifying inventory"
        ),
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    summary = asyncio.run(
        run_pipeline(
            mode=args.mode,
            dry_run=args.dry_run,
        )
    )

    print("\n========== PIPELINE SUMMARY ==========")

    print(f"Status: {summary['status']}")

    print(
        f"Investigations discovered: "
        f"{summary['investigations_discovered']}"
    )

    print(
        f"Investigations scanned: "
        f"{summary['investigations_scanned']}"
    )

    print(
        f"Investigations completed: "
        f"{summary['investigations_completed']}"
    )

    print(
        f"Investigations partial: "
        f"{summary['investigations_partial']}"
    )

    print(
        f"Investigations failed: "
        f"{summary['investigations_failed']}"
    )

    print(f"Files found: {summary['files_found']}")

    print(f"Files downloaded: {summary['files_downloaded']}")

    print(f"Unchanged files: {summary['unchanged_files']}")

    print(f"Downloaded MB: {summary['downloaded_mb']}")

    print(
        f"Pending approval: "
        f"{len(summary['pending_approval'])}"
    )

    print(f"Errors: {len(summary['errors'])}")

    report_paths = summary.get(
        "report_paths",
        {},
    )

    if report_paths:

        print(
            f"JSON report: {report_paths.get('json')}"
        )

        print(
            f"HTML report: {report_paths.get('html')}"
        )

    print("======================================")