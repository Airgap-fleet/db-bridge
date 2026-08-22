# Moneypenny Cron Job Fix — 2026-08-21

## Problem
Cron job `655d8b9c505b` (Moneypenny Daily Brief) failing with model configuration errors:
- `job.model=None` — no model configured
- `openrouter:nvidia/nemotron-3-ultra:free` — invalid model ID
- `nvidia/nemotron-3-ultra:free` — invalid model ID
- `openrouter:nvidia/nemotron-3-ultra` — invalid model ID
- `nemotron-3-ultra` — invalid model ID

## Root Cause
OpenRouter model ID format requires provider prefix but cron job model field doesn't accept `openrouter:` prefix. The actual model name on OpenRouter is `nvidia/nemotron-3-ultra` (no `:free` suffix for cron config).

## Fix Applied
```bash
# Set default model in config.yaml
hermes config set model.default "openrouter:nvidia/nemotron-3-ultra"

# Update cron job with correct model ID
hermes cron edit 655d8b9c505b --model nvidia/nemotron-3-ultra
```

## Current Status
- Config.yaml: `model.default = openrouter:nvidia/nemotron-3-ultra` ✓
- Cron job model: `nvidia/nemotron-3-ultra` ✓
- Next scheduled run: 2026-08-22 06:00 BST
- Last manual run: 2026-08-21 19:05 (failed - model ID still wrong)

## Notes
The `:free` suffix is an OpenRouter pricing tier indicator, not part of the model ID. Cron jobs use the base model name. Default model in config.yaml uses full provider:model format.

## Next Steps
- Verify tomorrow's 06:00 automated run succeeds
- Check output at `/c/Users/brook/AppData/Local/hermes/profiles/moneypenny/cron/output/655d8b9c505b/`
- Brief should write to `03_Context/market-intel/YYYY-MM-DD.md`