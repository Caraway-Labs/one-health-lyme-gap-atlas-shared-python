"""API-style and prospective MCP-style portable contract fixtures."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from lyme_gap_atlas_shared import CountyInputs as LegacyCountyInputs
from lyme_gap_atlas_shared.domain import (
    CountyInputs,
    Provenance,
    ScoreSettings,
    normalize_county_fips,
    priority_label,
    score_county,
)


def test_api_legacy_and_domain_exports_share_identity() -> None:
    assert LegacyCountyInputs is CountyInputs
    assert ScoreSettings().model_dump() == {
        "ecological_share": 65,
        "low_incidence_breakpoint": 10,
        "missing_human_weakness": 75,
    }


def test_prospective_mcp_style_json_round_trip_and_pure_scoring() -> None:
    payload = {
        "fips": "08001",
        "in_contiguous_tick_scope": True,
        "human_status": "no_county_linked_record",
        "incidence_floor_2023": None,
        "tick_status": "Unknown",
        "burgdorferi_status": "Unknown",
    }
    county = CountyInputs.model_validate_json(
        CountyInputs.model_validate(payload).model_dump_json()
    )
    assert county.fips == normalize_county_fips(payload["fips"])
    result = score_county(county, ScoreSettings())
    assert result == score_county(county, ScoreSettings())
    assert result.tick_signal == 0
    assert result.pathogen_signal == 0
    assert priority_label(result.score)


def test_provenance_round_trip_and_invalid_contracts() -> None:
    provenance = Provenance(
        source="publisher",
        source_url="https://example.org/source",
        retrieved_at=datetime(2026, 1, 2, tzinfo=UTC),
        publisher_release="2025",
        geography="county 08001",
        methodology_version="alpha-v1",
        limitations="coverage is incomplete",
    )
    assert Provenance.model_validate_json(provenance.model_dump_json()) == provenance
    with pytest.raises(ValidationError):
        CountyInputs.model_validate({"fips": "801", "tick_status": "missing"})
    for value in ("801", " 08001", "08001 ", "0800A", "080010"):
        with pytest.raises(ValueError, match="five ASCII digits"):
            normalize_county_fips(value)
