# ADR-002: Mandatory Fail-Closed Enforcement

**Status:** Accepted
**Date:** 2026-11-07

## Context

AI agents must not execute protected operations
when authorization is missing or unreliable.

## Decision

- Default authorization is DENY.
- Policy evaluation failures deny execution.
- Every protected operation passes through a PEP.
- Authorization applies to the authenticated caller,
  requested action, resource and relevant parameters.
- Direct execution paths must not bypass enforcement.
- REQUIRE_APPROVAL is not execution permission.
- Advisory governance agents cannot override policies.

## Consequences

- Reduced risk of unauthorized execution.
- Policy outages may interrupt protected operations.
- Enforcement bypass testing is mandatory.
