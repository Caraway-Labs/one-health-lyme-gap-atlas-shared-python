# Infrastructure migration from shared Python

The portable consumer import is `lyme_gap_atlas_shared.domain`. It does not
import settings, connectors, tracing, credentials, SQL, or runtime services.
The base distribution requires Pydantic only. Snowflake and observability
dependencies are optional and must be explicitly requested. An MCP consumer
that installs only the base distribution cannot import the Snowflake helper
through its approved dependency; it must not request the infrastructure extras.

## Current consumers and target ownership

API pins `v0.1.7`. It imports `SnowflakeSettings` from `settings` in `config`,
`feedback`, and `knowledge_chat`; `connect` from `snowflake` in `feedback`,
`knowledge_chat`, and `repository`; and logging/tracing functions in `app`.
It also imports root score models and functions. The API owns its server-side
Snowflake runtime, connection policy, and future replacement settings.

Data pins `v0.1.6`. Its ingestion, migrations, registration, release,
verification scripts, and other operational modules import `SnowflakeSettings`
from `settings` and `connect` from `snowflake`; its CLI imports shared
logging/tracing. The data repository owns its pipeline and administrative
Snowflake connections and future replacement settings.

MCP has no shared-python dependency or import today. Its future domain
adoption belongs to MCP Epic #11 / Story #13, not this repository. No live
MCP compatibility is claimed here.

## Compatibility path

`settings.SnowflakeSettings` and `snowflake.connect` /
`snowflake.connection_parameters` are deprecated import shims to the
`infrastructure` namespace. They preserve the current object identities,
PAT connector password flow, key-pair loading, network timeout bounds, query
tag, and optional database selection. The implementation remains isolated
until the owning API/data repositories migrate; this story does not copy the
connection code into either consumer.

The old v0.1.x pins continue to use their immutable tags. At a coordinated
future upgrade, API/data must request `snowflake` and `observability` extras
(or the temporary `legacy` extra), update their lockfiles, and run their own
CI. The shared-package tests and targeted source-overridden consumer tests
cannot substitute for that upgrade evidence. Keep the old pins if an upgrade
fails; do not remove the shims before a reviewed major removal decision.

The shims are deprecated as of 2026-09-26. Their earliest possible removal is
2027-03-26, subject to completed consumer migration and a separate reviewed
decision. No package release or downstream pin change occurs in Story #24.
