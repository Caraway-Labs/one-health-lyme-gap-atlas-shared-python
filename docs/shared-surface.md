# Shared surface and consumer inventory

The portable public API is `lyme_gap_atlas_shared.domain`. The root exports
below remain supported aliases for existing API callers. Modules not listed as
portable are runtime integrations and are not part of MCP's approved surface.

| Existing export | Classification | Ownership and migration |
| --- | --- | --- |
| Root `CountyInputs`, `Score`, `ScoreSettings`, `Provenance`; `models` classes | Portable contract/model | Also exported by `domain`; retain root imports for API |
| Root `score_county`, `priority_label`, `score_color`; `scoring` functions | Pure deterministic domain logic | Also exported by `domain`; retain root imports for API |
| `domain.normalize_county_fips` | Validation/normalization | Strict five ASCII digits; no padding or geographic inference |
| `observability.redact`, `JsonFormatter`, `configure_logging`, `parse_otlp_headers`, `configure_tracing`, `flush_tracing`, `shutdown_tracing` | Observability/runtime configuration | Optional `observability` extra; API/data own runtime setup; no domain import |
| `settings.SnowflakeSettings` | Infrastructure-specific configuration | Deprecated shim to `infrastructure.settings`; API/data must eventually own settings |
| `snowflake.connection_parameters`, `snowflake.connect` | Infrastructure-specific connection | Deprecated shims to `infrastructure.snowflake`; API/data must eventually own connection construction |

No current shared export is a consumer-specific route or DTO. `Score` and
`ScoreSettings` are already reused by the API. Its public `CountyDetail`,
`CountyScoreSummary`, and response wrappers are API-specific because they
encode OpenAPI and serving behavior. API profile, privacy, and report models
also remain API-owned. No MCP import or dependency on shared-python was found
at the time of this decision; MCP compatibility fixtures describe the intended
adoption shape rather than claiming a live MCP integration.

Current consumers: API pins `v0.1.7` and imports root models/scoring,
`observability`, `settings.SnowflakeSettings`, and `snowflake.connect`.
Data pins `v0.1.6` and imports settings/connection helpers across ingestion,
migrations, verification and CLI modules, plus observability in its CLI.
Neither repository is edited by this epic. Their existing tags keep the prior
dependency set. Their next upgrade must select extras explicitly and run their
own quality gates; the shared-package tests cover import compatibility and
wire-format samples but are not a substitute for consumer CI.

### Classification rule

Put stable Atlas contracts, identifiers, provenance/uncertainty semantics,
validation and pure calculations in `domain`. Keep SQL, connectors, credentials,
Neo4j, routes, MCP tool registration, caching, deployment and orchestration in
their owning services. Do not move API response models here solely because
they resemble domain objects. Cross-consumer adoption requires an agreed
contract and versioned release.
