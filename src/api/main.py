from fastapi import FastAPI

from src.contracts.policy import (
    GovernanceRequest,
    GovernanceDecision,
)
from src.policy.opa_adapter import evaluate_policy

app = FastAPI(
    title="AI-A05 Governance Service",
    version="0.1.0",
    description="Independent AI Governance and Policy Enforcement",
)


@app.get("/health")
def health():
    return {
        "status": "running",
        "service": "AI-A05",
    }


@app.post(
    "/governance/evaluate",
    response_model=GovernanceDecision,
)
def evaluate(request: GovernanceRequest):
    return evaluate_policy(request)
