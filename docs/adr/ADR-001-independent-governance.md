# ADR-001: Independent Governance Architecture

**Status:** Accepted
**Date:** 2026-11-07

## Context

Enterprise AI systems require governance that is
independent of individual agents, models and tools.

## Decision

AI-A05 will provide a standalone governance service
with separate control, decision and enforcement planes.

Policy decisions will be evaluated through an
independent OPA/Rego policy engine.

Integration adapters will support REST, Python,
MCP and A2A consumers.

## Consequences

- Governance can be reused across projects.
- Policies can change without modifying agent logic.
- Protected operations require trusted enforcement.
- Independent deployment introduces availability,
  authentication and operational requirements.
