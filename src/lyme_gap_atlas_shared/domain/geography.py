"""Canonical county identifier validation; no lookup or inferred geography."""

import re


def normalize_county_fips(value: str) -> str:
    """Return a five-digit county FIPS or reject ambiguous input.

    Leading zeroes are significant. We do not pad, geocode, or infer a county.
    """
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{5}", value) is None:
        raise ValueError("county FIPS must be exactly five ASCII digits")
    return value


__all__ = ["normalize_county_fips"]
