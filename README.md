# one-health-lyme-gap-atlas-shared-python

Typed shared contracts for the One Health Lyme Gap Atlas API and data loader.

Today this package owns deterministic Alpha scoring, provenance and Snowflake
connection construction, as well as redacted logging and optional OTLP tracing.
The [portable domain boundary](docs/adr/0001-portable-domain-boundary.md)
lets the REST API and future MCP consumers use shared contracts as peer adapters without
pulling persistence into the portable surface. The runtime dependency set is
split into explicit extras: the base distribution now requires only Pydantic.

The new `lyme_gap_atlas_shared.domain` namespace re-exports the existing
portable models and scoring functions, plus strict county FIPS validation.
Its public exports are listed in `domain.__all__`. Existing root imports still
work. Snowflake settings and connection helpers are isolated under
`infrastructure` and require the `snowflake` extra. Their old import paths are
deprecated compatibility shims. Logging and tracing require `observability`;
the temporary `legacy` extra installs both sets for API/data migration.

See the [current export and consumer inventory](docs/shared-surface.md) and
[infrastructure migration guide](docs/infrastructure-migration.md). The
[versioning policy](docs/versioning.md) explains why source version 1.0.0 is
a major dependency-contract change and how consumers upgrade.

```powershell
uv sync --extra dev --extra legacy --locked
uv run ruff check .
uv run mypy
uv run pytest -q
uv build
```
