# AI-A05 Day 4 — Security Hardening and Operational Readiness

**Date:** 8 November 2026
**Scope:** Local Python 3.12 / FastAPI / OPA prototype
**Security posture:** Demonstrator; not production certified

## Executive summary

Day 4 strengthens the A05 execution paths that can be protected within this repository. JWT verification remains mandatory for protected API operations. Policy and pre-execution audit failures block protected execution. Finance approval state and lifecycle events now persist in SQLite, and approval consumption is atomic across concurrent callers on the same host. MCP authorization carries a validated tool argument object into the OPA input, while the A05-to-A04 adapter remains limited to a synthetic customer lookup.

The key external trust boundary remains open: A04's local policy uses `AI_A04_ROLE` from its process environment. A05 cannot secure an independently launched or directly reachable A04 MCP server. No A04 files were changed. All finance operations continue to call the simulated handler; there is no real payment integration.

## Architecture and trust boundaries

1. **API caller → A05:** The FastAPI dependency requires a bearer token and verifies RS256 signature, issuer, audience, required time claims, token ID, subject, and role shape using the configured public key. Protected endpoints derive the actor from the verified identity; caller-supplied `agent_id` on the evaluation endpoint must match it.
2. **A05 → policy:** Finance and MCP evaluations call the local OPA binary with structured input. Invalid output, nonzero exit, timeout, or unavailable binary maps to DENY. PEP execution requires PERMIT with no unresolved obligations.
3. **A05 → protected finance simulation:** The server-owned registry fixes tool/action/resource. The policy request includes the complete parameter dictionary. Finance approval digests bind action, resource, amount, and currency and are also associated with the requester.
4. **A05 → audit:** Authorization is audited before protected execution. Audit JSONL files are appended with restrictive file permissions, flushed, and synced. They remain mutable local files, not tamper-proof evidence. Finance approvals also keep lifecycle evidence transactionally alongside SQLite state.
5. **A05 → A04 MCP:** The A05 adapter authorizes the JWT-derived role, validates the known call shape, records authorization before subprocess launch, restricts invocation to `get_customer`, and validates the result. Its child process receives a small environment allowlist plus `AI_A04_ROLE=reader`; A04 loads its own database settings from its project `.env`. This only governs calls through this adapter.
6. **Direct A04 access:** A04's development policy treats an environment variable as the role and does not authenticate the A05 identity. Anyone able to launch A04 or select its environment may choose that role. Any transport exposed outside the adapter is not protected by A05.

The updated component view is [diagrams/02-component-architecture.mmd](../../diagrams/02-component-architecture.mmd). The approval state flow is [diagrams/04-approval-lifecycle.mmd](../../diagrams/04-approval-lifecycle.mmd).

## Threat model and review findings

