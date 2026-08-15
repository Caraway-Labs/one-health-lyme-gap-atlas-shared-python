"""Snowflake connection construction for local PAT and service key-pair use."""

import base64
from typing import Any

import snowflake.connector
from cryptography.hazmat.primitives import serialization
from snowflake.connector import SnowflakeConnection

from .settings import SnowflakeSettings


def connection_parameters(settings: SnowflakeSettings) -> dict[str, Any]:
    parameters: dict[str, Any] = {
        "account": settings.snowflake_account,
        "user": settings.snowflake_user,
        "warehouse": settings.snowflake_warehouse,
        "role": settings.snowflake_role,
        "database": settings.snowflake_database,
        "login_timeout": 15,
        "network_timeout": 30,
        "session_parameters": {"QUERY_TAG": "one-health-lyme-gap-atlas"},
    }
    if settings.snowflake_auth_method == "pat":
        if settings.snowflake_pat is None:
            raise ValueError("SNOWFLAKE_PAT is required for PAT authentication")
        parameters.update(
            authenticator="PROGRAMMATIC_ACCESS_TOKEN",
            password=settings.snowflake_pat.get_secret_value(),
        )
        return parameters

    if settings.snowflake_private_key_b64 is None:
        raise ValueError("SNOWFLAKE_PRIVATE_KEY_B64 is required for key-pair authentication")
    password = (
        settings.snowflake_private_key_passphrase.get_secret_value().encode()
        if settings.snowflake_private_key_passphrase
        else None
    )
    key = serialization.load_pem_private_key(
        base64.b64decode(settings.snowflake_private_key_b64.get_secret_value()),
        password=password,
    )
    parameters["private_key"] = key
    parameters["authenticator"] = "SNOWFLAKE_JWT"
    return parameters


def connect(settings: SnowflakeSettings) -> SnowflakeConnection:
    return snowflake.connector.connect(**connection_parameters(settings))

