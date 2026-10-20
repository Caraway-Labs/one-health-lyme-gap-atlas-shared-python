"""Approved k50 numerical oracle and immutable research-snapshot regression."""

import csv
import math
from pathlib import Path

import pytest
from pydantic import ValidationError

from lyme_gap_atlas_shared.domain import CountyInputs, ScoreSettings, score_color, score_county
from lyme_gap_atlas_shared.models import LegacyScoreSettings


def county(incidence: float | None) -> CountyInputs:
    return CountyInputs(
        fips="36027",
        in_contiguous_tick_scope=True,
        human_status="published_count_floor",
        incidence_floor_2023=incidence,
        tick_status="Established",
        burgdorferi_status="Present",
        svi_percentile=0.5,
        uninsured_percentile=0.5,
        rucc_2023=5,
    )


@pytest.mark.parametrize("incidence", [0, 5, 9.9, 10, 10.1, 25, 50, 100, 200, 700, 1640])
@pytest.mark.parametrize("context", [0.0, 0.5, 1.0])
def test_numerical_vectors(incidence: float, context: float) -> None:
    record = county(incidence).model_copy(
        update={
            "svi_percentile": context,
            "uninsured_percentile": context,
            "rucc_2023": 1 if context == 0 else 9,
        }
    )
    result = score_county(record, ScoreSettings())
    expected_h = 100.0 / (1.0 + incidence / 50.0)
    community = 80 * context + (0 if context == 0 else 20)
    assert result.score == round(expected_h * (65 + 0.35 * community) / 100, 1)
    assert result.human_weakness == round(expected_h, 1)
    assert 0 <= result.score <= 100


@pytest.mark.parametrize("value", [-1, math.inf, -math.inf, math.nan])
def test_invalid_incidence(value: float) -> None:
    with pytest.raises(ValidationError):
        county(value)


def test_missing_zero_legacy_and_breakpoint_rejection() -> None:
    assert score_county(county(None), ScoreSettings()).human_weakness == 75
    assert score_county(county(0), ScoreSettings()).human_weakness == 100
    absent = county(100).model_copy(update={"human_status": "no_county_linked_record"})
    assert score_county(absent, ScoreSettings()).human_weakness == 75
    assert score_county(county(10), LegacyScoreSettings()).score == 0
    assert score_county(county(10), ScoreSettings()).score > 0
    with pytest.raises(ValidationError, match="Extra inputs"):
        ScoreSettings.model_validate({"low_incidence_breakpoint": 10})


def test_exact_research_snapshot() -> None:
    path = Path(__file__).parent / "fixtures/gap-score-v11-k50.csv"
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3144
    computed = []
    for row in rows:
        record = CountyInputs(
            fips=row["fips"],
            in_contiguous_tick_scope=row["in_contiguous_tick_scope"] == "True",
            human_status=row["human_status"],
            incidence_floor_2023=float(row["incidence_floor_2023"])
            if row["incidence_floor_2023"]
            else None,
            tick_status=row["tick_status"],
            burgdorferi_status=row["burgdorferi_status"],
            svi_percentile=float(row["svi_percentile"]) if row["svi_percentile"] else None,
            uninsured_percentile=float(row["uninsured_percentile"])
            if row["uninsured_percentile"]
            else None,
            rucc_2023=int(row["rucc_2023"]) if row["rucc_2023"] else None,
        )
        result = score_county(record, ScoreSettings())
        if not record.in_contiguous_tick_scope:
            assert row["score"] == ""
            continue
        assert result.score == float(row["score"]), row["fips"]
        assert result.human_weakness == round(float(row["human"]), 1), row["fips"]
        assert result.ecological == round(float(row["ecological"]), 1)
        assert result.community == pytest.approx(float(row["community"]), abs=0.051)
        computed.append((record, result, row))
    eligible = sorted(
        (r for r in computed if r[0].in_contiguous_tick_scope),
        key=lambda r: (-r[1].score, r[0].fips),
    )
    for rank, (_, result, row) in enumerate(eligible, 1):
        assert rank == int(row["national_rank"])
        assert score_color(result.score) in {
            "#a9d2db",
            "#55a8a3",
            "#87b982",
            "#efc64a",
            "#f49a32",
            "#e9602b",
        }