| Threat or bypass path | A05 control implemented | Evidence and remaining boundary |
|---|---|---|
| Missing, forged, expired, wrong-issuer or wrong-audience JWT | RS256-only verification, required claims, 401 on invalid credentials | `tests/security/test_agent_identity.py`; a compromised signing key or stolen still-valid token remains usable until expiry |
| Caller substitutes another agent ID | Identity is taken from JWT; evaluation endpoint checks body ID equality | `tests/security/test_authenticated_api.py` and `test_authenticated_tool_execution.py` |
| Unknown or approval-required tool call reaches handler | Server-owned registry; PEP executes only explicit PERMIT with no obligations | `tests/integration/test_tool_registry.py`; simulation only |
| OPA unavailable, malformed, or timed out | Policy adapters return DENY; PEP fails closed | `tests/unit/test_enforcement.py`, `tests/security/test_mcp_authorization.py`; API OPA failure is operationally indistinguishable from policy denial in the user-facing response |
| Authorization audit unavailable before protected execution | PEP and finance workflow deny before handler call; A04 adapter raises before subprocess launch | `tests/security/test_mcp_audit_failures.py`, finance workflow audit-failure tests |
| Approval changed, replayed, consumed concurrently, self-approved, or expired | Requester and canonical operation digest binding; self-approval check; expiry; transactional consume; one winner | `tests/security/test_approval_engine.py` and `tests/integration/test_finance_approval_workflow.py` |
| Approval state lost on service restart | SQLite persisted rows and lifecycle events, default `runtime/approvals.sqlite3` | Restart recovery test constructs a new engine on the same DB path |
| MCP authorization for unsupported or malformed arguments | Known A04 signatures are checked; extra keys and wrong types are denied; arguments are included in policy input | `tests/security/test_mcp_authorization.py`; validation schema mirrors A04 and must be kept in sync |
| Client treats `/mcp/authorize` response as an execution credential | Endpoint only returns a policy decision; A05 adapter independently reauthorizes before its own execution | A decision response is advisory and not a signed, short-lived capability; clients must not use it as one |
| Caller bypasses A05 and invokes A04 directly | **Not closed by A05** | A04-side authentication and enforcement are required. `AI_A04_ROLE` is client-controlled by design in the A04 development policy. |
| A05 process secrets leak into an A04 child process | Child receives only runtime locale/path variables and the compatibility role value | A04 reads its DB settings from its own `.env`; the live integration path should be revalidated if A04 configuration changes |
| Audit evidence altered, deleted, or lost with host | File mode 0600 and SQLite transaction improve local handling | No remote append-only store, signatures, hash chain, retention/backup automation, or host compromise protection |

## Controls and persistence details

### Approval lifecycle

`ApprovalEngine` stores approval status, requester, operation digest, approver, creation/expiry/consumption timestamps in SQLite. Each create, approve/reject, expiry, and consume transition writes a metadata-only lifecycle event in the same transaction. Consumption uses `BEGIN IMMEDIATE`, expiry checking, and a conditional status/digest/requester update. SQLite serializes same-host writers and provides restart recovery. It does not coordinate several hosts that use independent database files, provide HA, or replace a managed transactional service.

`A05_APPROVAL_DB` overrides the default path. The created database file is restricted to mode 0600. Protect the parent directory and its WAL/SHM sidecars using host permissions. Do not put the database in a source-controlled path or a shared directory writable by untrusted users.

### Audit and execution

Finance authorization records are written before simulation. If this pre-execution write fails, the workflow denies execution and, for a previously approved transaction, does not consume the approval. JSONL records omit request context and carry identity/action/resource/decision metadata. The MCP adapter similarly writes its authorization event before spawning A04. Post-execution audit failure cannot undo an already completed action; this prototype uses simulation only and does not claim atomic action-plus-audit behavior.

### Exact authorization scope

The finance registry binds a fixed tool name to `payment.create` on `erp.payments`. The finance operation digest covers action, resource, amount, and currency; requester identity is separately checked. MCP authorization fixes action=`tool.call` and resource=`a04.mcp`, uses the JWT subject and roles, and validates the tool's known argument keys and value types before evaluation. The adapter's executable scope is narrower than the OPA catalog: only `get_customer(customer_id)` with its demo ID allow-list reaches the subprocess.

## Adversarial and operational validation

The test suite includes invalid JWT signatures/claims, spoofed agent IDs and roles, policy denial and OPA failure, missing audit evidence, MCP subprocess timeout and response failure, argument injection/shape violations, approval digest mismatch, self-approval, expiry, concurrent replay, and restart recovery. Specific file locations:

- JWT: `tests/security/test_agent_identity.py`
- PEP, enforcement and audit: `tests/unit/test_enforcement.py`, `tests/unit/test_audit.py`, `tests/integration/test_enforcement_audit.py`
- MCP argument and policy failures: `tests/security/test_mcp_authorization.py`, `tests/security/test_mcp_audit_failures.py`, `tests/security/test_a04_mcp_adapter.py`
- Approval persistence and races: `tests/security/test_approval_engine.py`, `tests/integration/test_finance_approval_workflow.py`
- Authenticated endpoints: `tests/security/test_authenticated_api.py`, `tests/security/test_authenticated_finance.py`, `tests/security/test_authenticated_mcp.py`

