
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor

import pytest

from src.approvals import engine
from src.approvals.engine import ApprovalEngine


@pytest.fixture
def approvals(tmp_path):
    return ApprovalEngine(tmp_path / "approvals.sqlite3")


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

    monkeypatch.setattr("src.approvals.engine.utcnow", lambda: future)

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


def test_state_and_audit_survive_engine_restart(tmp_path, payment):
    db_path = tmp_path / "approvals.sqlite3"
    first = ApprovalEngine(db_path)
    request = first.create("finance-agent", payment)
    first.decide(request.approval_id, "finance-manager", True)

    restarted = ApprovalEngine(db_path)
    assert restarted.get(request.approval_id).status == "APPROVED"
    assert restarted.consume(request.approval_id, "finance-agent", payment)
    assert not ApprovalEngine(db_path).consume(
        request.approval_id, "finance-agent", payment
    )
    assert [event["event_type"] for event in restarted.events(request.approval_id)] == [
        "CREATED", "APPROVED", "CONSUMED"
    ]


def test_concurrent_consumption_has_single_winner(tmp_path, payment):
    engine = ApprovalEngine(tmp_path / "approvals.sqlite3")
    request = engine.create("finance-agent", payment)
    engine.decide(request.approval_id, "finance-manager", True)

    def consume():
        return ApprovalEngine(tmp_path / "approvals.sqlite3").consume(
            request.approval_id, "finance-agent", payment
        )

    with ThreadPoolExecutor(max_workers=8) as workers:
        outcomes = list(workers.map(lambda _: consume(), range(16)))
    assert outcomes.count(True) == 1
    assert [event["event_type"] for event in engine.events(request.approval_id)].count(
        "CONSUMED"
    ) == 1


def test_expiration_is_persisted_and_audited(tmp_path, payment, monkeypatch):
    db_path = tmp_path / "approvals.sqlite3"
    engine = ApprovalEngine(db_path)
    request = engine.create("finance-agent", payment, ttl_seconds=1)
    future = request.expires_at + timedelta(seconds=1)
    monkeypatch.setattr("src.approvals.engine.utcnow", lambda: future)
    assert ApprovalEngine(db_path).get(request.approval_id).status == "EXPIRED"
    assert engine.events(request.approval_id)[-1]["event_type"] == "EXPIRED"
