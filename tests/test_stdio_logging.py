"""Regression: structured logs must never land on stdout (stdio MCP)."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

from postgresql_mcp.logging import configure_logging, get_logger

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_structlog_writes_json_to_stderr_not_stdout() -> None:
    stream = io.StringIO()
    configure_logging(level="INFO", stream=stream)
    get_logger("stdio-audit").info("stdio_must_stay_clean", marker="audit")

    output = stream.getvalue()
    assert "stdio_must_stay_clean" in output
    payload = json.loads(output.strip().splitlines()[-1])
    assert payload["marker"] == "audit"
    assert payload["event"] == "stdio_must_stay_clean"


def test_configure_logging_does_not_write_to_stdout(capsys: object) -> None:
    configure_logging(level="INFO")
    get_logger("stdio-audit").warning("keep_stdout_clean", probe=True)
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert "keep_stdout_clean" not in captured.out
    assert "keep_stdout_clean" in captured.err


def test_mcp_initialize_stdout_is_jsonrpc_only() -> None:
    """Protocol-only handshake must succeed; pool is lazy (no live DSN)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "db_bridge_self_test",
        REPO_ROOT / "scripts" / "self_test.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    rc = module.run_self_test(
        full=False,
        dsn=None,
        python=sys.executable,
        cwd=REPO_ROOT,
    )
    assert rc == 0
