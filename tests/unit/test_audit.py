import json
import stat

from src.audit.recorder import AuditRecorder
from src.contracts.policy import (
    GovernanceRequest,
    GovernanceDecision,
    PolicyDecision,
)


def test_audit_record_created(tmp_path):
    recorder = AuditRecorder(tmp_path / "audit.jsonl")

    request = GovernanceRequest(
        agent_id="finance-agent",
        action="payment.create",
        resource="erp.payments",
        context={"amount": 2500, "currency": "EUR"},
    )

    decision = GovernanceDecision(
        request_id=request.request_id,
        decision=PolicyDecision.PERMIT,
        policy_id="finance",
        policy_version="1.0",
        reason="Action permitted",
    )

    event = recorder.record(
        request=request,
        decision=decision,
        executed=True,
        execution_status="success",
    )

    assert event.executed is True
    assert event.decision == "PERMIT"

    with (tmp_path / "audit.jsonl").open() as f:
        saved = json.loads(f.readline())

    assert saved["request_id"] == str(request.request_id)
    assert saved["agent_id"] == "finance-agent"
    assert saved["execution_status"] == "success"
    assert "context" not in saved
    assert stat.S_IMODE((tmp_path / "audit.jsonl").stat().st_mode) == 0o600


def test_multiple_audit_events(tmp_path):
    recorder = AuditRecorder(tmp_path / "audit.jsonl")

    for amount in [2500, 75000]:
        request = GovernanceRequest(
            agent_id="finance-agent",
            action="payment.create",
            resource="erp.payments",
            context={"amount": amount},
        )

        decision = GovernanceDecision(
            request_id=request.request_id,
            decision=PolicyDecision.DENY,
            policy_id="finance",
            policy_version="1.0",
            reason="Test denial",
        )

        recorder.record(
            request,
            decision,
            executed=False,
            execution_status="blocked",
        )

    lines = (tmp_path / "audit.jsonl").read_text().splitlines()
    assert len(lines) == 2
