# AI-A05 — Comprehensive Technical Project Report

**Project:** AI Governance & Policy Enforcement
**Report scope:** Four-day architecture, implementation, integration, validation, security hardening, and operational readiness
**Implementation status:** Local engineering prototype; not production certified
**Python target:** 3.12
**Evidence date:** 8 November 2026

## Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Context and Motivation](#2-business-context-and-motivation)
3. [Objectives, Scope and Non-Goals](#3-objectives-scope-and-non-goals)
4. [Architectural Principles](#4-architectural-principles)
5. [Complete System Architecture](#5-complete-system-architecture)
6. [Technology Stack and Rationale](#6-technology-stack-and-rationale)
7. [Day 1 — Architecture and Contracts](#7-day-1--architecture-and-contracts)
8. [Day 2 — Policy Enforcement and Tool Governance](#8-day-2--policy-enforcement-and-tool-governance)
9. [Day 3 — Authentication, MCP Integration and Human Approvals](#9-day-3--authentication-mcp-integration-and-human-approvals)
10. [Day 4 — Security Hardening and Operational Readiness](#10-day-4--security-hardening-and-operational-readiness)
11. [Identity, Authentication and Authorization](#11-identity-authentication-and-authorization)
12. [OPA/Rego Policy Decisions and Enforcement](#12-oparego-policy-decisions-and-enforcement)
13. [A04 MCP Enterprise Integration](#13-a04-mcp-enterprise-integration)
14. [Human Approval and Finance Workflow](#14-human-approval-and-finance-workflow)
15. [Auditing, Persistence and Recovery](#15-auditing-persistence-and-recovery)
16. [End-to-End Execution Scenarios](#16-end-to-end-execution-scenarios)
17. [Threat Model, Trust Boundaries and Residual Risks](#17-threat-model-trust-boundaries-and-residual-risks)
18. [Testing Strategy and Verified Results](#18-testing-strategy-and-verified-results)
19. [Operational Runbook](#19-operational-runbook)
20. [Integration with A01–A04 and Future A06](#20-integration-with-a01a04-and-future-a06)
21. [Architecture Decisions and Trade-offs](#21-architecture-decisions-and-trade-offs)
22. [Production Readiness Gap Assessment](#22-production-readiness-gap-assessment)
23. [Conclusions and Next Steps](#23-conclusions-and-next-steps)
24. [Appendices: Repository Structure, Diagrams, Tests and References](#24-appendices-repository-structure-diagrams-tests-and-references)

## 1. Executive Summary

AI-A05 is a four-day engineering prototype that demonstrates how an organization can place explicit checks around actions initiated by AI agents. Before a protected action runs, the service can verify who the agent is, consult business rules, require a person to approve a sensitive request, and record decision and execution metadata. The demonstration uses simulated payments; it does not connect to a payment network or move money.

The service is implemented in Python with FastAPI, signed JSON Web Tokens (JWTs), Open Policy Agent (OPA) and Rego policies, a trusted tool registry, SQLite-backed finance approvals, and local JSON Lines audit files. It also contains an adapter that makes a narrow, governed customer lookup call into the related A04 Model Context Protocol (MCP) project.

The four-day progression moved from architecture and contracts to policy enforcement, authenticated tool use and approvals, then to security review and operational documentation. The key implemented safeguards include default-deny policy behavior, fail-closed handling of policy failures, execution only through registered server-owned handlers, approval binding to the requester and exact operation, and atomic one-time approval consumption on a single host.

This is evidence of selected controls in a local demonstrator, not a production security guarantee. The most important unresolved boundary is A04 direct access: A04's development authorization trusts an `AI_A04_ROLE` process environment variable and does not authenticate A05's caller. The A05 adapter governs only traffic routed through itself. Other gaps include non-managed signing keys, no token revocation, mutable local audit files, single-host SQLite, no high-availability design, and no isolated execution sandbox.

## 2. Business Context and Motivation

AI agents can call tools that read customer information, update business records, or initiate financial workflows. An enterprise therefore needs more than a model-level instruction such as “be careful.” It needs enforcement at the boundary where a request becomes a tool operation, a clear relationship between the authenticated principal and its permitted actions, human oversight for selected risk levels, and records that support investigation.

A05 explores that control pattern as an independently runnable governance service. Its business value in this project is illustrative: it shows how policies can define autonomy bands, how a sensitive request can enter an approval lifecycle, and how the action can be checked again at execution time. It does not demonstrate a complete enterprise governance operating model, certified compliance controls, or integration to live business transaction systems.

The financial examples use Euro amounts and the policy currently encoded in `policies/finance.rego`. The examples are deterministic simulations: €2,000 is within the automatic-permit range, €12,000 falls in the approval range, and €60,000 exceeds the policy ceiling and is denied.

## 3. Objectives, Scope and Non-Goals

### Objectives demonstrated

- Define stable governance request and decision contracts.
- Verify caller identity from a signed JWT before protected API operations.
- Evaluate finance and MCP requests using local OPA/Rego policies.
- Enforce decisions before executing a server-owned tool handler.
- Demonstrate explicit human approval for selected finance operations.
- Persist approval lifecycle state and metadata events across process restart.
- Record authorization and execution events in local JSONL files.
- Exercise a governed, limited A05-to-A04 MCP adapter path.
- Document security limits, recovery procedures, and operational assumptions.

### In scope

The repository implements a FastAPI service, JWT verifier, governance contracts, policy adapters, finance policy, MCP policy, policy enforcement point (PEP), server-owned tool registry, simulated finance handler, approval API and state machine, audit recorders, and A04 adapter. Tests cover unit behavior, API paths, approval workflows, authentication, and selected security cases.

### Non-goals and exclusions

- Real payment execution, banking connectivity, or ERP write integration.
- A production-grade policy administration/control plane or policy distribution service.
- A general purpose MCP gateway that secures every A04 transport.
- Production key lifecycle, rotation, revocation, or identity federation.
- Multi-host approval coordination, high availability, or disaster recovery service.
- Tamper-proof or remotely managed audit evidence.
- A production execution sandbox, regulatory certification, or comprehensive compliance mapping.
- Completed A06 Digital Business Twin integration. A06 appears as a future consumer in architecture planning only.

## 4. Architectural Principles

The architecture specification defines an independent governance service, mandatory checks at protected execution points, default-deny behavior, separation of policy decision and execution, explicit identity, least privilege, human oversight, traceable decisions, and explainable outcomes. The implementation realizes a subset of those principles locally:

| Principle | Implemented evidence | Boundary |
|---|---|---|
| Independent governance | A05 is a separate FastAPI application and repository from A04. | A04 does not delegate all authorization to A05. |
| Decision and execution separation | OPA adapter evaluates; PEP/finance workflow gates handler calls. | Tool coverage is limited to demo handlers. |
| Default deny / fail closed | Rego defaults to `DENY`; OPA errors map to denial; PEP requires explicit permit. | API response may not distinguish policy denial from evaluator outage. |
| Identity from trusted authentication | Protected endpoints derive agent identity and roles from a verified JWT. | JWT signing key operations and revocation are outside the prototype. |
| Human oversight | `REQUIRE_APPROVAL` produces a persistent approval workflow. | This is a local API workflow, not a staffed enterprise case-management service. |
| Traceability | Structured decision/execution JSONL and approval lifecycle rows. | Local files/database can be changed or lost by host administrators. |
| Exact approval scope | Requester plus canonical operation digest and expiry are checked on consume. | Consume and downstream action are not one atomic transaction. |
| Advisory governance cannot override enforcement | Only code paths that call A05 enforcement are governed. | Direct A04 calls remain an open bypass boundary. |

## 5. Complete System Architecture

A caller sends an HTTP request with a bearer token to the A05 FastAPI application. The authentication dependency verifies the token and constructs an `AgentIdentity`. Business routes then send structured inputs to the relevant local OPA policy adapter. Depending on the result, the request is denied, returned as a policy decision, routed into approval, or passed to a server-owned handler. Audit writes are made around protected execution. Finance approvals live in SQLite.

### Component responsibilities

| Component | Implementation | Responsibility |
|---|---|---|
| API | `src/api/main.py` | Health, authenticated governance evaluation, simulated tool execution, MCP authorization, finance request/decision/execute endpoints. |
| Identity verifier | `src/identity/jwt_verifier.py` | RS256-only signature and claim validation; converts trusted claims into immutable identity data. |
| Contracts | `src/contracts/policy.py` | Pydantic governance request, decision enum, policy version, explanation, obligations, timestamp. |
| Policy adapters | `src/policy/opa_adapter.py`, `src/integrations/mcp_authorization.py` | Invoke local OPA binary with structured JSON input and map outcomes. |
| Policy files | `policies/finance.rego`, `policies/mcp.rego` | Finance autonomy thresholds and role/tool decisions. |
| PEP | `src/enforcement/pep.py` | Fail-closed enforcement; blocks non-permit or unresolved-obligation outcomes; audits before action. |
| Tool registry | `src/tools/registry.py` | Maps a known tool name to a fixed action/resource, validation function, and server-owned handler. |
| Finance handler | `src/tools/payment.py` | Returns a simulation result with an explicit no-real-payment message. |
| Approval service | `src/approvals/` | Authenticated role gate and finance workflow for request, decision, re-evaluation, consumption, and simulation. |
| Approval store | `src/approvals/engine.py` | SQLite state machine, lifecycle events, expiry, exact-operation digest, transactional one-time consume. |
| Audit | `src/audit/recorder.py`, `src/integrations/mcp_audit.py` | Append metadata-only JSONL audit events with restrictive file mode and flush/sync behavior. |
| A04 adapter | `src/integrations/a04_mcp_adapter.py` | Authorizes and audits one synthetic customer lookup before invoking A04 in a subprocess. |

### Data and trust flow

1. The API verifies the bearer token using the public key path in `A05_JWT_PUBLIC_KEY`.
2. Endpoint logic builds a request from verified identity and validated request data.
3. The adapter invokes OPA with the policy file and JSON input; the local OPA executable is `tools/opa_linux_amd64`.
4. A policy response is mapped into `PERMIT`, `DENY`, or `REQUIRE_APPROVAL`.
5. Execution paths require an explicit permit or a currently valid approval and record pre-execution audit evidence.
6. Finance approval state and its lifecycle events persist to SQLite under `A05_APPROVAL_DB` or `runtime/approvals.sqlite3` by default.
7. The A04 helper launches a child Python process with a reduced environment and limits its own invocation to `get_customer`.

The architecture is local-process oriented. The OPA binary is invoked as a subprocess rather than as a remote policy service. Runtime files and the sibling A04 environment are local dependencies, so moving the prototype to another host requires explicit path, key, policy, and integration configuration.

## 6. Technology Stack and Rationale

| Technology | Role and rationale in this prototype |
|---|---|
| Python 3.12 | Primary language for service, policies integration, adapters, and tests. |
| FastAPI | HTTP API framework with dependency-based authentication and Pydantic request validation. |
| Pydantic v2 | Validates and serializes governance contracts and API bodies. Several request models reject extra fields. |
| PyJWT with cryptography | Verifies RS256 JSON Web Tokens against a configured PEM public key. |
| Open Policy Agent (OPA) | Local policy evaluation engine. It returns data decisions; A05 interprets those decisions. |
| Rego | Declarative policy language used to encode finance thresholds and MCP role/tool rules. |
| SQLite | Single-host durable state for approvals and their lifecycle events; enables restart recovery and transactional consumption. |
| JSON Lines (JSONL) | Human-inspectable append-oriented local event records, one JSON object per line. |
| pytest and HTTPX | Unit, integration, API, and security behavior tests. |
| Uvicorn | ASGI server for local execution. |
| MCP | Protocol used by sibling A04 to expose enterprise-style tools; A05 integration is a narrow local adapter. |

The architecture specification also lists PostgreSQL, Docker Compose, OpenTelemetry, optional LangGraph, and Ollama as candidate technologies. They are not the implemented A05 runtime stack described here. The current project does not configure a PostgreSQL service, container deployment, or OpenTelemetry instrumentation.

## 7. Day 1 — Architecture and Contracts

Day 1 established the independent governance-service concept and recorded its intended planes: control, decision, and enforcement. It introduced four Architecture Decision Records (ADRs), five Mermaid diagrams, and the governance request/decision contracts.

A `GovernanceRequest` carries a request ID, agent ID, action, resource, and context dictionary. A `GovernanceDecision` carries the same request ID, decision, policy ID/version, explanation, obligations, and evaluation timestamp. The decision enum has three values: `PERMIT`, `DENY`, and `REQUIRE_APPROVAL`.

The architecture specification is broader than the implementation. Its control plane includes policy administration/versioning, governance profiles, compliance mappings, and simulation; its service list also names sandboxing, explanation, monitoring, and advisory governance agents. These are design concepts, not delivered services. The delivered scope is the local API, decision adapters, enforcement, approval, audit, and demonstrated integrations.

### Day 1 architecture outputs

- Independent A05 boundary to keep governance policy separate from consuming business tools.
- Initial contracts and architectural planes.
- ADRs describing independent governance, fail-closed enforcement, human approval, and audit explainability.
- System context and component view to show intended relationships and protected boundaries.

## 8. Day 2 — Policy Enforcement and Tool Governance

Day 2 implemented local OPA/Rego evaluation, the policy enforcement point, a trusted tool registry, simulated payment handler, and audit recorder. The tool registry is the trusted mapping from the public tool identifier to fixed internal action, resource, validation, and handler. Callers cannot supply a Python handler or choose the policy resource through the API.

The PEP verifies that the decision relates to the request and executes only when the decision is exactly `PERMIT` and no obligations remain. If a policy adapter returns an error or invalid output, it returns `DENY`. The registry validates the arguments before entering the PEP. Audit authorization is recorded before invoking the handler; inability to record required audit evidence blocks execution.

This model demonstrates a reference enforcement point, but it cannot protect code paths that bypass the registry or run outside A05. Each real downstream execution boundary would need equivalent enforcement, identity validation, argument validation, and audit behavior.

## 9. Day 3 — Authentication, MCP Integration and Human Approvals

Day 3 added API authentication, identity-aware finance roles, MCP authorization, the A04 adapter, and a person-in-the-loop approval lifecycle. The service accepts bearer JWTs on protected endpoints. The `/mcp/authorize` endpoint evaluates a tool and argument request, but its response is a policy decision rather than an execution credential. The A05 A04 adapter independently authorizes before its subprocess call.

Finance operations were separated into request, approve/reject, and execute phases. The `finance_approver` role is required to decide an approval. The requester cannot approve their own operation. Execution re-evaluates current policy, verifies that the policy still requires approval, checks that the approval belongs to the requester and exact operation, consumes it once, then invokes the simulation.

Day 3 established the human oversight pattern; Day 4 moved the state from process memory into SQLite. The current Day 4 architecture documentation supersedes the earlier in-memory approval description in the module docstring.

## 10. Day 4 — Security Hardening and Operational Readiness

Day 4 tightened the repository-local boundaries and documented operational practices. Work included persistent approval state, transactional lifecycle evidence, atomic same-host consumption, exact MCP argument validation before policy evaluation, reduced child environment for A04, pre-execution audit gating, threat review, diagrams, and a recovery runbook.

The strongest concrete improvement was approval consumption: the SQLite transaction serializes writers with `BEGIN IMMEDIATE`; consumption uses expiry, requester, digest, and status conditions in a conditional update. Tests cover concurrent attempts and restart persistence. This provides a single winner when multiple local callers race against one database file.

The change does not make downstream action and approval consumption a single atomic operation. If the process crashes after an approval is committed as consumed and before the simulation/handler call completes, the approval remains consumed and the operation may not have occurred. In a real system, idempotency keys and a durable execution/outbox design would be needed to reconcile this window.

Day 4 also made the A04 trust boundary explicit. The adapter only controls requests made through the adapter. A04's independent process policy uses `AI_A04_ROLE` from its environment and does not verify the A05 agent JWT; direct A04 execution remains outside A05's protection.

## 11. Identity, Authentication and Authorization

### JWT validation

The FastAPI authentication dependency requires an HTTP bearer token. It reads the configured public key from `A05_JWT_PUBLIC_KEY`. The verifier accepts only the `RS256` algorithm and validates signature, issuer (`ai-a05-dev-issuer` by default), audience (`ai-a05-governance` by default), expiration, issued-at and not-before timing, and required claims `sub`, `iss`, `aud`, `exp`, `iat`, and `jti`. It also requires a non-empty string subject and token ID and a list of non-empty string roles.

The resulting `AgentIdentity` is immutable and carries agent ID, roles, issuer, and token ID. Endpoints use this identity rather than trusting a caller-provided actor. The general governance evaluation endpoint additionally rejects a request whose `agent_id` does not match the verified subject. The finance approver role check is performed in the authenticated finance service.

Missing credentials or invalid tokens are rejected. If key configuration or key file access is unavailable, the API reports verification unavailable and does not proceed. The verifier has no token-revocation lookup, key rotation workflow, certificate discovery, issuer management, or distributed identity cache. A stolen still-valid token remains a risk until it expires or the signing key is changed operationally.

### Authorization layers

Authorization is not one global check. It is applied at several local boundaries:

- JWT identity establishes the caller principal and roles.
- OPA evaluates policy inputs such as agent, role, action, resource, amount, currency, tool, and arguments.
- The registry constrains callable names and fixes action/resource/handler mappings.
- The PEP gates the actual handler call.
- The authenticated finance service gates approval decisions by role.
- The approval engine enforces requester, approver separation, operation digest, expiry, state, and one-time use.
- The A04 adapter adds a separate A05 decision and argument restriction for its own child process.

The API does not become a complete authorization gateway for any external system merely because it offers a decision endpoint. A downstream system must authenticate the caller and enforce authorization itself or accept a protected, verifiable capability at its own entry point.

## 12. OPA/Rego Policy Decisions and Enforcement

OPA is the policy decision engine; Rego is its policy language. A05 supplies structured JSON input and queries a named decision document from a bundled local OPA binary. The adapters parse the raw result into the A05 decision enum. Process errors, timeouts, invalid values, or unavailable binaries are converted to `DENY`.

### Finance policy

`finance.rego` authorizes only `finance-agent` for action `payment.create`, resource `erp.payments`, currency EUR, and positive numeric amount. Its autonomy bands are:

| Amount | Policy result | Workflow behavior |
|---:|---|---|
| €2,000 | `PERMIT` | Record authorization, then call simulated handler and record execution. |
| €12,000 | `REQUIRE_APPROVAL` | Create a pending approval; do not execute until an authorized human approves and the requester later executes the exact request. |
| €60,000 | `DENY` | Return denied; no approval is created and no handler runs. |

The implemented policy uses thresholds `amount <= 5000` for permit and `5000 < amount <= 50000` for approval. Values outside the authorized identity/action/resource/currency/positive-amount conditions default to deny. Note that generic `/tools/execute` does not create an approval; it returns the policy outcome and never executes an approval-required operation. The separate `/finance/payments/request` API implements the approval lifecycle.

### MCP policy

`mcp.rego` maps tool categories to role sets under action `tool.call` and resource `a04.mcp`. `reader` can access customer, ERP, and finance categories defined by the policy; `finance_reader` can access customer and finance categories but not ERP. The adapter first validates known tool argument shapes and sends the validated arguments into OPA input. Unknown tools and malformed or extra arguments deny.

### Policy enforcement points

The PEP is used by the trusted registry. The finance workflow independently implements the policy and audit/approval sequence before calling the simulated handler. The A04 helper separately calls MCP authorization before spawning its subprocess. Enforcement therefore exists in these three code paths, not as a transparent interception layer across arbitrary software.

## 13. A04 MCP Enterprise Integration

A04 is the sibling project `../a-04-mcp-enterprise-integration`. It provides MCP server/client components and synthetic enterprise-style customer, ERP, CRM, and finance reads. A05's `execute_a04_tool` helper uses a local subprocess to start the A04 MCP client path and returns structured data for a narrowly allowed synthetic customer lookup.

Before launching A04, the adapter derives identity from the verified A05 JWT object, validates the tool name and arguments, evaluates the MCP policy, and records an authorization audit event. It only permits actual invocation of `get_customer` with `customer_id` in the demo allow-list (`C001`, `C002`) and with exactly that argument key. The subprocess has a timeout and receives only selected environment variables plus `AI_A04_ROLE=reader`; it does not inherit ambient A05 secrets. The returned data must be a dictionary with an ID matching the requested customer. The adapter logs execution outcome metadata without customer payloads.

The MCP policy catalog is broader than the executable adapter. Authorization decisions for other known A04 tools do not mean the A05 adapter will execute them. The adapter explicitly blocks every executable name except `get_customer`.

### Open A04 direct-access boundary

A04's development policy reads `AI_A04_ROLE` from the process environment. A04 does not validate the calling A05 JWT or require a mutually authenticated service identity. A client that can launch A04 or reach an exposed A04 transport may choose the environment role and avoid A05 entirely. Therefore A05's adapter-side checks do not secure A04 itself.

Closing this boundary requires A04-side work: remove client-selectable role authorization; authenticate A05 or another trusted service identity at every A04 transport; derive roles from trusted identity; validate tool names and arguments and enforce policy inside A04 before every tool handler; and control network/process access so bypass routes are unavailable. That remediation is not implemented in this A05 repository.

## 14. Human Approval and Finance Workflow

A finance request goes through these stages:

1. **Request:** The authenticated agent submits amount and currency. OPA evaluates current policy. A permit request is audited and simulated immediately. A request requiring approval is stored as `PENDING`; a denial ends the flow.
2. **Decision:** A JWT identity must contain `finance_approver`. The approval engine rejects self-approval and only permits a decision while state is `PENDING`. It stores `APPROVED` or `REJECTED` with approver identity and a lifecycle event.
3. **Execution:** The original requester submits the approval ID and operation again. Policy is re-evaluated. It must still return `REQUIRE_APPROVAL`. The service records authorization before consumption, then atomically consumes an unexpired matching approval, and only then calls the simulated handler.

The operation hash is SHA-256 over canonical JSON of action, resource, amount, and currency. The approval row separately stores the requester identity. Consumption checks status, requester, expiry, and digest. This prevents changing amount/currency/action/resource, switching to another requester, using a rejected/expired approval, or reusing a consumed approval.

SQLite guarantees local transaction semantics for the approval file, but approval consumption and the external operation are separate actions. In this prototype the operation is an in-process simulation. For a real payment or remote tool, a crash after consumption but before action can lose the request; a crash after action but before success audit can leave an executed operation with incomplete evidence. A downstream idempotency key and reconciliation workflow are needed before any real execution scenario.

## 15. Auditing, Persistence and Recovery

### JSONL audit

The audit recorder writes structured metadata such as request ID, agent, action, resource, decision, policy/version, explanation, executed flag, status, event type, and timestamp. Finance audit does not copy full request context. MCP adapter audit omits customer payloads. Files are opened with append semantics, set to mode `0600`, flushed, and synced. Pre-execution audit failure blocks protected execution. A post-execution audit failure cannot reverse an action that has already happened.

These are local files, not tamper-proof records. Host administrators can modify/delete them; the files can be lost with the host; no remote collection, cryptographic chain/signatures, retention system, alerting, or independent access control is implemented.

### SQLite approval state

The default database is `runtime/approvals.sqlite3`; `A05_APPROVAL_DB` may override it. It stores approvals and lifecycle events in separate tables. The transition and corresponding event are committed in the same transaction. The database file is set to mode `0600`, while its parent directory and WAL/SHM sidecars still depend on OS-level protection.

SQLite and `BEGIN IMMEDIATE` provide serialized same-host writes and restart recovery. They do not provide a distributed lock across independent database copies, multi-host HA, automated schema migrations, or managed backup. The local runtime files are ignored by Git and must not be committed.

### Recovery steps

Stop the service cleanly before making a filesystem copy. For live backup, use SQLite's online backup API; otherwise copy after shutdown so WAL state is handled safely. Preserve restrictive permissions. Back up approval DB and JSONL audit files separately. Restore with A05 stopped, verify ownership and mode, then start and confirm a known pending approval in a local controlled check. Do not expose approval details publicly.

## 16. End-to-End Execution Scenarios

### Scenario A — €2,000 automatic simulation

An authenticated `finance-agent` sends `POST /finance/payments/request` with amount 2000 and EUR. JWT identity is verified. OPA returns `PERMIT`. The service records an authorization event before calling `simulated_payment`; the result explicitly says no real payment was executed. An execution event is then appended. If pre-execution audit fails, the handler is not called.

### Scenario B — €12,000 approval and simulation

The same agent requests 12000 EUR. OPA returns `REQUIRE_APPROVAL`, and the workflow persists a pending approval with a five-minute default lifetime and a `CREATED` event. A separate identity with `finance_approver` decides approval; self-approval is rejected. The requester calls the execute route with the same amount/currency and approval ID. Current policy is evaluated again. If still in the approval band, A05 records authorization and attempts atomic exact-operation consumption. Only the winning consume invokes the simulation. A changed request, other requester, expired approval, policy change, or replay fails closed.

### Scenario C — €60,000 denial

The same identity requests 60000 EUR. It is above the policy maximum, so OPA returns `DENY`. No pending approval is created, and no payment handler executes. The policy is the authority for this prototype's threshold; a future finance deployment would need approved policy governance, testing, and change control.

### Scenario D — A04 customer lookup through A05

A valid JWT is converted into `AgentIdentity`. The adapter validates `get_customer` and a permitted demo ID, checks OPA, writes a pre-launch audit event, then runs the sibling A04 client in a subprocess with a reduced environment and reader role. It verifies the returned customer ID and audits the result. Direct A04 access is not governed by this flow.

## 17. Threat Model, Trust Boundaries and Residual Risks

| Threat | Implemented control | Residual risk / boundary |
|---|---|---|
| Missing, forged, expired, wrong-issuer or wrong-audience token | RS256-only verification and required claim checks. | Compromised key and stolen unexpired token remain effective; no revocation. |
| Agent ID/role spoofing in request body | Protected identity is derived from JWT; evaluate endpoint checks actor equality. | Token issuer/key governance is external. |
| Unknown or malformed tool request | Registry and request validation; explicit known argument schemas. | Registry/schema drift and future handler mistakes require review. |
| OPA failure or malformed decision | Adapters return DENY; PEP does not execute. | Operational outage can look like policy denial to caller. |
| Audit unavailable before execution | PEP, finance, and adapter gates block action before invocation. | Post-action audit can fail after action; no atomic audit/action. |
| Approval replay or parameter substitution | Digest, requester, expiry, state and atomic consumption checks. | Crash window between consumption and action; only local DB concurrency. |
| Approval loss/restart | SQLite persistent state and restart test. | Host/database loss without backup loses approvals. |
| Direct A04 invocation | None in A05 for direct paths. | Open bypass; A04 process role is environment-selected. |
| Audit alteration/deletion | Append mode, restrictive file mode, fsync. | Not tamper-proof or remote; privileged host user can alter evidence. |
| Child process secret exposure | Reduced environment allowlist. | Adapter still grants A04's development reader role; A04 config assumptions may change. |
| Malicious or compromised handler | Fixed demo handler and narrow adapter scope. | No runtime sandbox, network isolation, resource limits, or independent execution gateway. |
| Denial of service / resource exhaustion | Subprocess timeouts exist for policy and A04 calls. | No API rate limiting, quotas, load shedding, or HA. |

Trust zones are the external caller, A05 API process, local OPA/policy files, local SQLite and audit files, A05-to-A04 subprocess boundary, and A04's own process/transports. A05 controls only requests that pass through the A05 boundary. Identity, policy, audit, and execution guarantees must be independently repeated at any downstream protected boundary.

## 18. Testing Strategy and Verified Results

The test suite is organized into unit, integration, and security folders. Unit tests cover contracts, enforcement, and audit behavior. Integration tests exercise API flows, tool registry, finance approval lifecycle, and adapter behavior. Security tests cover JWT claims/signature, identity spoofing, role authorization, malformed tool arguments, OPA failure, audit failures, approval replay, expiry, self-approval, concurrent consumption, and restart recovery.

The Day 4 security report records that an earlier Codex environment run had timeout problems: a complete 105-test run did not finish under its 60-second cap, and a separate live A04 customer lookup exceeded its 15-second subprocess timeout. That report records 74 passing tests in a broader subset and a locally reproducible TestClient/AnyIO hang. These are historical environment results, not the final validation result for this report.

A later Ubuntu run recorded **105 passed in 3.25 seconds**. During this report task, the full suite and the requested policy/dependency/diff/link checks were rerun; exact current outcomes are recorded below after the validation commands. A live A04 integration test may be skipped or fail if the sibling environment is absent or unresponsive; that does not establish protection of A04 direct access.

### Validation results for this report

| Check | Result |
|---|---|
| `python -m pytest -v` | Collected 105 tests. The live A04 customer lookup failed at the adapter's integration boundary; subsequent tests passed through the initial enforcement/workflow batch, then the run stalled at `tests/integration/test_governance_api.py::test_health`. Interrupted after roughly 90 seconds with exit 130; this run is incomplete and is not reported as a pass. |
| `tools/opa_linux_amd64 check policies` | Passed (exit 0). |
| `python -m pip check` | Passed: “No broken requirements found.” Pip emitted a local cache ownership warning; the cache was disabled (exit 0). |
| `git diff --check` | Passed (exit 0). |
| Local Markdown links in this report | Passed: 47 links checked, 0 missing. |

The current environment's pytest stall is consistent with the earlier Codex `TestClient`/AnyIO timeout problem described above, but this task's run did not independently prove the exact cause. The later Ubuntu result of 105 passed in 3.25 seconds is recorded as external project evidence, not as the outcome of this current rerun.

## 19. Operational Runbook

### Start

1. Use Python 3.12 and install `python -m pip install -e ".[dev]"` in the local environment.
2. Configure `A05_JWT_PUBLIC_KEY` to a readable public PEM from the trusted test issuer. Keep private keys and bearer tokens outside the repository.
3. Validate policy syntax with `tools/opa_linux_amd64 check policies`.
4. Optionally set `A05_APPROVAL_DB` to a protected local database path.
5. Start on loopback with `uvicorn src.api.main:app --host 127.0.0.1 --port 8000`.
6. Use `/health` for process-level status. This endpoint is not a complete readiness probe for JWT key, OPA, SQLite, or A04 dependencies.

### Operate and investigate

- Correlate requests using the recorded request ID and event timestamps.
- Check policy ID/version and reason alongside execution status.
- Treat `DENY` as non-execution; investigate OPA health separately if denials spike.
- Approval decisions require a verified `finance_approver` token; never approve from the requester identity.
- Protect `runtime/approvals.sqlite3`, its WAL/SHM files, and JSONL logs with OS ownership and restricted permissions.
- Do not use the A05 adapter result as evidence that direct A04 transport access is protected.

### Stop, backup, and recover

1. Stop with Ctrl-C and wait for process exit.
2. Use SQLite online backup while running only if implemented through the SQLite backup API; otherwise copy the database after clean shutdown.
3. Copy audit files separately and preserve permissions.
4. Restore files with the service stopped, then confirm the approval database opens and expected pending records remain.
5. Restart and exercise a controlled local health and approval recovery check.
6. Never commit runtime databases, JSONL logs, private keys, JWTs, or virtual environments.

## 20. Integration with A01–A04 and Future A06

The architecture specification identifies potential consumers A02 (agent orchestration/A2A), A03 (enterprise retrieval and knowledge), A04 (MCP enterprise integration), A06 (Digital Business Twin), and independent enterprise applications. This project demonstrates only a local A04 adapter path and its own finance simulation. It does not establish completed integration with A01, A02, A03, or A06.

A04 is a demonstrated integration at the adapter level: the adapter invokes a synthetic customer lookup through the sibling MCP implementation. The direct A04 trust boundary remains open and must be addressed in A04 itself. A06 is a future architectural consumer, not a delivered integration. Any A01–A03 relationships are likewise portfolio-level possibilities unless supported by a separate implementation and evidence.

## 21. Architecture Decisions and Trade-offs

| Decision | Benefit | Cost / limitation |
|---|---|---|
| Independent governance service (ADR-001) | Separates policy decisions from individual tool implementations. | Consumers must integrate correctly; bypass paths remain possible. |
| Fail-closed enforcement (ADR-002) | Policy outage or invalid result cannot silently permit protected execution. | Availability failure blocks work; caller may see generic denial. |
| Human approval for risk band (ADR-003) | Demonstrates oversight and separation of duties. | Creates workflow state and operational burden; approval is local prototype behavior. |
| Structured audit for explainability (ADR-004) | Supports request-level review and test assertions. | Local mutable files lack enterprise integrity/retention. |
| Local OPA subprocess | Simple deployable policy evaluation without a network service. | Binary/version management, process overhead, local file dependency. |
| SQLite approval store | Lightweight durable state and transactions with no service dependency. | Single-host scope; no cluster coordination or managed HA. |
| JSONL audit files | Simple structured output and human inspection. | No remote durability, access separation, query service, or tamper evidence. |
| A04 subprocess adapter | Isolates environment and limits A05 invocation to a narrow demo operation. | Process/path coupling and no in-server A04 identity enforcement. |
| Synthetic payment handler | Safe demonstration of governance behavior. | Does not prove downstream payment integration or transaction semantics. |

## 22. Production Readiness Gap Assessment

| Area | Demonstrated | Required before production use |
|---|---|---|
| Identity | RS256 JWT signature and claims checked. | Managed issuer/key lifecycle, rotation, revocation, short TTL, federation and monitoring. |
| Policy governance | Local Rego rules and fail-closed evaluation. | Signed/versioned distribution, approval/change control, policy test pipeline, rollback and ownership. |
| Enforcement | PEP and dedicated finance/MCP gates. | Mandatory protected gateway at every real tool boundary, bypass prevention, independent assurance. |
| Human approvals | Role check, self-approval block, exact binding, one-time consume. | Enterprise identity separation, delegated authority, notification, escalation, SLA and immutable case history. |
| Persistence | SQLite with transaction and restart recovery. | Managed database, HA, migration strategy, multi-instance concurrency, backup/restore drills. |
| Audit | Local append-oriented metadata records. | Remote durable append-only storage, integrity proof, retention, access separation, alerting, privacy review. |
| A04 | Narrow adapter path demonstrated. | A04-side authentication and authorization on all transports; eliminate environment-selected role. |
| Runtime security | Loopback startup guidance and subprocess timeout/reduced environment. | TLS/reverse proxy, secrets manager, network policy, process/container isolation, patching and resource limits. |
| Resilience | Fail-closed behavior and local recovery instructions. | Load/fault testing, service health/readiness probes, SLOs, monitoring, HA and incident procedures. |
| Financial execution | Simulation only. | Dedicated payment gateway, idempotency, reconciliation, segregation of duties and end-to-end controls. |
| Assurance | Automated repository tests. | Independent security review, penetration testing, abuse-case coverage, compliance mapping where required. |

The prototype should not be connected to live financial or sensitive enterprise operations without closing these gaps and conducting an independent deployment-specific risk assessment.

## 23. Conclusions and Next Steps

A05 demonstrates a coherent governance path for a small set of local operations: authenticate a caller, evaluate explicit policy, enforce a decision before execution, request approval where policy requires it, bind approval to exact intent, and retain local evidence. The tests and implementation provide useful engineering evidence for this pattern.

The strongest next step is to close the A04 trust boundary at A04's own entry points, then replace local prototype dependencies with operational services appropriate to the deployment: managed identity/key lifecycle, policy change governance, durable audit, managed approval persistence, idempotent execution, monitoring, and tested recovery. Any future A06 integration should consume an explicit A05 contract and enforce policy at every business action boundary. Finance remains simulated until those measures and independent reviews are complete.

## 24. Appendices: Repository Structure, Diagrams, Tests and References

### A. Relevant repository structure

```text
src/
  api/main.py                         FastAPI routes and dependency wiring
  identity/jwt_verifier.py            JWT validation and AgentIdentity
  contracts/policy.py                 Governance request and decision schemas
  policy/opa_adapter.py               Finance OPA invocation
  enforcement/pep.py                  Policy enforcement point
  tools/registry.py                   Trusted tool registry
  tools/payment.py                    Simulated finance handler
  approvals/                          Authenticated finance workflow and SQLite engine
  audit/recorder.py                   Finance/tool JSONL audit
  integrations/                       A04 adapter, MCP policy and MCP audit
policies/
  finance.rego                        Finance autonomy thresholds
  mcp.rego                            MCP tool/role policy
docs/
  AI-A05-Architecture-Specification.md
  adr/                                Four architecture decision records
  reports/                            Security and comprehensive project reports
```

The full project also includes `tests/unit`, `tests/integration`, and `tests/security`; the five diagram source files and rendered assets; ADRs; architecture specification; and the Day 4 security/operations report.

### B. Five architecture diagrams

| View | Mermaid source | PNG rendering | SVG rendering |
|---|---|---|---|
| System context | [Source](../../diagrams/01-system-context.mmd) | [PNG](../../diagrams/rendered/01-system-context.png) | [SVG](../../diagrams/rendered/01-system-context.svg) |
| Component architecture | [Source](../../diagrams/02-component-architecture.mmd) | [PNG](../../diagrams/rendered/02-component-architecture.png) | [SVG](../../diagrams/rendered/02-component-architecture.svg) |
| Policy decision sequence | [Source](../../diagrams/03-policy-decision-sequence.mmd) | [PNG](../../diagrams/rendered/03-policy-decision-sequence.png) | [SVG](../../diagrams/rendered/03-policy-decision-sequence.svg) |
| Approval lifecycle | [Source](../../diagrams/04-approval-lifecycle.mmd) | [PNG](../../diagrams/rendered/04-approval-lifecycle.png) | [SVG](../../diagrams/rendered/04-approval-lifecycle.svg) |
| Audit and operational recovery | [Source](../../diagrams/05-audit-operational-recovery.mmd) | [PNG](../../diagrams/rendered/05-audit-operational-recovery.png) | [SVG](../../diagrams/rendered/05-audit-operational-recovery.svg) |

Each diagram has a Mermaid source plus both PNG and SVG renderings. The diagram set depicts the implemented local prototype and known gaps, not a complete future-state enterprise deployment.

### C. Test inventory

- Unit: policy contracts, PEP decisions/failure behavior, JSONL audit.
- Integration: governance API, tool registry, enforcement/audit, finance approval workflow, live A04 adapter scenarios.
- Security: JWT identity and authenticated APIs, finance roles, approval state machine/concurrency/restart, MCP policy and argument validation, adapter subprocess/audit failure.

### D. Architecture and security references

- [Architecture specification](../AI-A05-Architecture-Specification.md)
- [ADR-001 — Independent governance](../adr/ADR-001-independent-governance.md)
- [ADR-002 — Fail-closed enforcement](../adr/ADR-002-fail-closed-enforcement.md)
- [ADR-003 — Human approval](../adr/ADR-003-human-approval.md)
- [ADR-004 — Audit explainability](../adr/ADR-004-audit-explainability.md)
- [Day 4 security and operational readiness report](AI-A05-Day-4-Security-and-Operational-Readiness.md)
- [Project README](../../README.md)
- [Sibling A04 repository](../../../a-04-mcp-enterprise-integration/README.md)
