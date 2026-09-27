# Shared surface and consumer inventory

This is an inventory of the current package and its ownership. Story #23 adds
`lyme_gap_atlas_shared.domain` as a portable import surface. Existing root
imports remain available and retain object identity. Runtime integration
dependencies are opt-in extras from Story #24 onward. The source version is
not changed until Story #25; consumers stay on their pinned tags meanwhile.

| Existing export | Classification | Ownership and migration |
| --- | --- | --- |
| Root `CountyInputs`, `Score`, `ScoreSettings`, `Provenance`; `models` classes | Portable contract/model | Also exported by `domain`; retain root imports for API |
| Root `score_county`, `priority_label`, `score_color`; `scoring` functions | Pure deterministic domain logic | Also exported by `domain`; retain root imports for API |
| `domain.normalize_county_fips`; `CountyInputs.fips` pattern | Validation/normalization | Strict five ASCII digits in helper; no padding or geographic inference |
| `observability.redact`, `JsonFormatter`, `configure_logging`, `parse_otlp_headers`, `configure_tracing`, `flush_tracing`, `shutdown_tracing` | Observability/runtime configuration | Explicit `observability` extra; API/data own runtime setup |
| `settings.SnowflakeSettings` | Infrastructure-specific configuration | Deprecated shim to `infrastructure.settings`; API/data must eventually own settings |
| `snowflake.connection_parameters`, `snowflake.connect` | Infrastructure-specific connection | Deprecated shims to `infrastructure.snowflake`; API/data must eventually own construction |

No current shared export is a consumer-specific route or DTO. `Score` and
`ScoreSettings` are already reused by the API. Its public `CountyDetail`,
`CountyScoreSummary`, and response wrappers are API-specific because they
encode OpenAPI and serving behavior. API profile, privacy, and report models
also remain API-owned. API county FIPS patterns and report FIPS validation are
near-duplicates of the shared `CountyInputs.fips` rule, but their request and
response schemas remain API-owned until a coordinated contract change. MCP's
current system-tool request/response shapes are transport-specific; no reusable
Atlas domain DTO was identified there. No MCP import or dependency on
shared-python was found at the time of this inventory. Later MCP compatibility
fixtures can describe an intended adoption shape; they cannot claim live MCP
integration.

Current consumers: API pins `v0.1.7` and imports root models/scoring,
`observability`, `settings.SnowflakeSettings`, and `snowflake.connect`.
Data pins `v0.1.6` and imports settings/connection helpers across ingestion,
migrations, verification and CLI modules, plus observability in its CLI.
Neither repository is edited by this epic. Their existing tags keep the prior
dependency set. Their next upgrade must select extras explicitly and run their own quality
gates; package-local fixtures will not substitute for consumer CI.

### Classification rule

Put stable Atlas contracts, identifiers, provenance/uncertainty semantics,
validation and pure calculations in the `domain` surface. Keep SQL,
connectors, credentials, Neo4j, routes, MCP tool registration, caching,
deployment and orchestration in their owning services. Do not move API response
models here solely because they resemble domain objects. Cross-consumer
adoption requires an agreed contract and versioned release.
