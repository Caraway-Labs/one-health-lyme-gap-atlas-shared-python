# 0001: Portable Atlas Domain Boundary

Status: Accepted
Date: 2026-09-26
Decision owner: Atlas shared Python maintainers and product engineering leads

## Context

The REST API and data loader consume shared contracts and Snowflake connection
helpers. MCP is a peer adapter that needs reusable domain semantics without
acquiring persistence capabilities. The previous base dependency set installed
the Snowflake connector and OTLP runtime for every consumer.

## Decision

REST and MCP are peer interface adapters. Both may import
`lyme_gap_atlas_shared.domain`, which exposes contracts, validation and pure
deterministic calculations. Shared Python may know the Atlas domain, but its
portable surface must not know where Atlas data lives. Only Pydantic is a base
runtime dependency. Infrastructure modules are under `infrastructure` and
require explicit optional extras. Old `settings` and `snowflake` import paths
remain deprecated compatibility shims during migration.

Dependency direction is adapter -> domain. An adapter owns its transport,
credentials, persistence, cache, deployment configuration and runtime
orchestration. HTTP from MCP to REST is appropriate at a genuine service
boundary, but is not needed just to call stable pure Python logic. There is no
new deployed service or repository.

Good shared additions include an evidence DTO with source and methodology,
strict county identifier validation, or deterministic scoring with explicit
inputs. A Snowflake query wrapper, Neo4j client, FastAPI route, MCP tool,
service cache, or hidden API client does not belong in the domain namespace.
API-specific public response models remain owned by API and its OpenAPI
contract; only independently useful, agreed domain concepts move here.

## Consequences

New MCP consumers install the base package and import `domain`. Existing API
and data pins remain functional. When they adopt this release, API/data must
request the `snowflake` and, if used, `observability` extras, or the temporary
`legacy` extra. This opt-in is intentional and must be coordinated with their
own dependency updates. The old Snowflake paths remain until a major release.
No Snowflake or Neo4j driver is pulled in by a base installation. Import
guards and serialization fixtures enforce the boundary.

## Alternatives considered

Moving helpers immediately to API/data would break many pinned imports and
requires coordinated consumer changes outside this epic. Keeping all drivers
in the base package would expose persistence to MCP. A new service or repo is
unnecessary. An optional isolated namespace with deprecated shims gives
consumers a bounded migration path.

## Acceptance criteria

- Base dependency and `domain` import have no persistence or telemetry runtime.
- Existing model and scoring imports preserve identity and behavior.
- Legacy connection construction keeps PAT/key-pair safeguards and requires
  explicit `snowflake` extra when upgrading.
- Tests cover API/MCP style contracts, deterministic logic, and import guards.

## Rollout, observability, and rollback

Publish a new minor version after green checks. Migrate API/data pins with
explicit extras and their own tests; MCP adopts base only. If a consumer
upgrade fails, retain its earlier pinned tag while correcting its dependency
declaration. Do not remove deprecated paths before a coordinated major release.

## Links to affected contracts and tests

- `docs/shared-surface.md`
- `docs/versioning.md`
- `tests/test_domain_contract.py`
- `tests/test_architecture.py`
- Workspace ADR 0002: public API and Snowflake access
