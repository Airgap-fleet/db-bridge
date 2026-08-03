# Hardware Specifications

## Primary Machine (Obi-Wan / Anakin host)
- **OS**: Windows 11 Pro (WSL2 / Git Bash)
- **Processor**: AMD Ryzen 7 8745H w/ Radeon 780M Graphics (3.80 GHz)
- **RAM**: 32.0 GB installed (29.8 GB usable)
- **GPU**: AMD Radeon 780M Graphics (2 GB VRAM) — **iGPU, can accelerate inference via ROCm/Vulkan**
- **Storage**: 954 GB total, 121 GB used (833 GB free) — SSD assumed

## Ollama Models (Local)
| Model | Size | Context | Reasoning | Status |
|-------|------|---------|-----------|--------|
| `qwen2.5:14B` | 9.0 GB | 128K | ❌ | Installed |
| `qwen2.5:14B-64k` | 9.0 GB | 64K | ❌ | Installed |
| `qwen3.6:27B` | 17 GB | 128K | Maybe | Installed (heavy for CPU) |
| `deepseek-r1:8b` | 5.2 GB | 128K | ✅ | **Planned** — native reasoning |

## GPU Acceleration Notes
- **Radeon 780M (RDNA 3, 2GB VRAM)** — supports ROCm (Linux) / DirectML (Windows) / Vulkan
- On Windows: Ollama can use **DirectML** for GPU acceleration (`OLLAMA_DML=1`)
- 2GB VRAM limits model size — but can offload layers for 8B-14B models
- Check: `ollama run --help` for GPU flags, or set `OLLAMA_GPU_LAYERS` env var

## Hermes Profiles
- **obi-wan**: Orchestrator, Nemotron 3 Ultra (OpenRouter free), fallback → local Ollama
- **anakin**: Quant analyst/trading, separate OpenRouter API key

## Network & APIs
- Local Ollama endpoint: `http://localhost:11434/v1` (OpenAI-compatible)
- OpenRouter: Primary cloud provider
- Alpha Vantage / FRED: Market data APIs (keys in 00_Master/secrets.md)

## Performance Expectations (CPU vs GPU)
| Model | CPU-only (est.) | GPU-accelerated (est.) |
|-------|-----------------|------------------------|
| 8B (deepseek-r1:8b) | ~8-12 tok/s | ~20-30 tok/s |
| 14B (qwen2.5:14b) | ~4-6 tok/s | ~12-18 tok/s |
| 27B (qwen3.6:27b) | ~1-2 tok/s | ~5-8 tok/s |

## Recommendation
- Enable GPU acceleration for Ollama: set `OLLAMA_DML=1` (Windows DirectML) or use WSL2 with ROCm
- deepseek-r1:8b (5.2GB) fits in 2GB VRAM with layer offloading — best offline reasoning model
- 32GB RAM + GPU offload = comfortable headroom for 14B models