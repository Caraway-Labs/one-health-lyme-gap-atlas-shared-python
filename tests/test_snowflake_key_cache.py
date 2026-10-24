"""Per-process private-key caching for the deprecated Snowflake helper."""

from types import SimpleNamespace
from typing import Any

import pytest
import snowflake.connector

from lyme_gap_atlas_shared.infrastructure import snowflake as helper
from lyme_gap_atlas_shared.infrastructure.settings import SnowflakeSettings


class FakeLoader:
    """Stands in for cryptography's PEM loader and records each parse."""

    def __init__(self) -> None:
        self.calls: list[tuple[bytes, bytes | None]] = []
        self.fail = False

    def __call__(self, data: bytes, password: bytes | None = None) -> object:
        self.calls.append((data, password))
        if self.fail:
            raise ValueError("bad key")
        return object()  # a new key object per parse, so identity shows reloads


@pytest.fixture(autouse=True)
def fresh_cache(monkeypatch: pytest.MonkeyPatch) -> FakeLoader:
    helper._clear_private_key_cache()
    loader = FakeLoader()
    monkeypatch.setattr(helper, "serialization", SimpleNamespace(load_pem_private_key=loader))
    yield loader
    helper._clear_private_key_cache()


@pytest.fixture
def fake_connector(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    def connect(**kwargs: Any) -> object:
        calls.append(kwargs)
        return object()

    monkeypatch.setattr(snowflake.connector, "connect", connect)
    return calls


def _key_pair_settings(key_path: Any, passphrase: str | None = None) -> SnowflakeSettings:
    return SnowflakeSettings(
        snowflake_account="account",
        snowflake_user="service",
        snowflake_auth_method="key_pair",
        snowflake_private_key_path=key_path,
        snowflake_private_key_passphrase=passphrase,
    )


def test_repeated_connects_parse_key_once(
    tmp_path, fresh_cache: FakeLoader, fake_connector: list[dict[str, Any]]
) -> None:
    key_path = tmp_path / "pipeline.p8"
    key_path.write_bytes(b"key-material-v1")
    settings = _key_pair_settings(key_path, passphrase="pass-one")

    for _ in range(5):
        helper.connect(settings)

    assert len(fresh_cache.calls) == 1
    assert len(fake_connector) == 5
    keys = {id(call["private_key"]) for call in fake_connector}
    assert len(keys) == 1


def test_changed_key_material_reloads(
    tmp_path, fresh_cache: FakeLoader, fake_connector: list[dict[str, Any]]
) -> None:
    key_path = tmp_path / "pipeline.p8"
    key_path.write_bytes(b"key-material-v1")
    settings = _key_pair_settings(key_path)

    helper.connect(settings)
    key_path.write_bytes(b"key-material-v2")
    helper.connect(settings)

    assert [data for data, _ in fresh_cache.calls] == [b"key-material-v1", b"key-material-v2"]
    assert fake_connector[0]["private_key"] is not fake_connector[1]["private_key"]


def test_changed_passphrase_reloads_same_key_bytes(
    tmp_path, fresh_cache: FakeLoader, fake_connector: list[dict[str, Any]]
) -> None:
    key_path = tmp_path / "pipeline.p8"
    key_path.write_bytes(b"key-material")

    helper.connect(_key_pair_settings(key_path, passphrase="first"))
    helper.connect(_key_pair_settings(key_path, passphrase="second"))
    helper.connect(_key_pair_settings(key_path))

    assert [password for _, password in fresh_cache.calls] == [b"first", b"second", None]


def test_base64_and_path_sources_share_identity_for_same_bytes(
    tmp_path, fresh_cache: FakeLoader, fake_connector: list[dict[str, Any]]
) -> None:
    import base64

    raw = b"key-material"
    key_path = tmp_path / "pipeline.p8"
    key_path.write_bytes(raw)
    helper.connect(_key_pair_settings(key_path))
    b64_settings = SnowflakeSettings(
        snowflake_account="account",
        snowflake_user="service",
        snowflake_auth_method="key_pair",
        snowflake_private_key_b64=base64.b64encode(raw).decode(),
    )
    helper.connect(b64_settings)

    assert len(fresh_cache.calls) == 1


def test_failed_parse_is_not_cached(
    tmp_path, fresh_cache: FakeLoader, fake_connector: list[dict[str, Any]]
) -> None:
    key_path = tmp_path / "pipeline.p8"
    key_path.write_bytes(b"broken")
    settings = _key_pair_settings(key_path)
    fresh_cache.fail = True

    for _ in range(2):
        with pytest.raises(ValueError, match="bad key"):
            helper.connect(settings)
    assert len(fresh_cache.calls) == 2

    fresh_cache.fail = False
    helper.connect(settings)
    helper.connect(settings)
    assert len(fresh_cache.calls) == 3
    assert fake_connector and len(fake_connector) == 2


def test_cache_is_bounded_and_stores_no_raw_secrets(
    tmp_path, fresh_cache: FakeLoader, fake_connector: list[dict[str, Any]]
) -> None:
    secret_bytes = b"SECRET-KEY-BYTES"
    secret_passphrase = b"SECRET-PASSPHRASE"
    key_path = tmp_path / "pipeline.p8"
    key_path.write_bytes(secret_bytes)
    helper.connect(_key_pair_settings(key_path, passphrase=secret_passphrase.decode()))

    for index in range(helper._KEY_CACHE_MAX_ENTRIES + 3):
        key_path.write_bytes(secret_bytes + str(index).encode())
        helper.connect(_key_pair_settings(key_path))

    assert len(helper._key_cache) == helper._KEY_CACHE_MAX_ENTRIES
    for cache_id, key in helper._key_cache.items():
        assert len(cache_id) == 64
        assert secret_bytes.decode() not in cache_id
        assert secret_passphrase.decode() not in cache_id
        assert not isinstance(key, (bytes, str))


def test_connection_parameters_unchanged_for_key_pair(tmp_path, fresh_cache: FakeLoader) -> None:
    key_path = tmp_path / "pipeline.p8"
    key_path.write_bytes(b"key-material")
    parameters = helper.connection_parameters(_key_pair_settings(key_path))

    assert parameters["authenticator"] == "SNOWFLAKE_JWT"
    assert parameters["login_timeout"] == 15
    assert parameters["network_timeout"] == 600
    assert parameters["database"] == "ONE_HEALTH_LYME_GAP_ATLAS"
    assert parameters["private_key"] is not None
