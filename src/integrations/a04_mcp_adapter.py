
import json
import os
import subprocess
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.contracts.policy import PolicyDecision
from src.identity.jwt_verifier import AgentIdentity
from src.integrations.mcp_authorization import authorize_mcp_tool
from src.integrations.mcp_audit import record_mcp_event


A04_ROOT = (
    Path.home()
    / "development/ai-projects"
    / "a-04-mcp-enterprise-integration"
)


def execute_a04_tool(
    identity: AgentIdentity,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute a synthetic A04 MCP tool through A05 governance.

    Local development integration only.

    Security:
    - Authorize before execution.
    - Reject unsupported tools and invalid arguments.
    - Record authorization and execution outcomes.
    - Fail closed if pre-execution auditing fails.
    - Do not include customer data in audit records.

    Limitation:
    A04 does not yet independently enforce A05 decisions.
    """

    request_id = str(uuid4())
    policy_id = "a04-mcp"

    def audit(
        event: str,
        outcome: str,
        reason: str = "",
    ) -> None:
        record_mcp_event(
            request_id=request_id,
            agent_id=identity.agent_id,
            tool_name=tool_name,
            event=event,
            outcome=outcome,
            policy_id=policy_id,
            reason=reason,
        )

    # --------------------------------------------------
    # 1. Authorization
    # --------------------------------------------------

    try:
        decision = authorize_mcp_tool(
            identity=identity,
            tool_name=tool_name,
        )
    except Exception:
        audit(
            "authorization",
            "DENY",
            "Policy evaluation unavailable",
        )
        raise RuntimeError(
            "MCP authorization unavailable"
        ) from None

    # Audit before proceeding. Audit failure prevents execution.
    audit(
        "authorization",
        decision.decision.value,
        decision.reason,
    )

    if decision.decision != PolicyDecision.PERMIT:
        return {
            "request_id": request_id,
            "executed": False,
            "decision": decision.decision.value,
            "reason": decision.reason,
        }

    # --------------------------------------------------
    # 2. Restrict enabled tools
    # --------------------------------------------------

    if tool_name != "get_customer":
        audit(
            "execution",
            "DENIED",
            "Tool not enabled in A05 demonstration",
        )

        return {
            "request_id": request_id,
            "executed": False,
            "decision": "DENY",
            "reason": "Tool not enabled in A05 demonstration",
        }

    # --------------------------------------------------
    # 3. Validate tool arguments
    # --------------------------------------------------

    customer_id = arguments.get("customer_id")

    if (
        not isinstance(customer_id, str)
        or customer_id not in {"C001", "C002"}
        or set(arguments) != {"customer_id"}
    ):
        audit(
            "execution",
            "DENIED",
            "Invalid customer lookup arguments",
        )

        return {
            "request_id": request_id,
            "executed": False,
            "decision": "DENY",
            "reason": "Invalid customer lookup arguments",
        }

    # --------------------------------------------------
    # 4. Build A04 MCP invocation
    # --------------------------------------------------

    script = """
import asyncio
import json

from mcp import Client
from src.server.main import mcp


async def main():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_customer",
            {"customer_id": CUSTOMER_ID},
        )

        if result.is_error:
            raise RuntimeError("MCP tool failed")

        data = result.structured_content

        if data is None:
            for block in result.content:
                if block.type == "text":
                    data = json.loads(block.text)
                    break

        if data is None:
            raise RuntimeError(
                "MCP tool returned no usable data"
            )

        print(json.dumps(data))


asyncio.run(main())
""".replace("CUSTOMER_ID", json.dumps(customer_id))

    env = os.environ.copy()

    # A04 development-only role mechanism.
    # Not a trusted production identity boundary.
    env["AI_A04_ROLE"] = "reader"

    # --------------------------------------------------
    # 5. Execute MCP tool
    # --------------------------------------------------

    try:
        result = subprocess.run(
            [
                str(A04_ROOT / ".venv/bin/python"),
                "-c",
                script,
            ],
            cwd=A04_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )

        customer_data = json.loads(
            result.stdout.strip()
        )

        if not isinstance(customer_data, dict):
            raise ValueError(
                "MCP returned invalid customer data"
            )

        if customer_data.get("id") != customer_id:
            raise ValueError(
                "MCP customer ID mismatch"
            )

    except (
        OSError,
        subprocess.SubprocessError,
        ValueError,
        TypeError,
    ):
        audit(
            "execution",
            "FAILED",
            "MCP execution or response validation failed",
        )

        raise RuntimeError(
            "A04 MCP execution failed"
        ) from None

    # --------------------------------------------------
    # 6. Record successful execution
    # --------------------------------------------------

    audit(
        "execution",
        "SUCCESS",
    )

    # --------------------------------------------------
    # 7. Return governed result
    # --------------------------------------------------

    return {
        "request_id": request_id,
        "executed": True,
        "decision": decision.decision.value,
        "result": customer_data,
    }
