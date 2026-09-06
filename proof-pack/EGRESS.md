# Egress observation notes

The **running** bridge is intended to stay local-first:

- stdio MCP to the desktop client
- PostgreSQL only at the configured DSN (typically `localhost` or a LAN host you chose)
- **no telemetry, no phone-home, no crash-reporting endpoint**

Installer **setup** may use the network (PyPI, `uv`, Python). That is expected and is not the same as runtime egress.

## This is not a certification

These notes and `observe-egress.ps1` are observation aids. They do not prove the absence of all outbound channels, and they are not a penetration test.

## Suggested observation (Windows)

1. Record listening / established TCP endpoints.
2. Run `.\scripts\self_test.ps1 -ProtocolOnly` (no DSN).
3. Record endpoints again.
4. Expect no new connections to unexpected remote hosts. Protocol-only should not open Postgres.

For a full DB demo, expect a connection to the DSN host only. That requires Postgres.

```powershell
.\proof-pack\observe-egress.ps1
```

On Linux, `ss -tnp` or `netstat -tnp` before and after `python scripts/self_test.py --protocol-only` is equivalent.

## Honest limits

- A process can open sockets after your snapshot.
- DNS, SMB, and UDP are not fully covered by a simple TCP dump.
- Docker or a remote DSN will show as an outbound (or bridge-network) connection — that is the database, not telemetry.
