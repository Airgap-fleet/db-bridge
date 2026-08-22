"""Database connection and initialization for Mission Control Dashboard."""

import sqlite3
import time
import os
import functools
import random

# Configuration
HERMES_HOME = os.path.expanduser("~/AppData/Local/hermes")
KANBAN_DB = os.path.join(HERMES_HOME, "kanban.db")
DASHBOARD_DIR = os.path.dirname(os.path.dirname(__file__))

# Kanban status flow
STATUS_FLOW = ["triage", "todo", "ready", "running", "blocked", "done"]
PRIORITY_MAP = {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}


def with_retry(max_attempts=5, base_delay=0.05):
    """Retry decorator with exponential backoff for sqlite3.OperationalError: database is locked."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            for attempt in range(max_attempts):
                try:
                    return fn(*a, **kw)
                except sqlite3.OperationalError as e:
                    if 'locked' in str(e).lower() and attempt < max_attempts - 1:
                        time.sleep(base_delay * (2 ** attempt) + random.uniform(0, 0.01))
                        continue
                    raise
        return wrapper
    return deco


def get_kanban_conn():
    """Get connection to Hermes Kanban DB with WAL mode."""
    conn = sqlite3.connect(KANBAN_DB, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def get_dashboard_conn():
    """Get connection to dashboard DB."""
    conn = sqlite3.connect(os.path.join(DASHBOARD_DIR, "dashboard.db"), check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def init_dashboard_db():
    """Initialize dashboard-specific tables (agent registry, config)."""
    conn = sqlite3.connect(os.path.join(DASHBOARD_DIR, "dashboard.db"), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            color TEXT NOT NULL,
            profile_name TEXT,  -- Hermes profile name
            last_seen INTEGER DEFAULT 0,
            status TEXT DEFAULT 'unknown'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS gateway_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            payload TEXT,
            timestamp INTEGER NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            content TEXT NOT NULL,
            task_ref TEXT,
            channel TEXT DEFAULT 'general',
            created_at INTEGER NOT NULL,
            agent_name TEXT,
            agent_color TEXT
        )
    """)
    conn.commit()

    # Seed agent registry (maps to Hermes profiles)
    agents = [
        ("obi-wan", "Obi-Wan Kenobi", "Orchestrator", "#00d4aa", "obi-wan"),
        ("scotty", "Scotty", "Backend Engineer", "#ff6b35", "scotty"),
        ("k-2so", "K-2SO", "Frontend Engineer", "#e91e63", "k-2so"),
        ("moneypenny", "Moneypenny", "Sales & Outreach", "#ffd700", "moneypenny"),
        ("geppetto", "Geppetto", "Solution Architect", "#9c27b0", "geppetto"),
    ]
    for a in agents:
        c.execute("""
            INSERT OR REPLACE INTO agents (id, name, role, color, profile_name, last_seen, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (*a, int(time.time()), "active"))
    conn.commit()
    print("✓ Dashboard DB initialized")
    return conn


def get_all_tasks():
    """Fetch all tasks from Hermes Kanban DB with enriched data."""
    conn = get_kanban_conn()
    c = conn.cursor()
    c.execute("""
        SELECT 
            t.id, t.title, t.body as description, t.assignee, t.status,
            t.priority, t.created_at, t.started_at, t.completed_at,
            t.worker_pid, t.last_heartbeat_at, t.consecutive_failures,
            t.model_override, t.provider_override, t.skills,
            t.goal_mode, t.max_retries
        FROM tasks t
        ORDER BY t.created_at DESC
    """)
    tasks = []
    for row in c.fetchall():
        task = dict(row)
        task["priority_label"] = PRIORITY_MAP.get(task["priority"], "Medium")
        task["status_label"] = task["status"].capitalize()
        tasks.append(task)
    conn.close()
    return tasks


def get_task_events(task_id, limit=50):
    """Fetch events for a specific task."""
    conn = get_kanban_conn()
    c = conn.cursor()
    c.execute("""
        SELECT event_type, payload, timestamp
        FROM task_events
        WHERE task_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (task_id, limit))
    events = [dict(row) for row in c.fetchall()]
    conn.close()
    return events


def get_all_agents():
    """Get agent registry from dashboard DB + live status from kanban."""
    conn = get_dashboard_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM agents")
    agents = [dict(row) for row in c.fetchall()]
    conn.close()

    # Enrich with kanban data (active tasks, last heartbeat)
    kanban_conn = get_kanban_conn()
    kc = kanban_conn.cursor()
    for agent in agents:
        kc.execute("""
            SELECT COUNT(*) as active_tasks,
                   MAX(last_heartbeat_at) as last_heartbeat
            FROM tasks
            WHERE assignee = ? AND status IN ('running', 'ready', 'blocked')
        """, (agent["id"],))
        row = kc.fetchone()
        if row:
            agent["active_tasks"] = row["active_tasks"]
            agent["last_heartbeat"] = row["last_heartbeat"]
            # Determine status from heartbeat
            if row["last_heartbeat"]:
                since = time.time() - row["last_heartbeat"]
                if since < 300:
                    agent["status"] = "active"
                elif since < 7200:
                    agent["status"] = "idle"
                else:
                    agent["status"] = "dormant"
            else:
                agent["status"] = "unknown"
    kanban_conn.close()
    return agents


