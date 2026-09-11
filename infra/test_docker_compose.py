"""
Smoke tests for infra/docker-compose.plane.yml

Validates:
- YAML syntax parses without errors
- Expected top-level structure (services, volumes)
- Each service has required Docker Compose keys
- Healthcheck definitions are present for services that need them
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

COMPOSE_PATH = Path(__file__).resolve().parent / "docker-compose.plane.yml"

# Services we expect to find in the compose file
EXPECTED_SERVICES = {
    "plane-db",
    "dragonfly",
    "plane-api",
    "plane-web",
    "plane-worker",
    "plane-beat",
}

# Services that should have a healthcheck
SERVICES_WITH_HEALTHCHECK = {
    "plane-db",
    "dragonfly",
    "plane-api",
    "plane-web",
}


# ---------------------------------------------------------------------------
# YAML parse
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def compose_data() -> dict:
    """Load and parse the compose YAML once per module."""
    if not COMPOSE_PATH.exists():
        pytest.fail(f"Compose file not found: {COMPOSE_PATH}")
    text = COMPOSE_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        pytest.fail("Parsed YAML is not a mapping")
    return data


# ---------------------------------------------------------------------------
# Basic structure
# ---------------------------------------------------------------------------
class TestComposeStructure:
    def test_yaml_parses(self, compose_data: dict) -> None:
        """The YAML should parse without errors (handled by fixture)."""
        assert compose_data is not None

    def test_has_services_key(self, compose_data: dict) -> None:
        assert "services" in compose_data, "Top-level 'services' key missing"

    def test_has_volumes_key(self, compose_data: dict) -> None:
        assert "volumes" in compose_data, "Top-level 'volumes' key missing"

    def test_services_is_dict(self, compose_data: dict) -> None:
        assert isinstance(compose_data["services"], dict)


# ---------------------------------------------------------------------------
# Service presence
# ---------------------------------------------------------------------------
class TestServices:
    def test_all_expected_services_present(self, compose_data: dict) -> None:
        actual = set(compose_data["services"].keys())
        missing = EXPECTED_SERVICES - actual
        assert not missing, f"Missing services: {missing}"

    def test_each_service_has_image(self, compose_data: dict) -> None:
        for name, svc in compose_data["services"].items():
            assert "image" in svc, f"Service '{name}' has no 'image'"

    def test_each_service_has_restart_policy(self, compose_data: dict) -> None:
        for name, svc in compose_data["services"].items():
            assert "restart" in svc, f"Service '{name}' has no 'restart'"


# ---------------------------------------------------------------------------
# Healthchecks
# ---------------------------------------------------------------------------
class TestHealthchecks:
    def test_expected_services_have_healthchecks(self, compose_data: dict) -> None:
        for name in SERVICES_WITH_HEALTHCHECK:
            svc = compose_data["services"].get(name)
            assert svc, f"Service '{name}' not found"
            assert "healthcheck" in svc, f"Service '{name}' missing healthcheck"

    def test_healthchecks_have_test_command(self, compose_data: dict) -> None:
        for name in SERVICES_WITH_HEALTHCHECK:
            hc = compose_data["services"][name].get("healthcheck", {})
            assert "test" in hc, f"Service '{name}' healthcheck has no 'test'"


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
class TestDependencies:
    def test_plane_api_depends_on_db_and_cache(self, compose_data: dict) -> None:
        api = compose_data["services"]["plane-api"]
        deps = api.get("depends_on", {})
        assert "plane-db" in deps, "plane-api should depend on plane-db"
        assert "dragonfly" in deps, "plane-api should depend on dragonfly"

    def test_plane_web_depends_on_api(self, compose_data: dict) -> None:
        web = compose_data["services"]["plane-web"]
        deps = web.get("depends_on", {})
        assert "plane-api" in deps, "plane-web should depend on plane-api"


# ---------------------------------------------------------------------------
# Volumes
# ---------------------------------------------------------------------------
class TestVolumes:
    def test_declared_volumes_present(self, compose_data: dict) -> None:
        volumes = compose_data.get("volumes", {})
        assert "plane-db-data" in volumes, "Named volume 'plane-db-data' not declared"
