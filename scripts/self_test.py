#!/usr/bin/env python3
"""MCP stdio self-test for airgap-db-bridge.

Modes
-----
protocol-only
    Send ``initialize`` + ``tools/list``. The connection pool is lazy, so
    this does **not** require a live PostgreSQL instance.

    Protocol-only PASS is **not** full tool coverage and does **not** prove
    that query/execute/list_tables work.

full
    Also call a database tool. Requires an explicit DSN (``--dsn`` or
    ``DB_BRIDGE_DSN`` / legacy aliases). Fails loudly if no DSN is given.
    A running Postgres (or docker-compose) must accept the DSN.

Build class: UNSIGNED INTERNAL — this script is not Authenticode-signed.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any, BinaryIO

PROTOCOL_VERSION = "2024-11-05"
CLIENT_INFO = {"name": "airgap-db-bridge-self-test", "version": "1.0.3"}
CAVEAT = (
    "protocol-only PASS is not full tool coverage and does not prove a live "
    "PostgreSQL connection"
)


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def resolve_dsn(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    return _first_env("DB_BRIDGE_DSN", "POSTGRES_DSN", "POSTGRESQL_MCP_DSN")


def resolve_command(python: str | None) -> list[str]:
    if python:
        return [python, "-m", "postgresql_mcp"]
    exe = shutil.which("airgap-db-bridge")
    if exe:
        return [exe]
    return [sys.executable, "-m", "postgresql_mcp"]


def _write_message(stream: BinaryIO, message: Mapping[str, Any]) -> None:
    body = json.dumps(message, separators=(",", ":")).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    stream.write(header + body)
    stream.flush()


def _read_headers(stream: BinaryIO, timeout_s: float) -> dict[str, str]:
    deadline = time.monotonic() + timeout_s
    raw = b""
    while time.monotonic() < deadline:
        chunk = stream.read(1)
        if not chunk:
            time.sleep(0.01)
            continue
        raw += chunk
        if raw.endswith(b"\r\n\r\n") or raw.endswith(b"\n\n"):
            break
        # NDJSON fallback: a bare JSON object with no LSP headers.
        if raw.startswith(b"{") and raw.endswith(b"\n") and raw.count(b"{") == raw.count(b"}"):
            return {"x-raw-json": raw.decode("utf-8")}
    else:
        raise TimeoutError("timed out waiting for MCP headers on stdout")

    text = raw.decode("ascii", errors="replace")
    if text.lstrip().startswith("{"):
        return {"x-raw-json": text}
    headers: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        headers[key.strip().lower()] = value.strip()
    return headers


def _read_message(stream: BinaryIO, timeout_s: float = 15.0) -> dict[str, Any]:
    headers = _read_headers(stream, timeout_s)
    if "x-raw-json" in headers:
        return json.loads(headers["x-raw-json"])
    length_s = headers.get("content-length")
    if not length_s:
        raise RuntimeError(f"MCP response missing Content-Length: {headers!r}")
    length = int(length_s)
    deadline = time.monotonic() + timeout_s
    body = b""
    while len(body) < length and time.monotonic() < deadline:
        chunk = stream.read(length - len(body))
        if not chunk:
            time.sleep(0.01)
            continue
        body += chunk
    if len(body) < length:
        raise TimeoutError("timed out waiting for MCP body")
    return json.loads(body.decode("utf-8"))


class McpStdioClient:
    """Minimal JSON-RPC MCP client over stdio (Content-Length framing)."""

    def __init__(self, command: list[str], env: dict[str, str], cwd: Path | None) -> None:
        self._id = 0
        self.proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(cwd) if cwd else None,
            env=env,
        )
        if self.proc.stdin is None or self.proc.stdout is None:
            raise RuntimeError("failed to open stdio pipes to the bridge")

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._id += 1
        message: dict[str, Any] = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params is not None:
            message["params"] = params
        assert self.proc.stdin is not None
        _write_message(self.proc.stdin, message)
        assert self.proc.stdout is not None
        return _read_message(self.proc.stdout)

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        message: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            message["params"] = params
        assert self.proc.stdin is not None
        _write_message(self.proc.stdin, message)

    def close(self) -> tuple[bytes, bytes]:
        if self.proc.stdin:
            try:
                self.proc.stdin.close()
            except OSError:
                pass
        try:
            stdout, stderr = self.proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            stdout, stderr = self.proc.communicate()
        return stdout, stderr


def _fail(message: str, extra: str | None = None) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    if extra:
        print(extra, file=sys.stderr)
    print(f"NOTE: {CAVEAT}", file=sys.stderr)
    return 1


def run_self_test(
    *,
    full: bool,
    dsn: str | None,
    python: str | None,
    cwd: Path | None,
) -> int:
    print("airgap-db-bridge self-test — UNSIGNED INTERNAL", flush=True)
    if full:
        if not dsn:
            return _fail(
                "full DB self-test requires a DSN",
                "Pass --dsn or set DB_BRIDGE_DSN "
                "(legacy POSTGRES_DSN / POSTGRESQL_MCP_DSN are accepted when unset).",
            )
        print("mode: full (live PostgreSQL required)", flush=True)
    else:
        print(f"mode: protocol-only — {CAVEAT}", flush=True)

    env = os.environ.copy()
    if dsn:
        env["DB_BRIDGE_DSN"] = dsn
    env.setdefault("DB_BRIDGE_LOG_LEVEL", "WARNING")

    command = resolve_command(python)
    print(f"command: {' '.join(command)}", flush=True)

    client = McpStdioClient(command, env, cwd)
    try:
        init = client.request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": CLIENT_INFO,
            },
        )
        if "error" in init:
            return _fail("initialize returned an error", json.dumps(init, indent=2))
        if "result" not in init:
            return _fail("initialize response missing result", json.dumps(init, indent=2))
        print("PASS initialize", flush=True)

        client.notify("notifications/initialized")

        listed = client.request("tools/list")
        if "error" in listed:
            return _fail("tools/list returned an error", json.dumps(listed, indent=2))
        tools = listed.get("result", {}).get("tools")  # type: ignore[union-attr]
        if not isinstance(tools, list) or not tools:
            return _fail("tools/list returned no tools", json.dumps(listed, indent=2))
        names = sorted(
            str(t.get("name")) for t in tools if isinstance(t, dict) and t.get("name")
        )
        print(f"PASS tools/list ({len(names)} tools: {', '.join(names)})", flush=True)

        if not full:
            print(f"PASS protocol-only ({CAVEAT})", flush=True)
            return 0

        call = client.request(
            "tools/call",
            {"name": "list_tables", "arguments": {"schema": "public"}},
        )
        if "error" in call:
            return _fail(
                "list_tables failed — full DB self-test did not reach Postgres",
                json.dumps(call, indent=2),
            )
        result = call.get("result")
        if isinstance(result, dict) and result.get("isError"):
            return _fail(
                "list_tables returned an MCP tool error — check DSN and that Postgres is running",
                json.dumps(result, indent=2),
            )
        print("PASS list_tables (live database)", flush=True)
        print("PASS full DB self-test", flush=True)
        return 0
    except (TimeoutError, json.JSONDecodeError, RuntimeError, OSError) as exc:
        stderr = b""
        try:
            if client.proc.stderr:
                stderr = client.proc.stderr.read() or b""
        except OSError:
            pass
        extra = stderr.decode("utf-8", errors="replace")
        return _fail(str(exc), extra)
    finally:
        client.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "MCP stdio self-test for airgap-db-bridge. "
            "Protocol-only PASS is not full tool coverage."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--protocol-only",
        action="store_true",
        help="initialize + tools/list only (default). No live Postgres required.",
    )
    mode.add_argument(
        "--full",
        action="store_true",
        help="also call list_tables; requires --dsn or DB_BRIDGE_DSN",
    )
    parser.add_argument("--dsn", default=None, help="PostgreSQL DSN for full mode")
    parser.add_argument(
        "--python",
        default=None,
        help="Python interpreter that has airgap-db-bridge installed",
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="Working directory for the server process",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    full = bool(args.full)
    dsn = resolve_dsn(args.dsn)
    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    return run_self_test(full=full, dsn=dsn, python=args.python, cwd=cwd)


if __name__ == "__main__":
    raise SystemExit(main())
