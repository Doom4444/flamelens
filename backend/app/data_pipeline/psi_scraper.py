import json
import logging
import re
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


# =========================================================
# CONFIGURATION
# =========================================================

SEARCH_URL = (
    "https://psi.nasa.gov/physci/repo/search"
    "?q=combustion&data_source=psi&data_type=investigation"
)

OUTPUT_DIR = Path("data/metadata")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MARKDOWN_FILE = OUTPUT_DIR / "psi_descriptions_numbered.md"
JSONL_FILE = OUTPUT_DIR / "psi_descriptions.jsonl"
FAILED_FILE = OUTPUT_DIR / "psi_failed_ids.json"

PAGE_TIMEOUT = 60000
CONTENT_TIMEOUT = 45000
MAX_RETRIES = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("psi_scraper")


# =========================================================
# HELPERS
# =========================================================

def clean_url(url: str) -> str:
    """Remove query parameters and fragments from investigation URLs."""
    parts = urlsplit(url)
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path.rstrip("/"), "", "")
    )


def clean_text(value: str) -> str:
    """Normalize whitespace."""
    return re.sub(r"\s+", " ", value or "").strip()


def escape_markdown(value: str) -> str:
    """Escape Markdown table delimiters."""
    return clean_text(value).replace("|", r"\|")


