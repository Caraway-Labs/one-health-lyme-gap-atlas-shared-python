"""Portable, stable Atlas domain surface for peer API and MCP adapters.

Importing this namespace requires only Pydantic. Runtime integration modules
(`settings`, `snowflake`, and `observability`) are deliberately excluded.
"""

from ..models import CountyInputs, Provenance, Score, ScoreSettings
from ..scoring import priority_label, score_color, score_county
from .geography import normalize_county_fips

__all__ = [
    "CountyInputs",
    "Provenance",
    "Score",
    "ScoreSettings",
    "normalize_county_fips",
    "priority_label",
    "score_color",
    "score_county",
]
