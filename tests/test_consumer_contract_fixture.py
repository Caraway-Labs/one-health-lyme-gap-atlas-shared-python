"""Frozen shared-domain wire format for API and prospective MCP adapters."""

import json
from pathlib import Path

import lyme_gap_atlas_shared as legacy
import lyme_gap_atlas_shared.domain as domain
from lyme_gap_atlas_shared import CountyInputs as LegacyCountyInputs
from lyme_gap_atlas_shared import Score as LegacyScore
from lyme_gap_atlas_shared.domain import (
    CountyInputs,
    Provenance,
    Score,
    ScoreSettings,
    normalize_county_fips,
    score_county,
)


def test_public_portable_export_compatibility() -> None:
    assert set(domain.__all__) == {
        "CountyInputs", "Provenance", "Score", "ScoreSettings",
        "normalize_county_fips", "priority_label", "score_color", "score_county",
    }
    for name in set(domain.__all__) - {"normalize_county_fips"}:
        assert getattr(domain, name) is getattr(legacy, name)


def test_api_and_prospective_mcp_contract_fixture() -> None:
    fixture = json.loads(
        (Path(__file__).parent / "fixtures" / "portable_contract_v1.json").read_text(
            encoding="utf-8"
        )
    )
    assert CountyInputs is LegacyCountyInputs
    assert Score is LegacyScore

    county = CountyInputs.model_validate(fixture["county_inputs"])
    settings = ScoreSettings.model_validate(fixture["score_settings"])
    assert county.model_dump(mode="json") == fixture["county_inputs"]
    assert settings.model_dump(mode="json") == fixture["score_settings"]
    assert normalize_county_fips(county.fips) == county.fips

    score = score_county(county, settings)
    assert score.model_dump(mode="json") == fixture["score"]
    assert Score.model_validate_json(score.model_dump_json()) == score

    provenance = Provenance.model_validate(fixture["provenance"])
    assert provenance.model_dump(mode="json") == fixture["provenance"]
    assert Provenance.model_validate_json(provenance.model_dump_json()) == provenance
