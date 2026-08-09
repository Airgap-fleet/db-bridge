# IP Protection Strategy — AFaaS

> **Decision Log:** 2026-08-07 — Master & Obi-Wan discussion on protecting AFaaS IP

---

## Patent Assessment
**Verdict:** Core business model ("Agent Fleet as a Service") NOT patentable. Specific technical inventions *may* be patentable if:
- Novel algorithm with measurable technical improvement
- Non-obvious to skilled practitioner
- Technical solution to technical problem (not business method)

**Recommendation:** Do not pursue patents for business model. Only patent genuinely novel technical methods (e.g., unique delegation protocol, AMD/DirectML optimization pipeline) if they emerge.

---

## Protection Strategy (Layered)

| Layer | Asset | Protection | Mechanism |
|-------|-------|------------|-----------|
| **Core** | Delegation engine, agent orchestration logic | Trade Secret | Never open-source, never in cloud prompts, vault-only |
| **Core** | Agent soul specs, prompts, configurations | Trade Secret + Copyright | Vault-only, marked CONFIDENTIAL |
| **Core** | AMD/DirectML optimization configs | Trade Secret | Your moat — 8B on 2GB VRAM |
| **Product** | MCP Servers (Obsidian, Filesystem, PostgreSQL, etc.) | Source-Available License | Free use, no resale, attribution — builds ecosystem |
| **Product** | Deployment playbooks, runbooks | Trade Secret + Contract | Contractual IP assignment |
| **Legal** | Client deliverables | Contract | MSA: "Contractor retains framework IP. Client licenses deployed fleet." |
| **Brand** | "AFaaS", agent names, logos | Trademark | UK IPO registration (£170, 10 years) |

---

## Immediate Actions (This Month)
1. Add IP clause to MSA template in `00_Master/contracts/`
2. Mark internal vault docs with `CONFIDENTIAL — TRADE SECRET` headers
3. Do not publish core delegation/orchestration code (MCP servers OK)
4. File UK trademark for "AFaaS" (£170)

---

## When to Engage IP Attorney
- Before first pilot contract (review IP clauses)
- If genuinely novel technical method invented (benchmark-proven)
- Before open-sourcing any component
- Estimated: £500-2K initial consultation

---

## Core Principle
**Moat = Execution speed + Domain expertise + Customer trust + Trade secrets**
Not patents. First pilot = strongest moat.

---

*Logged by Obi-Wan per Master directive. Review at first pilot contract stage.*