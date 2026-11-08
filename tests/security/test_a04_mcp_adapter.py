from unittest.mock import patch
import json

from src.identity.jwt_verifier import AgentIdentity
from src.integrations.a04_mcp_adapter import execute_a04_tool


def identity(role):
    return AgentIdentity(
        agent_id="test-agent",
        roles=(role,),
        issuer="ai-a05-dev-issuer",
        token_id="test-token",
    )


def test_blocked_agent_does_not_execute():
    with patch(
        "src.integrations.a04_mcp_adapter.authorize_mcp_tool"
    ) as authorize, patch(
        "src.integrations.a04_mcp_adapter.subprocess.run"
    ) as runner:

        from src.contracts.policy import (
            GovernanceDecision,
            PolicyDecision,
        )
        from uuid import uuid4

        authorize.return_value = GovernanceDecision(
            request_id=uuid4(),
            decision=PolicyDecision.DENY,
            policy_id="a04-mcp",
            policy_version="1.0",
            reason="Access denied",
        )

        result = execute_a04_tool(
            identity("blocked"),
            "get_customer",
            {"customer_id": "C001"},
        )

        assert result["executed"] is False
        assert result["decision"] == "DENY"

        authorize.assert_called_once()
        runner.assert_not_called()


def test_invalid_arguments_rejected():
    result = execute_a04_tool(
        identity("reader"),
        "get_customer",
        {"customer_id": "INVALID"},
    )

    assert result["executed"] is False


def test_child_process_does_not_inherit_ambient_secrets(monkeypatch):
    monkeypatch.setenv("A05_PRIVATE_TOKEN", "must-not-cross-boundary")
    customer = {"id": "C001", "name": "Demo", "status": "active"}
    with (
        patch("src.integrations.a04_mcp_adapter.authorize_mcp_tool") as authorize,
        patch("src.integrations.a04_mcp_adapter.record_mcp_event"),
        patch("src.integrations.a04_mcp_adapter.subprocess.run") as runner,
    ):
        from src.contracts.policy import GovernanceDecision, PolicyDecision
        from uuid import uuid4
        authorize.return_value = GovernanceDecision(
            request_id=uuid4(), decision=PolicyDecision.PERMIT,
            policy_id="a04-mcp", policy_version="1.0", reason="Allowed",
        )
        runner.return_value.stdout = json.dumps(customer)
        runner.return_value.stderr = ""
        execute_a04_tool(identity("reader"), "get_customer", {"customer_id": "C001"})

    child_env = runner.call_args.kwargs["env"]
    assert child_env["AI_A04_ROLE"] == "reader"
    assert "A05_PRIVATE_TOKEN" not in child_env
