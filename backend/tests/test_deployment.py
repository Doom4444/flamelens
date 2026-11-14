"""Deployment-readiness checks.

These tests guard the production invariants that are easy to break silently:
metadata must ship with the app, environment configuration must parse, and the
hosting configuration must keep SPA routes and health checks working.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.config import Settings
from app.data_pipeline.metadata_repository import store as metadata_store
from app.main import REQUIRED_METADATA_FILES, _validate_metadata_artifacts

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_required_metadata_inventories_are_present() -> None:
    for filename in REQUIRED_METADATA_FILES:
        assert (metadata_store.metadata_dir / filename).is_file(), filename


def test_metadata_validation_loads_all_inventories() -> None:
    # Raises if a file is missing or contains invalid JSON.
    _validate_metadata_artifacts()


def test_metadata_validation_fails_fast_when_inventory_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(metadata_store, "metadata_dir", tmp_path)
    with pytest.raises(RuntimeError) as excinfo:
        _validate_metadata_artifacts()
    message = str(excinfo.value)
    assert "investigations_inventory.json" in message
    # Error text must not leak absolute filesystem paths into responses/logs.
    assert str(tmp_path) not in message


def test_is_production_flag() -> None:
    assert Settings(ENVIRONMENT="production").is_production
    assert Settings(ENVIRONMENT="Production ").is_production
    assert not Settings(ENVIRONMENT="development").is_production


def test_cors_origins_accepts_comma_separated_list() -> None:
    settings = Settings(
        CORS_ORIGINS="https://flamelens.vercel.app, https://staging.vercel.app"
    )
    assert settings.CORS_ORIGINS == [
        "https://flamelens.vercel.app",
        "https://staging.vercel.app",
    ]


def test_cors_origins_accepts_json_list() -> None:
    settings = Settings(CORS_ORIGINS='["https://flamelens.vercel.app"]')
    assert settings.CORS_ORIGINS == ["https://flamelens.vercel.app"]


def test_dockerfile_ships_metadata_and_honours_port() -> None:
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    for filename in REQUIRED_METADATA_FILES:
        assert filename in dockerfile, filename
    assert "FLAMELENS_METADATA_DIR=/app/data/metadata" in dockerfile
    assert "0.0.0.0" in dockerfile
    assert "${PORT:-8000}" in dockerfile
    assert "USER flamelens" in dockerfile


def test_dockerignore_excludes_local_only_directories() -> None:
    ignored = (REPO_ROOT / ".dockerignore").read_text(encoding="utf-8")
    assert "data/knowledge" in ignored
    assert "frontend" in ignored
    assert "**/.env" in ignored


def test_render_blueprint_uses_health_endpoint_and_dockerfile() -> None:
    blueprint = (REPO_ROOT / "render.yaml").read_text(encoding="utf-8")
    assert "healthCheckPath: /api/v1/health" in blueprint
    assert "dockerfilePath: ./Dockerfile" in blueprint
    assert "FLAMELENS_METADATA_DIR" in blueprint


def test_vercel_config_has_spa_rewrite() -> None:
    config = json.loads((REPO_ROOT / "frontend" / "vercel.json").read_text(encoding="utf-8"))
    destinations = {rewrite.get("destination") for rewrite in config["rewrites"]}
    assert "/index.html" in destinations


def test_frontend_has_no_production_localhost_fallback() -> None:
    api_service = (
        REPO_ROOT / "frontend" / "src" / "services" / "api.ts"
    ).read_text(encoding="utf-8")
    # The localhost literal may only appear inside the Vite dev-server branch.
    assert "import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''" in api_service
