# AI-A05 — AI Governance & Policy Enforcement

**Version:** 0.2
**Status:** Prototype specification with Day 4 implementation notes
**Python:** 3.12.3
**Portfolio:** AI Architecture Series

## 1. Purpose

AI-A05 is a standalone, reusable governance platform
for AI agents, enterprise tools and autonomous workflows.

It provides enforceable authorization, risk-based autonomy,
human approval, audit evidence, explainability and
governance monitoring.

## 2. Architectural Principles

1. Independent governance service.
2. Mandatory enforcement at protected execution boundaries.
3. Default deny and fail-closed authorization.
4. Separation of policy decisions and execution.
5. Explicit identity and least-privilege authorization.
6. Human oversight for sensitive actions.
7. Traceable, versioned governance decisions.
8. Explainable policy outcomes.
9. Optional sandboxed execution and simulation.
10. Agentic governance is advisory, not authoritative.

## 3. Architecture Planes

### 3.1 Control Plane

Responsibilities:
- Policy administration and versioning
- Governance profile management
- Approval workflow management
- Policy testing and simulation
- Compliance mappings
- Governance configuration

### 3.2 Decision Plane

Responsibilities:
- Policy evaluation using OPA/Rego
- Agent and resource authorization
- Risk and autonomy-level checks
- Decision obligations
- Policy decision explanations

Decision outcomes:
- PERMIT
- DENY
- REQUIRE_APPROVAL

OPA provides policy evaluation. The A05 service
maps evaluated policy results into the three
governance outcomes.

### 3.3 Enforcement Plane

Responsibilities:
- Mandatory authorization checks
- Protected tool execution
- Agent delegation authorization
- MCP gateway enforcement
- Approval verification
- Sandbox routing
- Prevention of unauthorized execution

## 4. Governance Services

- Policy Decision Point (PDP)
- Policy Enforcement Point (PEP)
- Policy Administration Point (PAP)
- Identity and Access Control
- Human Approval Service
- Sandbox Controller
- Audit and Evidence Service
- Explanation Service
- Observability Service
- Governance Agent Interface

## 5. Agentic Governance

Optional advisory agents:
- Risk Assessment Agent
- Compliance Assessment Agent
- Audit Investigation Agent
- Policy Recommendation Agent
- Explainability Agent
- Governance Monitoring Agent

Governance agents cannot authorize their own actions,
override enforced policies, or deploy policy changes
without independent authorization.

## 6. Integration Architecture

Supported integration models:
- REST API
- Python SDK / adapter
- MCP enforcement gateway
- A2A delegation adapter
- Sidecar policy decision service

Potential consumers:
- A02 — Agent Orchestration & A2A
- A03 — Enterprise RAG & Knowledge
- A04 — MCP & Enterprise Integration
- A06 — Digital Business Twin
- Independent enterprise applications

Protected actions must pass through an enforcement
boundary even if a client has not explicitly enabled
an optional advisory governance feature.

## 7. Sandbox Architecture

Initial scope:
- Policy dry-run
- Shadow policy evaluation
- Mock enterprise tools
- Synthetic test data

Future scope:
- Strong execution isolation
- Restricted network and filesystem access
- Ephemeral execution environments
- Resource limits and execution monitoring

## 8. Audit and Explainability

Capture:
- Request and correlation identifiers
- Authenticated actor and agent identity
- Requested action and resource
- Relevant decision inputs
- Policy identifier and version
- Decision and explanation
- Required obligations
- Approval evidence
- Execution outcome
- Timestamps and trace identifiers

Sensitive information must be minimized or redacted.

Audit records should be protected against unauthorized
modification. Production deployment requires appropriate
durable storage, integrity controls and retention rules.

## 9. Security Requirements

- Default deny
- Fail closed on authorization failures
- Authenticated callers
- Least privilege
- No direct bypass of protected tool gateways
- Trusted policy distribution
- Separation of duties
- Approval bound to exact action parameters
- Revalidation before execution
- Protection against replay and stale authorizations
- Adversarial and integration testing

## 10. Technology Stack

- Python 3.12
- FastAPI / Uvicorn
- Pydantic v2
- OPA / Rego
- PostgreSQL
- Docker Compose
- OpenTelemetry
- pytest / HTTPX
- Optional LangGraph and Ollama

## 11. Four-Day Delivery

Day 1:
Architecture, ADRs, diagrams, contracts.

Day 2:
Policy decision service and enforcement prototype.

Day 3:
Agent/MCP integrations, approval workflow,
audit events and sandboxed mock actions.

Day 4:
Security validation, operations documentation,
technical report and infographic.

## 12. Initial Acceptance Criteria

1. Governance service runs independently.
2. Policy requests conform to validated contracts.
3. Unauthorized requests are denied.
4. Protected tools cannot execute without authorization.
5. Approval-required actions are suspended.
6. Approval cannot be reused for a different action.
7. Every decision produces structured audit evidence.
8. Decision explanations identify applicable policy rules.
9. Policy evaluation failures block execution.
10. Automated tests validate the demonstrated controls.

## 13. Explicit Limitations

The initial four-day prototype does not claim
production-grade sandbox isolation, regulatory
certification, comprehensive compliance coverage,
or complete tamper-proof audit infrastructure.

Those require additional engineering and validation.

## 14. Day 4 Demonstrated Topology and Trust Boundaries

The running prototype implements the FastAPI API, JWT verification, local OPA/Rego evaluation, a server-owned simulated finance tool, local JSONL audit output, and a SQLite-backed finance approval state machine. The `runtime/` directory is local operational state and is excluded from version control. Approval rows and lifecycle event rows are stored in one SQLite database; lifecycle state changes and their corresponding events use a transaction. Consumption is serialized with `BEGIN IMMEDIATE` and a conditional update, and remains bound to the requester and a digest of action, resource, amount, and currency.

The A05 MCP integration is a client/adapter boundary, not an independently protected MCP server. For calls through the A05 adapter, A05 authenticates the JWT, checks the identity role in the A05 policy, validates the known tool argument shape, audits authorization before invocation, and restricts actual execution to the synthetic `get_customer` operation. The adapter sets `AI_A04_ROLE=reader` only for its own child process. A04's development policy reads that environment value and does not verify the A05 agent identity. A04 may also be launched or contacted outside the adapter. Therefore A05 cannot claim to secure direct A04 access. A04 must independently authenticate its caller, derive authorization from trusted identity, validate arguments and enforce policy at each MCP tool boundary before that claim can be made.

SQLite is suitable for restart recovery and single-host concurrency in this demonstrator; it is not a distributed lock service, HA database, or tamper-resistant evidence store. JSONL and SQLite files require OS-level access protection, backup, retention, and integrity controls in any deployment. The implementation does not provide key rotation, token revocation, rate limiting, network isolation, process sandboxing, or production secret management.

The complete control-by-control assessment, adversarial validation, and safe operation steps are in [the Day 4 report](reports/AI-A05-Day-4-Security-and-Operational-Readiness.md).
