import json
import subprocess
from pathlib import Path

from src.contracts.policy import (
    GovernanceRequest,
    GovernanceDecision,
    PolicyDecision,
)

ROOT = Path(__file__).resolve().parents[2]
OPA_BINARY = ROOT / "tools/opa_linux_amd64"
POLICY_FILE = ROOT / "policies/finance.rego"

QUERY = "data.governance.finance.decision"


def evaluate_policy(
    request: GovernanceRequest,
) -> GovernanceDecision:
    try:
        result = subprocess.run(
            [
                str(OPA_BINARY),
                "eval",
                "--data", str(POLICY_FILE),
                "--stdin-input",
                "--format", "raw",
                QUERY,
            ],
            input=json.dumps(request.model_dump(mode="json")),
            text=True,
            capture_output=True,
            timeout=5,
            check=True,
        )

        outcome = PolicyDecision(result.stdout.strip())

        reasons = {
            PolicyDecision.PERMIT:
                "Action permitted by finance policy",
            PolicyDecision.DENY:
                "Action denied by finance policy",
            PolicyDecision.REQUIRE_APPROVAL:
                "Human approval required by finance policy",
        }

        return GovernanceDecision(
            request_id=request.request_id,
            decision=outcome,
            policy_id="finance",
            policy_version="1.0",
            reason=reasons[outcome],
            obligations=(
                ["human_approval"]
                if outcome == PolicyDecision.REQUIRE_APPROVAL
                else []
            ),
        )

    except (
        subprocess.SubprocessError,
        OSError,
        ValueError,
    ):
        return GovernanceDecision(
            request_id=request.request_id,
            decision=PolicyDecision.DENY,
            policy_id="finance",
            policy_version="1.0",
            reason="Policy evaluation unavailable or invalid",
            obligations=[],
        )
