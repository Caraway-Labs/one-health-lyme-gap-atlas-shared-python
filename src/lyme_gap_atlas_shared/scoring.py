"""Authoritative deterministic Alpha scoring implementation."""

from .models import CountyInputs, Score, ScoreSettings


def _clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return min(maximum, max(minimum, value))


def score_county(county: CountyInputs, settings: ScoreSettings) -> Score:
    if county.human_status == "published_count_floor" and county.incidence_floor_2023 is not None:
        human = 100 * _clamp(
            1 - county.incidence_floor_2023 / settings.low_incidence_breakpoint, 0, 1
        )
    else:
        human = float(settings.missing_human_weakness)

    tick_signal = {"Established": 100.0, "Reported": 55.0, "No records": 0.0}[
        county.tick_status
    ]
    pathogen_signal = 100.0 if county.burgdorferi_status == "Present" else 0.0
    ecological = 0.6 * tick_signal + 0.4 * pathogen_signal

    svi_signal = (county.svi_percentile or 0) * 100
    access_signal = (county.uninsured_percentile or 0) * 100
    rural_signal = _clamp(((county.rucc_2023 or 1) - 1) / 8 * 100)
    community = 0.5 * svi_signal + 0.3 * access_signal + 0.2 * rural_signal

    ecological_share = settings.ecological_share / 100
    score = human * (ecological_share * ecological + (1 - ecological_share) * community) / 100
    return Score(
        score=round(score, 1),
        human_weakness=round(human, 1),
        ecological=round(ecological, 1),
        community=round(community, 1),
        tick_signal=tick_signal,
        pathogen_signal=pathogen_signal,
        svi_signal=round(svi_signal, 1),
        access_signal=round(access_signal, 1),
        rural_signal=round(rural_signal, 1),
    )


def priority_label(score: float) -> str:
    if score >= 70:
        return "Priority 1 — Investigate"
    if score >= 50:
        return "Priority 2 — Review"
    if score >= 30:
        return "Watch — Monitor signals"
    return "Lower Atlas priority — Not a safety finding"


def score_color(score: float, in_scope: bool = True) -> str:
    if not in_scope:
        return "#e4e9ea"
    if score >= 75:
        return "#e9602b"
    if score >= 65:
        return "#f49a32"
    if score >= 50:
        return "#efc64a"
    if score >= 35:
        return "#87b982"
    if score >= 20:
        return "#55a8a3"
    return "#a9d2db"

