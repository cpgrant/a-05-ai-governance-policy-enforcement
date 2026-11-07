from dataclasses import dataclass
from typing import Any, Callable

from src.audit.recorder import AuditRecorder
from src.contracts.policy import GovernanceRequest
from src.enforcement.pep import (
    EnforcementResult,
    PolicyEnforcementPoint,
)


class UnknownToolError(Exception):
    pass


class DuplicateToolError(Exception):
    pass


@dataclass(frozen=True)
class RegisteredTool:
    name: str
    action: str
    resource: str
    handler: Callable[[dict[str, Any]], Any]


class TrustedToolRegistry:
    def __init__(
        self,
        audit: AuditRecorder | None = None,
    ):
        self._tools: dict[str, RegisteredTool] = {}
        self._pep = PolicyEnforcementPoint(audit=audit)

    def register(self, tool: RegisteredTool) -> None:
        if tool.name in self._tools:
            raise DuplicateToolError(tool.name)

        self._tools[tool.name] = tool

    def execute(
        self,
        tool_name: str,
        agent_id: str,
        parameters: dict[str, Any],
    ) -> EnforcementResult:

        tool = self._tools.get(tool_name)

        if tool is None:
            raise UnknownToolError(tool_name)

        request = GovernanceRequest(
            agent_id=agent_id,
            action=tool.action,
            resource=tool.resource,
            context=parameters,
        )

        return self._pep.execute(
            request,
            lambda: tool.handler(parameters.copy()),
        )
