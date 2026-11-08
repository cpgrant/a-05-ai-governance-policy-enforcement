"""SQLite-backed approval state machine for the local prototype."""

import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def operation_hash(operation: dict[str, Any]) -> str:
    payload = json.dumps(
        operation, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass
class Approval:
    approval_id: str
    requester_id: str
    operation_digest: str
    created_at: datetime
    expires_at: datetime
    status: str = "PENDING"
    approver_id: str | None = None
    consumed_at: datetime | None = None


class ApprovalEngine:
    """Persist approval state and lifecycle evidence in SQLite.

    SQLite is appropriate for this single-host demonstrator. It is not a
    multi-host consensus store or a tamper-resistant audit system.
    """

    def __init__(self, db_path: str | Path | None = None):
        configured = db_path or os.environ.get(
            "A05_APPROVAL_DB", "runtime/approvals.sqlite3"
        )
        self.db_path = str(configured)
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 10000")
        try:
            yield connection
        finally:
            connection.close()

    def _initialize(self):
        with self._connect() as db:
            db.execute("PRAGMA journal_mode = WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    requester_id TEXT NOT NULL,
                    operation_digest TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    approver_id TEXT,
                    consumed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS approval_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    approval_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    details TEXT NOT NULL
                );
            """)
        if self.db_path != ":memory:" and Path(self.db_path).exists():
            os.chmod(self.db_path, 0o600)

    @staticmethod
    def _event(db, approval_id, event_type, actor_id, details=""):
        db.execute(
            "INSERT INTO approval_events "
            "(approval_id,event_type,actor_id,occurred_at,details) "
            "VALUES (?,?,?,?,?)",
            (approval_id, event_type, actor_id, utcnow().isoformat(), details),
        )

    @staticmethod
    def _model(row) -> Approval:
        return Approval(
            approval_id=row["approval_id"],
            requester_id=row["requester_id"],
            operation_digest=row["operation_digest"],
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            status=row["status"],
            approver_id=row["approver_id"],
            consumed_at=(datetime.fromisoformat(row["consumed_at"])
                         if row["consumed_at"] else None),
        )

    def _expire_if_needed(self, db, approval_id, row):
        if row["status"] in {"PENDING", "APPROVED"} and utcnow() >= datetime.fromisoformat(row["expires_at"]):
            db.execute(
                "UPDATE approvals SET status='EXPIRED' WHERE approval_id=? AND status=?",
                (approval_id, row["status"]),
            )
            self._event(db, approval_id, "EXPIRED", "system")
            return db.execute(
                "SELECT * FROM approvals WHERE approval_id=?", (approval_id,)
            ).fetchone()
        return row

    def create(self, requester_id: str, operation: dict[str, Any], ttl_seconds: int = 300) -> Approval:
        if not requester_id:
            raise ValueError("Requester identity required")
        if not isinstance(ttl_seconds, int) or not 1 <= ttl_seconds <= 3600:
            raise ValueError("Invalid approval lifetime")
        if not isinstance(operation, dict) or not operation:
            raise ValueError("Operation required")
        digest = operation_hash(operation)
        now = utcnow()
        approval = Approval(
            approval_id=str(uuid4()), requester_id=requester_id,
            operation_digest=digest, created_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "INSERT INTO approvals VALUES (?,?,?,?,?,?,?,?)",
                (approval.approval_id, requester_id, digest, now.isoformat(),
                 approval.expires_at.isoformat(), "PENDING", None, None),
            )
            self._event(db, approval.approval_id, "CREATED", requester_id, digest)
            db.commit()
        return approval

    def get(self, approval_id: str) -> Approval:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
            if row is None:
                db.rollback()
                raise KeyError("Unknown approval")
            row = self._expire_if_needed(db, approval_id, row)
            model = self._model(row)
            db.commit()
            return model

    def decide(self, approval_id: str, approver_id: str, approve: bool) -> Approval:
        if not approver_id:
            raise PermissionError("Approver identity required")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
            if row is None:
                db.rollback()
                raise KeyError("Unknown approval")
            row = self._expire_if_needed(db, approval_id, row)
            if row["status"] != "PENDING":
                db.commit()
                raise PermissionError("Approval is no longer pending")
            if approver_id == row["requester_id"]:
                db.rollback()
                raise PermissionError("Self-approval is prohibited")
            status = "APPROVED" if approve else "REJECTED"
            db.execute(
                "UPDATE approvals SET status=?, approver_id=? WHERE approval_id=? AND status='PENDING'",
                (status, approver_id, approval_id),
            )
            self._event(db, approval_id, status, approver_id)
            result = db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
            db.commit()
            return self._model(result)

    def consume(self, approval_id: str, requester_id: str, operation: dict[str, Any]) -> bool:
        """Atomically consume a matching, unexpired approval exactly once."""
        digest = operation_hash(operation)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM approvals WHERE approval_id=?", (approval_id,)).fetchone()
            if row is None:
                db.rollback()
                return False
            row = self._expire_if_needed(db, approval_id, row)
            if (row["status"] != "APPROVED" or row["requester_id"] != requester_id
                    or row["operation_digest"] != digest):
                db.commit()
                return False
            now = utcnow().isoformat()
            changed = db.execute(
                "UPDATE approvals SET status='CONSUMED', consumed_at=? "
                "WHERE approval_id=? AND status='APPROVED' AND expires_at>? "
                "AND requester_id=? AND operation_digest=?",
                (now, approval_id, now, requester_id, digest),
            ).rowcount
            if changed:
                self._event(db, approval_id, "CONSUMED", requester_id)
            db.commit()
            return changed == 1

    def events(self, approval_id: str) -> list[dict[str, str]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT event_type, actor_id, occurred_at, details FROM approval_events "
                "WHERE approval_id=? ORDER BY event_id", (approval_id,)
            ).fetchall()
            return [dict(row) for row in rows]