Day 4 validation commands:

```bash
python -m pytest -v
tools/opa_linux_amd64 check policies
python -m pip check
git diff --check
```

The A04 live integration test may be skipped when A04's local Python environment is unavailable. Its success would demonstrate only the adapter path, not protection of direct A04 access.

### Day 4 validation outcome

- The focused approval, finance workflow, MCP authorization, MCP audit-failure, A04 adapter-mock, Rego policy, tool registry, and unit tests passed. A broader run excluding the five existing `TestClient` API test modules and the live A04 integration collected and passed **74 tests**.
- Pytest collected **105 tests** total. The complete `python -m pytest -q` run was attempted with a 60-second cap but did not complete. The live A04 lookup independently fails with `TimeoutExpired` at the adapter's 15-second limit; its denial and invalid-argument integration cases pass. Mocked A04 failure and pre-audit failure tests pass.
- The installed Starlette/httpx2 `TestClient` also hangs for a request against a minimal empty FastAPI application. The stack remains blocked waiting for the AnyIO portal response, so the affected API files could not be verified in this environment. This was reproduced without importing or calling A05 routes.
- `tools/opa_linux_amd64 check policies`, `python -m pip check`, and `git diff --check` passed. `pip check` emitted only a local pip-cache ownership warning. The tracked-file scan found no virtual environment, runtime audit data, private key, or credential files.

## Safe startup, shutdown, and recovery

1. Use the project Python 3.12 environment. Confirm `tools/opa_linux_amd64` is the expected local OPA binary and run `tools/opa_linux_amd64 check policies`.
2. Configure `A05_JWT_PUBLIC_KEY` to a readable public-key PEM from the test issuer. Keep private keys and bearer tokens outside this repository and logs. Configure `A05_APPROVAL_DB` only when a non-default local database path is needed.
3. Bind the demonstrator to loopback: `uvicorn src.api.main:app --host 127.0.0.1 --port 8000`. No Docker service or other repository is needed for local A05-only validation. A04 integration calls the sibling project only when explicitly exercised.
4. Stop with Ctrl-C and wait for the server process to exit before making a filesystem-level SQLite copy. SQLite WAL files may contain committed data until checkpoint/close.
5. Back up the approval DB using SQLite's online backup API or, after clean shutdown, copy the database file. Preserve restrictive permissions. Back up `runtime/audit.jsonl` and `runtime/a04_mcp_audit.jsonl` separately if the local evidence is needed.
6. To recover, stop A05, restore the approval DB to the configured path with owner-only access, restore audit files separately, then restart. Verify a known pending approval is present using a local test or a new engine instance; do not expose approval contents publicly.
7. Runtime files are ignored by Git. Never commit runtime DBs, JSONL audit data, private keys, JWTs, or virtual environments. Rotate/reissue test signing material if private material was exposed.

## Demonstrated properties vs. production requirements

| Demonstrated in this prototype | Required before production use |
|---|---|
| JWT signature and claim verification; fail-closed policy outcome | Managed key distribution/rotation, audience governance, short token TTLs, revocation and issuer operations |
| Pre-execution audit gate on A05 finance/tool execution | Remote durable audit service, tamper evidence, access separation, retention, alerting, tested restore |
| SQLite approval persistence and atomic same-host consume | Managed transactional store, HA, multi-instance concurrency design, migrations, backup/restore drills |
| Fixed simulated finance handler and exact operation digest | Independently protected real tool gateway with idempotency and downstream reconciliation |
| Narrow A05 MCP adapter call | A04 authentication and in-server authorization on every MCP entry point, with no client-selected role env |
| Local test coverage of listed adversarial cases | Independent security assessment, deployment threat modeling, load/fault testing, runtime isolation and monitoring |
