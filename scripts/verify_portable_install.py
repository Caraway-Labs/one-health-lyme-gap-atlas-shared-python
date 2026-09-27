"""Run with a fresh base-only wheel installation, outside the dev environment."""

import importlib.metadata
import importlib.util
import sys

from lyme_gap_atlas_shared.domain import (
    CountyInputs,
    Provenance,
    Score,
    ScoreSettings,
    normalize_county_fips,
    score_county,
)

assert importlib.metadata.version("one-health-lyme-gap-atlas-shared") == "1.0.0"
assert normalize_county_fips("08001") == "08001"
county = CountyInputs(
    fips="08001",
    in_contiguous_tick_scope=True,
    human_status="no_county_linked_record",
    incidence_floor_2023=None,
    tick_status="Unknown",
    burgdorferi_status="Unknown",
)
assert Score.model_validate_json(score_county(county, ScoreSettings()).model_dump_json())
assert Provenance.model_fields["source"].is_required()

excluded = ("snowflake", "pydantic_settings", "opentelemetry", "neo4j")
for name in excluded:
    assert importlib.util.find_spec(name) is None, f"{name} present in base installation"
    assert not any(module == name or module.startswith(name + ".") for module in sys.modules)
assert "lyme_gap_atlas_shared.infrastructure" not in sys.modules

print("Portable base-wheel isolation passed")
