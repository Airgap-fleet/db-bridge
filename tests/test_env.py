"""Tests for canonical DB_BRIDGE_* env resolution and legacy aliases."""

from __future__ import annotations

import os

from postgresql_mcp.env import apply_legacy_env
from postgresql_mcp.models import PostgreSQLConfig


def test_apply_legacy_env_maps_postgres_when_canonical_unset(monkeypatch: object) -> None:
    monkeypatch.delenv("DB_BRIDGE_DSN", raising=False)  # type: ignore[attr-defined]
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://legacy:pw@host:5432/db")  # type: ignore[attr-defined]
    applied = apply_legacy_env()
    assert applied["DB_BRIDGE_DSN"] == "POSTGRES_DSN"
    assert os.environ["DB_BRIDGE_DSN"] == "postgresql://legacy:pw@host:5432/db"


def test_apply_legacy_env_maps_postgresql_mcp_when_unset(monkeypatch: object) -> None:
    monkeypatch.delenv("DB_BRIDGE_DSN", raising=False)  # type: ignore[attr-defined]
    monkeypatch.delenv("POSTGRES_DSN", raising=False)  # type: ignore[attr-defined]
    monkeypatch.setenv("POSTGRESQL_MCP_DSN", "postgresql://mcp:pw@host:5432/db")  # type: ignore[attr-defined]
    applied = apply_legacy_env()
    assert applied["DB_BRIDGE_DSN"] == "POSTGRESQL_MCP_DSN"


def test_apply_legacy_env_canonical_wins(monkeypatch: object) -> None:
    monkeypatch.setenv("DB_BRIDGE_DSN", "postgresql://canonical:pw@host:5432/db")  # type: ignore[attr-defined]
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://legacy:pw@host:5432/db")  # type: ignore[attr-defined]
    applied = apply_legacy_env()
    assert "DB_BRIDGE_DSN" not in applied
    assert os.environ["DB_BRIDGE_DSN"] == "postgresql://canonical:pw@host:5432/db"


def test_config_reads_db_bridge_prefix(monkeypatch: object) -> None:
    monkeypatch.setenv("DB_BRIDGE_DSN", "postgresql://env:secret@env:5432/env")  # type: ignore[attr-defined]
    monkeypatch.setenv("DB_BRIDGE_POOL_SIZE", "25")  # type: ignore[attr-defined]
    monkeypatch.setenv("DB_BRIDGE_READ_ONLY", "true")  # type: ignore[attr-defined]
    monkeypatch.setenv("DB_BRIDGE_QUERY_TIMEOUT", "45.5")  # type: ignore[attr-defined]
    monkeypatch.setenv("DB_BRIDGE_LOG_LEVEL", "WARNING")  # type: ignore[attr-defined]

    config = PostgreSQLConfig()
    assert str(config.dsn).startswith("postgresql://env:")
    assert "@env:5432/env" in str(config.dsn)
    assert config.pool_size == 25
    assert config.read_only is True
    assert config.query_timeout == 45.5
    assert config.log_level == "WARNING"


def test_config_reads_legacy_postgres_when_canonical_unset(monkeypatch: object) -> None:
    for name in (
        "DB_BRIDGE_DSN",
        "DB_BRIDGE_POOL_SIZE",
        "DB_BRIDGE_READ_ONLY",
        "DB_BRIDGE_QUERY_TIMEOUT",
        "DB_BRIDGE_LOG_LEVEL",
    ):
        monkeypatch.delenv(name, raising=False)  # type: ignore[attr-defined]
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://env:secret@env:5432/env")  # type: ignore[attr-defined]
    monkeypatch.setenv("POSTGRES_POOL_SIZE", "25")  # type: ignore[attr-defined]
    monkeypatch.setenv("POSTGRES_READ_ONLY", "true")  # type: ignore[attr-defined]
    monkeypatch.setenv("POSTGRES_QUERY_TIMEOUT", "45.5")  # type: ignore[attr-defined]
    monkeypatch.setenv("POSTGRES_LOG_LEVEL", "WARNING")  # type: ignore[attr-defined]

    config = PostgreSQLConfig()
    assert str(config.dsn).startswith("postgresql://env:")
    assert config.pool_size == 25
    assert config.read_only is True
    assert config.query_timeout == 45.5
    assert config.log_level == "WARNING"
