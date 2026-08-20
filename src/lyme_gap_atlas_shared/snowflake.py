"""Snowflake connection construction for local PAT and service key-pair use."""

import base64
from typing import Any

import snowflake.connector
from cryptography.hazmat.primitives import serialization
from snowflake.connector import SnowflakeConnection

from .settings import SnowflakeSettings


def connection_parameters(
    settings: SnowflakeSettings, *, include_database: bool = True
) -> dict[str, Any]:
    parameters: dict[str, Any] = {
        "account": settings.snowflake_account,
        "user": settings.snowflake_user,
        "warehouse": settings.snowflake_warehouse,
        "role": settings.snowflake_role,
        "login_timeout": 15,
        "network_timeout": 30,
        "session_parameters": {"QUERY_TAG": "one-health-lyme-gap-atlas"},
    }
    if include_database:
        parameters["database"] = settings.snowflake_database
    if settings.snowflake_auth_method == "pat":
        if settings.snowflake_pat is None:
            raise ValueError("SNOWFLAKE_PAT is required for PAT authentication")
        # Snowflake's Python connector accepts a PAT in the password field and
        # detects it during standard authentication. Setting the endpoint PAT
        # authenticator instead would make the connector read ``token`` and use
        # the REST endpoint flow rather than the documented connector flow.
        parameters["password"] = settings.snowflake_pat.get_secret_value()
        return parameters

    if settings.snowflake_private_key_b64 is None and settings.snowflake_private_key_path is None:
        raise ValueError(
            "SNOWFLAKE_PRIVATE_KEY_B64 or SNOWFLAKE_PRIVATE_KEY_PATH is required "
            "for key-pair authentication"
        )
    password = (
        settings.snowflake_private_key_passphrase.get_secret_value().encode()
        if settings.snowflake_private_key_passphrase
        else None
    )
    if settings.snowflake_private_key_b64 is not None:
        private_key_bytes = base64.b64decode(settings.snowflake_private_key_b64.get_secret_value())
    else:
        assert settings.snowflake_private_key_path is not None
        private_key_bytes = settings.snowflake_private_key_path.read_bytes()
    key = serialization.load_pem_private_key(private_key_bytes, password=password)
    parameters["private_key"] = key
    parameters["authenticator"] = "SNOWFLAKE_JWT"
    return parameters


def connect(settings: SnowflakeSettings, *, include_database: bool = True) -> SnowflakeConnection:
    """Connect to Snowflake, optionally before the target database exists."""
    return snowflake.connector.connect(
        **connection_parameters(settings, include_database=include_database)
    )
