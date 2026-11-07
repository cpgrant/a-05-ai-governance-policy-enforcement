from pathlib import Path
from unittest.mock import patch

import pytest

from src.identity.jwt_verifier import AgentIdentity
from src.integrations.a04_mcp_adapter import (
    A04_ROOT,
    execute_a04_tool,
)


def identity(role: str) -> AgentIdentity:
    return AgentIdentity(
        agent_id="a05-integration-test-agent",
        roles=(role,),
        issuer="ai-a05-dev-issuer",
        token_id="integration-test-token",
    )


@pytest.mark.integration
def test_a04_real_customer_lookup():
    python = A04_ROOT / ".venv/bin/python"

    if not python.exists():
        pytest.skip("A04 Python environment unavailable")

    result = execute_a04_tool(
        identity("reader"),
        "get_customer",
        {"customer_id": "C001"},
    )

    assert result["decision"] == "PERMIT"
    assert result["executed"] is True
    assert result["result"]["id"] == "C001"
    assert result["result"]["name"] == "ACME Corporation"
    assert result["result"]["status"] == "active"


@pytest.mark.integration
def test_a04_real_policy_denial():
    result = execute_a04_tool(
        identity("blocked"),
        "get_customer",
        {"customer_id": "C001"},
    )

    assert result["decision"] == "DENY"
    assert result["executed"] is False


@pytest.mark.integration
def test_a04_invalid_arguments_blocked():
    result = execute_a04_tool(
        identity("reader"),
        "get_customer",
        {"customer_id": "INVALID"},
    )

    assert result["decision"] == "DENY"
    assert result["executed"] is False
