"""NASA PSI downloader with a shared per-investigation disk budget."""



import asyncio

import logging

import re

from datetime import datetime, timezone

from pathlib import Path



from playwright.async_api import Page



from . import settings

from .normalizer import clean_name, generate_timestamp, generate_fingerprint

from .inventory import (

    local_file_is_valid,

    compare_file_record,

    investigation_disk_usage_bytes,

)

from .validator import validate_download_content





logger = logging.getLogger(__name__)



MB = 1024 * 1024

DOWNLOAD_DELAY_SECONDS = 0.5



DOWNLOAD_BUTTON_PATTERN = re.compile(

    r"^\s*download\s*$",

    re.IGNORECASE,

)





def utc_now() -> str:

    return datetime.now(timezone.utc).isoformat()





def size_to_bytes(size_mb: float) -> int:

    return int(round(float(size_mb) * MB))





def file_key(file_info: dict) -> str:

    return (

        str(file_info.get("path", ""))

        .replace("\\", "/")

        .strip("/")

        .casefold()

    )





def usage_bytes(investigation_id: str) -> int:

    return investigation_disk_usage_bytes(

        investigation_id,

        settings.DOWNLOAD_ROOT,

    )





def build_destination_path(

    file_info: dict,

    investigation_id: str,

) -> Path:

    parts = [

        part

        for part in str(file_info.get("path", "")).replace(

            "\\", "/"

        ).split("/")

        if part

    ]



    if parts and parts[0].casefold() == investigation_id.casefold():

        parts = parts[1:]



    if not parts:

        raise ValueError(

            f"Invalid repository path: {file_info.get('path')!r}"

        )



    original_name = Path(

        file_info.get("name") or parts[-1]

    ).name



    safe_dirs = [

        clean_name(part)

        for part in parts[:-1]

    ]



    safe_name = clean_name(original_name)



    stem = Path(safe_name).stem

    suffix = Path(safe_name).suffix



    timestamped_name = (

        f"{stem}_{generate_timestamp()}{suffix}"

    )



    destination_dir = (

        Path(settings.DOWNLOAD_ROOT)

        / clean_name(investigation_id)

    )



    for part in safe_dirs:

        destination_dir /= part



    destination_dir.mkdir(

        parents=True,

        exist_ok=True,

    )



    return destination_dir / timestamped_name





async def locate_visible_file(

    page: Page,

    scraper,

    target_path: str,

):

    snapshot = await scraper.snapshot_visible_tree(page)

    structured = scraper.attach_metadata(snapshot)



    target = (

        str(target_path)

        .replace("\\", "/")

        .casefold()

    )



    for row, info in structured:

        current = (

            str(info.get("path", ""))

            .replace("\\", "/")

            .casefold()

        )



        if current == target:

            if info.get("folder"):

                raise RuntimeError(

                    f"Target path is a folder: {target_path}"

                )



            return row



    raise RuntimeError(

        f"File row is not visible after completed crawl: {target_path}"

    )





