import pytest

from src.audit.recorder import AuditRecorder
from src.tools.registry import (
    RegisteredTool,
    TrustedToolRegistry,
    UnknownToolError,
    DuplicateToolError,
)
from src.tools.payment import simulated_payment


def registry(tmp_path):
    r = TrustedToolRegistry(
        audit=AuditRecorder(tmp_path / "audit.jsonl")
    )

    r.register(
        RegisteredTool(
            name="finance.payment.create",
            action="payment.create",
            resource="erp.payments",
            handler=simulated_payment,
        )
    )

    return r


def test_registered_tool_executes(tmp_path):
    result = registry(tmp_path).execute(
        "finance.payment.create",
        "finance-agent",
        {"amount": 2500, "currency": "EUR"},
    )

    assert result.executed is True
    assert result.result["status"] == "simulated"


def test_large_payment_blocked(tmp_path):
    result = registry(tmp_path).execute(
        "finance.payment.create",
        "finance-agent",
        {"amount": 75000, "currency": "EUR"},
    )

    assert result.executed is False
    assert result.decision.decision.value == "DENY"


def test_approval_required_blocks_execution(tmp_path):
    result = registry(tmp_path).execute(
        "finance.payment.create",
        "finance-agent",
        {"amount": 25000, "currency": "EUR"},
    )

    assert result.executed is False
    assert result.decision.decision.value == (
        "REQUIRE_APPROVAL"
    )


def test_unknown_tool_rejected(tmp_path):
    with pytest.raises(UnknownToolError):
        registry(tmp_path).execute(
            "unregistered.tool",
            "finance-agent",
            {},
        )


def test_duplicate_registration_rejected(tmp_path):
    r = registry(tmp_path)

    with pytest.raises(DuplicateToolError):
        r.register(
            RegisteredTool(
                name="finance.payment.create",
                action="payment.create",
                resource="erp.payments",
                handler=simulated_payment,
            )
        )


def test_unknown_agent_denied(tmp_path):
    result = registry(tmp_path).execute(
        "finance.payment.create",
        "unknown-agent",
        {"amount": 500, "currency": "EUR"},
    )

    assert result.executed is False
