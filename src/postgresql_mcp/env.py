"""Canonical environment resolution for DB Bridge.

Canonical prefix: ``DB_BRIDGE_*`` (especially ``DB_BRIDGE_DSN``).

Legacy prefixes are copied into the canonical names only when the
canonical variable is unset:

* ``POSTGRES_*``
* ``POSTGRESQL_MCP_*``

This module does not phone home and does not invent extra settings.
"""

from __future__ import annotations

import os
from collections.abc import MutableMapping

CANONICAL_PREFIX = "DB_BRIDGE_"
LEGACY_PREFIXES: tuple[str, ...] = ("POSTGRES_", "POSTGRESQL_MCP_")

# Settings fields that exist on PostgreSQLConfig (and close aliases).
SETTINGS_KEYS: tuple[str, ...] = (
    "DSN",
    "POOL_SIZE",
    "READ_ONLY",
    "QUERY_TIMEOUT",
    "LOG_LEVEL",
)


def apply_legacy_env(
    environ: MutableMapping[str, str] | None = None,
) -> dict[str, str]:
    """Map legacy env vars onto ``DB_BRIDGE_*`` when unset.

    Returns a dict of ``{canonical_name: legacy_name}`` for values that
    were copied. Existing ``DB_BRIDGE_*`` values always win.
    """
    env: MutableMapping[str, str] = os.environ if environ is None else environ
    applied: dict[str, str] = {}
    for key in SETTINGS_KEYS:
        canonical = f"{CANONICAL_PREFIX}{key}"
        if env.get(canonical):
            continue
        for prefix in LEGACY_PREFIXES:
            legacy = f"{prefix}{key}"
            value = env.get(legacy)
            if value:
                env[canonical] = value
                applied[canonical] = legacy
                break
    return applied


def first_env(*names: str, default: str | None = None) -> str | None:
    """Return the first non-empty environment value among ``names``."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default
