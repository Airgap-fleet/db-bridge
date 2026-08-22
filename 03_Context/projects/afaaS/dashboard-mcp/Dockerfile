FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY pyproject.toml uv.lock* ./
RUN pip install --no-cache-dir uv && uv sync --frozen

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD uv run python -c "import dashboard_mcp; print('Dashboard MCP Server is running')" || exit 1

# Default command
CMD ["uv", "run", "dashboard-mcp"]