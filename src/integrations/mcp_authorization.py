import json
import subprocess
from pathlib import Path
from uuid import uuid4

from src.identity.jwt_verifier import AgentIdentity
from src.contracts.policy import (
    GovernanceDecision,
    PolicyDecision,
)

ROOT = Path(__file__).resolve().parents[2]
OPA = ROOT / "tools/opa_linux_amd64"
POLICY = ROOT / "policies/mcp.rego"


def authorize_mcp_tool(
    identity: AgentIdentity,
    tool_name: str,
) -> GovernanceDecision:
    request_id = uuid4()

    policy_input = {
        "agent_id": identity.agent_id,
        "roles": list(identity.roles),
        "action": "tool.call",
        "resource": "a04.mcp",
        "tool_name": tool_name,
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
