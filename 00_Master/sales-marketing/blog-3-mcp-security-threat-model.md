# MCP Security: Threat Modeling for Enterprise Deployment

**Published:** 2026-08-22  
**Author:** AFaaS Team  
**Tags:** #MCP #Security #ThreatModeling #Enterprise #Compliance

---

## Why Threat Model an MCP Server?

Your CISO will ask: *"What happens if an agent goes rogue? Can it read `/etc/passwd`? Write to production configs? Exfiltrate data?"*

MCP servers are **privileged intermediaries** between AI agents and your infrastructure. They execute tool calls with the permissions of the user running them. A compromised or misbehaving agent with MCP access = **arbitrary code execution on your network**.

This post walks through a **STRIDE threat model** for Obsidian Vault MCP, the mitigations we built in, and the security questionnaire responses your buyers will need.

---

## STRIDE Analysis: Obsidian Vault MCP

| Threat Category | Scenario | Likelihood | Impact | Mitigation (Built-in) |
|-----------------|----------|------------|--------|----------------------|
| **Spoofing** | Agent impersonates another agent/user | Low (stdio) / Medium (SSE) | High | API key auth required for SSE/HTTP; stdio inherits OS user |
| **Tampering** | Agent modifies notes maliciously | Medium | Medium | Audit logs (JSON); atomic writes; vault git history |
| **Repudiation** | "Agent didn't do that — no proof" | Medium | High | Structured JSON logs with timestamps, tool, params, result |
| **Information Disclosure** | Agent reads files outside vault | **High (if unmitigated)** | **Critical** | **Path sandboxing: all paths resolved relative to vault root; `../` and absolute paths rejected** |
| **Denial of Service** | Agent loops, huge files, fills disk | Medium | Medium | File size limit (configurable, default 10MB); max results cap (1000); timeout on tool calls |
| **Elevation of Privilege** | Agent escapes vault, gets shell | Low (if sandboxed) | Critical | No shell execution; no arbitrary command tools; path validation on every call |

---

## Attack Surface Map

```
┌─────────────────────────────────────────────────────────────────┐
│                      TRUST BOUNDARIES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐         MCP Protocol          ┌─────────────┐  │
│  │   AI Agent  │◄──────────────────────────────►│ MCP Server  │  │
│  │ (Untrusted) │      (JSON-RPC over stdio/    │ (Trusted    │  │
│  │             │       SSE/HTTP)               │  Process)   │  │
│  └─────────────┘                                └──────┬──────┘  │
│                                                         │         │
│                              ┌──────────────────────────┼──────┐  │
│                              ▼                          ▼      ▼  │
│                     ┌───────────────┐           ┌───────────────┐  │
│                     │  Vault Files  │           │  Config/Env   │  │
│                     │  (User Data)  │           │  (Secrets)    │  │
│                     └───────────────┘           └───────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: The MCP server is the **only** component that touches the filesystem. The agent only sends JSON-RPC messages. Compromise the agent → you get MCP tool calls. Compromise the server → you get filesystem access (sandboxed).

---

## Built-in Mitigations (Defense in Depth)

### 1. Path Sandboxing (Primary Defense)
```python
# Every path goes through _resolve_path()
def _resolve_path(self, path: str) -> Path:
    resolved = (self.vault_root / path).resolve()
    # CRITICAL: Ensure resolved path is within vault root
    if not resolved.is_relative_to(self.vault_root):
        raise SecurityError(f"Path {path} escapes vault root")
    return resolved