def get_investigation_id(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


# =========================================================
# 1. COLLECT INVESTIGATION URLS
# =========================================================

def collect_investigation_urls(page):

    logger.info("Opening NASA PSI search page...")

    try:
        page.goto(
            SEARCH_URL,
            wait_until="commit",
            timeout=PAGE_TIMEOUT,
        )
    except PlaywrightTimeoutError:
        logger.warning("Navigation timed out; checking whether the page rendered.")

    page.wait_for_selector(
        'a[href*="/data/investigations/"]',
        timeout=CONTENT_TIMEOUT,
    )

    urls = []
    seen = set()

    page_number = 1

    while True:

        logger.info("Collecting investigation links from page %s", page_number)

        current_links = page.locator(
            'a[href*="/data/investigations/"]'
        ).evaluate_all(
            """elements => elements.map(element => element.href)"""
        )

        for url in current_links:

            url = clean_url(url)

            if url not in seen:
                seen.add(url)
                urls.append(url)

        logger.info("Collected %s unique investigations", len(urls))

        next_button = page.locator(
            "button.mat-paginator-navigation-next"
        ).first

        if next_button.count() == 0:
            break

        if next_button.is_disabled():
            break

        # Capture current page links to detect pagination changes.
        previous_signature = "|".join(current_links)

        next_button.click()

        try:
            page.wait_for_function(
                """
                previous => {
                    const links = Array.from(
                        document.querySelectorAll(
                            'a[href*="/data/investigations/"]'
                        )
                    ).map(a => a.href);

                    return links.length > 0 &&
                           links.join("|") !== previous;
                }
                """,
                arg=previous_signature,
                timeout=15000,
            )

        except PlaywrightTimeoutError:
            logger.warning("Pagination did not produce new results.")
            break

        page_number += 1

    logger.info("Total investigations discovered: %s", len(urls))

    return urls


# =========================================================
# 2. EXPAND ANGULAR MATERIAL PANELS
# =========================================================

def expand_panels(page):

    for _ in range(10):

        collapsed = page.locator(
            'mat-expansion-panel-header[aria-expanded="false"]'
        )

        if collapsed.count() == 0:
            break

        collapsed.first.click()

        page.wait_for_timeout(300)


# =========================================================
# 3. EXTRACT DESCRIPTION PANEL
# =========================================================

def extract_description(page):

    page.wait_for_function(
        """
        () => {
            const panel = document.querySelector("description-panel");

            return panel &&
                   panel.innerText &&
                   panel.innerText.trim().length > 20;
        }
        """,
        timeout=CONTENT_TIMEOUT,
    )

    return page.locator("description-panel").evaluate(
        """
        panel => {

            const result = {
                project: [],
                sections: [],
            };

            // Project metadata table
            const table = panel.querySelector("table");

            if (table) {

                table.querySelectorAll("tr").forEach(row => {

                    const cells = row.querySelectorAll("td, th");

                    if (cells.length >= 2) {

                        result.project.push({
                            field: cells[0].innerText.trim(),
                            value: cells[1].innerText.trim()
                        });

                    }

                });

            }

            // Description sections
            const sections = panel.querySelectorAll(
                "div.ng-star-inserted"
            );

            sections.forEach(section => {

                const heading = section.querySelector("h3");

                if (!heading) return;

                const title = heading.innerText.trim();

                if (title === "Project") return;

                const sectionData = {
                    title: title,
                    content: "",
                    contacts: []
                };

                if (title.includes("Contact")) {

                    const contacts = section.querySelectorAll(
                        ".contact-container"
                    );

                    contacts.forEach(contact => {

                        const nameElement = contact.querySelector("a");

                        const tooltip = contact.querySelector(".tooltip");

                        sectionData.contacts.push({
                            name: nameElement
                                ? nameElement.innerText.trim()
                                : "",
                            details: tooltip
                                ? tooltip.innerText.trim()
                                : ""
                        });

                    });

                } else {

                    const content = section.querySelector(".indent");

                    if (content) {
                        sectionData.content = content.innerText.trim();
                    }

                }

                result.sections.push(sectionData);

            });

            return result;
        }
        """
    )


# =========================================================
# 4. CONVERT STRUCTURED DATA TO MARKDOWN
# =========================================================

def to_markdown(data, index, investigation_id, url):

    md = f"# {index}. {investigation_id}\n\n"

    md += f"**Source:** {url}\n\n"

    # Project metadata
    if data["project"]:

        md += "## Project\n\n"
        md += "| Field | Value |\n"
        md += "| :--- | :--- |\n"

        for item in data["project"]:

            field = escape_markdown(item["field"])
            value = escape_markdown(item["value"])

            md += f"| **{field}** | {value} |\n"

        md += "\n"

    # Description sections
    for section in data["sections"]:

        title = section["title"]

        md += f"## {title}\n\n"

        if section["contacts"]:

            for contact in section["contacts"]:

                name = clean_text(contact["name"])
                details = clean_text(contact["details"])

                md += f"- **{name}**"

                if details:
                    md += f" ({details})"

                md += "\n"

            md += "\n"

        elif section["content"]:

            md += section["content"].strip() + "\n\n"

    return md.strip()


# =========================================================
# 5. SAVE RESULTS INCREMENTALLY
# =========================================================

def save_results(results, failed):

    markdown = "\n\n---\n\n".join(results)

    MARKDOWN_FILE.write_text(
        markdown + "\n",
        encoding="utf-8",
    )

    FAILED_FILE.write_text(
        json.dumps(failed, indent=4),
        encoding="utf-8",
    )


# =========================================================
# 6. PROCESS INVESTIGATION
# =========================================================

def process_investigation(page, url, index):

    investigation_id = get_investigation_id(url)

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            logger.info(
                "[%s] Processing %s | Attempt %s",
                index,
                investigation_id,
                attempt,
            )

            try:
                page.goto(
                    url,
                    wait_until="commit",
                    timeout=PAGE_TIMEOUT,
                )
            except PlaywrightTimeoutError:
                logger.warning(
                    "%s navigation timed out; checking rendered content.",
                    investigation_id,
                )

            page.wait_for_selector(
                "mat-expansion-panel-header",
                timeout=CONTENT_TIMEOUT,
            )

            expand_panels(page)

            data = extract_description(page)

            if not data["project"] and not data["sections"]:
                raise ValueError("Description panel contains no extractable data")

            markdown = to_markdown(
                data,
                index,
                investigation_id,
                url,
            )

            record = {
                "investigation_id": investigation_id,
                "source_url": url,
                "data": data,
            }

            with JSONL_FILE.open("a", encoding="utf-8") as file:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")

            logger.info("Successfully extracted %s", investigation_id)

            return markdown

        except Exception as error:

            logger.warning(
                "%s failed on attempt %s: %s",
                investigation_id,
                attempt,
                error,
            )

            if attempt < MAX_RETRIES:
                time.sleep(2)

    return None


# =========================================================
# 7. MAIN PIPELINE
# =========================================================

def run():

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            channel="chrome",
            headless=False,
        )

        context = browser.new_context(
            viewport={"width": 1440, "height": 1000},
        )

        page = context.new_page()

        page.set_default_timeout(CONTENT_TIMEOUT)

        urls = collect_investigation_urls(page)

        results = []
        failed = []

        # Keep numbering sequential among successful records.
        successful_count = 0

        for position, url in enumerate(urls, start=1):

            investigation_id = get_investigation_id(url)

            logger.info(
                "Progress: %s/%s | %s",
                position,
                len(urls),
                investigation_id,
            )

            markdown = process_investigation(
                page,
                url,
                successful_count + 1,
            )

            if markdown:

                results.append(markdown)
                successful_count += 1

            else:

                failed.append({
                    "investigation_id": investigation_id,
                    "url": url,
                })

            # Save after every investigation.
            save_results(results, failed)

        browser.close()

        logger.info("=" * 50)
        logger.info("SCRAPING COMPLETED")
        logger.info("Discovered: %s", len(urls))
        logger.info("Successful: %s", successful_count)
        logger.info("Failed: %s", len(failed))
        logger.info("Markdown: %s", MARKDOWN_FILE)
        logger.info("=" * 50)


if __name__ == "__main__":
    run()