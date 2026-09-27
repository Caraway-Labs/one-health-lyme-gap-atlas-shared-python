# one-health-lyme-gap-atlas-shared-python

Typed shared contracts for the One Health Lyme Gap Atlas API and data loader.

Today this package owns deterministic Alpha scoring, provenance and Snowflake
connection construction, as well as redacted logging and optional OTLP tracing.
The proposed [portable domain boundary](docs/adr/0001-portable-domain-boundary.md)
will let the REST API and MCP consume shared contracts as peer adapters without
pulling persistence into the portable surface. The runtime dependency set is
unchanged in this story.

The new `lyme_gap_atlas_shared.domain` namespace re-exports the existing
portable models and scoring functions, plus strict county FIPS validation.
Its public exports are listed in `domain.__all__`. Existing root imports still
work. This story does not change the package dependency set; infrastructure
isolation is tracked separately.

See the [current export and consumer inventory](docs/shared-surface.md).

```powershell
uv sync --extra dev --locked
uv run ruff check .
uv run mypy
uv run pytest -q
uv build
```
