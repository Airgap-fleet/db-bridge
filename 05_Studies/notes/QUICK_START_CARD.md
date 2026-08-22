# 🚀 MCP Server Business — Quick Start Card

*"Activate this team to run your business autonomously."*

---

## 🔑 Prerequisites

1. **Hermes Desktop App** installed and configured
2. **GitHub account** for code/repos/issue tracking
3. **Stripe/Billing** set up (or choose: RevenueCat, Paddle)
4. Vault location: `C:\the force\05_Studies\notes\`

---

## 📚 Required Reading

1. **Start Here**: [[MCP_SERVER_BUSINESS_OPERATIONS_MANUAL]] (Full manual)
2. **Protocol Basics**: [[01-mcp-server-business-fundamentals]] (MCP concepts)
3. **Team Structure**: See [[MCP_SERVER_BUSINESS_OPERATIONS_MANUAL]] section 2.6

---

## 🎯 Team Activation Sequence

### Step 1: Load CEO (Rupert)
```bash
# Rupert already loaded at: C:\the force\02_Sub-Agents\rupert-soul.md
skill_view(name='rupert-mcp-biz-manager')  # Verify skill exists
```

**CEO Coordinates**:
- Revenue operations (pipeline → cash)
- Sales strategy & pricing
- Client success oversight
- Market intelligence gathering

### Step 2: Spawn Supporting Agents

Use `delegate_task` for each role. Example:

```python
# Infrastructure Layer
delegate_task(goal="Setup monitoring dashboards and deploy K8s cluster for MCP server hosting", context="See section 2.6 in operations manual")

# Customer Layer  
delegate_task(goal="Build automated onboarding emails and support triage system", context="Onboard first customers autonomously")

# Sales Layer
delegate_task(goal="Scrape LinkedIn/GitHub for enterprise prospects matching our ideal customer profile", actions_required=False)
```

### Step 3: Configure Tools

1. **GitHub** → `setup_mcp(server='github')` or use gh CLI login
2. **Stripe** → Create keys in dashboard, pass `STRIPE_KEY` env var
3. **Hermes Session** → Ensure `memory` and `skill_manage` accessible
4. **Notion/Vault** → Grant read/write permissions (if external)

---

## ⚙️ Deployment Phases

| Phase | Timeline | Focus | Agents Active | Manual Intervention |
|-------|----------|-------|---------------|---------------------|
| **MVP** | Days 1-30 | Launch server, first $ paid customers | CEO, CTO, Dev, QA | Billing setup, initial PR reviews |
| **Growth** | Days 31-90 | Scale acquisition, improve docs | +PM, Docs, BI, SDR | Content approvals, partner outreach |
| **Enterprise** | Days 91-180 | Compliance, security prep, enterprise deals | +CSM, Sec, DB, AC | SOC2 certs, contract legal review |
| **Scale Ops** | Day 180+ | Team building, culture, global expansion | All roles + VP layer | Strategic hiring, culture setting |

---

## 📊 First Week Checklist

- [ ] CEO (Rupert) loaded and verified in vault
- [ ] GitHub repo created with LICENSE, README, CONTRIBUTING docs
- [ ] Stripe test mode enabled with webhook endpoint
- [ ] Monitoring dashboard deployed (Datadog/Sentry free tier)
- [ ] First agent tasks spawned:
  - Dev → Write sample MCP server
  - QA → Setup CI test suite  
  - Docs → Create API reference stub
  - PM → Define product roadmap

---

## 🆘 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Agent doesn't spawn | Check `delegate_task` context length <65k tokens; truncate with `skill_view` to get focused summaries first |
| GitHub auth failing | Use `gh CLI login` in terminal before delegation |
| Stripe webhooks not firing | Verify endpoint SSL cert + check webhook logs in Stripe dashboard |
| Billing integration error | Use RevenueCat instead (simpler for MVP) or consult CLO for contract review |

---

## 📞 Getting Help

1. **Check operations manual**: All SOPs in `MCP_SERVER_BUSINESS_OPERATIONS_MANUAL.md`
2. **Review related docs**: [[01-mcp-server-business-fundamentals]], [[3-MANAGEMENT_LEADERSHIP_FUNDAMENTALS]]
3. **Session search**: Use `session_search(query='agent team')` to recall past setups

---

## 🎓 Next Steps After Activation

Week 1: Verify first customer signup and payment flows  
Week 2: Launch beta landing page with waitlist capture  
Week 3: Ship v0.1 MCP server to GitHub + publish docs  
Week 4: First revenue milestone review → pivot or persevere?

---

*"From zero to autonomous revenue engine — your complete agent team awaits."* 🚀
