from lyme_gap_atlas_shared.observability import redact


def test_redact_masks_nested_secrets() -> None:
    assert redact({"user": "safe", "token": "bad", "nested": {"password": "bad"}}) == {
        "user": "safe",
        "token": "[REDACTED_SECRET]",
        "nested": {"password": "[REDACTED_SECRET]"},
    }

