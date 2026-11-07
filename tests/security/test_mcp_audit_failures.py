
import json
import subprocess
from unittest.mock import patch
from uuid import uuid4

import pytest

from src.contracts.policy import GovernanceDecision, PolicyDecision
from src.identity.jwt_verifier import AgentIdentity
from src.integrations import a04_mcp_adapter
from src.integrations.a04_mcp_adapter import execute_a04_tool
from src.integrations.mcp_audit import record_mcp_event


def identity():
    return AgentIdentity(
        agent_id="audit-failure-test-agent",
        roles=("reader",),
        issuer="ai-a05-dev-issuer",
        token_id="audit-failure-test",
    )


def permitted_decision():
    return GovernanceDecision(
        request_id=uuid4(),
        decision=PolicyDecision.PERMIT,
        policy_id="a04-mcp",
        policy_version="1.0",
        reason="Authorized",
    )


def test_execution_failure_is_audited(tmp_path):
    """A failed MCP subprocess must generate a FAILED audit event."""

    audit_file = tmp_path / "audit.jsonl"

    def write_test_audit(**kwargs):
        return record_mcp_event(
            audit_path=audit_file,
            **kwargs,
        )

    with (
        patch.object(
            a04_mcp_adapter,
            "authorize_mcp_tool",
            return_value=permitted_decision(),
        ),
        patch.object(
            a04_mcp_adapter,
            "record_mcp_event",
            side_effect=write_test_audit,
        ),
        patch.object(
            a04_mcp_adapter.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(
                cmd="a04-mcp",
                timeout=15,
            ),
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="A04 MCP execution failed",
        ):
            execute_a04_tool(
                identity(),
                "get_customer",
                {"customer_id": "C001"},
            )

    records = [
        json.loads(line)
        for line in audit_file.read_text().splitlines()
    ]

    assert len(records) == 2

    assert records[0]["event"] == "authorization"
    assert records[0]["outcome"] == "PERMIT"

    assert records[1]["event"] == "execution"
    assert records[1]["outcome"] == "FAILED"

    assert records[0]["request_id"] == records[1]["request_id"]


def test_audit_unavailable_prevents_execution():
    """Failure to record authorization must prevent MCP execution."""

    with (
        patch.object(
            a04_mcp_adapter,
            "authorize_mcp_tool",
            return_value=permitted_decision(),
        ),
        patch.object(
            a04_mcp_adapter,
            "record_mcp_event",
            side_effect=OSError("Audit unavailable"),
        ),
        patch.object(
            a04_mcp_adapter.subprocess,
            "run",
        ) as executor,
    ):
        with pytest.raises(
            OSError,
            match="Audit unavailable",
        ):
            execute_a04_tool(
                identity(),
                "get_customer",
                {"customer_id": "C001"},
            )

        executor.assert_not_called()
