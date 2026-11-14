"""Integration tests for the JSON-backed metadata API.

These tests read the real Stage 1 audit inventories (read-only) and assert that
the API preserves NASA PSI metadata, separates remote inventory size from local
storage, and never fabricates measurements.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

GLOBAL_REMOTE_BYTES = 492_609_577_604
GLOBAL_FILES = 1_520
GLOBAL_INVESTIGATIONS = 26
GLOBAL_DATASET_GROUPS = 383


def test_overview_totals_match_inventories():
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()

    totals = data["totals"]
    assert totals["investigations"] == GLOBAL_INVESTIGATIONS
    assert totals["files"] == GLOBAL_FILES
    assert totals["dataset_groups"] == GLOBAL_DATASET_GROUPS
    assert totals["remote_inventory_size_bytes"] == GLOBAL_REMOTE_BYTES
    assert totals["local_downloaded_size_bytes"] == 0
    assert totals["downloaded_files"] == 0
    assert totals["investigations_with_file_inventory"] == 7
    assert totals["investigations_without_file_inventory"] == 19

    # File-type distribution must add up to the file count.
    assert sum(row["count"] for row in data["file_type_distribution"]) == GLOBAL_FILES
    assert "It is not local storage." in data["data_notes"][0]


def test_investigations_pagination_and_search():
    first = client.get("/api/v1/investigations?page=1&page_size=10").json()
    second = client.get("/api/v1/investigations?page=2&page_size=10").json()

    assert first["pagination"]["total_items"] == GLOBAL_INVESTIGATIONS
    assert first["pagination"]["total_pages"] == 3
    assert first["pagination"]["has_next"] is True
    assert second["pagination"]["has_previous"] is True
    ids_first = {item["investigation_id"] for item in first["items"]}
    ids_second = {item["investigation_id"] for item in second["items"]}
    assert ids_first.isdisjoint(ids_second)

    by_id = client.get("/api/v1/investigations?q=PSI-25").json()
    assert by_id["pagination"]["total_items"] >= 1
    assert any(item["investigation_id"] == "PSI-25" for item in by_id["items"])

    by_title = client.get("/api/v1/investigations?q=BASS").json()
    assert by_title["pagination"]["total_items"] >= 1
    assert all("bass" in (item["title"] or "").lower() or "bass" in (item["acronym"] or "").lower()
               for item in by_title["items"])

    filtered = client.get("/api/v1/investigations?has_file_inventory=true").json()
    assert filtered["pagination"]["total_items"] == 7
    assert all(item["file_inventory_available"] for item in filtered["items"])


def test_investigation_detail_preserves_source_metadata():
    response = client.get("/api/v1/investigations/PSI-25")
    assert response.status_code == 200
    data = response.json()

    assert data["investigation_id"] == "PSI-25"
    assert data["title"]
    assert data["psi_api_url"].startswith("https://psi.nasa.gov")
    assert data["snapshot_sha256"]
    assert data["audit_level"] == "full_audit"
    assert data["file_count"] == 695
    assert data["storage"]["local_downloaded_size_bytes"] == 0
    assert data["dataset_groups"]
    assert data["description"]["objectives"]


def test_investigation_detail_unknown_id_returns_structured_404():
    response = client.get("/api/v1/investigations/PSI-9999")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["type"] == "EntityNotFoundException"
    assert error["details"]["identifier"] == "PSI-9999"


def test_files_pagination_filter_and_unknown_sizes_not_invented():
    response = client.get("/api/v1/investigations/PSI-25/files?page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total_items"] == 695
    assert data["totals"]["local_downloaded_size_bytes"] == 0
    assert data["totals"]["downloaded_items"] == 0
    assert data["totals"]["known_size_items"] + data["totals"]["unknown_size_items"] == 695

    archives = client.get(
        "/api/v1/investigations/PSI-25/files?format_category=archive&page_size=5"
    ).json()
    assert archives["pagination"]["total_items"] > 0
    assert all(item["format_category"] == "archive" for item in archives["items"])

    pending = client.get("/api/v1/files?download_status=PENDING&page_size=5").json()
    assert pending["pagination"]["total_items"] > 0
    assert all(item["download_status"] == "PENDING" for item in pending["items"])

    searched = client.get("/api/v1/files?q=bass&page_size=5").json()
    assert searched["pagination"]["total_items"] > 0


def test_storage_summary_separates_remote_and_local():
    response = client.get("/api/v1/investigations/PSI-99/storage-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["investigation_id"] == "PSI-99"
    assert data["storage"]["remote_inventory_size_bytes"] == 12_512
    assert data["storage"]["psi_reported_total_file_size_bytes"] == 16_931_016_137
    assert data["storage"]["local_downloaded_size_bytes"] == 0
    assert data["storage"]["remote_inventory_complete"] is False
    assert data["file_counts"]["total_discovered"] == 2


def test_storage_summary_without_inventory_is_explicit():
    response = client.get("/api/v1/investigations/PSI-10/storage-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["storage"]["remote_inventory_complete"] is False
    assert data["storage"]["remote_inventory_size_bytes"] == 0
    assert data["storage"]["local_downloaded_size_bytes"] == 0
    assert data["notes"]


def test_csv_export_has_header_and_all_records():
    response = client.get("/api/v1/investigations/PSI-25/files/export?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=" in response.headers["content-disposition"]
    lines = response.text.strip().splitlines()
    assert lines[0].startswith("file_id,investigation_id")
    assert len(lines) == 696  # header + 695 files


def test_json_export_has_all_records():
    response = client.get("/api/v1/investigations/PSI-25/files/export?format=json")
    assert response.status_code == 200
    payload = response.json()
    assert payload["record_count"] == 695
    assert len(payload["records"]) == 695
    assert payload["records"][0]["investigation_id"] == "PSI-25"
    assert payload["records"][0]["downloaded"] is False


def test_global_export_respects_filters():
    response = client.get("/api/v1/files/export?format=json&extension=.pdf&investigation_id=PSI-25")
    assert response.status_code == 200
    payload = response.json()
    assert payload["record_count"] > 0
    assert all(record["extension"] == ".pdf" for record in payload["records"])


def test_comparison_is_metadata_only():
    response = client.get("/api/v1/comparison?ids=PSI-22,PSI-25")
    assert response.status_code == 200
    data = response.json()
    assert data["comparison_scope"] == "metadata_and_file_inventory"
    assert data["measurement_comparison_available"] is False
    assert len(data["investigations"]) == 2
    left, right = data["investigations"]
    assert {left["investigation_id"], right["investigation_id"]} == {"PSI-22", "PSI-25"}
    assert "no scientific comparability" in data["notice"].lower()


def test_comparison_rejects_same_investigation():
    response = client.get("/api/v1/comparison?ids=PSI-22,PSI-22")
    assert response.status_code == 422
    assert response.json()["error"]["type"] == "ScientificAnalysisException"


def test_assistant_returns_citations_for_known_topic():
    response = client.post(
        "/api/v1/assistant/query",
        json={"query": "electric field effects on laminar diffusion flames", "limit": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["answer_type"] == "metadata_retrieval"
    assert data["citations"]
    assert len(data["citations"]) <= 3
    for citation in data["citations"]:
        assert citation["investigation_id"].startswith("PSI-")
        assert citation["title"]
        assert citation["snippet"]
    assert any("No experimental measurements are invented" in d for d in data["disclaimers"])


def test_assistant_states_absence_of_evidence():
    response = client.post(
        "/api/v1/assistant/query",
        json={"query": "quantum chromodynamic viscosity of plutonium plasma", "limit": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["citations"] == []
    assert "does not contain enough evidence" in data["answer"]


def test_assistant_validates_short_query():
    response = client.post("/api/v1/assistant/query", json={"query": "x"})
    assert response.status_code == 422
    assert response.json()["error"]["type"] == "ValidationError"


def test_datasets_endpoint_exposes_derivation():
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == GLOBAL_DATASET_GROUPS
    assert data["method"]
    assert data["items"][0]["derivation"] == "top_level_filename_category + psi_subcategory"


def test_storage_analytics_marks_local_storage_zero():
    response = client.get("/api/v1/analytics/storage")
    assert response.status_code == 200
    data = response.json()
    assert data["global"]["remote_inventory_size_bytes"] == GLOBAL_REMOTE_BYTES
    assert data["global"]["local_downloaded_size_bytes"] == 0
    assert len(data["investigations"]) == 7
    assert len(data["investigations_without_file_inventory"]) == 19
    assert sum(row["storage"]["share_of_remote_bytes"] for row in data["investigations"]) <= 100.01
