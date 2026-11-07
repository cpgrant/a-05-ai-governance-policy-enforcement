# AI-A05 — AI Governance & Policy Enforcement

Part of the AI Architecture Portfolio.

## Purpose

A standalone, reusable governance architecture
for enterprise AI agents and autonomous workflows.

## Core Capabilities

- Independent policy evaluation
- Mandatory authorization and enforcement
- Risk-based autonomy
- Human approval workflows
- Audit evidence and explainability
- Policy and tool sandboxing
- Advisory agentic governance
- Integration with MCP and A2A systems

## Technology Stack

- Python 3.12.3
- FastAPI / Pydantic
- Open Policy Agent / Rego (planned)
- PostgreSQL (planned)
- Docker Compose (planned)
- OpenTelemetry (planned)
- LangGraph / Ollama (optional)

## Architecture

See docs/AI-A05-Architecture-Specification.md.

Diagrams are available in diagrams/ and
diagrams/rendered/.

Architecture decisions are recorded in docs/adr/.

## Current Status

Day 1 architecture baseline.

Implemented:
- Python project configuration
- Governance request and decision contracts
- Initial contract tests
- Architecture specification and diagrams
- Architecture Decision Records

Not yet implemented:
- Independent policy evaluation
- Runtime enforcement
- Human approval execution workflow
- Audit persistence
- Sandboxed execution
- Enterprise integration adapters

## Development

Install:

    python -m pip install -e ".[dev]"

Run tests:

    python -m pytest -v

## Security

This repository is an architecture and engineering
prototype, not a production-certified security system.

Protected enterprise actions must not rely on
unverified prototype enforcement controls.

## Day 2 — Governance Engine & Enforcement

Implemented:
- OPA/Rego financial authorization policy
- Python OPA policy adapter
- FastAPI governance evaluation endpoint
- Policy Enforcement Point
- Fail-closed authorization handling
- JSONL authorization and execution auditing
- Trusted tool registry prototype
- Simulated enterprise payment execution
- Automated policy, API, enforcement and audit tests

Validation:
- 27 automated tests passing

Security limitations:
- Agent identity is not yet authenticated.
- Tool parameters require stronger schema validation.
- Audit persistence is not production-grade.
- Human approval is not implemented.
- Runtime isolation and prevention of direct tool bypass
  require additional engineering.

Next:
- Enterprise integration and secure identity binding
- Human approval lifecycle
- MCP tool authorization
