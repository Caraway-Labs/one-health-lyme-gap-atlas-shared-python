from lyme_gap_atlas_shared import CountyInputs, ScoreSettings, priority_label, score_county


def test_alpha_scoring_and_missing_human_semantics() -> None:
    county = CountyInputs(
        fips="08001",
        in_contiguous_tick_scope=True,
        human_status="no_county_linked_record",
        incidence_floor_2023=None,
        tick_status="Established",
        burgdorferi_status="Present",
        svi_percentile=0.5,
        uninsured_percentile=0.5,
        rucc_2023=5,
    )
    score = score_county(county, ScoreSettings())
    assert score.human_weakness == 75
    assert score.ecological == 100
    assert score.community == 50
    assert score.score == 61.9
    assert priority_label(score.score) == "Priority 2 — Review"


def test_published_incidence_uses_breakpoint() -> None:
    county = CountyInputs(
        fips="06037",
        in_contiguous_tick_scope=True,
        human_status="published_count_floor",
        incidence_floor_2023=10,
        tick_status="No records",
        burgdorferi_status="No records",
    )
    assert score_county(county, ScoreSettings()).human_weakness == 0

