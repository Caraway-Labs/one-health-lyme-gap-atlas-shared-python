# Shared package versioning and consumer upgrade policy

Use semantic versions for the published package and immutable Git tags.
The source version and tag must match; this release corrects the historical
source/tag mismatch (main declared 0.1.5 while API pinned v0.1.7). Before
tagging, verify `pyproject.toml`, lockfile, built wheel metadata and tag SHA.

- Patch: compatible bug fix without schema, signature, default or dependency
  contract change.
- Minor: additive portable export or compatible field/enum expansion.
- Major: removal of a deprecated import, incompatible model schema or
  serialization, changed scoring semantics, or a required dependency break.
  Version 1.0.0 introduces the base/extra split; consumers that upgrade must
  opt in to runtime extras, even though old import paths remain available.

Preserve existing exports by default. Mark deprecations in module docs and
release notes, provide a replacement and migration period spanning at least
one minor release, and remove only in a coordinated major release after API,
data and MCP consumers have migrated. The Snowflake shims are deprecated as
of 2026-09-26 and will not be removed before 2027-03-26 or before consumers
have migrated. A breaking change needs an ADR,
migration plan, deprecation date, fixture updates and owner review. Public
REST shape changes belong to the API's OpenAPI process, not this package.

Release sequence: verify clean main and consumer pins; update source version
and lockfile; run Ruff, mypy, pytest, base-install import guard and wheel build;
review built metadata; merge reviewed work; tag that exact main commit; then
upgrade API/data/MCP pins in their own repositories with explicit extras and
consumer tests. No downstream pin is changed in this epic.

API/data upgrading from `v0.1.x` must use `one-health-lyme-gap-atlas-shared[snowflake,observability]`
if they use both integration modules (or `[legacy]` temporarily). MCP must use
the base distribution and import only `lyme_gap_atlas_shared.domain`. The
package cannot prevent a separately installed Snowflake driver from being
used by unrelated MCP code; the dependency and import gate enforces the
approved shared-package boundary.
