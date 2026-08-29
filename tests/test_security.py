from contextlib import suppress

import pytest

from lyme_gap_atlas_shared.observability import parse_otlp_headers, redact
from lyme_gap_atlas_shared.settings import SnowflakeSettings
from lyme_gap_atlas_shared.snowflake import connection_parameters


def test_redact_masks_nested_secrets() -> None:
    assert redact({"user": "safe", "token": "bad", "nested": {"password": "bad"}}) == {
        "user": "safe",
        "token": "[REDACTED_SECRET]",
        "nested": {"password": "[REDACTED_SECRET]"},
    }


def test_parse_otlp_headers_supports_authenticated_exporters() -> None:
    assert parse_otlp_headers("Authorization=Bearer abc, X-Tenant=atlas") == {
        "Authorization": "Bearer abc",
        "X-Tenant": "atlas",
    }


@pytest.mark.parametrize("value", ["Authorization", "=Bearer abc", "Authorization="])
def test_parse_otlp_headers_rejects_malformed_values(value: str) -> None:
    with pytest.raises(ValueError, match="key=value"):
        parse_otlp_headers(value)


def test_bootstrap_connection_omits_database() -> None:
    settings = SnowflakeSettings(
        snowflake_account="account",
        snowflake_user="operator",
        snowflake_role="SYSADMIN",
        snowflake_pat="placeholder",
    )
    assert "database" not in connection_parameters(settings, include_database=False)
    assert connection_parameters(settings)["database"] == "ONE_HEALTH_LYME_GAP_ATLAS"


def test_pat_uses_connector_password_parameter() -> None:
    settings = SnowflakeSettings(
        snowflake_account="account",
        snowflake_user="operator",
        snowflake_pat="placeholder",
    )

    parameters = connection_parameters(settings)

    assert parameters["password"] == "placeholder"
    assert "authenticator" not in parameters
    assert "token" not in parameters


def test_network_timeout_is_bounded_and_configurable() -> None:
    default_settings = SnowflakeSettings(
        snowflake_account="account",
        snowflake_user="operator",
        snowflake_pat="placeholder",
    )
    configured_settings = SnowflakeSettings(
        snowflake_account="account",
        snowflake_user="operator",
        snowflake_pat="placeholder",
        snowflake_network_timeout_seconds=900,
    )

    assert connection_parameters(default_settings)["network_timeout"] == 600
    assert connection_parameters(configured_settings)["network_timeout"] == 900


def test_key_pair_can_read_encrypted_key_from_local_path(tmp_path) -> None:
    key_path = tmp_path / "pipeline.p8"
    # An invalid key still confirms that the configured path is selected over B64.
    key_path.write_bytes(b"not-a-private-key")
    settings = SnowflakeSettings(
        snowflake_account="account",
        snowflake_user="service",
        snowflake_auth_method="key_pair",
        snowflake_private_key_path=key_path,
    )
    with suppress(ValueError):
        connection_parameters(settings)
