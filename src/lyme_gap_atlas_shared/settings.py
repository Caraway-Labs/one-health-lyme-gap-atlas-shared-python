"""Typed settings that never leak secret values in representations."""

from typing import Literal

from pydantic import SecretStr
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
    snowflake_auth_method: Literal["pat", "key_pair"] = "pat"
    snowflake_pat: SecretStr | None = None
    snowflake_private_key_b64: SecretStr | None = None
    snowflake_private_key_passphrase: SecretStr | None = None
