"""Typed settings that never leak secret values in representations."""

from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SnowflakeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    snowflake_account: str = ""
    snowflake_user: str = ""
    snowflake_warehouse: str = "COMPUTE_WH"
    snowflake_role: str = ""
    snowflake_database: str = "ONE_HEALTH_LYME_GAP_ATLAS"
    snowflake_landing_schema: str = "LANDING"
    snowflake_presentation_schema: str = "PRESENTATION"
    # A MERGE can legitimately take longer than the connector's short HTTP
    # request default while Snowflake continues to execute it. Keep this
    # bounded below the platform job budget, but make it configurable per
    # environment rather than cancelling the statement from the client.
    snowflake_network_timeout_seconds: Annotated[int, Field(ge=30, le=1740)] = 600
    snowflake_auth_method: Literal["pat", "key_pair"] = "pat"
    snowflake_pat: SecretStr | None = None
    snowflake_private_key_b64: SecretStr | None = None
    snowflake_private_key_path: Path | None = None
    snowflake_private_key_passphrase: SecretStr | None = None
