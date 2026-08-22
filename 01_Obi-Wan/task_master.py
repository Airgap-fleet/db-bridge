#!/usr/bin/env python3
"""
Obi-Wan Task Master — Single Source of Truth for Task Management

RULE: Only ONE task running at a time. Period.
- All tasks flow through this module
- Enforces serial execution
- Integrates with Mission Control Kanban DB
- Integrates with Obsidian Vault for persistence
"""

import sqlite3
import time
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

KANBAN_DB = Path(r"C:/Users/brook/AppData/Local/hermes/kanban.db")
VAULT = Path(r"C:/the force")
TASK_STATE_FILE = VAULT / "01_Obi-Wan" / "current_task.json"


class TaskStatus(str, Enum):
    TODO = "todo"
    TRIAGE = "triage"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    DONE = "done"
    ARCHIVED = "archived"


@dataclass
class Task:
    id: str
    title: str
    status: TaskStatus
    assignee: str
    created_at: int
    updated_at: int
    parent_id: Optional[str] = None
    depends_on: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_db_row(cls, row):
        # Actual schema: id, title, body, assignee, status, priority, created_by, created_at, ...
        return cls(
            id=row[0],
            title=row[1],
            status=TaskStatus(row[4]),
            assignee=row[3],
            created_at=row[7] if len(row) > 7 else 0,
            updated_at=row[7] if len(row) > 7 else 0,
            parent_id=None,
            depends_on=None,
            metadata={"body": row[2]} if len(row) > 2 and row[2] else None
        )


