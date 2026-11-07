import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_PATH = Path("runtime/a04_mcp_audit.jsonl")


def record_mcp_event(
    *,
    request_id: str,
    agent_id: str,
    tool_name: str,
    event: str,
    outcome: str,
    policy_id: str,
    reason: str = "",
    audit_path: Path | None = None,
) -> dict[str, Any]:
    """Append metadata-only audit event. No customer payloads."""

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "agent_id": agent_id,
        "tool_name": tool_name,
        "event": event,
        "outcome": outcome,
        "policy_id": policy_id,
        "reason": reason,
    }

    path = audit_path if audit_path is not None else AUDIT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    # O_APPEND prevents overwriting previous audit records.
    # This is not a tamper-resistant audit store.
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    fd = os.open(path, flags, 0o600)

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(record) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        raise

    return record