def create_task(title, description="", assignee="", priority=1, skills=None, model_override=None):
    """Create a new task in Hermes Kanban DB."""
    @with_retry()
    def _create():
        import uuid
        task_id = f"t_{uuid.uuid4().hex[:8]}"
        now = int(time.time())

        conn = get_kanban_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO tasks (
                id, title, body, assignee, status, priority,
                created_at, workspace_kind, goal_mode, skills,
                model_override, created_by
            ) VALUES (?, ?, ?, ?, 'triage', ?, ?, 'scratch', 1, ?, ?, 'dashboard')
        """, (task_id, title, description, assignee, priority, now, skills, model_override))

        # Log event
        import json
        c.execute("""
            INSERT INTO task_events (task_id, kind, payload, created_at)
            VALUES (?, 'created', ?, ?)
        """, (task_id, json.dumps({"assignee": assignee, "status": "triage"}), now))

        conn.commit()
        conn.close()

        return task_id
    return _create()


def update_task_status(task_id, status):
    """Update task status in Kanban DB."""
    @with_retry()
    def _update():
        import json
        now = int(time.time())
        conn = get_kanban_conn()
        c = conn.cursor()
        c.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        c.execute("""
            INSERT INTO task_events (task_id, kind, payload, created_at)
            VALUES (?, 'status_changed', ?, ?)
        """, (task_id, json.dumps({"new_status": status}), now))
        conn.commit()
        conn.close()
    return _update()


def update_task(task_id, title=None, description=None, status=None, priority=None, assignee=None):
    """Update task fields in Kanban DB."""
    @with_retry()
    def _update():
        conn = get_kanban_conn()
        c = conn.cursor()
    
        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("body = ?")
            params.append(description)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)
        if assignee is not None:
            updates.append("assignee = ?")
            params.append(assignee)
    
        if not updates:
            conn.close()
            return False
    
        params.append(task_id)
        c.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        updated = c.rowcount > 0
        conn.close()
        return updated
    return _update()


def delete_task(task_id):
    """Delete task from Kanban DB."""
    @with_retry()
    def _delete():
        conn = get_kanban_conn()
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        task_deleted = c.rowcount > 0
        c.execute("DELETE FROM task_events WHERE task_id = ?", (task_id,))
        conn.commit()
        conn.close()
        return task_deleted
    return _delete()


def get_messages(task_ref=None):
    """Get messages from dashboard DB, optionally filtered by task_ref."""
    conn = get_dashboard_conn()
    c = conn.cursor()
    if task_ref:
        c.execute("SELECT * FROM messages WHERE task_ref = ? ORDER BY created_at DESC", (task_ref,))
    else:
        c.execute("SELECT * FROM messages ORDER BY created_at DESC")
    messages = [dict(row) for row in c.fetchall()]
    conn.close()
    return messages


def get_messages_by_channel(channel):
    """Get messages from dashboard DB filtered by channel."""
    conn = get_dashboard_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE channel = ? ORDER BY created_at DESC", (channel,))
    messages = [dict(row) for row in c.fetchall()]
    conn.close()
    return messages


def create_message(agent_id, content, task_ref=None, channel='general', agent_name=None, agent_color=None):
    """Create a new message in dashboard DB."""
    @with_retry()
    def _create():
        now = int(time.time())
        conn = get_dashboard_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO messages (agent_id, content, task_ref, channel, created_at, agent_name, agent_color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (agent_id, content, task_ref, channel, now, agent_name, agent_color))
        conn.commit()
        message_id = c.lastrowid
        conn.close()
        return message_id
    return _create()


def create_agent(agent_id, name, role, color, profile_name=None):
    """Create a new agent in dashboard DB."""
    @with_retry()
    def _create():
        now = int(time.time())
        conn = get_dashboard_conn()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO agents (id, name, role, color, profile_name, last_seen, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (agent_id, name, role, color, profile_name, now, "active"))
        conn.commit()
        conn.close()
        return agent_id
    return _create()


def delete_agent(agent_id):
    """Delete agent from dashboard DB."""
    @with_retry()
    def _delete():
        conn = get_dashboard_conn()
        c = conn.cursor()
        c.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
        conn.commit()
        deleted = c.rowcount > 0
        conn.close()
        return deleted
    return _delete()