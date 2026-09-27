# Shared surface and consumer inventory

This is an inventory of the current package and its proposed ownership. The
`lyme_gap_atlas_shared.domain` namespace does not exist yet; Story #23 owns it.
All listed exports below still use their original import paths.

| Existing export | Classification | Ownership and migration |
| --- | --- | --- |
| Root `CountyInputs`, `Score`, `ScoreSettings`, `Provenance`; `models` classes | Portable contract/model | Candidate for `domain`; retain root imports for API |
| Root `score_county`, `priority_label`, `score_color`; `scoring` functions | Pure deterministic domain logic | Candidate for `domain`; retain root imports for API |
| `CountyInputs.fips` five-digit pattern | Validation/normalization | Candidate strict FIPS helper; do not pad or infer geography |
| `observability.redact`, `JsonFormatter`, `configure_logging`, `parse_otlp_headers`, `configure_tracing`, `flush_tracing`, `shutdown_tracing` | Observability/runtime configuration | API/data own runtime setup; optional dependency isolation is later work |
| `settings.SnowflakeSettings` | Infrastructure-specific configuration | API/data must eventually own settings; later isolation must preserve consumers |
| `snowflake.connection_parameters`, `snowflake.connect` | Infrastructure-specific connection | API/data must eventually own construction; later isolation must preserve consumers |

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
dependency set. If later work makes infrastructure dependencies optional,
their next upgrade must select extras explicitly and run their own quality
gates; package-local fixtures will not substitute for consumer CI.

### Classification rule

Put stable Atlas contracts, identifiers, provenance/uncertainty semantics,
validation and pure calculations in the proposed `domain` surface. Keep SQL,
connectors, credentials, Neo4j, routes, MCP tool registration, caching,
deployment and orchestration in their owning services. Do not move API response
models here solely because they resemble domain objects. Cross-consumer
adoption requires an agreed contract and versioned release.
