import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OPA = ROOT / "tools/opa_linux_amd64"
POLICY = ROOT / "policies/mcp.rego"


@pytest.mark.parametrize(
    "role,tool,expected",
    [
        ("reader", "get_customer_db", "PERMIT"),
        ("reader", "get_inventory_status_db", "PERMIT"),
        ("finance_reader", "list_customer_invoices_db", "PERMIT"),
        ("finance_reader", "get_inventory_status_db", "DENY"),
        ("blocked", "get_customer_db", "DENY"),
        ("administrator", "get_customer_db", "DENY"),
    ],
)
def test_mcp_role_authorization(role, tool, expected):
    request = {
        "resource": "a04.mcp",
        "action": "tool.call",
        "tool_name": tool,
        "roles": [role],
    }

    result = subprocess.run(
        [
            str(OPA),
            "eval",
            "--data", str(POLICY),
            "--stdin-input",
            "--format", "raw",
            "data.governance.mcp.decision",
        ],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=5,
        check=True,
    )

    assert result.stdout.strip() == expected
