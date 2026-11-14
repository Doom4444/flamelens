import asyncio
import logging
import re

from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin, urlparse

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

from . import settings


logger = logging.getLogger(__name__)


class PSIClient:
    """
    NASA PSI browser and API client.

    Responsibilities:
    - Browser lifecycle management.
    - NASA PSI API communication.
    - Investigation discovery.
    - Automatic pagination.
    - Investigation page navigation.
    - Repository activation and readiness checks.
    - Error diagnostics.
    """

    API_SEARCH_URL = (
        f"{settings.NASA_BASE_URL}/geode-py/ws/repo/search"
    )

    REPOSITORY_SELECTOR = "#btn-repo-files"

    TREE_SELECTOR = (
        "app-geode-tree a.panel-block.selectable:visible"
    )

    INVESTIGATION_ID_PATTERN = re.compile(
        r"PSI-\d+",
        re.IGNORECASE,
    )

    REQUIRED_SETTINGS = [
        "BROWSER_NAME",
        "HEADLESS",
        "MAX_NETWORK_RETRIES",
        "NAV_TIMEOUT_MS",
        "PAGE_READY_TIMEOUT_MS",
        "ELEMENT_TIMEOUT_MS",
        "RETRY_BASE_SECONDS",
        "LOG_ROOT",
        "TIMESTAMP_FORMAT",
        "NASA_BASE_URL",
        "NASA_SEARCH_URL",
        "MAX_SEARCH_PAGES",
        "initialize_directories",
    ]

    def __init__(self):

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        self._validate_settings()

    # ==================================================
    # 1. SETTINGS VALIDATION
    # ==================================================

    @staticmethod
    def _validate_settings():

        missing = [
            name
            for name in PSIClient.REQUIRED_SETTINGS
            if not hasattr(settings, name)
        ]

        if missing:
            raise RuntimeError(
                "Missing settings: "
                + ", ".join(missing)
            )

        if settings.BROWSER_NAME not in (
            "chromium",
            "firefox",
            "webkit",
        ):
            raise ValueError(
                f"Unsupported browser: {settings.BROWSER_NAME}"
            )

        if settings.MAX_NETWORK_RETRIES < 1:
            raise ValueError(
                "MAX_NETWORK_RETRIES must be at least 1."
            )

        if settings.MAX_SEARCH_PAGES < 1:
            raise ValueError(
                "MAX_SEARCH_PAGES must be at least 1."
            )

    # ==================================================
    # 2. BROWSER MANAGEMENT
    # ==================================================

    async def start(self):

        if self.browser:
            return

        logger.info("Starting Playwright browser...")

        try:

            self.playwright = await async_playwright().start()

            browser_type = getattr(
                self.playwright,
                settings.BROWSER_NAME,
            )

            self.browser = await browser_type.launch(
                headless=settings.HEADLESS,
            )

            self.context = await self.browser.new_context(
                accept_downloads=True,
                ignore_https_errors=False,
            )

            self.page = await self.context.new_page()

            self.page.set_default_timeout(
                settings.ELEMENT_TIMEOUT_MS,
            )

            logger.info("Browser started successfully.")

        except Exception:

            logger.exception("Browser startup failed.")

            await self.close()

            raise

    async def close(self):

        logger.info("Closing PSI browser...")

        if self.context:

            try:
                await self.context.close()

            except Exception:
                logger.exception("Context closing failed.")

            finally:
                self.context = None

        if self.browser:

            try:
                await self.browser.close()

            except Exception:
                logger.exception("Browser closing failed.")

            finally:
                self.browser = None

        if self.playwright:

            try:
                await self.playwright.stop()

            except Exception:
                logger.exception("Playwright stopping failed.")

            finally:
                self.playwright = None

        self.page = None

        logger.info("Browser closed.")

    async def __aenter__(self):

        await self.start()

        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        await self.close()

    def _require_page(self) -> Page:

        if self.page is None:
            raise RuntimeError(
                "PSI browser is not started. "
                "Call start() first."
            )

        return self.page

    # ==================================================
    # 3. NAVIGATION
    # ==================================================

    async def navigate(
        self,
        url: str,
        retries: Optional[int] = None,
        timeout_ms: Optional[int] = None,
    ):

        page = self._require_page()

        retries = (
            settings.MAX_NETWORK_RETRIES
            if retries is None
            else retries
        )

        timeout_ms = (
            settings.NAV_TIMEOUT_MS
            if timeout_ms is None
            else timeout_ms
        )

        last_error = None

        for attempt in range(1, retries + 1):

            try:

                logger.info(
                    "Navigating to %s (%s/%s)",
                    url,
                    attempt,
                    retries,
                )

                response = await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=timeout_ms,
                )

                if response and response.status >= 400:
                    raise RuntimeError(
                        f"HTTP {response.status}: {url}"
                    )

                logger.info(
                    "Navigation completed: %s",
                    page.url,
                )

                return response

            except Exception as exc:

                last_error = exc

                logger.warning(
                    "Navigation attempt %s failed: %s",
                    attempt,
                    exc,
                )

                if attempt < retries:

                    delay = (
                        settings.RETRY_BASE_SECONDS * attempt
                    )

                    await asyncio.sleep(delay)

        await self._save_diagnostics(
            "navigation_failed"
        )

        raise RuntimeError(
            f"Navigation failed after {retries} attempts. "
            f"Last error: {last_error}"
        ) from last_error

    # ==================================================
    # 4. DIAGNOSTICS
    # ==================================================

    async def _save_diagnostics(self, prefix: str):

        page = self.page

        if not page:
            return

        try:

            settings.initialize_directories()

            timestamp = datetime.now(
                timezone.utc
            ).strftime(
                settings.TIMESTAMP_FORMAT
            )

            screenshot_path = (
                settings.LOG_ROOT
                / f"{prefix}_{timestamp}.png"
            )

            await page.screenshot(
                path=str(screenshot_path),
                full_page=True,
            )

            logger.error(
                "Screenshot saved: %s",
                screenshot_path,
            )

            html_path = (
                settings.LOG_ROOT
                / f"{prefix}_{timestamp}.html"
            )

            html_content = await page.content()

            html_path.write_text(
                html_content,
                encoding="utf-8",
            )

            logger.error(
                "Page HTML saved: %s",
                html_path,
            )

        except Exception:
            logger.exception(
                "Could not save diagnostics."
            )

    # ==================================================
    # 5. API REQUEST
    # ==================================================

    async def _api_search(
        self,
        term: str,
        offset: int,
        page_size: int,
    ) -> dict:

        """
        Send a search request to NASA PSI API.
        """

        page = self._require_page()

        params = {
            "term": term,
            "source": "psi",
            "type": "investigation",
            "sort": "Public Release Date",
            "order": "desc",
            "from": offset,
            "size": page_size,
        }

        last_error = None

        for attempt in range(
            1,
            settings.MAX_NETWORK_RETRIES + 1,
        ):

            try:

                logger.info(
                    "NASA API request | offset=%s | size=%s",
                    offset,
                    page_size,
                )

                response = await page.request.get(
                    self.API_SEARCH_URL,
                    params=params,
                    timeout=settings.NAV_TIMEOUT_MS,
                )

                if not response.ok:
                    raise RuntimeError(
                        f"NASA API returned HTTP "
                        f"{response.status}"
                    )

                data = await response.json()

                if not isinstance(data, dict):
                    raise ValueError(
                        "NASA API returned an invalid JSON object."
                    )

                if "hits" not in data:
                    raise ValueError(
                        "NASA API response does not contain 'hits'."
                    )

                return data

            except Exception as exc:

                last_error = exc

                logger.warning(
                    "API request attempt %s failed: %s",
                    attempt,
                    exc,
                )

                if attempt < settings.MAX_NETWORK_RETRIES:

                    delay = (
                        settings.RETRY_BASE_SECONDS * attempt
                    )

                    await asyncio.sleep(delay)

        raise RuntimeError(
            f"NASA API request failed: {last_error}"
        ) from last_error

    # ==================================================
    # 6. INVESTIGATION DISCOVERY
    # ==================================================

    async def discover_investigations(
        self,
        search_term: str = "combustion",
        page_size: int = 25,
    ) -> list[dict]:

        """
        Discover investigations through NASA PSI API.

        Automatically retrieves all result pages.
        """

        self._require_page()

        if page_size < 1:
            raise ValueError(
                "page_size must be greater than zero."
            )

        logger.info(
            "Starting NASA investigation discovery. "
            "Search term: %s",
            search_term,
        )

        investigations = {}

        offset = 0
        total_results = None

        while True:

            if (
                offset // page_size
                >= settings.MAX_SEARCH_PAGES
            ):
                raise RuntimeError(
                    "Maximum search pages limit reached. "
                    "Discovery may be incomplete."
                )

            data = await self._api_search(
                term=search_term,
                offset=offset,
                page_size=page_size,
            )

            hits_data = data.get("hits", {})

            raw_hits = hits_data.get("hits", [])

            total_results = hits_data.get(
                "total",
                0,
            )

            # Some search engines return total as a dictionary.
            if isinstance(total_results, dict):
                total_results = total_results.get(
                    "value",
                    0,
                )

            total_results = int(total_results)

            logger.info(
                "API page received | offset=%s | "
                "returned=%s | total=%s",
                offset,
                len(raw_hits),
                total_results,
            )

            if not raw_hits:
                break

            for hit in raw_hits:

                source = hit.get("_source", {})

                accession = source.get("Accession")

                if not accession:
                    continue

                investigation_id = str(
                    accession
                ).strip().upper()

                if investigation_id in investigations:
                    continue

                title = source.get(
                    "Title",
                    investigation_id,
                )

                investigations[investigation_id] = {
                    "investigation_id": investigation_id,
                    "name": title,
                    "url": None,
                    "research_area": source.get(
                        "Research Area"
                    ),
                    "project_type": source.get(
                        "Project Type"
                    ),
                    "api_id": hit.get("_id"),
                    "source": source,
                }

            offset += len(raw_hits)

            if offset >= total_results:
                break

            if len(raw_hits) < page_size:
                break

        results = list(
            investigations.values()
        )

        logger.info(
            "Investigation discovery completed. "
            "Retrieved %s unique investigations.",
            len(results),
        )

        return results

    # ==================================================
    # 7. RESOLVE INVESTIGATION URL
    # ==================================================

    async def resolve_investigation_url(
        self,
        investigation_id: str,
    ) -> str:

        """
        Build and verify the NASA investigation landing-page URL.

        The URL structure was confirmed from NASA rendered search results.
        """

        page = self._require_page()

        normalized_id = str(
            investigation_id
        ).strip().upper()

        # Validate investigation ID.
        if not self.INVESTIGATION_ID_PATTERN.fullmatch(
            normalized_id
        ):
            raise ValueError(
                f"Invalid investigation ID: {investigation_id!r}"
            )

        # Build the confirmed NASA URL.
        candidate_url = urljoin(
            settings.NASA_BASE_URL,
            f"/physci/repo/data/investigations/{normalized_id}",
        )

        logger.info(
            "Resolving investigation URL | id=%s | url=%s",
            normalized_id,
            candidate_url,
        )

        try:

            response = await self.navigate(candidate_url)

            # Verify HTTP response.
            if response is None:
                raise RuntimeError(
                    "NASA returned no HTTP response."
                )

            if not response.ok:
                raise RuntimeError(
                    f"NASA returned HTTP {response.status}."
                )

            # Wait for page body.
            await page.locator("body").wait_for(
                state="visible",
                timeout=settings.PAGE_READY_TIMEOUT_MS,
            )

            # Verify final URL.
            parsed_url = urlparse(page.url)

            expected_path = (
                f"/physci/repo/data/investigations/{normalized_id}"
            )

            actual_path = parsed_url.path.rstrip("/")

            if actual_path.lower() != expected_path.lower():
                raise RuntimeError(
                    "NASA redirected to an unexpected URL. "
                    f"Expected: {expected_path} | "
                    f"Actual: {actual_path}"
                )

            # Verify that the page is not empty.
            body_text = (
                await page.locator("body").inner_text()
            ).strip()

            if not body_text:
                raise RuntimeError(
                    "Investigation page loaded with empty content."
                )

            # Verify page title.
            title = (await page.title()).strip()

            if not title:
                raise RuntimeError(
                    "Investigation page has no title."
                )

        except Exception as exc:

            await self._save_diagnostics(
                f"{normalized_id}_url_verification_failed"
            )

            raise RuntimeError(
                f"Could not verify investigation {normalized_id}. "
                f"URL: {page.url}. Reason: {exc}"
            ) from exc

        logger.info(
            "Investigation URL resolved successfully | "
            "id=%s | url=%s",
            normalized_id,
            page.url,
        )

        return page.url

    # ==================================================
    # 8. OPEN INVESTIGATION AND REPOSITORY
    # ==================================================

    async def open_investigation(
        self,
        investigation: dict,
    ) -> Page:

        page = self._require_page()

        investigation_id = str(
            investigation.get(
                "investigation_id",
                "UNKNOWN",
            )
        ).strip().upper()

        url = investigation.get("url")

        if not url:
            url = await self.resolve_investigation_url(
                investigation_id
            )

            investigation["url"] = url

        logger.info(
            "Opening investigation: %s",
            investigation_id,
        )

        await self.navigate(url)

        try:

            # ------------------------------------------
            # Verify the requested investigation URL.
            # ------------------------------------------

            parsed_url = urlparse(page.url)

            expected_path = (
                f"/physci/repo/data/investigations/{investigation_id}"
            )

            if (
                parsed_url.path.rstrip("/").lower()
                != expected_path.lower()
            ):
                raise RuntimeError(
                    f"Unexpected investigation URL: {page.url}"
                )

            # ------------------------------------------
            # Wait for Repository button.
            # ------------------------------------------

            repository_button = page.locator(
                self.REPOSITORY_SELECTOR
            )

            await repository_button.wait_for(
                state="visible",
                timeout=settings.PAGE_READY_TIMEOUT_MS,
            )

            # ------------------------------------------
            # Check whether tree is already visible.
            # ------------------------------------------

            tree = page.locator("app-geode-tree")

            tree_is_visible = False

            if await tree.count() > 0:
                tree_is_visible = await tree.first.is_visible()

            # ------------------------------------------
            # Open Repository if necessary.
            # ------------------------------------------

            if not tree_is_visible:

                logger.info(
                    "Opening repository section: %s",
                    investigation_id,
                )

                await repository_button.click(
                    timeout=settings.ELEMENT_TIMEOUT_MS
                )

            # ------------------------------------------
            # Wait for actual tree component.
            # ------------------------------------------

            await tree.first.wait_for(
                state="visible",
                timeout=settings.PAGE_READY_TIMEOUT_MS,
            )

            # ------------------------------------------
            # Wait for actual tree rows.
            # ------------------------------------------

            tree_rows = page.locator(
                self.TREE_SELECTOR
            )

            try:

                await tree_rows.first.wait_for(
                    state="visible",
                    timeout=settings.PAGE_READY_TIMEOUT_MS,
                )

            except Exception:

                await self._save_diagnostics(
                    f"{investigation_id}_empty_repository_tree"
                )

                body_preview = (
                    await page.locator("body").inner_text()
                )[:2000]

                raise RuntimeError(
                    "Repository component appeared, "
                    "but no visible tree rows were found.\n"
                    f"Investigation: {investigation_id}\n"
                    f"URL: {page.url}\n"
                    f"Page preview: {body_preview}"
                )

            row_count = await tree_rows.count()

            logger.info(
                "Repository tree loaded: %s | rows=%s",
                investigation_id,
                row_count,
            )

        except Exception as exc:

            await self._save_diagnostics(
                f"{investigation_id}_repository_failed"
            )

            raise RuntimeError(
                f"Could not open repository for {investigation_id}. "
                f"URL: {page.url}. Reason: {exc}"
            ) from exc

        logger.info(
            "Repository is ready: %s",
            investigation_id,
        )

        return page

    # ==================================================
    # 9. PAGE INFORMATION
    # ==================================================

    async def get_page_info(self) -> dict:

        page = self._require_page()

        return {
            "url": page.url,
            "title": await page.title(),
        }