from lyme_gap_atlas_shared.observability import redact
from lyme_gap_atlas_shared.settings import SnowflakeSettings
from lyme_gap_atlas_shared.snowflake import connection_parameters


def test_redact_masks_nested_secrets() -> None:
    assert redact({"user": "safe", "token": "bad", "nested": {"password": "bad"}}) == {
        "user": "safe",
        "token": "[REDACTED_SECRET]",
        "nested": {"password": "[REDACTED_SECRET]"},
    }


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
    try:
        connection_parameters(settings)
    except ValueError as error:
        assert "Could not deserialize key data" in str(error)
