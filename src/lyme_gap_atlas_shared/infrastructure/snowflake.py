"""Deprecated infrastructure-only Snowflake connection compatibility module.

Install the ``snowflake`` extra. This module is excluded from the portable
``domain`` namespace and will be removed only in a coordinated major release.
Consumer inventory, removal criteria and the network-timeout review are in
``docs/snowflake-connection-helper.md``.
"""

import base64
import hmac
import secrets
import threading
from collections import OrderedDict
from typing import Any

import snowflake.connector
from cryptography.hazmat.primitives import serialization
from snowflake.connector import SnowflakeConnection

from .settings import SnowflakeSettings

# Parsed private keys are cached per process so repeated connect() calls do not
# re-parse PEM material. Cache identities are HMAC-SHA256 digests of the key
# bytes and passphrase under a random per-process salt: a changed key or
# passphrase produces a new identity and is reloaded, and the digest cannot be
# checked offline against a guessed passphrase. Only the loaded key object is
# stored; raw key bytes and passphrases are never retained by the cache.
_KEY_CACHE_MAX_ENTRIES = 8
_key_cache_salt = secrets.token_bytes(32)
_key_cache: OrderedDict[str, Any] = OrderedDict()
_key_cache_lock = threading.Lock()


def _private_key_cache_id(private_key_bytes: bytes, password: bytes | None) -> str:
    mac = hmac.new(_key_cache_salt, digestmod="sha256")
    mac.update(len(private_key_bytes).to_bytes(8, "big"))
    mac.update(private_key_bytes)
    mac.update(b"\x00" if password is None else b"\x01" + password)
    return mac.hexdigest()


def _load_private_key(private_key_bytes: bytes, password: bytes | None) -> Any:
    """Return the parsed key, parsing at most once per distinct key material.

    Failed loads are not cached, so an invalid key raises on every attempt.
    """
    cache_id = _private_key_cache_id(private_key_bytes, password)
    with _key_cache_lock:
        cached = _key_cache.get(cache_id)
        if cached is not None:
            _key_cache.move_to_end(cache_id)
            return cached
    key = serialization.load_pem_private_key(private_key_bytes, password=password)
    with _key_cache_lock:
        _key_cache[cache_id] = key
        _key_cache.move_to_end(cache_id)
        while len(_key_cache) > _KEY_CACHE_MAX_ENTRIES:
            _key_cache.popitem(last=False)
    return key


def _clear_private_key_cache() -> None:
    """Drop cached key objects. Intended for tests and key-rotation tooling."""
    with _key_cache_lock:
        _key_cache.clear()


def connection_parameters(
    settings: SnowflakeSettings, *, include_database: bool = True
) -> dict[str, Any]:
    parameters: dict[str, Any] = {
        "account": settings.snowflake_account,
        "user": settings.snowflake_user,
        "warehouse": settings.snowflake_warehouse,
        "role": settings.snowflake_role,
        "login_timeout": 15,
        "network_timeout": settings.snowflake_network_timeout_seconds,
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
    parameters["private_key"] = _load_private_key(private_key_bytes, password)
    parameters["authenticator"] = "SNOWFLAKE_JWT"
    return parameters


def connect(settings: SnowflakeSettings, *, include_database: bool = True) -> SnowflakeConnection:
    """Connect to Snowflake, optionally before the target database exists."""
    return snowflake.connector.connect(
        **connection_parameters(settings, include_database=include_database)
    )
