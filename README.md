# one-health-lyme-gap-atlas-shared-python

Typed shared contracts for the One Health Lyme Gap Atlas API and data loader.

It owns the deterministic Alpha score, provenance/configuration models,
Snowflake connection construction, redacted JSON logging, and optional OTLP
tracing. It intentionally contains no FastAPI routes or pipeline orchestration.

```powershell
uv sync --extra dev
uv run ruff check .
uv run mypy
uv run pytest
```
