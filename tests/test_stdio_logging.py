"""Regression: structured logs must never land on stdout (stdio MCP)."""

from __future__ import annotations

import io
import json
import os
import subprocess
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


def _read_stdio_message(raw: bytes) -> dict[str, object]:
    text = raw.decode("utf-8", errors="replace")
    if "Content-Length:" in text:
        _, _, body = text.partition("\r\n\r\n")
        if not body:
            _, _, body = text.partition("\n\n")
        return json.loads(body)
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    raise AssertionError(f"stdout was not JSON-RPC:\n{text!r}")


def test_mcp_initialize_stdout_is_jsonrpc_only() -> None:
    """Spawn the server; initialize response must be JSON-RPC on stdout."""
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "stdio-logging-regression", "version": "1.0.3"},
        },
    }
    payload = json.dumps(init).encode("utf-8")
    framed = f"Content-Length: {len(payload)}\r\n\r\n".encode() + payload

    env = os.environ.copy()
    env["DB_BRIDGE_LOG_LEVEL"] = "INFO"
    # Do not require a live DSN — pool is lazy until a DB tool is called.
    proc = subprocess.Popen(
        [sys.executable, "-m", "postgresql_mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=REPO_ROOT,
        env=env,
    )
    try:
        stdout, stderr = proc.communicate(framed, timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        raise AssertionError(
            f"server timed out; stdout={stdout!r} stderr={stderr!r}"
        ) from None

    message = _read_stdio_message(stdout)
    assert message.get("jsonrpc") == "2.0"
    assert message.get("id") == 1
    assert "result" in message or "error" in message

    # Logs (if any) must not appear on stdout.
    stdout_text = stdout.decode("utf-8", errors="replace")
    assert "stdio_must_stay_clean" not in stdout_text
    for line in stdout_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("content-length"):
            continue
        if stripped.startswith("{"):
            parsed = json.loads(stripped)
            assert parsed.get("jsonrpc") == "2.0" or "event" not in parsed
