import logging

from typing import Optional
from urllib.parse import urljoin
from datetime import datetime, timezone

from playwright.async_api import Page

from . import settings
from .psi_client import PSIClient
from .normalizer import (
    normalize_text,
    parse_size_mb,
    is_raw_path,
    is_image_file,
    attach_paths,
)


logger = logging.getLogger(__name__)


class PSIScraper:
    """
    Dynamically explores NASA PSI investigation repository trees.

    Responsibilities:
    - Read repository rows efficiently.
    - Identify files and folders.
    - Detect folder expanded/collapsed state.
    - Expand collapsed folders safely.
    - Never collapse folders that are already open.
    - Build hierarchical file paths.
    - Collect metadata for discovered files and folders.
    - Preserve errors when a tree scan is incomplete.
    """

    TREE_SELECTOR = "a.panel-block.selectable:visible"

    FOLDER_ICON_SELECTOR = "i.fa-folder"

    OPEN_FOLDER_ICON_SELECTOR = "i.fa-folder-open"

    REQUIRED_SETTINGS = [
        "TREE_SETTLE_MS",
        "MAX_TREE_ACTIONS",
        "ELEMENT_TIMEOUT_MS",
    ]

    # Maximum time to wait for an individual folder expansion.
    # This is intentionally shorter than the general element timeout.
    FOLDER_EXPANSION_TIMEOUT_MS = 15000

    # Short pause after a successful expansion to allow child rows to render.
    POST_EXPANSION_WAIT_MS = 250

    def __init__(self, client: PSIClient):

        self.client = client

        self._validate_settings()

    # ==================================================
    # 1. SETTINGS VALIDATION
    # ==================================================

    @staticmethod
    def _validate_settings():

        missing = [
            name
            for name in PSIScraper.REQUIRED_SETTINGS
            if not hasattr(settings, name)
        ]

        if missing:
            raise RuntimeError(
                "Missing scraper settings: "
                + ", ".join(missing)
            )

        if settings.MAX_TREE_ACTIONS < 1:
            raise ValueError(
                "MAX_TREE_ACTIONS must be greater than zero."
            )

    # ==================================================
    # 2. PAGE VALIDATION
    # ==================================================

    @staticmethod
    def _validate_page(page: Page):

        if page is None or page.is_closed():
            raise RuntimeError(
                "Cannot scrape repository: browser page is unavailable."
            )

    # ==================================================
    # 3. TREE ROWS
    # ==================================================

    def visible_tree_rows(self, page: Page):

        return page.locator(self.TREE_SELECTOR)

    async def read_tree_row(self, row) -> dict:
        """
        Read one row using a single browser-side evaluation.
        """

        info = await row.evaluate(
            """
            element => {

                const nameElement = element.querySelector(
                    ".file-name-column .inline-flex"
                );

                const icon = element.querySelector(
                    "i.far.fa-lg"
                );

                const classes = element.className || "";

                const depthMatch = classes.match(
                    /(?:^|\\\\s)depth-(\\\\d+)(?:\\\\s|$)/
                );

                const iconClasses = icon
                    ? icon.className
                    : "";

                const ariaExpanded = element.getAttribute(
                    "aria-expanded"
                );

                const name = nameElement
                    ? nameElement.innerText.trim()
                    : "";

                const rowText = element.innerText.trim();

                const isFolder = (
                    iconClasses.includes("fa-folder")
                    || ariaExpanded === "true"
                    || ariaExpanded === "false"
                );

                const isOpen = (
                    iconClasses.includes("fa-folder-open")
                    || ariaExpanded === "true"
                );

                return {

                    name: name,

                    text: rowText,

                    depth: depthMatch
                        ? Number(depthMatch[1])
                        : 0,

                    folder: isFolder,

                    folder_open: isOpen,

                    aria_expanded: ariaExpanded,

                    icon_classes: iconClasses,

                    href: element.getAttribute("href")
                };
            }
            """
        )

        href = info.get("href")

        info["href"] = (
            urljoin(settings.NASA_BASE_URL, href)
            if href
            else None
        )

        info["name"] = normalize_text(
            info.get("name") or "unnamed"
        )

        info["text"] = normalize_text(
            info.get("text", "")
        )

        return info

    # ==================================================
    # 4. FAST TREE SNAPSHOT
    # ==================================================

    async def snapshot_visible_tree(
        self,
        page: Page
    ) -> list[tuple]:
        """
        Read all visible tree rows in one browser-side operation.

        This avoids multiple Playwright calls for every property
        of every row.
        """

        self._validate_page(page)

        rows = self.visible_tree_rows(page)

        row_data = await rows.evaluate_all(
            """
            elements => {

                return elements.map(element => {

                    const nameElement = element.querySelector(
                        ".file-name-column .inline-flex"
                    );

                    const icon = element.querySelector(
                        "i.far.fa-lg"
                    );

                    const classes = element.className || "";

                    const depthMatch = classes.match(
                        /(?:^|\\\\s)depth-(\\\\d+)(?:\\\\s|$)/
                    );

                    const iconClasses = icon
                        ? icon.className
                        : "";

                    const ariaExpanded = element.getAttribute(
                        "aria-expanded"
                    );

                    const isFolder = (
                        iconClasses.includes("fa-folder")
                        || ariaExpanded === "true"
                        || ariaExpanded === "false"
                    );

                    const isOpen = (
                        iconClasses.includes("fa-folder-open")
                        || ariaExpanded === "true"
                    );

                    return {

                        name: nameElement
                            ? nameElement.innerText.trim()
                            : "",

                        text: element.innerText.trim(),

                        depth: depthMatch
                            ? Number(depthMatch[1])
                            : 0,

                        folder: isFolder,

                        folder_open: isOpen,

                        aria_expanded: ariaExpanded,

                        icon_classes: iconClasses,

                        href: element.getAttribute("href")
                    };
                });
            }
            """
        )

        snapshot = []

        for index, info in enumerate(row_data):

            href = info.get("href")

            info["href"] = (
                urljoin(settings.NASA_BASE_URL, href)
                if href
                else None
            )

            info["name"] = normalize_text(
                info.get("name") or "unnamed"
            )

            info["text"] = normalize_text(
                info.get("text", "")
            )

            row = rows.nth(index)

            snapshot.append((row, info))

        return snapshot

    # ==================================================
    # 5. BUILD FILE METADATA
    # ==================================================

    @staticmethod
    def attach_metadata(
        snapshot: list[tuple]
    ) -> list[tuple]:

        output = attach_paths(snapshot)

        for _, info in output:

            info["size_mb"] = parse_size_mb(
                info.get("text", "")
            )

            info["is_raw"] = is_raw_path(
                info.get("path", "")
            )

            info["is_image"] = is_image_file(
                info.get("name", "")
            )

            info["file_type"] = (
                "folder"
                if info.get("folder")
                else "file"
            )

        return output

    # ==================================================
    # 6. FIND FOLDER FROM EXISTING SNAPSHOT
    # ==================================================

    @staticmethod
    def find_folder_in_snapshot(
        structured: list[tuple],
        target_path: str
    ):

        for row, info in structured:

            if info["path"] == target_path:
                return row, info

        return None, None

    async def find_folder_by_path(
        self,
        page: Page,
        target_path: str
    ):

        snapshot = await self.snapshot_visible_tree(page)

        structured = self.attach_metadata(snapshot)

        return self.find_folder_in_snapshot(
            structured,
            target_path
        )

    # ==================================================
    # 7. READ CURRENT FOLDER STATE
    # ==================================================

    async def get_folder_state(
        self,
        row
    ) -> str:
        """
        Return:
            open
            closed
            unknown
        """

        try:

            state = await row.evaluate(
                """
                element => {

                    const icon = element.querySelector(
                        "i.far.fa-lg"
                    );

                    if (!icon) {
                        return "unknown";
                    }

                    const classes = icon.className || "";

                    if (classes.includes("fa-folder-open")) {
                        return "open";
                    }

                    if (classes.includes("fa-folder")) {
                        return "closed";
                    }

                    return "unknown";
                }
                """
            )

            return state

        except Exception:

            return "unknown"

    # ==================================================
    # 8. EXPAND FOLDER
    # ==================================================

    async def expand_folder(
        self,
        page: Page,
        folder_path: str,
        existing_snapshot: Optional[list[tuple]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Expand a collapsed folder using its icon only.

        Important:
        - Never click an already-open folder.
        - Never click the whole row.
        - Never click the folder name.
        - Never retry blindly after an uncertain click.
        - Avoid repeatedly reading the entire tree.
        """

        try:

            # Reuse the existing snapshot when available.
            if existing_snapshot is not None:

                structured = self.attach_metadata(
                    existing_snapshot
                )

                row, info = self.find_folder_in_snapshot(
                    structured,
                    folder_path
                )

            else:

                row, info = await self.find_folder_by_path(
                    page,
                    folder_path
                )

            if row is None:

                return (
                    False,
                    f"Folder is no longer visible: {folder_path}"
                )

            if not info.get("folder"):

                return (
                    False,
                    f"Target is not a folder: {folder_path}"
                )

            # Check actual state immediately before clicking.

            state = await self.get_folder_state(row)

            if state == "open":

                logger.debug(
                    "Folder already open. Skipping click: %s",
                    folder_path
                )

                return True, None

            if state != "closed":

                return (
                    False,
                    f"Unknown folder state: {folder_path}"
                )

            # Locate the closed folder icon only.

            icon = row.locator(
                self.FOLDER_ICON_SELECTOR
            ).first

            if not await icon.count():

                return (
                    False,
                    f"Closed folder icon not found: {folder_path}"
                )

            if not await icon.is_visible():

                return (
                    False,
                    f"Folder icon is not visible: {folder_path}"
                )

            await icon.scroll_into_view_if_needed()

            # Recheck state immediately before clicking.

            current_state = await self.get_folder_state(row)

            if current_state == "open":

                return True, None

            if current_state != "closed":

                return (
                    False,
                    f"Folder state changed unexpectedly: {folder_path}"
                )

            logger.info(
                "Expanding folder: %s",
                folder_path
            )

            # Click the icon ONLY.

            await icon.click(
                timeout=settings.ELEMENT_TIMEOUT_MS
            )

            # Wait directly for the open icon.
            # Do not take another full tree snapshot here.

            open_icon = row.locator(
                self.OPEN_FOLDER_ICON_SELECTOR
            ).first

            await open_icon.wait_for(
                state="visible",
                timeout=self.FOLDER_EXPANSION_TIMEOUT_MS
            )

            # Allow a short time for child rows to render.

            await page.wait_for_timeout(
                self.POST_EXPANSION_WAIT_MS
            )

            logger.info(
                "Folder expanded successfully: %s",
                folder_path
            )

            return True, None

        except Exception as exc:

            logger.exception(
                "Folder expansion failed: %s",
                folder_path
            )

            return False, str(exc)

    # ==================================================
    # 9. CRAWL COMPLETE TREE
    # ==================================================

    async def crawl_tree(
        self,
        page: Page
    ) -> tuple[list[dict], list[dict]]:
        """
        Explore every folder dynamically.

        Returns:
            nodes:
                All discovered files and folders.

            errors:
                Any folders that could not be explored.
        """

        self._validate_page(page)

        nodes = {}

        expansion_errors = []

        attempted_folders = set()

        actions = 0

        logger.info(
            "Starting repository tree exploration."
        )

        while actions < settings.MAX_TREE_ACTIONS:

            # One bulk snapshot per exploration iteration.

            snapshot = await self.snapshot_visible_tree(page)

            if not snapshot:

                error = {
                    "path": "<tree>",
                    "error": "No visible rows found in repository tree."
                }

                return list(nodes.values()), (
                    expansion_errors + [error]
                )

            structured = self.attach_metadata(snapshot)

            candidate = None

            # Collect all currently visible nodes.

            for row, info in structured:

                path = info["path"]

                nodes[path] = info

                if not info["folder"]:
                    continue

                if path in attempted_folders:
                    continue

                state = await self.get_folder_state(row)

                # Already expanded: never click again.

                if state == "open":

                    attempted_folders.add(path)

                    continue

                if state == "closed":

                    candidate = path

                    break

                # Unknown state: do not click blindly.

                attempted_folders.add(path)

                expansion_errors.append(
                    {
                        "path": path,
                        "error": "Folder state could not be determined."
                    }
                )

            # No remaining collapsed folders.

            if candidate is None:
                break

            actions += 1

            attempted_folders.add(candidate)

            # Reuse the snapshot already collected.
            # This avoids another full scan just to locate the folder.

            success, error = await self.expand_folder(
                page,
                candidate,
                existing_snapshot=snapshot
            )

            if not success:

                expansion_errors.append(
                    {
                        "path": candidate,
                        "error": error or "Unknown expansion error."
                    }
                )

                logger.warning(
                    "Folder could not be expanded: %s | %s",
                    candidate,
                    error
                )

        else:

            expansion_errors.append(
                {
                    "path": "<tree>",
                    "error": (
                        "Maximum tree actions limit reached. "
                        "Repository scan may be incomplete."
                    )
                }
            )

        # Final snapshot to collect the latest visible nodes.

        final_snapshot = await self.snapshot_visible_tree(page)

        final_structured = self.attach_metadata(final_snapshot)

        for _, info in final_structured:

            nodes[info["path"]] = info

        logger.info(
            "Tree exploration finished | nodes=%s | errors=%s",
            len(nodes),
            len(expansion_errors)
        )

        return (
            list(nodes.values()),
            expansion_errors
        )

    # ==================================================
    # 10. SCRAPE ONE INVESTIGATION
    # ==================================================

    async def scrape_investigation(
        self,
        investigation: dict
    ) -> dict:

        investigation_id = investigation.get(
            "investigation_id"
        )

        if not investigation_id:

            raise ValueError(
                "Investigation is missing investigation_id."
            )

        logger.info(
            "Scraping investigation: %s",
            investigation_id
        )

        result = {
            "investigation_id": investigation_id,

            "name": investigation.get(
                "name",
                investigation_id
            ),

            "url": investigation.get("url"),

            "status": "failed",

            "nodes": [],

            "files": [],

            "folders": [],

            "errors": [],

            "started_at": None,

            "finished_at": None,
        }

        result["started_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        try:

            page = await self.client.open_investigation(
                investigation
            )

            result["url"] = page.url

            nodes, errors = await self.crawl_tree(page)

            result["nodes"] = nodes

            result["files"] = [
                node
                for node in nodes
                if not node["folder"]
            ]

            result["folders"] = [
                node
                for node in nodes
                if node["folder"]
            ]

            result["errors"] = errors

            if not nodes:

                result["status"] = "failed"

                result["errors"].append(
                    {
                        "path": "<tree>",
                        "error": (
                            "No repository nodes were discovered."
                        )
                    }
                )

            elif errors:

                result["status"] = "partial"

            else:

                result["status"] = "completed"

            logger.info(
                (
                    "%s | status=%s | files=%s | "
                    "folders=%s | errors=%s"
                ),

                investigation_id,

                result["status"],

                len(result["files"]),

                len(result["folders"]),

                len(result["errors"])
            )

        except Exception as exc:

            logger.exception(
                "Investigation scraping failed: %s",
                investigation_id
            )

            result["status"] = "failed"

            result["errors"].append(
                {
                    "path": "<investigation>",
                    "error": str(exc)
                }
            )

        finally:

            result["finished_at"] = datetime.now(
                timezone.utc
            ).isoformat()

        return result