# one-health-lyme-gap-atlas-shared-python

Typed shared contracts for the One Health Lyme Gap Atlas API and data loader.

Today this package owns deterministic Alpha scoring, provenance and Snowflake
connection construction, as well as redacted logging and optional OTLP tracing.
The proposed [portable domain boundary](docs/adr/0001-portable-domain-boundary.md)
will let the REST API and MCP consume shared contracts as peer adapters without
pulling persistence into the portable surface. This documentation change does
not alter the current runtime modules or dependencies.

See the [current export and consumer inventory](docs/shared-surface.md).

```powershell
uv sync --extra dev --locked
uv run ruff check .
uv run mypy
uv run pytest -q
uv build
```
