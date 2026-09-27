# 0001: Portable Atlas Domain Boundary

Status: Accepted
Date: 2026-09-26
Decision owner: Atlas shared Python maintainers and product engineering leads

## Context

The REST API and data loader consume shared contracts and Snowflake connection
helpers. MCP is a peer adapter that needs reusable domain semantics without
acquiring persistence capabilities. Before Stories #23 and #24, the base
dependency set installed the Snowflake connector and OTLP runtime for every
consumer. Owner merge of PR #27 approved this decision; Stories #23 and #24
implemented its namespace and dependency boundary.

## Decision

REST and MCP are peer interface adapters. The
`lyme_gap_atlas_shared.domain` surface exposes contracts, validation and
pure deterministic calculations. Shared Python may know the Atlas domain, but
its portable surface must not know where Atlas data lives. The base runtime
dependency is Pydantic only. Infrastructure modules are isolated behind
explicit extras while old `settings` and `snowflake` import paths remain
deprecated migration shims.

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

The ADR itself changed no runtime behavior in Story #22. Subsequent stories
added the portable namespace and isolated infrastructure dependencies. Import,
serialization, and base-install gates enforce the boundary. Existing API/data
pins remain functional. Any future
upgrade that requires explicit extras must be coordinated with consumer tests.
MCP adoption will occur in its own repository, not in this story.

## Alternatives considered

Moving helpers immediately to API/data would break many pinned imports and
requires coordinated consumer changes outside this epic. Keeping all drivers
in the base package would expose persistence to MCP. A new service or repo is
unnecessary. An optional isolated namespace with deprecated shims gives
consumers a bounded migration path.

## Acceptance criteria

- The current exports and consumers are inventoried and classified.
- Allowed dependency direction and excluded runtime concerns are documented.
- Story #22 changed no runtime modules, dependencies or behavior.
- Stories #23–#25 verify portable imports, legacy safeguards and fixtures.

## Rollout, observability, and rollback

The source version advances to 1.0.0 for the breaking base dependency
contract: consumers upgrading from 0.x must explicitly request infrastructure
extras. Tagging or publishing requires a separate authorized release task.
API/data retain earlier pins until their own tested upgrades; MCP adopts
the portable base in its own epic. Keep old Snowflake paths until coordinated
migration and a later removal decision.

## Links to affected contracts and tests

- `docs/shared-surface.md`
- `tests/test_domain_contract.py` and `tests/test_architecture.py`
- `docs/infrastructure-migration.md` and `docs/versioning.md`
- Workspace ADR 0002: public API and Snowflake access
