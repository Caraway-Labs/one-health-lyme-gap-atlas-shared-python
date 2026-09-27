# one-health-lyme-gap-atlas-shared-python

Portable, versioned Atlas domain contracts and deterministic logic for peer
REST API and MCP adapters.

Import `lyme_gap_atlas_shared.domain` for models, validation and scoring. The
base installation requires only Pydantic and cannot import Snowflake. Legacy
Snowflake settings/connection construction is isolated behind the `snowflake`
extra and deprecated import shims; existing API/data consumers must request
that extra when upgrading. Logging and OTLP tracing require the `observability`
extra. No FastAPI routes, MCP transport or pipeline orchestration live here.

See [the ADR](docs/adr/0001-portable-domain-boundary.md),
[surface inventory](docs/shared-surface.md), and [release policy](docs/versioning.md).

```powershell
uv sync --extra dev --extra legacy --locked
uv run ruff check .
uv run mypy
uv run pytest -q
uv build
```
