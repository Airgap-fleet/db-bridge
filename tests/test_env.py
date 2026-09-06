"""Tests for canonical DB_BRIDGE_* env resolution and legacy aliases."""

from __future__ import annotations

import pytest

from postgresql_mcp.env import SETTINGS_KEYS, apply_legacy_env
from postgresql_mcp.models import PostgreSQLConfig

_ENV_NAMES = tuple(
    f"{prefix}{key}"
    for prefix in ("DB_BRIDGE_", "POSTGRES_", "POSTGRESQL_MCP_")
    for key in SETTINGS_KEYS
)


@pytest.fixture(autouse=True)
def _clear_bridge_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def test_apply_legacy_env_maps_postgres_when_canonical_unset() -> None:
    env = {"POSTGRES_DSN": "postgresql://legacy:pw@host:5432/db"}
    applied = apply_legacy_env(env)
    assert applied["DB_BRIDGE_DSN"] == "POSTGRES_DSN"
    assert env["DB_BRIDGE_DSN"] == "postgresql://legacy:pw@host:5432/db"


def test_apply_legacy_env_maps_postgresql_mcp_when_unset() -> None:
    env = {"POSTGRESQL_MCP_DSN": "postgresql://mcp:pw@host:5432/db"}
    applied = apply_legacy_env(env)
    assert applied["DB_BRIDGE_DSN"] == "POSTGRESQL_MCP_DSN"


def test_apply_legacy_env_canonical_wins() -> None:
    env = {
        "DB_BRIDGE_DSN": "postgresql://canonical:pw@host:5432/db",
        "POSTGRES_DSN": "postgresql://legacy:pw@host:5432/db",
    }
    applied = apply_legacy_env(env)
    assert "DB_BRIDGE_DSN" not in applied
    assert env["DB_BRIDGE_DSN"] == "postgresql://canonical:pw@host:5432/db"


def test_config_reads_db_bridge_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_BRIDGE_DSN", "postgresql://env:secret@env:5432/env")
    monkeypatch.setenv("DB_BRIDGE_POOL_SIZE", "25")
    monkeypatch.setenv("DB_BRIDGE_READ_ONLY", "true")
    monkeypatch.setenv("DB_BRIDGE_QUERY_TIMEOUT", "45.5")
    monkeypatch.setenv("DB_BRIDGE_LOG_LEVEL", "WARNING")

    config = PostgreSQLConfig()
    assert str(config.dsn).startswith("postgresql://env:")
    assert "@env:5432/env" in str(config.dsn)
    assert config.pool_size == 25
    assert config.read_only is True
    assert config.query_timeout == 45.5
    assert config.log_level == "WARNING"


def test_config_reads_legacy_postgres_when_canonical_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://env:secret@env:5432/env")
    monkeypatch.setenv("POSTGRES_POOL_SIZE", "25")
    monkeypatch.setenv("POSTGRES_READ_ONLY", "true")
    monkeypatch.setenv("POSTGRES_QUERY_TIMEOUT", "45.5")
    monkeypatch.setenv("POSTGRES_LOG_LEVEL", "WARNING")

    config = PostgreSQLConfig()
    assert str(config.dsn).startswith("postgresql://env:")
    assert config.pool_size == 25
    assert config.read_only is True
    assert config.query_timeout == 45.5
    assert config.log_level == "WARNING"
