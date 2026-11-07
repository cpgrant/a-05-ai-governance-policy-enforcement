
from datetime import timedelta

import pytest

from src.approvals import engine
from src.approvals.engine import ApprovalEngine


@pytest.fixture
def approvals():
    return ApprovalEngine()


@pytest.fixture
def payment():
    return {
        "resource": "payment",
        "action": "create",
        "currency": "EUR",
        "amount": 12000,
    }


def test_create_approval(approvals, payment):
    approval = approvals.create("finance-agent", payment)

    assert approval.status == "PENDING"


def test_authorized_approval_transition(
    approvals, payment
):
    request = approvals.create("finance-agent", payment)

    approved = approvals.decide(
        request.approval_id,
        "finance-manager",
        True,
    )

    assert approved.status == "APPROVED"


def test_self_approval_blocked(approvals, payment):
    request = approvals.create("finance-agent", payment)

    with pytest.raises(PermissionError):
        approvals.decide(
            request.approval_id,
            "finance-agent",
            True,
        )


def test_rejected_approval_cannot_execute(
    approvals, payment
):
    request = approvals.create("finance-agent", payment)

    approvals.decide(
        request.approval_id,
        "finance-manager",
        False,
    )

    assert not approvals.consume(
        request.approval_id,
        "finance-agent",
        payment,
    )


def test_approval_bound_to_exact_operation(
    approvals, payment
):
    request = approvals.create("finance-agent", payment)

    approvals.decide(
        request.approval_id,
        "finance-manager",
        True,
    )

    changed = dict(payment)
    changed["amount"] = 25000

    assert not approvals.consume(
        request.approval_id,
        "finance-agent",
        changed,
    )


def test_one_time_use(approvals, payment):
    request = approvals.create("finance-agent", payment)

    approvals.decide(
        request.approval_id,
        "finance-manager",
        True,
    )

    assert approvals.consume(
        request.approval_id,
        "finance-agent",
        payment,
    )

    assert not approvals.consume(
        request.approval_id,
        "finance-agent",
        payment,
    )


def test_expired_approval_blocked(
    approvals, payment, monkeypatch
):
    request = approvals.create(
        "finance-agent",
        payment,
        ttl_seconds=1,
    )

    approvals.decide(
        request.approval_id,
        "finance-manager",
        True,
    )

    future = request.expires_at + timedelta(seconds=1)

    monkeypatch.setattr(engine, "utcnow", lambda: future)

    assert not approvals.consume(
        request.approval_id,
        "finance-agent",
        payment,
    )


def test_wrong_requester_blocked(
    approvals, payment
):
    request = approvals.create("finance-agent", payment)

    approvals.decide(
        request.approval_id,
        "finance-manager",
        True,
    )

    assert not approvals.consume(
        request.approval_id,
        "other-agent",
        payment,
    )
