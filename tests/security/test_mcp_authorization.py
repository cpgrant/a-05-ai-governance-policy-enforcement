from unittest.mock import patch

from src.contracts.policy import PolicyDecision
from src.identity.jwt_verifier import AgentIdentity
from src.integrations.mcp_authorization import authorize_mcp_tool


IDENTITY = AgentIdentity("agent-1", ("reader",), "issuer", "jti-1")


def test_exact_validated_arguments_are_sent_to_policy():
    with patch(
        "src.integrations.mcp_authorization.subprocess.run",
        return_value=type("Result", (), {"stdout": "PERMIT"})(),
    ) as run:
        result = authorize_mcp_tool(
            IDENTITY, "get_customer", {"customer_id": "C001"}
        )
    assert result.decision == PolicyDecision.PERMIT
    import json
    policy_input = json.loads(run.call_args.kwargs["input"])
    assert policy_input == {
        "agent_id": "agent-1",
        "roles": ["reader"],
        "action": "tool.call",
        "resource": "a04.mcp",
        "tool_name": "get_customer",
        "arguments": {"customer_id": "C001"},
    }


def test_unknown_tool_and_extra_or_invalid_arguments_fail_closed():
    cases = [
        ("unknown", {}),
        ("get_customer", {"customer_id": "C001", "admin": True}),
        ("get_inventory_status_db", {"sku": "SKU-1", "limit": 10}),
        ("list_customers_db", {"limit": True}),
        ("list_customer_invoices_db", {
            "customer_code": "C001", "as_of": "not-a-date"
        }),
    ]
    with patch("src.integrations.mcp_authorization.subprocess.run") as run:
        for tool, arguments in cases:
            result = authorize_mcp_tool(IDENTITY, tool, arguments)
            assert result.decision == PolicyDecision.DENY
        run.assert_not_called()


def test_opa_failure_fails_closed():
    import subprocess
    with patch(
        "src.integrations.mcp_authorization.subprocess.run",
        side_effect=subprocess.TimeoutExpired("opa", 5),
    ):
        result = authorize_mcp_tool(
            IDENTITY, "get_customer", {"customer_id": "C001"}
        )
    assert result.decision == PolicyDecision.DENY
