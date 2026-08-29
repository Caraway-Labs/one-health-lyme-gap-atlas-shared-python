"""Redacted structured logging and optional OTLP tracing."""

import json
import logging
import os
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SENSITIVE_FRAGMENTS = ("token", "secret", "password", "private_key", "authorization")


def redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: "[REDACTED_SECRET]"
            if any(fragment in str(key).lower() for fragment in SENSITIVE_FRAGMENTS)
            else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "context"):
            payload["context"] = redact(record.context)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


def parse_otlp_headers(value: str | None) -> dict[str, str]:
    """Parse the standard OTLP comma-separated ``key=value`` header setting."""
    if not value:
        return {}
    headers: dict[str, str] = {}
    for pair in value.split(","):
        key, separator, header_value = pair.strip().partition("=")
        if not separator or not key or not header_value:
            raise ValueError("OTEL_EXPORTER_OTLP_HEADERS must use comma-separated key=value pairs")
        headers[key.strip()] = header_value.strip()
    return headers


def configure_tracing(service_name: str) -> None:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return
    headers = parse_otlp_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS"))
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, headers=headers))
    )
    trace.set_tracer_provider(provider)
