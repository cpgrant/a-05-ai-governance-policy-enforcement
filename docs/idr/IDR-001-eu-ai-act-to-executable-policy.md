# IDR-001 — EU AI Act to Executable Policy (OPA/Rego)

**Type:** Ideation Decision Record  
**Status:** Proposed — For Investigation  
**Domain:** AI Governance, Regulatory Technology, Autonomous Enterprises  
**Related projects:** AI-A05 Governance & Policy Enforcement; future Regulatory Policy as Code project

## 1. The Idea

Investigate whether requirements from the EU AI Act can be translated into machine-readable and executable governance policies using Open Policy Agent (OPA) and Rego.

The objective is to explore a system capable of continuously evaluating AI systems, their permissions, operational decisions and supporting compliance evidence against approved regulatory interpretations.

**Central research question:**

How much of enterprise AI regulation can be transformed into continuously evaluated and enforceable policies while retaining legal interpretation, human accountability and regulatory oversight?

## 2. Business Opportunity

Organizations deploying autonomous AI face growing challenges in understanding regulatory obligations, enforcing governance requirements and demonstrating accountability.

Traditional compliance processes often rely on periodic assessments, documents and manual reviews.

A regulatory policy engine could support:

- Automated governance checks before deploying AI systems.
- Continuous enforcement of approved operating restrictions.
- Human approval for regulated or high-impact decisions.
- Evidence collection for internal and external audits.
- Detection of missing assessments or expired approvals.
- Consistent application of policies across multiple AI agents and enterprise systems.

## 3. Proposed Solution

A layered architecture:

1. **Regulatory sources:** EU AI Act, amendments and authoritative guidance.
2. **Legal interpretation:** Expert-reviewed obligations and applicability decisions.
3. **Regulatory knowledge model:** Structured requirements, classifications and control mappings.
4. **Policy generation:** Convert approved control specifications into executable OPA/Rego policies.
5. **Policy enforcement:** Evaluate deployment requests and agent actions.
6. **Evidence and monitoring:** Record decisions, supporting evidence, exceptions and policy versions.
7. **Human governance:** Legal review, policy approval, exceptions and residual-risk acceptance.

Legal interpretation and policy approval must remain under appropriate human responsibility.

## 4. Candidate Use Cases

| Use case | Example automated control |
|---|---|
| AI system registration | Require an approved system record |
| Risk classification | Route systems with unresolved classification for human review |
| Deployment authorization | Block deployment without required approvals |
| Human oversight | Require an appropriate human approval mechanism |
| Documentation | Check required document records exist and are approved |
| Auditability | Require logging capabilities before operations |
| Regulatory changes | Identify systems requiring reassessment following policy updates |

These are examples of enterprise controls informed by regulations, not complete implementations of legal obligations.

## 5. Research Challenges

- Translating legal language into unambiguous machine-readable requirements.
- Determining whether obligations apply to a particular AI system.
- Distinguishing legal obligations from internal corporate policies.
- Handling exceptions, interpretations and regulatory changes.
- Establishing trustworthy evidence rather than relying on agent-supplied assertions.
- Maintaining version history and traceability to legal sources.
- Avoiding false claims of automated regulatory compliance.

## 6. Relationship to Existing Architecture

**AI-A05** provides an initial technical foundation for policy evaluation, enforcement, approvals and auditing.

A future **Digital Business Twin (A06)** could provide structured information about enterprise systems, operational responsibilities, risk classifications and governance state.

A separate regulatory policy capability could evaluate that information against approved obligations.

These integrations remain architectural possibilities rather than implemented features.

## 7. Suggested Proof of Concept

Select five narrowly scoped internal governance controls mapped to relevant EU AI Act provisions.

For each control:

1. Identify the source provision and applicable version.
2. Obtain an approved interpretation.
3. Define a machine-readable control.
4. Implement the control using OPA/Rego.
5. Create representative permit, deny and review test cases.
6. Capture the policy version, decision and supporting evidence.
7. Evaluate whether the automation meaningfully reduces compliance risk.

The prototype must not claim to certify EU AI Act compliance.

## 8. Success Criteria

- Traceable mapping from approved requirements to executable policies.
- Repeatable and testable policy decisions.
- Clear distinction between automated checks and legal judgement.
- Explainable decisions and supporting evidence.
- Demonstrated handling of regulatory version changes.
- Identification of controls that cannot be reliably automated.

## 9. Open Questions

- Should the regulatory knowledge model use structured tables, knowledge graphs or both?
- Can LLMs assist in extracting candidate obligations without autonomously approving legal interpretations?
- How should jurisdiction, effective dates and regulatory amendments be represented?
- Which compliance evidence must come from independently trusted sources?
- How can the system identify conflicting or overlapping regulations?
- Should regulatory policy evaluation occur during deployment, execution or both?

## 10. Preliminary Recommendation

**Proceed with a limited research prototype.**

Reuse selected concepts from AI-A05, but keep the regulatory interpretation and obligation-mapping capability as a separate research project.

Do not expand the completed A05 reference implementation into a comprehensive regulatory compliance platform.

## 11. Decision Status

**Proposed — Not yet approved for implementation.**

Next decision: assess feasibility, regulatory scope, business value and the preferred architecture before allocating a development project.