async def trigger_download(
    page: Page,
    row,
    expected_filename: str | None = None,
):
    """Select the requested FILE row and download only that file.

    NASA's tree can mark both an expanded parent folder and its child file
    as ``is-selected``. Folder rows must therefore never be counted as
    selected files or clicked while clearing stale file selections.
    """
    target_text = " ".join((await row.inner_text()).split())
    target_handle = await row.element_handle()
    if target_handle is None:
        raise RuntimeError(f"Target file row is no longer attached: {target_text}")

    # In the PSI repository tree, file rows contain the fa-file-alt icon;
    # folder rows do not. Restrict every selection check to file rows.
    file_rows_selector = (
        "a.panel-block.selectable:visible:has(i.fa-file-alt)"
    )

    def selected_expression():
        return """element =>
            element.classList.contains('is-selected') ||
            element.classList.contains('selected') ||
            element.classList.contains('active') ||
            element.getAttribute('aria-selected') === 'true' ||
            element.getAttribute('aria-checked') === 'true' ||
            !!element.querySelector(
                'input[type=\"checkbox\"], [role=\"checkbox\"]:checked'
            )
        """

    async def selected_file_rows_state():
        return await page.locator(file_rows_selector).evaluate_all(
            r"""(elements) => elements.map((element, index) => ({
                index,
                text: (element.innerText || '').replace(/\s+/g, ' ').trim(),
                selected: element.classList.contains('is-selected') ||
                    element.classList.contains('selected') ||
                    element.classList.contains('active') ||
                    element.getAttribute('aria-selected') === 'true' ||
                    element.getAttribute('aria-checked') === 'true' ||
                    !!element.querySelector(
                        'input[type=\"checkbox\"], [role=\"checkbox\"]:checked'
                    )
            })).filter(item => item.selected)"""
        )

    async def target_is_selected():
        return await row.evaluate(selected_expression())

    # Clear stale selections from OTHER FILE rows only. Re-query after each
    # click because Angular may update/reorder the live tree after a click.
    for _ in range(50):
        selected = await selected_file_rows_state()
        other = None
        for item in selected:
            candidate = page.locator(file_rows_selector).nth(item["index"])
            same_row = await candidate.evaluate(
                "(element, target) => element === target",
                target_handle,
            )
            if not same_row:
                other = candidate
                break

        if other is None:
            break

        await other.click(timeout=settings.ELEMENT_TIMEOUT_MS)
        await page.wait_for_timeout(200)
    else:
        raise RuntimeError(
            "Could not clear previous selected file rows from NASA tree."
        )

    # Select the requested file if it is not already selected.
    if not await target_is_selected():
        name_cell = row.locator(".file-name-column").first
        click_target = name_cell if await name_cell.count() else row
        await click_target.click(timeout=settings.ELEMENT_TIMEOUT_MS)

    # Confirm exactly one selected FILE, ignoring selected parent folders.
    interval_ms = 250
    max_attempts = max(1, settings.ELEMENT_TIMEOUT_MS // interval_ms)
    confirmed = False
    selected = []

    for _ in range(max_attempts):
        await page.wait_for_timeout(interval_ms)
        selected = await selected_file_rows_state()
        if await target_is_selected() and len(selected) == 1:
            selected_row = page.locator(file_rows_selector).nth(
                selected[0]["index"]
            )
            if await selected_row.evaluate(
                "(element, target) => element === target",
                target_handle,
            ):
                confirmed = True
                break

    selected = await selected_file_rows_state()
    logger.info(
        "NASA file selection check | target=%s | selected_files=%s",
        target_text,
        selected,
    )

    if not confirmed:
        raise RuntimeError(
            "NASA UI did not confirm that the requested file is the only "
            f"selected file. Selected files: {selected!r}"
        )

    # Locate the Download button.
    button = page.get_by_role(
        "button",
        name=DOWNLOAD_BUTTON_PATTERN,
    ).first
    if not await button.count():
        button = page.get_by_text(DOWNLOAD_BUTTON_PATTERN).first
    if not await button.count() or not await button.is_visible():
        raise RuntimeError("Visible NASA Download button was not found.")

    async with page.expect_download(
        timeout=settings.DOWNLOAD_TIMEOUT_MS
    ) as event:
        await button.click(timeout=settings.ELEMENT_TIMEOUT_MS)

    download = await event.value
    actual_name = Path(download.suggested_filename).name.casefold()
    expected_name = (
        Path(expected_filename).name.casefold()
        if expected_filename
        else None
    )

    logger.info(
        "Download event received | expected=%s | actual=%s",
        expected_filename,
        download.suggested_filename,
    )

    # NASA metadata names may include the investigation and folder path,
    # while the browser download name may contain only the original leaf name.
    # Accept exact matches or an exact leaf-name suffix; reject unrelated files.
    filename_matches = bool(
        expected_name
        and (
            actual_name == expected_name
            or expected_name.endswith("_" + actual_name)
        )
    )

    if expected_name and not filename_matches:
        await download.cancel()
        raise RuntimeError(
            "NASA returned a different file than requested: "
            f"expected={expected_filename!r}, "
            f"actual={download.suggested_filename!r}. "
            "Download cancelled; no file was saved."
        )

    return download


async def log_download_diagnostics(

    download,

    temporary: Path,

    expected_name: str,

):

    """

    Log information about the actual browser download.

    """



    if not temporary.is_file():

        raise RuntimeError(

            "Download did not create a local file."

        )



    actual_size = temporary.stat().st_size



    with temporary.open("rb") as file:

        first_bytes = file.read(128)



    download_failure = await download.failure()



    logger.info(

        "Download diagnostics | "

        "expected_name=%s | "

        "actual_filename=%s | "

        "size=%s bytes | "

        "first_bytes=%s | "

        "browser_failure=%s",

        expected_name,

        download.suggested_filename,

        actual_size,

        repr(first_bytes),

        download_failure,

    )



    if download_failure:

        raise RuntimeError(

            f"Browser download failure: {download_failure}"

        )



    if actual_size <= 0:

        raise RuntimeError(

            "Downloaded file is empty."

        )



    return actual_size





async def download_one_file(

    page: Page,

    scraper,

    file_info: dict,

    investigation_id: str,

    allowed_total_bytes: int,

) -> dict:



    target_path = file_info.get("path")



    if not target_path:

        raise ValueError(

            "File metadata has no repository path."

        )



    row = await locate_visible_file(

        page,

        scraper,

        target_path,

    )



    logger.info(

        "Preparing download | investigation=%s | file=%s",

        investigation_id,

        target_path,

    )



    download = await trigger_download(

        page,

        row,

        expected_filename=file_info.get("name"),

    )



    destination = build_destination_path(

        file_info,

        investigation_id,

    )



    temporary = destination.with_name(

        destination.name + ".part"

    )



    try:

        await download.save_as(temporary)



        # DOWNLOAD DIAGNOSTICS

        actual_size = await log_download_diagnostics(

            download=download,

            temporary=temporary,

            expected_name=file_info.get(

                "name",

                destination.name,

            ),

        )



        # CONTENT VALIDATION

        valid, message = validate_download_content(

            temporary,

            file_info.get("name", destination.name),

        )



        if not valid:

            logger.error(

                "Content validation failed | "

                "file=%s | "

                "message=%s",

                target_path,

                message,

            )



            raise RuntimeError(

                f"Downloaded content failed validation: {message}"

            )



        logger.info(

            "Content validation passed | file=%s | message=%s",

            target_path,

            message,

        )



        # BUDGET VALIDATION

        current_usage = usage_bytes(investigation_id)



        if current_usage + actual_size > allowed_total_bytes:

            raise RuntimeError(

                "Budget guard rejected file: actual size would exceed "

                f"the allowed total "

                f"({(current_usage + actual_size) / MB:.3f} MB > "

                f"{allowed_total_bytes / MB:.3f} MB)."

            )



        if destination.exists():

            raise FileExistsError(

                f"Timestamped destination already exists: {destination}"

            )



        # Commit the file only after all validations pass.

        temporary.replace(destination)



        return {

            "local_path": str(destination),

            "saved_name": destination.name,

            "original_name": file_info.get(

                "name",

                destination.name,

            ),

            "downloaded_size_bytes": actual_size,

            "downloaded_size_mb": round(

                actual_size / MB,

                6,

            ),

            "downloaded_at": utc_now(),

            "validation_status": "valid",

            "validation_message": message,

        }



    except Exception:

        temporary.unlink(missing_ok=True)

        raise





def should_download(

    file_info: dict,

    old_record: dict | None,

    fingerprint: str,

):



    if not old_record:

        return True, "new"



    state = compare_file_record(

        fingerprint,

        old_record,

    )



    if state in ("new", "changed"):

        return True, state



    if state == "unchanged":



        if not local_file_is_valid(old_record):

            return True, "local_file_missing_or_invalid"



        return False, "unchanged"



    return True, "unknown_status"





def select_raw_files(

    raw_files: list[dict],

    remaining_bytes: int,

):

    """

    Sparse 0/1 knapsack plus up to the 5 MB overrun.

    """



    known = []

    unknown = []



    for item in raw_files:



        size = item.get("size_mb")



        if size is None or float(size) < 0:

            unknown.append(item)



        else:

            weight = size_to_bytes(size)



            if weight > 0:

                known.append((item, weight))



            else:

                unknown.append(item)



    # Sparse DP:

    # used bytes -> selected file indices.

    dp = {

        0: ()

    }



    for index, (_, weight) in enumerate(known):



        for used, indices in list(dp.items()):



            new_used = used + weight



            if (

                new_used <= remaining_bytes

                and new_used not in dp

            ):

                dp[new_used] = indices + (index,)



    best_used = max(dp)



    best_indices = list(

        dp[best_used]

    )



    selected = [

        known[index][0]

        for index in best_indices

    ]



    selected_set = set(best_indices)



    # Optional single-file overrun.

    overrun_candidate = None



    max_overrun = size_to_bytes(

        settings.RAW_AUTO_OVERRUN_MB

    )



    best_total = best_used



    for index, (item, weight) in enumerate(known):



        if index in selected_set:

            continue



        combined = best_used + weight



        if not (

            remaining_bytes

            < combined

            <= remaining_bytes + max_overrun

        ):

            continue



        if combined > best_total:

            best_total = combined

            overrun_candidate = item



    if overrun_candidate is not None:

        selected.append(overrun_candidate)



    selected_paths = {

        file_key(item)

        for item in selected

    }



    skipped = [

        item

        for item, _ in known

        if file_key(item) not in selected_paths

    ]



    skipped.extend(unknown)



    overrun_path = (

        file_key(overrun_candidate)

        if overrun_candidate

        else None

    )



    return (

        selected,

        skipped,

        {

            "selected_files": len(selected),

            "skipped_files": len(skipped),

            "selected_advertised_size_mb": round(

                sum(

                    float(item.get("size_mb") or 0)

                    for item in selected

                ),

                3,

            ),

            "used_overrun": overrun_candidate is not None,

            "overrun_file": (

                overrun_candidate.get("path")

                if overrun_candidate

                else None

            ),

            "overrun_file_key": overrun_path,

        },

    )





async def download_file_group(

    page: Page,

    scraper,

    files: list[dict],

    investigation_id: str,

    previous_files: dict,

    current_records: dict,

    result: dict,

    dry_run: bool,

    allowed_total_bytes: int,

    raw_overrun_key: str | None = None,

):



    for info in files:



        key = file_key(info)



        if not key:



            result["errors"].append({

                "stage": "download",

                "error": "File has no path",

            })



            continue



        old = previous_files.get(key)



        fingerprint = generate_fingerprint(info)



        needs_download, reason = should_download(

            info,

            old,

            fingerprint,

        )



        if not needs_download:



            current_records[key] = {

                **old,

                **info,

                "fingerprint": fingerprint,

                "last_seen": utc_now(),

                "download_status": "downloaded",

                "presence_status": "present",

            }



            result["unchanged_files"] += 1



            continue



        size_mb = info.get("size_mb")



        if size_mb is None or float(size_mb) < 0:



            result["pending_approval"].append({

                "path": info.get("path"),

                "name": info.get("name"),

                "size_mb": size_mb,

                "reason": "unknown_file_size",

                "download_reason": reason,

            })



            current_records[key] = {

                **(old or {}),

                **info,

                "fingerprint": fingerprint,

                "download_status": "pending_approval",

                "presence_status": "present",

                "last_seen": utc_now(),

            }



            continue



        if dry_run:



            result["planned_downloads"].append({

                "path": info.get("path"),

                "size_mb": size_mb,

                "reason": reason,

            })



            continue



        advertised_bytes = size_to_bytes(size_mb)



        current_usage = usage_bytes(investigation_id)



        this_file_limit = allowed_total_bytes



        if raw_overrun_key and key == raw_overrun_key:

            this_file_limit += size_to_bytes(

                settings.RAW_AUTO_OVERRUN_MB

            )



        if current_usage + advertised_bytes > this_file_limit:



            result["budget_skipped_files"].append({

                "path": info.get("path"),

                "size_mb": size_mb,

                "reason": "advertised_size_exceeds_remaining_budget",

            })



            current_records[key] = {

                **(old or {}),

                **info,

                "fingerprint": fingerprint,

                "download_status": "not_selected_budget",

                "presence_status": "present",

                "last_seen": utc_now(),

            }



            continue



        try:



            downloaded = await download_one_file(

                page,

                scraper,

                info,

                investigation_id,

                this_file_limit,

            )



            current_records[key] = {

                **info,

                **downloaded,

                "fingerprint": fingerprint,

                "download_status": "downloaded",

                "presence_status": "present",

                "last_seen": utc_now(),

            }



            result["downloaded_files"] += 1



            result["downloaded_mb"] += (

                downloaded["downloaded_size_mb"]

            )



            logger.info(

                "Downloaded %s (%.3f MB)",

                info.get("path"),

                downloaded["downloaded_size_mb"],

            )



        except Exception as exc:



            logger.exception(

                "Download failed: %s",

                info.get("path"),

            )



            result["errors"].append({

                "stage": "download",

                "file": info.get("path"),

                "error": str(exc),

            })



            current_records[key] = {

                **(old or {}),

                **info,

                "fingerprint": fingerprint,

                "download_status": "failed",

                "presence_status": "present",

                "error": str(exc),

                "last_seen": utc_now(),

            }



        await asyncio.sleep(

            DOWNLOAD_DELAY_SECONDS

        )





async def download_investigation_files(

    page: Page,

    scraper,

    investigation_result: dict,

    previous_files: dict | None = None,

    dry_run: bool = False,

) -> dict:

    """

    Download Non-Raw first, then Raw under one shared 500 MB budget.

    """



    investigation_id = investigation_result.get(

        "investigation_id"

    )



    if not investigation_id:

        raise ValueError(

            "Investigation result is missing investigation_id."

        )



    if investigation_result.get("status") != "completed":

        raise RuntimeError(

            f"Refusing download from incomplete scan: {investigation_id}"

        )



    files = investigation_result.get(

        "files",

        [],

    )



    previous_files = previous_files or {}



    result = {

        "investigation_id": investigation_id,

        "status": "started",

        "files_found": len(files),

        "downloaded_files": 0,

        "unchanged_files": 0,

        "downloaded_mb": 0.0,

        "pending_approval": [],

        "planned_downloads": [],

        "budget_skipped_files": [],

        "skipped_raw_files": [],

        "errors": [],

        "budget": {},

        "started_at": utc_now(),

    }



    current_records = {}



    try:



        limit_bytes = size_to_bytes(

            settings.PER_INVESTIGATION_LIMIT_MB

        )



        start_usage = usage_bytes(

            investigation_id

        )



        if start_usage > limit_bytes:



            logger.warning(

                "%s already exceeds the standard budget: %.3f MB",

                investigation_id,

                start_usage / MB,

            )



        non_raw = [

            file_info

            for file_info in files

            if not file_info.get("is_raw", False)

        ]



        raw = [

            file_info

            for file_info in files

            if file_info.get("is_raw", False)

        ]



        # Non-Raw priority does not bypass the shared total budget.

        await download_file_group(

            page=page,

            scraper=scraper,

            files=non_raw,

            investigation_id=investigation_id,

            previous_files=previous_files,

            current_records=current_records,

            result=result,

            dry_run=dry_run,

            allowed_total_bytes=limit_bytes,

        )



        # Calculate remaining budget after Non-Raw files.

        current_usage = usage_bytes(

            investigation_id

        )



        remaining = max(

            0,

            limit_bytes - current_usage,

        )



        # Select Raw files using 0/1 Knapsack.

        selected_raw, skipped_raw, selection = select_raw_files(

            raw,

            remaining,

        )



        result["skipped_raw_files"] = [

            {

                "path": file_info.get("path"),

                "size_mb": file_info.get("size_mb"),

                "reason": (

                    "unknown_size"

                    if file_info.get("size_mb") is None

                    else "outside_available_budget"

                ),

            }

            for file_info in skipped_raw

        ]



        # Unknown-size Raw files require manual approval.

        for item in skipped_raw:



            if (

                item.get("size_mb") is None

                or float(item.get("size_mb", -1)) < 0

            ):



                result["pending_approval"].append({

                    "path": item.get("path"),

                    "name": item.get("name"),

                    "size_mb": item.get("size_mb"),

                    "reason": "unknown_file_size",

                    "file_type": "raw",

                })



        # Only the one explicitly selected overrun Raw file

        # receives the additional 5 MB allowance.

        await download_file_group(

            page=page,

            scraper=scraper,

            files=selected_raw,

            investigation_id=investigation_id,

            previous_files=previous_files,

            current_records=current_records,

            result=result,

            dry_run=dry_run,

            allowed_total_bytes=limit_bytes,

            raw_overrun_key=selection["overrun_file_key"],

        )



        # Verify actual disk usage.

        actual_usage = usage_bytes(

            investigation_id

        )



        result["budget"] = {

            "limit_mb": settings.PER_INVESTIGATION_LIMIT_MB,

            "raw_auto_overrun_mb": settings.RAW_AUTO_OVERRUN_MB,

            "starting_usage_mb": round(

                start_usage / MB,

                3,

            ),

            "actual_usage_mb": round(

                actual_usage / MB,

                3,

            ),

            "remaining_mb": round(

                max(0, limit_bytes - actual_usage) / MB,

                3,

            ),

            "over_limit_mb": round(

                max(0, actual_usage - limit_bytes) / MB,

                3,

            ),

            "within_standard_budget": actual_usage <= limit_bytes,

            "within_absolute_budget": actual_usage <= (

                limit_bytes

                + size_to_bytes(settings.RAW_AUTO_OVERRUN_MB)

            ),

            "raw_selection": selection,

        }



        if not result["budget"]["within_absolute_budget"]:



            result["errors"].append({

                "stage": "budget_validation",

                "error": (

                    "Actual disk usage exceeded the 500 MB + 5 MB "

                    "absolute ceiling."

                ),

                "actual_usage_mb": round(

                    actual_usage / MB,

                    3,

                ),

            })



        if dry_run:

            result["status"] = "dry_run_completed"



        elif result["errors"]:

            result["status"] = "completed_with_errors"



        else:

            result["status"] = "completed"



    except Exception as exc:



        logger.exception(

            "Investigation download failed: %s",

            investigation_id,

        )



        result["status"] = "failed"



        result["errors"].append({

            "stage": "investigation_download",

            "error": str(exc),

        })



    finally:



        result["finished_at"] = utc_now()



    result["downloaded_mb"] = round(

        result["downloaded_mb"],

        3,

    )



    result["file_records"] = current_records



    return result
