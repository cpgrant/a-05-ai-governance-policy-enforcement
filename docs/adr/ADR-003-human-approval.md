# ADR-003: Scoped Human Approval

**Status:** Accepted
**Date:** 2026-11-07

## Context

Some enterprise actions require human authorization.

## Decision

Approval records must bind authorization to:

- Authenticated requesting identity
- Action and resource
- Relevant execution parameters
- Authorized approver
- Approval scope and expiry
- Applicable policy version

Approvals must be verified before execution.

Approvals cannot be reused for unrelated actions.
Approvals must be invalidated or re-evaluated when
their security-relevant conditions change.

## Consequences

- Supports bounded autonomous execution.
- Requires secure approval storage.
- Requires approval state and replay protection.
- Introduces additional workflow complexity.
