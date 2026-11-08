# AI-A05 — Business Governance & Risk Assessment

**Project:** AI-A05 — AI Governance & Policy Enforcement
**Audience:** Executive management, enterprise architecture, risk, compliance, public-sector and regulated-industry leaders
**Assessment basis:** Repository evidence and authoritative public sources reviewed on **8 November 2026**
**Status:** Business and risk assessment of a local engineering prototype; not a legal opinion or compliance attestation

## Purpose and status of statements

This report uses four labels to keep evidence and advice separate:

- **Observed** — directly supported by A05 code, policy, tests or project documentation.
- **External requirement/framework** — sourced from law or an established framework; applicability depends on the organisation and use case.
- **Illustrative** — a proposed operating model, autonomy level, risk method or scenario for discussion, not an A05 feature or validated enterprise assessment.
- **Recommendation** — an action proposed for a future enterprise deployment.

The implementation is a demonstration. It authenticates selected API calls, evaluates local policies, gates selected tool execution, manages a simulated finance approval workflow, and writes local audit data. It does not execute real payments, provide a complete governance management system, or establish that any organisation or system is legally compliant.

## Contents

1. [Executive summary](#1-executive-summary)
2. [The governance challenge](#2-the-governance-challenge)
3. [Enterprise AI governance requirements](#3-enterprise-ai-governance-requirements)
4. [Enterprise risk assessment](#4-enterprise-risk-assessment)
5. [Levels of AI autonomy](#5-levels-of-ai-autonomy)
6. [Financial governance case study](#6-financial-governance-case-study)
7. [Governance operating model](#7-governance-operating-model)
8. [Regulatory and standards considerations](#8-regulatory-and-standards-considerations)
9. [A05 control effectiveness assessment](#9-a05-control-effectiveness-assessment)
10. [Architectural trade-offs](#10-architectural-trade-offs)
11. [Deployment readiness assessment](#11-deployment-readiness-assessment)
12. [Management recommendations](#12-management-recommendations)
13. [Strategic implications for autonomous enterprises](#13-strategic-implications-for-autonomous-enterprises)
14. [Conclusions](#14-conclusions)
15. [Appendices](#15-appendices)

## 1. Executive summary

### The business challenge

AI agents increasingly do more than draft or recommend. When connected to enterprise tools, they may retrieve personal or commercially sensitive information, update records, trigger customer communications, or initiate financial and operational workflows. The business risk therefore moves from the quality of an answer to the authority, context, and consequences of an action.

An organisation remains accountable for delegated work. A model’s confidence, a prompt instruction, or a person’s occasional review is not a substitute for identity controls, defined authority, enforceable business rules, meaningful oversight, reliable records, and a way to stop or recover from unsafe operation.

### What A05 demonstrates

A05 is a practical local case study of a governance pattern: authenticate a caller, evaluate an explicit policy, stop or permit an operation at a controlled execution point, route selected actions to human approval, bind approval to the exact requester and operation, and retain local decision evidence. Its finance operation is simulated. The sibling A04 integration demonstrates one narrow customer lookup through an A05 adapter.

### Principal findings

- **Useful control pattern:** Local tests exercise JWT validation, default-deny policy decisions, registered tool execution, approval separation, exact-operation binding, one-time same-host approval consumption, restart recovery, and pre-execution audit gates.
- **Narrow demonstration:** These controls apply only to the paths implemented in A05. They do not establish complete coverage of all agents, tools, transports, data flows, or business processes.
- **Material trust boundary remains open:** A04 can be launched or reached directly, and its development role is selected through `AI_A04_ROLE`. A05 does not secure that route.
- **Prototype operations:** Audit files are local and mutable; approval storage is single-host SQLite; there is no managed identity lifecycle, revocation, high availability, runtime sandbox, or live payment integration.
- **Risk ratings are not made:** This repository provides no enterprise deployment context, threat likelihood data, asset valuations, control operating history, or risk appetite. The register therefore marks inherent and residual likelihood/impact **Not assessed** rather than assigning invented scores.
- **Regulatory conclusion:** No compliance claim is supported. Legal applicability requires system-specific classification and jurisdictional assessment. A05 has not been assessed or certified against the EU AI Act, GDPR, ISO standards, or sector rules.

### Executive recommendations

1. Keep A05 in research/prototype use and do not connect it to live transactions or sensitive production operations.
2. Close the A04 direct-access boundary inside A04 before treating it as governed integration.
3. Define an enterprise AI inventory, accountable business owner, risk criteria, approval authority, and stop authority before any pilot.
4. Replace local key, persistence, audit, and execution dependencies with managed controls; test recovery, incident response, and bypass resistance.
5. Have legal, privacy, security, operational risk, and internal audit assess the intended use and applicable obligations before deployment decisions.

## 2. The governance challenge

### From assistance to action

A conventional assistant produces information for a person to consider. An autonomous agent may select tools, assemble arguments, make successive decisions, and initiate a change. That shift creates new control questions: who authorised the agent, what authority was delegated, which context was used, what is the largest permitted impact, and where can the action be stopped?

The model remains probabilistic. It can misinterpret instructions, rely on inaccurate information, be influenced by malicious or irrelevant content, or choose an unintended tool. Even a technically correct model can cause harm when access is excessive, policy is stale, a downstream integration is bypassable, or the operating process has no accountable owner.

### Advice versus action

| Mode | Business effect | Governance emphasis |
|---|---|---|
| Advice | Produces information; a person decides whether to act. | Accuracy, disclosure, data protection, review and appropriate reliance. |
| Proposal | Prepares a specific action for approval. | Correct target and parameters, meaningful review, clear approver authority. |
| Bounded execution | Acts automatically within a defined scope. | Strong identity, least privilege, enforceable limits, monitoring, logs, stop/recovery controls. |
| Broad autonomy | Plans and acts across multiple systems and decisions. | End-to-end accountability, systemic risk assessment, continuous assurance and resilient controls. |

A human approval is only useful when the person has authority, relevant information, time, and a genuine ability to reject or amend the action. A click-through approval with no context or meaningful alternative is not effective oversight.

### Accountability

Delegation does not transfer the organisation’s legal or management accountability to an AI system. A business process owner should remain accountable for business outcomes; system owners should operate the system within approved boundaries; control functions should challenge risk; and independent assurance should test whether the governance operates as intended. The proposed allocation is detailed in Section 7. A05 itself implements no board, risk committee, policy-approval, or incident-management function.

## 3. Enterprise AI governance requirements

The matrix below is an illustrative enterprise requirements baseline. “A05 evidence” describes only the repository prototype and must not be read as proof of organisational effectiveness.

| Requirement | Business purpose / risk addressed | Required organisational capability | A05 evidence | Remaining gap |
|---|---|---|---|---|
| Identity and authorisation | Ensure only a known principal may request an operation within delegated authority; reduce impersonation and unauthorised access. | Trusted issuer, managed keys, role lifecycle, least privilege, service identity, revocation and periodic access review. | **Observed:** RS256 JWT verification; subject/role checks; protected endpoints derive identity from token. | No managed issuer/key lifecycle, revocation, federation or enterprise access review. |
| Business policy enforcement | Convert approved business limits into consistent execution constraints. | Named policy owner, approved policy lifecycle, versioning, testing, change control and enforcement at every execution boundary. | **Observed:** Local Rego decisions; default deny; PEP and fixed tool registry. | No policy administration/distribution service; limited tools; direct A04 bypass remains. |
| Risk identification and assessment | Understand impacts before selecting autonomy and controls. | Use-case inventory, impact assessment, risk criteria, affected-party analysis, treatment and acceptance records. | **Observed:** Architecture and Day 4 reports document selected threats and limitations. | No enterprise context or validated likelihood/impact assessment, inventory or risk acceptance. |
| Human oversight | Preserve meaningful human intervention in consequential decisions. | Defined triggers, trained and authorised reviewers, context-rich decisions, override/stop paths and workload design. | **Observed:** Finance approval path for the policy-defined middle band; finance approver role required. | No staffed workflow, reviewer guidance, escalation, service levels, or evidence of meaningful oversight in use. |
| Segregation of duties | Reduce collusion, error and self-authorisation. | Separate requester, approver, policy administrator and operator where proportionate; review conflicts. | **Observed:** Self-approval denied; approval role checked. | No enterprise role provisioning, broader conflict-of-interest controls, dual control or periodic review. |
| Data protection | Protect personal data and respect lawful purpose, minimisation, accuracy, retention and rights. | Data mapping, lawful basis, privacy by design, processor controls, retention/deletion, DPIA where required. | **Observed:** MCP adapter audit omits customer payloads; finance audit omits request context. | No data inventory, lawful-basis analysis, retention/deletion controls, rights workflow or DPIA. |
| Security | Protect confidentiality, integrity and availability of the AI and connected systems. | Threat modelling, secure development, secrets management, network controls, vulnerability response, independent testing. | **Observed:** JWT checks, timeouts, reduced child environment, restrictive local file modes, fail-closed behavior. | No production secrets, network isolation, sandbox, rate limiting, security monitoring or independent assessment. |
| Transparency and explainability | Enable users, operators and reviewers to understand why an action was allowed or stopped. | Explainable rules, clear notices, decision records, user communication and limits on misleading explanations. | **Observed:** Decision reason, policy ID/version and obligations are represented in contract/audit. | No policy authoring explanation interface, user transparency programme, or decision-quality evidence. |
| Auditability | Reconstruct who requested what, under which authority and what happened. | Durable, protected, searchable logs; time synchronisation; retention; access separation; evidence export and review. | **Observed:** Local JSONL events; SQLite lifecycle events; pre-execution audit gates. | Files remain mutable/local; no remote immutable evidence, retention, alerting or audit operations. |
| Incident management | Limit harm and learn from failures, misuse and near misses. | Detection, triage, escalation, containment, notification, recovery, root-cause analysis and lessons learned. | **Observed:** Failure paths deny selected actions; operational recovery notes exist. | No incident process, alerting, response roles, reporting workflow or tested kill switch. |
| Operational resilience | Continue or safely degrade critical services and recover data/state. | Resilience objectives, tested backups, recovery plans, dependency mapping, capacity and failover. | **Observed:** SQLite restart recovery and same-host atomic consume are tested. | Single-host DB; no HA, automated backups, restore exercise, service SLO or dependency failover. |
| Regulatory compliance | Determine and meet binding obligations applicable to the use, organisation and jurisdiction. | Legal applicability assessment, control mapping, evidence owners, monitoring of law and regulatory reporting. | **Observed:** None as a compliance programme; reports explicitly disclaim certification. | No legal analysis, conformity assessment, records, registrations, or regulator-ready evidence. |
| Continuous monitoring | Detect drift, policy exceptions, model/tool changes and control degradation. | Monitoring of actions, outcomes, errors, access, policy changes, incidents and model performance. | **Observed:** Per-event local records and test assertions. | No live telemetry, dashboards, alert thresholds, drift monitoring or routine control testing. |
| Change management | Prevent unreviewed changes to models, prompts, tools, policy, data or vendors from altering risk. | Change approval, impact review, regression testing, staged release, rollback and inventory updates. | **Observed:** Policy ID/version appears in decisions; ADRs document design choices. | No release governance, policy repository controls, version pinning/approval evidence or change-impact workflow. |

## 4. Enterprise risk assessment

### Method and rating limitations

A conventional risk assessment evaluates the organisation’s objectives and context, identifies events and causes, estimates likelihood and impact against agreed criteria, evaluates existing controls, determines residual risk, and assigns a treatment and accountable owner. Ratings should be based on evidence such as exposure, threat intelligence, transaction limits, operating history, control testing, affected populations, regulatory exposure, and approved risk appetite.

A05 is a repository prototype, not an operating enterprise service. The available evidence does not establish production exposure, threat frequency, asset values, transaction materiality, affected individuals, control effectiveness over time, or risk tolerance. Accordingly, the table marks inherent likelihood and impact **Not assessed**. Residual risk is also **Not assessed**; the control status and unresolved gap are described instead. This is not a low-risk judgement. An organisation must perform its own assessment before a pilot or deployment.

Risk owners below are **proposed role-level owners**, not named or appointed A05 stakeholders. Ratings should be assigned only after the organisation defines scales (for example, likelihood and impact bands with calibrated criteria), time horizon, scope, and risk appetite.

### Illustrative AI-agent risk register

| ID / risk | Business consequence | Inherent likelihood / impact | Demonstrated A05 controls | Residual risk | Recommended treatment | Proposed owner |
|---|---|---|---|---|---|---|
| R1. Unauthorised financial transaction | Loss, fraud, customer harm, accounting error or regulatory action. | Not assessed / Not assessed | Simulated handler only; policy thresholds; authenticated finance request; approval path. | Not assessed; no real payment boundary exists. | Do not connect live payments until a protected gateway, transaction limits, idempotency, reconciliation and independent approval controls are proven. | Finance process owner |
| R2. Agent identity spoofing | An attacker acts under another agent’s authority or misattributes responsibility. | Not assessed / Not assessed | RS256 verification, required claims, subject-derived identity; identity tests. | Not assessed; signing-key compromise and token theft/replay until expiry remain. | Managed identity issuer, key rotation, short TTLs, revocation and workload identity. | Identity and security owner |
| R3. Excessive permissions | Agent can read or change more than needed, increasing blast radius. | Not assessed / Not assessed | Policy role checks and a fixed registered tool. | Not assessed; role model is small and no access certification exists. | Define task-specific scopes and resource constraints; review permissions and test negative cases. | Business system owner |
| R4. Approval bypass | Sensitive action proceeds without valid human authority. | Not assessed / Not assessed | Finance workflow requires current `REQUIRE_APPROVAL`, authorized role, matching requester/digest and unconsumed state. | Not assessed; only governed A05 path is protected; downstream operation is not transactionally bound. | Enforce approval at the actual business execution boundary; test all bypass routes and crash cases. | Finance control owner |
| R5. Self-approval or conflicted approval | Requester authorises own action or reviewer has an unmanaged conflict. | Not assessed / Not assessed | Engine blocks requester from approving own request; approver role required by service. | Not assessed; no HR-backed roles or broad conflict controls. | Independent approver assignment, role-conflict review, dual control for material actions. | Finance control owner |
| R6. Policy manipulation or unauthorised change | Thresholds/roles are altered to permit unsafe actions or deny legitimate work. | Not assessed / Not assessed | Rego files are local; default deny; policy ID/version in decision. | Not assessed; no policy signing, deployment approval or administrative separation. | Controlled policy repository, peer review, signed artifacts, staged rollout, audit and rollback. | Policy owner / security |
| R7. Incorrect or unreliable AI decision | Agent selects a wrong target, amount, recipient or workflow despite valid policy. | Not assessed / Not assessed | Schema validation, exact approval binding; finance simulation. | Not assessed; policy does not assess model correctness or business truth. | Independent validations against authoritative data, thresholds, confirmation and outcome monitoring. | Business process owner |
| R8. Prompt injection and tool misuse | Malicious content induces unauthorised disclosure or action. | Not assessed / Not assessed | Tool allow-list, argument validation, narrow adapter execution. | Not assessed; no model/prompt security controls or general tool gateway. | Treat retrieved content as untrusted; constrain tools and data; red-team indirect injection paths. | AI system owner |
| R9. Data leakage | Personal, financial or confidential data reaches an unauthorised recipient or log. | Not assessed / Not assessed | MCP audit omits payload; reduced A04 child environment; selected input shape validation. | Not assessed; no classification, encryption, retention/deletion or access monitoring programme. | Data-flow mapping, minimisation, encryption, DLP, access controls, retention and privacy review. | Data protection / information owner |
| R10. Inadequate or altered audit evidence | Inability to investigate, prove decisions, meet retention duties or detect misuse. | Not assessed / Not assessed | Append-oriented JSONL, mode 0600, flush/sync; approval event transaction. | Not assessed; local files are mutable and may be lost with host. | Remote append-only service, integrity validation, separated administration, retention and restore tests. | Audit / operational risk owner |
| R11. Policy-engine outage or error | Safe work is blocked or, if failure handling is faulty, unsafe work proceeds. | Not assessed / Not assessed | OPA timeout/error/invalid output maps to deny; PEP requires permit. | Not assessed; availability and observability are not established; fail-closed outages interrupt service. | Monitor dependencies, fault-test, establish safe manual fallback and alerting; preserve fail-closed behavior. | Service owner |
| R12. A04 integration bypass | Direct access evades A05 decisions and role restrictions. | Not assessed / Not assessed | Adapter path authenticates through A05, authorizes, audits and only invokes synthetic `get_customer`. | Not assessed; direct A04 path is explicitly open. | Change A04: trusted caller authentication and authorization at every transport; remove client-selected role environment; restrict network access. | A04 service owner |
| R13. Operational interruption or lost approval state | Work stops or pending approvals disappear after host/database failure. | Not assessed / Not assessed | SQLite persistence and restart recovery; transaction serializes local consumption. | Not assessed; single-host DB and no managed backup/HA. | Managed transactional persistence, tested backups/restores, migrations, HA and documented degraded mode. | Service operations owner |
| R14. Regulatory non-compliance | Enforcement action, remediation cost, loss of trust or prohibited processing. | Not assessed / Not assessed | No compliance control evidenced; documentation identifies no compliance claim. | Not assessed; use-case applicability has not been assessed. | Legal classification and obligation mapping for each intended use; maintain evidence and owners. | Legal/compliance and business owner |
| R15. Loss of management control | Agent operation exceeds approved scope or continues after risk changes. | Not assessed / Not assessed | Local permit/deny gate; API can reject selected operations. | Not assessed; no central kill switch, broad monitoring or delegated authority inventory. | Establish suspend/revoke controls, operational command ownership, alerts and periodic autonomy review. | Executive sponsor / AI system owner |
| R16. Operational or regulatory change not reflected | New model, tool, policy, law or vendor changes invalidate prior approval and risk assumptions. | Not assessed / Not assessed | Policy identifier/version is represented in records. | Not assessed; no continuous change governance. | Inventory dependencies; require change-impact assessment, regression tests, release approval and re-authorisation. | AI system owner / change authority |

The register distinguishes an implemented mechanism from proven risk reduction. For example, a test showing self-approval rejection establishes behaviour in the tested code path; it does not demonstrate correct role provisioning, conflict monitoring or operational adoption.

## 5. Levels of AI autonomy

The following five-level model is **illustrative**, created for management discussion. It is not a certified standard and does not map automatically to the EU AI Act or another regulation.

| Level | Operating pattern | Typical control expectation |
|---|---|---|
| 0 — Human performs the task | A person performs the work; AI is not used for the decision or action. | Existing business controls apply. |
| 1 — AI advises | AI analyses or drafts; a person independently decides and acts. | Clear limits, source/quality checks, disclosure where appropriate, data controls. |
| 2 — AI proposes, human approves | AI prepares a specific action; an authorised human reviews details before execution. | Action-bound approval, reviewer authority, context, reject/edit option, evidence. |
| 3 — AI acts within defined limits | AI executes routine actions inside explicit, bounded policy; exceptions go to a human. | Strong identity, least privilege, deterministic limits, protected enforcement, monitoring and stop capability. |
| 4 — AI operates autonomously with monitoring | AI performs a broader workflow under live monitoring and exception escalation. | Resilience, outcome monitoring, tested intervention, independent assurance, change control and recovery. |
| 5 — Broad autonomy under enterprise governance | AI may plan and act across multiple domains within organisation-wide guardrails. | Extensive systemic and rights impact assessment, accountable governance, continuous assurance, robust containment and explicit risk acceptance. |

### Criteria for increasing autonomy

An organisation should increase autonomy only when it has evidence that the use case is understood, objectives and prohibited uses are explicit, performance is sufficiently reliable in representative conditions, permissions are proportionate, downstream controls cannot be bypassed, humans can intervene meaningfully, incidents can be contained, and the residual risk has been accepted by the authorised risk owner. The evidence should include adversarial testing, live-like validation, operational monitoring, recovery tests, independent challenge, and review of legal and privacy obligations.

Keep a human as the decision-maker where law requires it, impacts are serious or difficult to reverse, the system cannot explain material factors, relevant context is ambiguous, data quality is uncertain, the action affects rights or access to essential services, the system is outside validated conditions, or a human cannot monitor and intervene effectively. Human presence alone does not guarantee oversight.

## 6. Financial governance case study

### Verified policy behaviour

The current finance policy in `policies/finance.rego` applies only when the identity is `finance-agent`, action is `payment.create`, resource is `erp.payments`, currency is EUR, and amount is a positive number. It permits amounts at or below €5,000, requires approval above €5,000 through €50,000 inclusive, and otherwise defaults to deny. Therefore the three requested examples are consistent with the actual policy.

| Illustrative request | Policy outcome | Actual A05 workflow behaviour | Business interpretation |
|---|---|---|---|
| €2,000 | `PERMIT` | Authorization audit, then simulated handler and execution audit. | Low-value autonomy is permitted by the demo rule. This is not a recommendation that €5,000 is a safe enterprise threshold. |
| €12,000 | `REQUIRE_APPROVAL` | Creates pending approval; a `finance_approver` must approve; requester later re-submits exact operation; current policy is re-evaluated; approval is consumed once; simulation runs. | Human authority is required for the policy-defined middle band. An enterprise must define its own approval limit, context, approver authority and evidence. |
| €60,000 | `DENY` | Request is denied; no approval is created and no handler runs. | Above-ceiling requests are blocked in this demo rather than escalated. A real process may require an exception pathway with separate authority. |

**No real payment is executed.** The handler returns a simulated result, and there is no bank, ERP payment rail or live financial transaction integration.

### Approval safeguards and business responsibilities

The approval digest covers action, resource, amount and currency; requester identity is stored separately. The engine checks status, expiry, requester, digest and one-time consumption. The authenticated finance service requires the `finance_approver` role, and the engine prohibits self-approval. The workflow re-evaluates policy at execution time so a previous approval cannot override a policy outcome that no longer requires approval.

An enterprise finance owner would still need to define signing authority, monetary limits, delegated authority, recipient verification, sanctions/fraud checks where relevant, evidence retention, exception handling and reconciliation. A05 does not implement these controls. SQLite consumption and a downstream action are not one atomic transaction; a crash after consumption and before action can leave an approved request consumed without execution. Real execution requires idempotency and reconciliation controls at the downstream system.

## 7. Governance operating model

The following is a proposed operating model, not an organisational structure implemented by A05. It applies the IIA Three Lines Model as a way to clarify management ownership, risk challenge and independent assurance; it should be adapted to organisation size and existing governance.

### Proposed responsibilities

- **Board / executive management:** Set risk appetite, oversee material AI use, ensure resources and accountability, accept or escalate residual risk, and direct suspension when exposure exceeds appetite.
- **Business process owner:** Own the process outcome, action limits, exception rules, human approval requirements and business performance measures.
- **AI system owner:** Maintain system purpose, inventory, intended-use boundaries, risk file, model/tool/vendor dependencies, monitoring, change control and stop procedures.
- **Enterprise architecture:** Define integration patterns, trust boundaries, data flows, identity, resilience and alignment to enterprise standards.
- **AI engineering:** Implement controls, testing, model/tool evaluation, secure development, release records and technical incident support.
- **Information security:** Set security requirements, threat model, access and secrets controls, monitor vulnerabilities and challenge residual cyber risk.
- **Risk management:** Define methodology and appetite linkage, challenge assessments, track treatment and facilitate escalation.
- **Legal and compliance:** Interpret applicable law, obligations, records, notices, sector rules and regulatory engagement; advise, not replace, business accountability.
- **Internal audit:** Independently assess governance and control design/operation; should not own the controls it later assures.
- **Human approvers:** Review action context, authority, amount/target and exceptions; approve, reject or request correction; do not delegate accountability to the system.
- **Operational support:** Monitor service health, maintain logs and backups, respond to incidents, execute recovery and operate authorised suspension procedures.

### Illustrative RACI matrix

**R** = responsible for doing; **A** = accountable for the outcome (one proposed accountable role per row); **C** = consulted; **I** = informed. This is a generic proposal, not a record of A05 appointments.

| Activity | Board / exec | Business owner | AI system owner | Architecture / engineering | Security | Risk | Legal / compliance | Internal audit | Approver / operations |
|---|---|---|---|---|---|---|---|---|---|
| Set AI risk appetite and policy principles | A | C | C | I | C | R | C | I | I |
| Define business action scope and thresholds | I | A/R | C | C | C | C | C | I | C |
| Approve agent permissions and tool scope | I | A | R | R | C | C | C | I | I |
| Assess legal/privacy applicability | I | C | R | C | C | C | A/R | I | I |
| Implement and test technical controls | I | C | A | R | C | C | C | I | I |
| Authorise a sensitive transaction | I | A | I | I | I | C | C | I | R (authorised human) |
| Monitor behaviour and service operation | I | C | A | C | C | C | I | I | R (operations) |
| Investigate AI/security/business incident | I | A (business impact) | R | R | R | C | C | I | R (operations) |
| Suspend autonomous operation | I | A | R | C | C | C | C | I | R (operations executes) |
| Accept material residual risk | A (outside appetite) | A (within delegated limits) | R (document) | C | C | C/challenge | C | I | I |
| Independently assure controls | I | C | C | C | C | C | C | A/R | I |

An organisation should define escalation paths when accountable owners disagree, and ensure internal audit’s assurance role remains independent. A05 currently contains only the software role check for finance approvers; it does not implement this RACI or organisational governance.

## 8. Regulatory and standards considerations

### Applicability principles

Legal applicability depends on the provider/deployer role, system purpose and capabilities, affected people, processing, sector, location and deployment date. A component such as A05 cannot be labelled “compliant” in isolation from the system and organisation using it. The following is a high-level orientation, verified against public authoritative sources on 8 November 2026; it is not legal advice. Legal counsel should review classification and obligations for each concrete use.

| Instrument | Status and relevance | A05 assessment |
|---|---|---|
| **EU AI Act — Regulation (EU) 2024/1689, as amended** | Binding EU regulation with phased application. AI literacy and prohibited practice provisions began applying earlier; the general application date is 2 August 2026. Following the 2026 AI Omnibus amendment, high-risk Annex III rules apply from 2 December 2027 and high-risk AI embedded in Annex I regulated products from 2 August 2028. Whether an agent is high-risk depends on its intended purpose and legal classification, not merely its use of autonomy. Provider/deployer duties can include risk management, documentation, logging, human oversight, monitoring and other duties where relevant. | No classification, conformity assessment, risk management system, required documentation set or conformity evidence has been performed. A05 is not claimed compliant. A financial tool example does not itself establish that the system is in an AI Act high-risk category. |
| **GDPR — Regulation (EU) 2016/679** | Binding where personal data processing falls within territorial and material scope. Relevant principles include lawfulness, fairness, transparency, purpose limitation, data minimisation, accuracy, storage limitation and security; accountability and privacy by design apply. DPIAs are required where processing is likely to result in high risk, subject to legal assessment. Article 22 may be relevant to certain solely automated decisions producing legal or similarly significant effects; its conditions and exceptions require case-specific legal review. | The A04 demo handles synthetic customer data. The repository does not supply a lawful-basis analysis, privacy notice, data-subject rights workflow, retention schedule, DPIA, processor assessment or production security evidence. |
| **NIST AI Risk Management Framework (AI RMF 1.0)** | Voluntary, non-sector-specific framework. Its functions are Govern, Map, Measure and Manage; risk management is continuous and should consider context, affected parties, measurement, treatment and monitoring. NIST reports the framework is being revised, so organisations should check the current version. | A05’s architecture, tests and threat notes can inform a small prototype evidence set, but there is no organisational GOVERN structure or full MAP/MEASURE/MANAGE lifecycle. |
| **ISO/IEC 42001:2023** | International standard specifying requirements for an AI Management System (AIMS) and continual improvement. Certification is an organisational/system-management assessment route, not inferred from owning a software control. | No AIMS scope, management system, audit, certification or statement of conformity exists for A05. |
| **ISO/IEC 23894:2023** | Voluntary guidance on integrating AI-related risk management into organisational activities. Useful to tailor risk identification, analysis, evaluation, treatment and monitoring. | The report’s risk register is an illustrative starting point, not a completed ISO/IEC 23894 assessment. |
| **ISO 31000:2018** | General risk management guidelines (not a certifiable standard); supports context, criteria, assessment, treatment, monitoring and communication. ISO’s current catalogue indicates it remains current while a revision is underway. | A05 has no approved enterprise criteria, risk appetite, risk owners or accepted residual-risk records. |
| **IIA Three Lines Model** | Governance model / professional guidance, not legislation. Helps distinguish governing body accountability, management’s first- and second-line roles, and independent internal audit. | Used only to shape the proposed role allocation in this report; A05 has no such organisation structure. |
| **Financial services / operational resilience rules** | Obligations depend on regulated entity, service, jurisdiction and criticality. For EU financial entities, DORA (Regulation (EU) 2022/2554) has binding ICT risk governance, resilience, incident and third-party requirements within its scope. Other prudential, outsourcing, recordkeeping and payment rules may apply. | A05 is not a regulated service and has no DORA assessment. If adopted by a financial entity, the entity must assess scope and integration with its ICT risk management, change, incident, resilience, third-party and audit obligations. |

### Legal review questions

Before using A05-like controls in a real workflow, counsel and compliance should determine: (1) whether the system falls within the AI Act definition and which actor roles apply; (2) intended-purpose classification and transition dates; (3) whether automated decisions affect people’s rights or access to services; (4) what personal data is processed and the lawful basis, transparency, retention and DPIA requirements; (5) sector-specific authorisation and recordkeeping rules; and (6) cross-border, outsourcing and third-party obligations.

## 9. A05 control effectiveness assessment

Evidence ratings describe implementation and tests, not enterprise effectiveness over time. **Demonstrated** means the specific behaviour is implemented and has repository tests. **Partially demonstrated** means there is a limited mechanism or path but coverage or assurance is incomplete. **Not demonstrated** means no meaningful implementation evidence is present. **Not assessed** means repository evidence is insufficient to judge the capability.

| Control | Evidence rating | Evidence and plain-English limitation |
|---|---|---|
| Agent authentication | Demonstrated | RS256 JWT verification, issuer/audience/time/required claim checks and identity tests. No managed key operations or revocation. |
| Policy decisions | Demonstrated | Local Rego finance/MCP decisions with default deny and failure-to-deny handling. Policies are small local files without organisational lifecycle. |
| Policy enforcement | Partially demonstrated | PEP and trusted registry gate selected simulated execution paths. A05 cannot enforce on arbitrary callers or bypass routes. |
| Approval workflow | Demonstrated | Finance request, role-authorised decision, policy re-evaluation and exact-operation check are implemented and tested. It is not enterprise case management. |
| Segregation of duties | Partially demonstrated | Finance approver role and self-approval prohibition exist; role provisioning and broader conflict monitoring do not. |
| One-time approval consumption | Demonstrated | SQLite transaction and conditional update enforce one winner on the same host/database; concurrency and restart tests exist. No multi-host coordination or atomic coupling to downstream action. |
| Audit records | Partially demonstrated | Local structured JSONL; pre-execution failure blocks selected actions. Files are mutable and there is no central retention, monitoring or independent integrity protection. |
| Approval persistence | Demonstrated | SQLite state/lifecycle events persist through a new engine instance and process-level restart pattern. Not HA, managed backup or multi-host state. |
| Failure handling | Demonstrated | Selected OPA errors and pre-execution audit failures deny; subprocess timeouts exist. Service-wide availability, alerting and recovery are not assessed. |
| A04 MCP integration | Partially demonstrated | A05 adapter governs a narrow synthetic `get_customer` subprocess path and validates response; live lookup has had environment timeout evidence. Direct A04 access remains open. |
| Data protection and privacy governance | Not demonstrated | Payload minimisation is present in some logs, but there is no organisational privacy programme, lawful basis or retention controls. |
| Model reliability / prompt-injection resistance | Not assessed | A05 governs tool calls but does not measure the model or provide general prompt-injection controls. |
| Regulatory compliance | Not assessed | No legal applicability assessment, conformity evidence or audit against regulation/standards exists. |
| Continuous monitoring and incident management | Not demonstrated | Local event output exists; no live monitoring, alerting or incident process. |

## 10. Architectural trade-offs

| Choice | Business benefit | Cost / risk | Leadership question |
|---|---|---|---|
| Centralised versus distributed governance | Central rules can improve consistency and visibility; local enforcement can keep critical decisions near the execution boundary. | Central service can become an availability dependency; distributed policy can drift or be inconsistently applied. | Which decisions must be central, and what safe operating mode applies if central policy is unavailable? |
| Agent autonomy versus human approval | More autonomy can reduce routine handling and delay; approval can provide oversight for consequential cases. | Too little autonomy burdens staff; poorly designed approval creates rubber-stamping and delay. | Which actions are reversible, material, rights-affecting or outside validated conditions? |
| Security versus operational speed | Strong checks reduce unauthorised action and support trust. | Extra authentication, logging and approval can add latency or block service during outage. | What service interruption is acceptable to preserve safety and control? |
| Policy flexibility versus consistency | Flexible rules can reflect business context and change quickly. | Uncontrolled change may create inconsistent decisions or policy manipulation. | Who owns changes, evidence, review, release and rollback? |
| Local versus enterprise audit | Local records are simple and inexpensive for a prototype. | Local mutable storage lacks central retention, integrity, search, access separation and resilience. | What evidence must the organisation retain, prove and retrieve, and for how long? |
| Integration versus independent trust boundaries | Reuse of existing tools can accelerate adoption. | A05 checks cannot govern an independently reachable service that does not authenticate A05. | Where is the authoritative enforcement point, and are all alternate routes closed? |
| Simplicity versus operational resilience | SQLite and subprocesses simplify local demonstration. | Single-host state, local binaries and paths create recovery and availability limits. | What service criticality justifies managed persistence, failover and tested recovery? |

These are enterprise design choices, not universally optimal answers. Risk appetite, consequences, service criticality, user rights, and legal duties should determine the balance.

## 11. Deployment readiness assessment

### Stage gates

| Stage | Purpose | Minimum evidence and controls before entry |
|---|---|---|
| Research prototype | Learn architecture and test hypotheses using synthetic data and non-production actions. | Clear scope; isolated environment; synthetic data; no live transaction credentials; documented limitations; basic tests and safe shutdown. |
| Controlled pilot | Validate a bounded use case with selected users and controlled consequences. | Named accountable owner; approved use case and risk assessment; data/privacy/legal review; closed trust boundaries; least privilege; human approval and stop authority; monitoring and incident plan; tested backup/restore; pilot exit criteria. |
| Limited operational deployment | Use in a real but low-impact, bounded process with fallback. | Independent security review; production identity/key management; robust policy change control; resilient audit/persistence; end-to-end integration enforcement; operational support/SLO; recovery and incident drills; user training; accepted residual risks. |
| Enterprise production | Scale across business units or material processes. | Approved enterprise architecture and control framework; continuous assurance; capacity/HA and disaster recovery; compliance mapping and evidence; third-party oversight; model/tool change governance; audit access; regulatory reporting readiness; independent assurance and risk sign-off. |

### Current position

**Reasoned assessment: Research prototype.** A05 has real code and tests for selected controls, but it uses a local OPA binary, local JSONL and SQLite, simulation-only finance, test/development identity conventions, and a narrow sibling-project subprocess adapter. The open A04 direct-access route means the architecture cannot claim end-to-end governance over that integration. No production security assessment, legal classification, enterprise risk acceptance, service resilience evidence, or operating model exists.

The later Ubuntu run recorded 105 passing tests in 3.25 seconds; the Day 4 report also documents earlier environment timeout issues, including the live A04 lookup. Tests increase confidence in specific code behaviour. They do not prove regulatory compliance, operational readiness, security in a different deployment, or that all paths are enforced.

## 12. Management recommendations

Priorities are proposed based on risk containment and decision dependency, not an assessed likelihood score.

| Priority / recommendation | Business rationale and expected benefit | Proposed owner | Dependency |
|---|---|---|---|
| **P0 — Keep prototype isolated; prohibit live financial or sensitive production action.** | Prevents a demonstration from being mistaken for an execution control; limits potential impact while gaps remain. | Executive sponsor and business owner | Publish scope and permitted-use statement. |
| **P0 — Close A04 direct access at A04 itself.** | Removes an explicit route around A05 policy and identity checks. | A04 service owner with security | A04-side trusted identity, in-server authorization for every transport, role derivation and network restriction. |
| **P1 — Establish a named business owner, AI system owner and risk acceptance authority.** | Creates accountability for outcomes, permissions, monitoring and stopping operation. | Executive management | Governance charter and delegated authority. |
| **P1 — Perform use-case, data protection and legal applicability assessment.** | Determines AI Act, GDPR, sector and affected-person obligations before pilot design. | Legal/compliance and privacy lead with business owner | Intended purpose, user population, data flows, jurisdictions and deployment model. |
| **P1 — Define enterprise risk criteria and complete deployment-specific risk assessment.** | Enables calibrated likelihood/impact ratings and treatment based on context rather than prototype assumptions. | Risk management with business/system owners | Asset and process criticality, threat scenarios, risk appetite and control evidence. |
| **P1 — Implement managed identity and credential lifecycle.** | Reduces spoofing, stolen-token and unmanaged-key exposure. | Identity/security owner | Trusted enterprise issuer, workload identities, key rotation, revocation and monitoring design. |
| **P1 — Put policy changes under controlled governance.** | Prevents unreviewed thresholds or roles from silently changing business authority. | Policy owner, risk and engineering | Policy inventory, approvals, tests, versioning, signed deployment and rollback. |
| **P1 — Design protected execution and approval transaction semantics.** | Prevents bypass and addresses consume-before-action crash windows for live operations. | Business system owner and architecture | Downstream idempotency, exact action binding, reconciliation and failure-state design. |
| **P2 — Replace local audit and SQLite with managed services appropriate to criticality.** | Improves availability, integrity, retention, search and multi-instance operation. | Operations and security | Data classification, retention policy, architecture and service SLO. |
| **P2 — Add monitoring, incident, suspension and recovery procedures; exercise them.** | Makes control failures observable and enables timely containment. | Operations, security and AI system owner | Alert thresholds, incident ownership, kill/suspend authority and tested backups. |
| **P2 — Conduct independent security and abuse-case testing.** | Challenges assumptions, including prompt injection, direct routes, race conditions and misuse. | Security assurance / independent tester | Stable pilot architecture and threat model. |
| **P3 — Prepare a controlled pilot with explicit entry/exit gates.** | Provides measured evidence before broader use while retaining reversibility. | Business owner and AI system owner | All P0/P1 controls, user training, pilot metrics and fallback process. |
| **P3 — Build a longer-term governance platform architecture only from validated needs.** | Avoids premature platform investment while retaining a path to multi-agent governance. | Architecture leadership | Pilot findings, integration inventory, resilience targets and operating model. |

## 13. Strategic implications for autonomous enterprises

A portfolio architecture can distribute capabilities: orchestration plans work, retrieval provides information, integration exposes tools, governance constrains action, and a business twin may later simulate process effects. Governance enables autonomy when it makes authority explicit and enforceable; it does not remove human or organisational accountability.

| Portfolio project | Intended relationship to A05 | Evidence status in this repository |
|---|---|---|
| A01 — Enterprise AI Reference Architecture | Enterprise-wide architectural context and shared patterns. | No operational A01 integration demonstrated here. |
| A02 — Agent Orchestration & A2A | Potential consumer of governance decisions for delegated agent actions. | Named as a potential consumer in architecture planning; not implemented in this repository. |
| A03 — Enterprise RAG & Knowledge | Potential governance of access and actions informed by enterprise retrieval. | No operational A03 integration demonstrated here. |
| A04 — MCP & Enterprise Integration | Tool execution boundary for enterprise systems. | Narrow A05-to-A04 synthetic customer lookup through adapter demonstrated; direct A04 trust boundary remains open. |
| A05 — Governance & Policy Enforcement | Identity-aware policy decisions, enforcement on selected paths, approval and local evidence. | Implemented prototype, not production platform. |
| A06 — Digital Business Twin (future) | Could model consequences and test policy scenarios before actions. | Future architectural direction only; no integration or capability demonstrated. |

A sound future pattern would bind each action to identity, purpose, scope, policy version, approval where needed, and a downstream enforcement decision. A simulation or digital twin may inform decisions, but should not become the authority that approves its own recommendations. Business owners remain accountable for the chosen level of autonomy and residual risk.

## 14. Conclusions

A05 demonstrates a useful, testable pattern for governing selected AI-initiated operations: authenticate, evaluate policy, enforce at a protected point, request human approval when required, bind approval to exact intent, and retain evidence. It makes the business principle tangible: greater autonomy depends on bounded authority, meaningful oversight and enforceable controls.

The prototype is not ready for a controlled pilot involving real enterprise data or operations. It lacks a complete organisational governance model, production identity lifecycle, enterprise audit and persistence, operational monitoring, tested recovery, and independent security/legal assurance. Most significantly, A04 direct access remains outside A05’s controls. Financial activity remains simulated.

Management should treat the project as a research prototype and use it to guide architecture and risk conversations. Before increasing autonomy, define the use case and accountability, assess legal and business impacts, close all bypass routes, strengthen operating controls, test failure and intervention paths, and obtain explicit risk acceptance at the correct level.

## 15. Appendices

### Appendix A — Governance requirements matrix

The requirements matrix is in [Section 3](#3-enterprise-ai-governance-requirements). It covers identity, policy, risk, human oversight, segregation, privacy, security, transparency, audit, incidents, resilience, compliance, monitoring and change management.

### Appendix B — AI-agent risk register

The illustrative register is in [Section 4](#4-enterprise-risk-assessment). All likelihood and impact scores are marked **Not assessed** because deployment context and calibrated evidence are unavailable.

### Appendix C — RACI matrix

The proposed RACI is in [Section 7](#7-governance-operating-model). It is illustrative and does not describe implemented A05 responsibilities.

### Appendix D — Control assessment

The evidence ratings are in [Section 9](#9-a05-control-effectiveness-assessment). They refer to repository implementation/tests only and do not establish operating effectiveness in an enterprise.

### Appendix E — Architecture diagrams

| View | Mermaid source | PNG | SVG |
|---|---|---|---|
| System context | [Source](../../diagrams/01-system-context.mmd) | [PNG](../../diagrams/rendered/01-system-context.png) | [SVG](../../diagrams/rendered/01-system-context.svg) |
| Component architecture | [Source](../../diagrams/02-component-architecture.mmd) | [PNG](../../diagrams/rendered/02-component-architecture.png) | [SVG](../../diagrams/rendered/02-component-architecture.svg) |
| Policy decision sequence | [Source](../../diagrams/03-policy-decision-sequence.mmd) | [PNG](../../diagrams/rendered/03-policy-decision-sequence.png) | [SVG](../../diagrams/rendered/03-policy-decision-sequence.svg) |
| Approval lifecycle | [Source](../../diagrams/04-approval-lifecycle.mmd) | [PNG](../../diagrams/rendered/04-approval-lifecycle.png) | [SVG](../../diagrams/rendered/04-approval-lifecycle.svg) |
| Audit and recovery | [Source](../../diagrams/05-audit-operational-recovery.mmd) | [PNG](../../diagrams/rendered/05-audit-operational-recovery.png) | [SVG](../../diagrams/rendered/05-audit-operational-recovery.svg) |

### Appendix F — Repository evidence and references

#### Internal project evidence

- [README](../../README.md)
- [Comprehensive technical project report](AI-A05-Comprehensive-Technical-Project-Report.md)
- [Day 4 security and operational readiness report](AI-A05-Day-4-Security-and-Operational-Readiness.md)
- [Architecture specification](../AI-A05-Architecture-Specification.md)
- [ADR-001 — Independent governance](../adr/ADR-001-independent-governance.md)
- [ADR-002 — Fail-closed enforcement](../adr/ADR-002-fail-closed-enforcement.md)
- [ADR-003 — Human approval](../adr/ADR-003-human-approval.md)
- [ADR-004 — Audit explainability](../adr/ADR-004-audit-explainability.md)
- Implementation evidence: `policies/finance.rego`, `policies/mcp.rego`, `src/identity/jwt_verifier.py`, `src/enforcement/pep.py`, `src/approvals/engine.py`, `src/approvals/finance_workflow.py`, `src/integrations/a04_mcp_adapter.py`; tests under `tests/unit`, `tests/integration` and `tests/security`.

#### Authoritative public sources checked 8 November 2026

1. European Union, [Regulation (EU) 2024/1689 — Artificial Intelligence Act, consolidated with 2026 amendment](https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng), including application timetable and obligations. See also the European Commission’s [AI Act overview and current timeline](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai).
2. European Union, [Regulation (EU) 2016/679 — General Data Protection Regulation](https://eur-lex.europa.eu/eli/reg/2016/679/oj), particularly Articles 5, 22, 25, 32 and 35 where relevant.
3. NIST, [AI Risk Management Framework 1.0](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10) and [AI RMF resources](https://airc.nist.gov/airmf-resources/). The NIST overview states the framework is voluntary and being revised.
4. ISO, [ISO/IEC 42001:2023 — AI management systems](https://www.iso.org/standard/42001).
5. ISO, [ISO/IEC 23894:2023 — AI risk management guidance](https://www.iso.org/standard/77304.html).
6. ISO, [ISO 31000:2018 — Risk management guidelines](https://www.iso.org/standard/65694.html).
7. The Institute of Internal Auditors, [Three Lines Model](https://www.theiia.org/en/content/position-papers/2020/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense/).
8. European Union, [Regulation (EU) 2022/2554 — Digital Operational Resilience Act (DORA)](https://eur-lex.europa.eu/eli/reg/2022/2554/oj).

Legal and regulatory statements are a management-level summary as at the verification date. Counsel should confirm the current consolidated text, national implementation and sector-specific interpretation at the time of any actual deployment.
