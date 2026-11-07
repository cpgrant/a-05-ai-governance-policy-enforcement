import os
from pathlib import Path

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Security,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from src.contracts.policy import (
    GovernanceRequest,
    GovernanceDecision,
)
from src.identity.jwt_verifier import (
    AgentIdentity,
    AgentAuthenticationError,
    JWTAgentVerifier,
)
from src.policy.opa_adapter import evaluate_policy


app = FastAPI(
    title="AI-A05 Governance Service",
    version="0.2.0",
)

bearer = HTTPBearer(auto_error=False)


def authenticated_agent(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer),
) -> AgentIdentity:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    public_key_path = os.environ.get("A05_JWT_PUBLIC_KEY")

    if not public_key_path:
        raise HTTPException(
            status_code=503,
            detail="Identity verification unavailable",
        )

    try:
        public_key = Path(public_key_path).read_text()
        verifier = JWTAgentVerifier(public_key)
        return verifier.verify(credentials.credentials)

    except AgentAuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (OSError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="Identity verification unavailable",
        )


@app.get("/health")
def health():
    return {"status": "running", "service": "AI-A05"}


@app.post(
    "/governance/evaluate",
    response_model=GovernanceDecision,
)
def evaluate(
    request: GovernanceRequest,
    identity: AgentIdentity = Depends(authenticated_agent),
):
    if request.agent_id != identity.agent_id:
        raise HTTPException(
            status_code=403,
            detail="Agent identity mismatch",
        )

    return evaluate_policy(request)


# Authenticated tool execution prototype.
# Only server-owned handlers are registered.
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from src.audit.recorder import AuditRecorder
from src.tools.registry import (
    RegisteredTool,
    TrustedToolRegistry,
    UnknownToolError,
)
from src.tools.payment import simulated_payment


class ToolExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(min_length=1)
    parameters: dict[str, Any]


tool_registry = TrustedToolRegistry(
    audit=AuditRecorder(Path("runtime/audit.jsonl"))
)

tool_registry.register(
    RegisteredTool(
        name="finance.payment.create",
        action="payment.create",
        resource="erp.payments",
        handler=simulated_payment,
    )
)


@app.post("/tools/execute")
def execute_tool(
    request: ToolExecutionRequest,
    identity: AgentIdentity = Depends(authenticated_agent),
):
    try:
        outcome = tool_registry.execute(
            tool_name=request.tool_name,
            agent_id=identity.agent_id,
            parameters=request.parameters,
        )

    except UnknownToolError:
        raise HTTPException(
            status_code=404,
            detail="Tool unavailable",
        )

    return {
        "agent_id": identity.agent_id,
        "executed": outcome.executed,
        "decision": outcome.decision.decision.value,
        "reason": outcome.decision.reason,
        "result": outcome.result,
    }


from src.integrations.mcp_authorization import authorize_mcp_tool


class MCPAuthorizationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str = Field(min_length=1)


@app.post(
    "/mcp/authorize",
    response_model=GovernanceDecision,
)
def authorize_mcp(
    request: MCPAuthorizationRequest,
    identity: AgentIdentity = Depends(authenticated_agent),
):
    return authorize_mcp_tool(
        identity=identity,
        tool_name=request.tool_name,
    )


# ---------------------------------------------------------
# Authenticated Finance Approval API
# ---------------------------------------------------------

from src.approvals.authenticated_finance import (
    AuthenticatedFinanceService,
)


finance_service = AuthenticatedFinanceService()


class FinancePaymentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: int = Field(gt=0)
    currency: str = "EUR"


class FinanceApprovalDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approve: bool


@app.post("/finance/payments/request")
def request_finance_payment(
    request: FinancePaymentRequest,
    identity: AgentIdentity = Depends(authenticated_agent),
):
    return finance_service.request_payment(
        identity=identity,
        amount=request.amount,
        currency=request.currency,
    )


@app.post("/finance/approvals/{approval_id}/decide")
def decide_finance_approval(
    approval_id: str,
    request: FinanceApprovalDecisionRequest,
    identity: AgentIdentity = Depends(authenticated_agent),
):
    try:
        return finance_service.decide_approval(
            identity=identity,
            approval_id=approval_id,
            approve=request.approve,
        )

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Approval not found",
        )

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Approval not authorized or not pending",
        )


@app.post("/finance/approvals/{approval_id}/execute")
def execute_finance_approval(
    approval_id: str,
    request: FinancePaymentRequest,
    identity: AgentIdentity = Depends(authenticated_agent),
):
    try:
        return finance_service.execute_approved_payment(
            identity=identity,
            approval_id=approval_id,
            amount=request.amount,
            currency=request.currency,
        )

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Approval not found",
        )
