from __future__ import annotations

from typing import Any

import pytest

import lyme_gap_atlas_shared.observability as observability


class FakeProvider:
    def __init__(self, *_: Any, **__: Any) -> None:
        self.processors: list[Any] = []
        self.flushes = 0
        self.shutdowns = 0

    def add_span_processor(self, processor: Any) -> None:
        self.processors.append(processor)

    def force_flush(self) -> None:
        self.flushes += 1

    def shutdown(self) -> None:
        self.shutdowns += 1


@pytest.fixture(autouse=True)
def reset_tracing_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(observability, "_tracer_provider", None)


def test_configure_tracing_is_a_noop_without_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    monkeypatch.setattr(observability, "TracerProvider", lambda *_args, **_kwargs: pytest.fail())

    observability.configure_tracing("atlas")

    assert observability._tracer_provider is None


def test_configure_tracing_is_idempotent_and_shutdown_flushes_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: list[FakeProvider] = []
    registered: list[FakeProvider] = []
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://telemetry.example/v1/traces")
    monkeypatch.setattr(
        observability,
        "TracerProvider",
        lambda *_args, **_kwargs: created.append(FakeProvider()) or created[-1],
    )
    monkeypatch.setattr(observability, "BatchSpanProcessor", lambda exporter: exporter)
    monkeypatch.setattr(observability, "OTLPSpanExporter", lambda **_kwargs: object())
    monkeypatch.setattr(observability.trace, "set_tracer_provider", registered.append)

    observability.configure_tracing("atlas")
    observability.configure_tracing("atlas")
    observability.flush_tracing()
    observability.shutdown_tracing()
    observability.shutdown_tracing()

    assert len(created) == 1
    assert registered == created
    assert created[0].flushes == 2
    assert created[0].shutdowns == 1


def test_configure_tracing_failure_is_private_and_non_fatal(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://telemetry.example/v1/traces")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_HEADERS", "Authorization=Bearer do-not-log")
    monkeypatch.setattr(
        observability,
        "OTLPSpanExporter",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("do-not-log")),
    )

    observability.configure_tracing("atlas")

    assert observability._tracer_provider is None
    assert "RuntimeError" in caplog.text
    assert "do-not-log" not in caplog.text


def test_shutdown_attempts_both_operations_when_flush_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = FakeProvider()

    def failed_flush() -> None:
        provider.flushes += 1
        raise RuntimeError("network unavailable")

    provider.force_flush = failed_flush  # type: ignore[method-assign]
    monkeypatch.setattr(observability, "_tracer_provider", provider)

    observability.shutdown_tracing()

    assert provider.flushes == 1
    assert provider.shutdowns == 1
