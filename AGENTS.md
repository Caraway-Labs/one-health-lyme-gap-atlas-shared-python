# Atlas shared-Python instructions

Read the workspace [AGENTS.md](../AGENTS.md), [technology and governance
baseline](../TECHNOLOGY_AND_GOVERNANCE.md), and this repository's `README.md`
before material work. For API or Snowflake boundary changes, also read
[ADR 0002](../docs/adr/0002-public-api-and-snowflake-access.md).

- This repository owns typed shared contracts, deterministic scoring,
  provenance/configuration models, Snowflake connection construction, and
  redacted logging. Do not add FastAPI routes, browser concerns, pipeline
  orchestration, or duplicate consumer-owned API models here.
- Treat exported models and behavior as versioned dependencies of the API and
  data repositories. Preserve backward compatibility by default; coordinate a
  release/version update and downstream compatibility tests before a breaking
  change.
- Keep credentials as secret values and redact them from errors, logs, fixtures,
  and source control. Do not weaken least-privilege connection safeguards.

Run the CI-equivalent checks before handoff:

```powershell
uv sync --extra dev --locked
uv run ruff check .
uv run mypy
uv run pytest -q
uv build
```
