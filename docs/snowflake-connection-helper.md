# Shared Snowflake connection helper: ownership, deprecation and caching

Status: deprecated compatibility module. Scope: `lyme_gap_atlas_shared.snowflake`
and `lyme_gap_atlas_shared.infrastructure.snowflake` (shim and implementation),
with `settings` / `infrastructure.settings` for `SnowflakeSettings`.

Ownership: the shared-Python maintainers own the helper until it is removed.
Each consuming repository owns its own connection construction, credentials,
and connection policy. New Snowflake connection code must not be added to this
package. See [infrastructure-migration.md](infrastructure-migration.md) for the
dependency and extras model, and [versioning.md](versioning.md) for the release
policy.

This document is a plan and inventory. It does not remove the module, change
any default, or authorize a release or pin change.

## Consumer inventory

Inventory taken from `origin/main` at `5cc27b0` on 2026-10-24 by scoped text
search of each sibling repository's `src/` and `scripts/` directories. Consumers
pin released tags, so the pinned versions may not yet contain this list.

| Consumer | Pinned version (per migration doc) | Imports found | Files |
| --- | --- | --- | --- |
| API (`one-health-lyme-gap-atlas-api`) | `v0.1.7` | `settings.SnowflakeSettings`, `snowflake.connect` | `config.py`, `feedback.py`, `knowledge_chat.py`, `dependency_telemetry.py` |
| Data (`one-health-lyme-gap-atlas-data`) | `v0.1.6` | `settings.SnowflakeSettings`, `snowflake.connect` | 26 modules under `src/lyme_gap_atlas_data/` (25 import both; `cli.py` imports settings only; includes `migrations.py`, `ingestion/runtime.py`, `semantic_release.py`, `source_evidence.py`) and 5 files under `scripts/` (`verify_*_dev.py`) |
| Machine-learning | none | none in `src/` or `scripts/` | none |
| Knowledge-graph | none | none in `src/` or `scripts/` | none |
| MCP | none | no shared-python dependency today | none (future adoption: MCP Epic #11 / Story #13, base distribution, `domain` only) |

Notes on the inventory:

- `repository.py` is listed as a `connect` consumer in the migration doc, but
  the current API `main` has no `lyme_gap_atlas_shared` import there. The
  migration doc should be corrected when the API pin is next moved.
- Only `src/` and `scripts/` were searched. Test, notebook, and documentation
  references were not inventoried and must be checked before removal.
- The API's `dependency_telemetry.py` wraps `connect` for telemetry. Removing
  the shim requires that wrapper to move into the API.

## Deprecation and removal plan

Current dates and window, as recorded in [infrastructure-migration.md](infrastructure-migration.md)
and [versioning.md](versioning.md):

- Deprecated as of 2026-09-26.
- Earliest possible removal: 2027-03-26, and only after the criteria below are met.
- Current package source version: `2.0.0`. Removal would be a major release
  (next major, `3.0.0` at the time of writing), as the versioning policy
  requires for removing a deprecated import.

Removal criteria, all of which must hold:

1. API and data `main` branches, and their deployed pins, no longer import
   `lyme_gap_atlas_shared.snowflake`, `lyme_gap_atlas_shared.infrastructure.snowflake`,
   `lyme_gap_atlas_shared.settings`, or `lyme_gap_atlas_shared.infrastructure.settings`.
   Each consumer must show this with its own CI or grep gate, not only with
   shared-python tests.
2. API and data have their own connection construction and settings for their
   runtime and operational paths, and run it in their own CI.
3. At least one minor release has shipped with the deprecation notice in its
   release notes, and the 2027-03-26 date has passed.
4. An ADR records the removal decision, with a migration plan and owner review,
   as [versioning.md](versioning.md) requires for breaking changes.
5. The removal PR removes the shim, the `snowflake` implementation under
   `infrastructure`, and the tests that pin the shim's identity, and updates the
   README, the migration doc, and the consumer inventory above.

Follow-up work (not filed by this PR): a removal Story should be filed only
after criteria 1 and 2 are met. Until then this repository keeps the module.

## Key material caching

`connection_parameters()` and `connect()` keep their behavior. The one change is
that the parsed private key is cached per process:

- Each call still reads the configured key source (base64 setting or file path),
  so a rotated key file or changed passphrase is detected on the next call.
- The cache identity is an HMAC-SHA256 digest of the key bytes and passphrase
  presence and value, under a random 32-byte salt created at import. The salt
  means the stored digest cannot be checked offline against a guessed passphrase.
- Only the loaded key object is stored. The cache holds at most 8 entries and
  evicts the least recently used one.
- Failed parses are not cached, so an invalid key raises on each attempt.
- Nothing about the cache is logged. Raw key bytes, passphrases, and PATs are
  not stored in the cache.

Tests are in `tests/test_snowflake_key_cache.py`. They use a fake loader and a
fake connector, not Snowflake or real key material.

## Network timeout review: `snowflake_network_timeout_seconds = 600`

The default is 600 seconds, with bounds 30 to 1740 (see
`infrastructure/settings.py`). The default is documented here only. It is not
changed.

Context from this review:

- The settings comment says the 600 s value exists because a data MERGE can run
  longer than the connector's short HTTP default while Snowflake keeps executing it.
- API request budgets in the API repository are much shorter. Its public query
  timeout defaults to 15 s (capped at 60 s in settings and at 30 s in
  `cdc_surveillance.py`), its PDF render timeout to 5 s, and its knowledge-graph
  generation timeout to 16 s. Those budgets apply to statements and renders
  that the API sets explicitly.
- The connection-level `network_timeout` applies to the connector's network
  operations. It does not replace the per-statement timeouts the API passes to
  `cursor.execute`. A stalled HTTP call on an API request path can therefore
  hold a request thread far longer than the API's own budget. Connector
  behavior should be verified against the pinned connector version before a
  value is chosen.

Recommendation (document only, no default change):

1. Keep 600 s for data pipeline and administrative consumers, whose long MERGE
   and DDL operations need it.
2. The API should set its own, lower `network_timeout` on connections it
   constructs, once it owns construction (its own settings). A candidate to
   evaluate is 60 s, to be validated against the API's request budgets and the
   connector's behavior. It is not measured here.
3. Do not change the shared default without written agreement from the API and
   data owners, because changing it would change data-pipeline behavior.

## Open items

- Correct the `repository.py` entry in the migration doc at the next API pin change.
- Record the API and data owners' agreement on the timeout recommendation.
- File the removal Story only after criteria 1 and 2 hold.
