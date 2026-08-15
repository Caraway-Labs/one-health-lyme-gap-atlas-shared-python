"""Stable cross-repository domain models."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScoreSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    ecological_share: int = Field(default=65, ge=40, le=85)
    low_incidence_breakpoint: int = Field(default=10, ge=5, le=25)
    missing_human_weakness: int = Field(default=75, ge=40, le=90)

    @field_validator("ecological_share", "missing_human_weakness")
    @classmethod
    def multiple_of_five(cls, value: int) -> int:
        if value % 5:
            raise ValueError("must be a multiple of five")
        return value


class CountyInputs(BaseModel):
    model_config = ConfigDict(frozen=True)

    fips: str = Field(pattern=r"^\d{5}$")
    in_contiguous_tick_scope: bool
    human_status: Literal["published_count_floor", "no_county_linked_record"]
    incidence_floor_2023: float | None
    tick_status: Literal["Established", "Reported", "No records"]
    burgdorferi_status: Literal["Present", "No records"]
    svi_percentile: float | None = Field(default=None, ge=0, le=1)
    uninsured_percentile: float | None = Field(default=None, ge=0, le=1)
    rucc_2023: int | None = Field(default=None, ge=1, le=9)


class Score(BaseModel):
    model_config = ConfigDict(frozen=True)

    score: float = Field(ge=0, le=100)
    human_weakness: float = Field(ge=0, le=100)
    ecological: float = Field(ge=0, le=100)
    community: float = Field(ge=0, le=100)
    tick_signal: float = Field(ge=0, le=100)
    pathogen_signal: float = Field(ge=0, le=100)
    svi_signal: float = Field(ge=0, le=100)
    access_signal: float = Field(ge=0, le=100)
    rural_signal: float = Field(ge=0, le=100)


class Provenance(BaseModel):
    model_config = ConfigDict(frozen=True)

    source: str
    source_url: str
    retrieved_at: datetime
    publisher_release: str
    geography: str
    methodology_version: str
    limitations: str