```
- Rejects absolute paths
- Rejects `../` traversal
- Resolves symlinks (configurable, default: no follow)
- Validated on **every** tool call

### 2. File Size Limits
```python
max_file_size: int = Field(default=10_485_760, ge=1024, le=1_073_741_824)
```
- Prevents memory exhaustion via huge files
- Configurable per deployment

### 3. Structured Audit Logging
Every tool call logs:
```json
{
  "timestamp": "2026-08-22T10:30:45.123Z",
  "level": "INFO",
  "event": "tool_call",
  "tool": "write_note",
  "params": {"path": "meeting-notes.md", "size": 2048},
  "result": "success",
  "duration_ms": 12
}
```
- Immutable (write to append-only log / SIEM)
- Correlates agent → tool → file → outcome
- Enables retrospective investigation

### 4. Transport Security
| Transport | Auth | Encryption | Use Case |
|-----------|------|------------|----------|
| **stdio** | OS user | N/A (local) | Developer, single-user, highest security |
| **SSE** | API Key (Bearer) | TLS 1.3 (terminate at proxy) | Team shared, remote agents |
| **Streamable HTTP** | API Key (Bearer) | TLS 1.3 | Production, load balanced, K8s |

**No anonymous access on network transports.**

### 5. No Arbitrary Execution
- No `exec`, `eval`, `subprocess` tools
- No shell command exposure
- Tools are **whitelisted, parameterized operations only**

---

## Security Questionnaire Responses (Pre-filled)

### SOC 2 / ISO 27001 Common Questions

| Question | Response |
|----------|----------|
| **Data encryption at rest?** | Vault files are standard filesystem — encrypt via OS (BitLocker, LUKS, FileVault). MCP server writes plaintext; relies on volume encryption. |
| **Data encryption in transit?** | stdio: N/A (local). SSE/HTTP: TLS 1.3 termination at reverse proxy (nginx, Traefik, cloud LB). |
| **Authentication mechanism?** | stdio: OS user context. SSE/HTTP: API Key (Bearer token, 256-bit entropy, configurable header). |
| **Authorization model?** | Single-tenant per MCP instance. All tools available to authenticated agent. For RBAC: deploy separate instances per role (read-only vs read-write). |
| **Audit logging?** | Structured JSON logs to stdout. Fields: timestamp, tool, parameters (sanitized), result, duration, error. Integrates with ELK, Splunk, Datadog. |
| **Vulnerability management?** | Dependencies scanned via `pip-audit` in CI. Base image updated monthly. Security patches released within 72h of CVE publication. |
| **Incident response?** | Runbook provided. Logs enable forensic analysis. Support SLA: 4h response (Professional), 1h (Enterprise). |
| **Penetration testing?** | Annual third-party pen test (Enterprise tier). Source available for customer audit. |
| **Data retention?** | MCP server retains no data. Vault files follow customer retention policy. Logs: customer-controlled (stdout). |
| **Subprocessors?** | None. Pure Python, no external API calls at runtime. Dependencies: FastMCP, Pydantic, structlog, PyYAML — all open source. |

---

## Deployment Hardening Checklist

### For All Deployments
- [ ] Run as dedicated non-root user (`mcp-user`)
- [ ] Vault directory: `chown mcp-user:mcp-user /vault; chmod 750 /vault`
- [ ] Set `OBSIDIAN_MCP_MAX_FILE_SIZE` appropriate to use case
- [ ] Enable `OBSIDIAN_MCP_FOLLOW_SYMLINKS=false` (default)
- [ ] Forward logs to SIEM / centralized logging

### For SSE/HTTP Deployments
- [ ] Generate strong API key: `openssl rand -hex 32`
- [ ] Store API key in secret manager (AWS Secrets Manager, HashiCorp Vault, K8s Secret)
- [ ] Terminate TLS at reverse proxy (nginx/Traefik/Caddy)
- [ ] Rate limit at proxy: `limit_req zone=mcp burst=10 nodelay;`
- [ ] Restrict network: only allow agent IPs / VPC CIDR
- [ ] Health endpoint: `GET /health` → 200 OK (add to MCP server)

### For Kubernetes
```yaml
# Deployment security context
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]

# Volume mounts
volumes:
- name: vault
  persistentVolumeClaim:
    claimName: obsidian-vault
- name: api-key
  secret:
    secretName: obsidian-mcp-api-key
```

---

## Incident Response Runbook (Summary)

| Phase | Actions | Owner |
|-------|---------|-------|
| **Detect** | Alert on: error rate > 5%, tool call latency > 5s, unauthorized access attempts (401/403) | Monitoring |
| **Triage** | Check logs: which tool, which params, which agent, success/failure | Support Eng |
| **Contain** | Revoke API key (rotate), stop MCP process, isolate network | DevOps |
| **Investigate** | Correlate agent ID, tool sequence, file modifications, git diff vault | Tech Lead |
| **Remediate** | Restore vault from git/snapshot, patch config, rotate credentials | DevOps |
| **Report** | Timeline, root cause, impact, prevention | Tech Lead → Customer |

---

## What We Don't Protect Against (Shared Responsibility)

| Risk | Customer Responsibility |
|------|------------------------|
| OS compromise | Patch management, hardening, monitoring |
| Vault file permissions | POSIX ACLs, git history, backup strategy |
| Agent behavior | Prompt engineering, tool allowlisting, output validation |
| Network segmentation | VPC, firewall rules, zero-trust architecture |
| Secret management | API key rotation, secure storage, least privilege |
| Physical security | Data center / device protection |

---

## Compliance Mapping

| Framework | Control | MCP Support |
|-----------|---------|-------------|
| **SOC 2 Type II** | CC6.1 (Logical Access) | API key auth, path sandboxing |
| | CC7.2 (System Monitoring) | Structured JSON logs |
| | CC8.1 (Change Management) | SemVer, CHANGELOG, CI gates |
| **ISO 27001** | A.9.2 (User Access) | Per-instance API keys |
| | A.12.4 (Logging) | JSON audit logs |
| | A.14.2 (Security in Dev) | Bandit, pip-audit in CI |
| **Cyber Essentials** | Boundary Firewalls | Network restrict at proxy |
| | Secure Configuration | Non-root, read-only FS, caps dropped |
| | Access Control | API key + transport separation |

---

## Quick Security Self-Assessment (For Prospects)

Ask your team:
1. **Where does the vault live?** → Must be on same machine or mounted volume (no network FS for stdio)
2. **Who runs the MCP server?** → Dedicated service account, not root, not your user
3. **How do agents connect?** → stdio for local; SSE/HTTP + TLS + API key for remote
4. **Where do logs go?** → stdout → your log aggregator (ELK, Splunk, CloudWatch)
5. **What's the blast radius?** → One vault per MCP instance. Compromise = that vault only.

---

## Next Steps for Your Deployment

1. **Review this threat model** with your security team
2. **Run the hardening checklist** for your deployment mode
3. **Integrate logs** with your SIEM
4. **Schedule pen test** (we coordinate for Enterprise tier)
5. **Add to your asset register** — MCP server as "AI Infrastructure Component"

---

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [STRIDE Methodology](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI Risk Management Framework](https://airc.nist.gov/AI_RMF_Knowledge_Base)

---

*AFaaS provides security review, threat modeling workshops, and penetration testing for MCP deployments. Enterprise tier includes annual third-party pen test. mcp@afaas.io*