import asyncio
import logging

from backend.app.data_pipeline.psi_client import PSIClient
from backend.app.data_pipeline.scraper import PSIScraper


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# Test only this investigation
TEST_INVESTIGATION_IDS = ["PSI-159"]


async def main():

    results = []

    async with PSIClient() as client:

        scraper = PSIScraper(client)

        # ==============================================
        # STEP 1: DISCOVER INVESTIGATIONS
        # ==============================================

        print("\n" + "=" * 70)
        print("DISCOVERING NASA PSI INVESTIGATIONS")
        print("=" * 70)

        all_investigations = await client.discover_investigations(
            search_term="combustion"
        )

        print(
            f"\nTotal investigations discovered: "
            f"{len(all_investigations)}"
        )

        # ==============================================
        # STEP 2: SELECT INVESTIGATIONS FOR TESTING
        # ==============================================

        investigations = [
            investigation
            for investigation in all_investigations
            if investigation["investigation_id"]
            in TEST_INVESTIGATION_IDS
        ]

        found_ids = {
            investigation["investigation_id"]
            for investigation in investigations
        }

        missing_ids = (
            set(TEST_INVESTIGATION_IDS) - found_ids
        )

        if missing_ids:

            print(
                "\nWARNING: These investigations were not found:"
            )

            for investigation_id in sorted(missing_ids):
                print(f"- {investigation_id}")

        if not investigations:

            print("\nNo matching investigations to test.")
            return

        print(
            f"\nInvestigations selected for testing: "
            f"{len(investigations)}"
        )

        # ==============================================
        # STEP 3: SCRAPE SELECTED INVESTIGATIONS
        # ==============================================

        for index, investigation in enumerate(
            investigations,
            start=1
        ):

            investigation_id = investigation["investigation_id"]

            print("\n" + "-" * 70)

            print(
                f"[{index}/{len(investigations)}] "
                f"Scraping {investigation_id}"
            )

            print("-" * 70)

            try:

                result = await scraper.scrape_investigation(
                    investigation
                )

                results.append(result)

                print(f"Status: {result['status']}")
                print(f"Files: {len(result['files'])}")
                print(f"Folders: {len(result['folders'])}")
                print(f"Errors: {len(result['errors'])}")

            except Exception as error:

                logging.exception(
                    "Unexpected error while scraping %s",
                    investigation_id
                )

                results.append({
                    "investigation_id": investigation_id,
                    "status": "failed",
                    "files": [],
                    "folders": [],
                    "nodes": [],
                    "errors": [str(error)]
                })

        # ==============================================
        # STEP 4: FINAL REPORT
        # ==============================================

        completed = [
            result
            for result in results
            if result["status"] == "completed"
        ]

        partial = [
            result
            for result in results
            if result["status"] == "partial"
        ]

        failed = [
            result
            for result in results
            if result["status"] == "failed"
        ]

        total_files = sum(
            len(result["files"])
            for result in results
        )

        total_folders = sum(
            len(result["folders"])
            for result in results
        )

        total_errors = sum(
            len(result["errors"])
            for result in results
        )

        print("\n\n" + "=" * 70)
        print("FINAL SCRAPER TEST REPORT")
        print("=" * 70)

        print(
            f"Total investigations discovered: "
            f"{len(all_investigations)}"
        )

        print(
            f"Investigations selected: "
            f"{len(investigations)}"
        )

        print(
            f"Investigations tested: "
            f"{len(results)}"
        )

        print(f"Completed: {len(completed)}")
        print(f"Partial: {len(partial)}")
        print(f"Failed: {len(failed)}")

        print(f"Total files discovered: {total_files}")
        print(f"Total folders discovered: {total_folders}")
        print(f"Total errors: {total_errors}")

        if partial or failed:

            print("\nINVESTIGATIONS NEEDING REVIEW:")

            for result in partial + failed:

                print(
                    f"\n{result['investigation_id']} "
                    f"| Status: {result['status']}"
                )

                for error in result["errors"]:
                    print(f"  - {error}")

        print("\n" + "=" * 70)

        if len(completed) == len(investigations):

            print("ALL SELECTED INVESTIGATIONS SCRAPED SUCCESSFULLY!")

        else:

            print("SOME INVESTIGATIONS NEED REVIEW.")

        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())