class TaskMaster:
    """Single-task orchestrator. One task at a time, always."""

    def __init__(self):
        self.db = KANBAN_DB
        self._ensure_schema()
        self._load_current()

    def _ensure_schema(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    assignee TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    parent_id TEXT,
                    depends_on TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    payload TEXT,
                    created_at INTEGER NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee)")

    def _load_current(self):
        """Load current running task from vault."""
        if TASK_STATE_FILE.exists():
            with open(TASK_STATE_FILE) as f:
                self.current_task = json.load(f)
        else:
            self.current_task = None

    def _save_current(self, task: Optional[Task]):
        """Save current running task to vault."""
        if task:
            with open(TASK_STATE_FILE, "w") as f:
                json.dump(asdict(task), f, default=str)
            self.current_task = asdict(task)
        else:
            if TASK_STATE_FILE.exists():
                TASK_STATE_FILE.unlink()
            self.current_task = None

    def get_running_tasks(self, assignee: Optional[str] = None) -> List[Task]:
        """Get all currently running tasks."""
        with sqlite3.connect(self.db) as conn:
            if assignee:
                cursor = conn.execute(
                    "SELECT * FROM tasks WHERE status = ? AND assignee = ?",
                    (TaskStatus.RUNNING.value, assignee)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM tasks WHERE status = ?",
                    (TaskStatus.RUNNING.value,)
                )
            return [Task.from_db_row(row) for row in cursor.fetchall()]

    def enforce_single_task(self, assignee: str = "obi-wan") -> int:
        """Archive all but one running task for assignee. Returns count archived."""
        running = self.get_running_tasks(assignee)
        if len(running) <= 1:
            return 0

        # Keep the oldest (first created), archive the rest
        running.sort(key=lambda t: t.created_at)
        to_archive = running[1:]
        now = int(time.time() * 1000)

        with sqlite3.connect(self.db) as conn:
            for task in to_archive:
                conn.execute(
                    "UPDATE tasks SET status = ? WHERE id = ?",
                    (TaskStatus.ARCHIVED.value, task.id)
                )
                conn.execute(
                    "INSERT INTO task_events (task_id, kind, payload, created_at) VALUES (?, ?, ?, ?)",
                    (task.id, "archived", json.dumps({"reason": "Single-task enforcement"}), now)
                )
            conn.commit()

        self._save_current(None)  # Clear current since we're resetting
        return len(to_archive)

    def start_task(self, task_id: str, assignee: str = "obi-wan") -> Task:
        """Start a task — enforces single-task rule."""
        # First, enforce single task
        self.enforce_single_task(assignee)

        now = int(time.time() * 1000)
        with sqlite3.connect(self.db) as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Task {task_id} not found")

            task = Task.from_db_row(row)

            # Check dependencies
            if task.depends_on:
                for dep_id in task.depends_on:
                    dep_cursor = conn.execute("SELECT status FROM tasks WHERE id = ?", (dep_id,))
                    dep_row = dep_cursor.fetchone()
                    if dep_row and dep_row[0] != TaskStatus.DONE.value:
                        raise ValueError(f"Dependency {dep_id} not done (status: {dep_row[0]})")

            # Update to running - use started_at as the timestamp
            conn.execute(
                "UPDATE tasks SET status = ?, started_at = ? WHERE id = ?",
                (TaskStatus.RUNNING.value, now, task_id)
            )
            conn.execute(
                "INSERT INTO task_events (task_id, kind, payload, created_at) VALUES (?, ?, ?, ?)",
                (task_id, "started", json.dumps({"assignee": assignee}), now)
            )
            conn.commit()

        task.status = TaskStatus.RUNNING
        task.updated_at = now
        self._save_current(task)
        return task

    def complete_task(self, task_id: str, success: bool = True, output: str = "") -> Task:
        """Complete a running task."""
        now = int(time.time() * 1000)
        new_status = TaskStatus.DONE.value if success else TaskStatus.BLOCKED.value

        with sqlite3.connect(self.db) as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Task {task_id} not found")

            task = Task.from_db_row(row)
            if task.status != TaskStatus.RUNNING:
                raise ValueError(f"Task {task_id} is not running (status: {task.status})")

            # Use completed_at for done, keep started_at for blocked
            if success:
                conn.execute(
                    "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
                    (new_status, now, task_id)
                )
            else:
                conn.execute(
                    "UPDATE tasks SET status = ? WHERE id = ?",
                    (new_status, task_id)
                )
            conn.execute(
                "INSERT INTO task_events (task_id, kind, payload, created_at) VALUES (?, ?, ?, ?)",
                (task_id, "completed" if success else "blocked",
                 json.dumps({"output": output, "success": success}), now)
            )
            conn.commit()

        task.status = TaskStatus(new_status)
        task.updated_at = now
        self._save_current(None)  # Clear current
        return task

    def get_next_task(self, assignee: str = "obi-wan") -> Optional[Task]:
        """Get next todo/triage task for assignee with satisfied dependencies."""
        with sqlite3.connect(self.db) as conn:
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE assignee = ? AND status IN (?, ?) ORDER BY created_at",
                (assignee, TaskStatus.TODO.value, TaskStatus.TRIAGE.value)
            )
            for row in cursor.fetchall():
                task = Task.from_db_row(row)
                if task.depends_on:
                    all_done = True
                    for dep_id in task.depends_on:
                        dep_cursor = conn.execute("SELECT status FROM tasks WHERE id = ?", (dep_id,))
                        dep_row = dep_cursor.fetchone()
                        if dep_row and dep_row[0] != TaskStatus.DONE.value:
                            all_done = False
                            break
                    if not all_done:
                        continue
                return task
        return None

    def create_task(self, task_id: str, title: str, assignee: str,
                    depends_on: Optional[List[str]] = None,
                    parent_id: Optional[str] = None,
                    metadata: Optional[Dict] = None) -> Task:
        """Create a new task."""
        now = int(time.time() * 1000)
        task = Task(
            id=task_id,
            title=title,
            status=TaskStatus.TODO,
            assignee=assignee,
            created_at=now,
            updated_at=now,
            parent_id=parent_id,
            depends_on=depends_on or [],
            metadata=metadata or {}
        )

        with sqlite3.connect(self.db) as conn:
            conn.execute(
                """INSERT INTO tasks (id, title, body, assignee, status, created_at, started_at, completed_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (task.id, task.title, json.dumps(task.metadata) if task.metadata else "",
                 task.assignee, task.status.value, now, None, None)
            )
            conn.execute(
                "INSERT INTO task_events (task_id, kind, payload, created_at) VALUES (?, ?, ?, ?)",
                (task_id, "created", json.dumps(metadata or {}), now)
            )
            conn.commit()

        return task

    def status(self) -> Dict:
        """Get current system status."""
        running = self.get_running_tasks()
        next_task = self.get_next_task()
        return {
            "current_task": self.current_task,
            "running_count": len(running),
            "running_tasks": [asdict(t) for t in running],
            "next_task": asdict(next_task) if next_task else None,
            "single_task_enforced": len(running) <= 1
        }


def main():
    import sys
    tm = TaskMaster()

    if len(sys.argv) < 2:
        print(json.dumps(tm.status(), indent=2, default=str))
        return

    cmd = sys.argv[1]

    if cmd == "enforce":
        count = tm.enforce_single_task()
        print(f"Archived {count} extra running tasks")
    elif cmd == "start":
        if len(sys.argv) < 3:
            print("Usage: task_master.py start <task_id> [assignee]")
            sys.exit(1)
        task = tm.start_task(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "obi-wan")
        print(f"Started: {task.id} - {task.title}")
    elif cmd == "complete":
        if len(sys.argv) < 3:
            print("Usage: task_master.py complete <task_id> [success] [output]")
            sys.exit(1)
        success = sys.argv[3].lower() != "false" if len(sys.argv) > 3 else True
        output = sys.argv[4] if len(sys.argv) > 4 else ""
        task = tm.complete_task(sys.argv[2], success, output)
        print(f"Completed: {task.id} - {task.status}")
    elif cmd == "status":
        print(json.dumps(tm.status(), indent=2, default=str))
    elif cmd == "next":
        task = tm.get_next_task()
        if task:
            print(f"Next: {task.id} - {task.title}")
        else:
            print("No ready tasks")
    elif cmd == "create":
        if len(sys.argv) < 5:
            print("Usage: task_master.py create <task_id> <title> <assignee> [depends_on_json]")
            sys.exit(1)
        depends_on = json.loads(sys.argv[5]) if len(sys.argv) > 5 else None
        task = tm.create_task(sys.argv[2], sys.argv[3], sys.argv[4], depends_on)
        print(f"Created: {task.id} - {task.title}")
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()