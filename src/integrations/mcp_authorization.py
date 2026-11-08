import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.identity.jwt_verifier import AgentIdentity
from src.contracts.policy import (
    GovernanceDecision,
    PolicyDecision,
)

ROOT = Path(__file__).resolve().parents[2]
OPA = ROOT / "tools/opa_linux_amd64"
POLICY = ROOT / "policies/mcp.rego"

# Mirrors the tool signatures in A04's MCP server. The A05 adapter currently
# invokes only get_customer, but the advisory authorization API validates all
# known A04 tools before returning a decision.
_ARGUMENTS = {
    "get_customer": {"customer_id": str},
    "list_customers": {},
    "get_customer_db": {"customer_code": str},
    "list_customers_db": {"limit": int},
    "get_customer_orders_db": {"customer_code": str, "limit": int},
    "get_order_details_db": {"order_number": str},
    "get_inventory_status_db": {"sku": str},
    "list_customer_invoices_db": {"customer_code": str, "as_of": str},
    "get_customer_financial_summary_db": {"customer_code": str, "as_of": str},
}


def _valid_arguments(tool_name: str, arguments: dict[str, Any]) -> bool:
    schema = _ARGUMENTS.get(tool_name)
    if schema is None or not isinstance(arguments, dict):
        return False
    required = set(schema)
    if tool_name == "list_customers_db":
        required = set()
    if tool_name == "get_customer_orders_db":
        required = {"customer_code"}
    if set(arguments) - set(schema) or not required.issubset(arguments):
        return False
    for key, value in arguments.items():
        expected = schema[key]
        if expected is int:
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                return False
        elif not isinstance(value, expected) or not value:
            return False
        elif isinstance(value, str) and (not value.strip() or len(value) > 128):
            return False
        if expected is int and value > 100:
            return False
    if "as_of" in arguments:
        try:
            date.fromisoformat(arguments["as_of"])
        except ValueError:
            return False
    return True


def authorize_mcp_tool(
    identity: AgentIdentity,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> GovernanceDecision:
    request_id = uuid4()
    arguments = {} if arguments is None else arguments

    if not _valid_arguments(tool_name, arguments):
        return GovernanceDecision(
            request_id=request_id,
            decision=PolicyDecision.DENY,
            policy_id="a04-mcp",
            policy_version="1.0",
            reason="Unknown tool or invalid arguments",
        )

    policy_input = {
        "agent_id": identity.agent_id,
        "roles": list(identity.roles),
        "action": "tool.call",
        "resource": "a04.mcp",
        "tool_name": tool_name,
        "arguments": arguments,
    }

    try:
        result = subprocess.run(
            [
                str(OPA),
                "eval",
                "--data", str(POLICY),
                "--stdin-input",
                "--format", "raw",
                "data.governance.mcp.decision",
            ],
            input=json.dumps(policy_input),
            text=True,
            capture_output=True,
            timeout=5,
            check=True,
        )

        decision = PolicyDecision(result.stdout.strip())

    except (OSError, subprocess.SubprocessError, ValueError):
        decision = PolicyDecision.DENY

    return GovernanceDecision(
        request_id=request_id,
        decision=decision,
        policy_id="a04-mcp",
        policy_version="1.0",
        reason=(
            "MCP tool authorized by role policy"
            if decision == PolicyDecision.PERMIT
            else "MCP tool authorization denied or unavailable"
        ),
    )
