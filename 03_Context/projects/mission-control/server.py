#!/usr/bin/env python3
"""
Mission Control Dashboard — Hermes Kanban Integration (Flask + SQLite)

Complete backend with:
- REST API for agents, tasks, messages
- SSE real-time updates
- AgentListener background thread (RoE rule evaluation)
- Heartbeat thread (agent status monitoring)
- 5 agents with comprehensive Rules of Engagement

Acceptance Criteria:
✓ Server starts without error
✓ Reads tasks/agents from kanban.db
✓ Frontend loads
✓ SSE endpoint responds with real-time updates
✓ Task creation via API works
✓ Agent status from gateway
"""

import os
import time
import threading
import sqlite3
import json
import functools
import random
from flask import Flask, send_from_directory, Response, request, jsonify

# Import RulesEngine and TaskManager for AgentListener
from services.rules_engine import evaluate_decision
from services.task_manager import create_task_with_broadcast


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

# Configuration
PORT = 8420
DASHBOARD_DIR = os.path.dirname(__file__)
DASHBOARD_DB = os.path.join(DASHBOARD_DIR, 'dashboard.db')
HERMES_HOME = os.path.expanduser("~/AppData/Local/hermes")
KANBAN_DB = os.path.join(HERMES_HOME, "kanban.db")

# Global state for background threads
listener_running = True
heartbeat_running = True
listener_thread = None
heartbeat_thread = None

# Agent status thresholds
ACTIVE_THRESHOLD = 300      # 5 minutes
IDLE_THRESHOLD = 7200       # 2 hours

# SSE clients
sse_clients = []
sse_lock = threading.Lock()


def get_kanban_conn():
    """Get connection to Hermes Kanban DB with WAL mode."""
    conn = sqlite3.connect(KANBAN_DB, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def get_dashboard_conn():
    """Get connection to dashboard.db."""
    conn = sqlite3.connect(DASHBOARD_DB, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def init_database():
    """Initialize dashboard.db with complete schema and indexes."""
    conn = get_dashboard_conn()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            color TEXT NOT NULL,
            profile_name TEXT,
            last_seen INTEGER DEFAULT 0,
            status TEXT DEFAULT 'unknown',
            rules_of_engagement TEXT,
            last_processed_message_id INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS gateway_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            payload TEXT,
            timestamp INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            content TEXT NOT NULL,
            task_ref TEXT,
            created_at INTEGER NOT NULL,
            agent_name TEXT,
            agent_color TEXT
        );

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
        CREATE INDEX IF NOT EXISTS idx_messages_agent_id ON messages(agent_id);
    """)
    conn.commit()
    conn.close()
    print("✓ Dashboard DB initialized successfully")


def seed_initial_data():
    """Seed initial 5 agents with comprehensive Rules of Engagement."""
    conn = get_dashboard_conn()
    cursor = conn.cursor()

    # Agent 1: Obi-Wan Kenobi
    obiwan_roe = '''# Protocol: Inter-Agent Handoff
IF @scotty OR @k-2so OR @moneypenny OR @geppetto OR "handoff to":
  - Create task in Inter-Agent Handoff with priority Medium
  - Assign to self
  - Reply "Handoff to requested agent completed"
  - Escalate

# Protocol: Oversight
IF message contains "concern" OR "review":
  - Create task in Oversight with priority High
  - Assign to self
  - Reply "I will review this immediately"
  - Escalate

# Protocol: Deployment
IF message contains "deploy" OR "release" OR "production":
  - Create task in Deployment with priority Critical
  - Assign to k-2so
  - Reply "Deploying to production environment"
  - Escalate

# Protocol: Emergency
IF status changes to "critical" OR "emergency":
  - Create task in Emergency with priority Critical
  - Assign to geppetto
  - Reply "Emergency protocol activated"
  - Escalate'''

    # Agent 2: Scotty
    scotty_roe = '''# Protocol: Inter-Agent Handoff
IF @obi-wan OR @k-2so OR @moneypenny OR @geppetto OR "handoff to":
  - Create task in Inter-Agent Handoff with priority Medium
  - Assign to self
  - Reply "Handoff to requested agent completed"
  - Escalate

# Protocol: Development
IF message contains "implement" OR "develop" OR "build":
  - Create task in Development with priority Medium
  - Assign to self
  - Reply "Starting implementation"
  - Escalate

# Protocol: Database
IF message contains "database" OR "migration" OR "schema":
  - Create task in Database with priority High
  - Assign to self
  - Reply "Handling database changes"
  - Escalate

# Protocol: Performance
IF message contains "slow" OR "optimize" OR "performance":
  - Create task in Performance with priority High
  - Assign to self
  - Reply "Investigating performance issue"
  - Escalate'''

    # Agent 3: K-2SO
    k2so_roe = '''# Protocol: Inter-Agent Handoff
IF @obi-wan OR @scotty OR @k-2so OR @moneypenny OR @geppetto OR "handoff to":
  - Create task in Inter-Agent Handoff with priority Medium
  - Assign to self
  - Reply "Handoff to requested agent completed"
  - Escalate

# Protocol: Frontend Dev
IF message contains "ui" OR "interface" OR "frontend":
  - Create task in Frontend Development with priority Medium
  - Assign to self
  - Reply "Building user interface"
  - Escalate

# Protocol: Testing
IF message contains "test" OR "qa" OR "quality":
  - Create task in Frontend Testing with priority Medium
  - Assign to self
  - Reply "Executing frontend test suite"
  - Escalate

# Protocol: Design System
IF message contains "design" OR "style" OR "component":
  - Create task in Design System with priority Low
  - Assign to self
  - Reply "Designing system components"
  - Escalate'''

    # Agent 4: Moneypenny
    moneypenny_roe = '''# Protocol: Inter-Agent Handoff
IF @obi-wan OR @scotty OR @k-2so OR @moneypenny OR @geppetto OR "handoff to":
  - Create task in Inter-Agent Handoff with priority Medium
  - Assign to self
  - Reply "Handoff to requested agent completed"
  - Escalate

# Protocol: Outreach
IF message contains "sell" OR "outreach" OR "prospect":
  - Create task in Outreach with priority High
  - Assign to self
  - Reply "Initiating customer outreach"
  - Escalate

# Protocol: CRM
IF message contains "crm" OR "customer" OR "client":
  - Create task in CRM Management with priority Medium
  - Assign to self
  - Reply "Updating customer records"
  - Escalate

# Protocol: Reporting
IF message contains "report" OR "metrics" OR "analytics":
  - Create task in Sales Reporting with priority Low
  - Assign to self
  - Reply "Generating sales report"
  - Escalate'''

    # Agent 5: Geppetto
    geppetto_roe = '''# Protocol: Inter-Agent Handoff
IF @obi-wan OR @scotty OR @k-2so OR @moneypenny OR "handoff to":
  - Create task in Inter-Agent Handoff with priority Medium
  - Assign to self
  - Reply "Handoff to requested agent completed"
  - Escalate

# Protocol: Architecture
IF message contains "arch" OR "design" OR "structure":
  - Create task in Architecture Design with priority High
  - Assign to self
  - Reply "Designing system architecture"
  - Escalate

# Protocol: MCP Planning
IF message contains "mcp" OR "model" OR "context":
  - Create task in MCP Planning with priority High
  - Assign to self
  - Reply "Planning MCP server implementation"
  - Escalate

# Protocol: Risk Assessment
IF message contains "risk" OR "security" OR "vulnerability":
  - Create task in Risk Assessment with priority Critical
  - Assign to self
  - Reply "Conducting risk assessment"
  - Escalate'''

    agents = [
        {
            'id': 'obi-wan',
            'name': 'Obi-Wan Kenobi',
            'role': 'Orchestrator',
            'color': '#00d4aa',
            'profile_name': 'obi-wan',
            'last_seen': int(time.time()),
            'status': 'active',
            'rules_of_engagement': obiwan_roe
        },
        {
            'id': 'scotty',
            'name': 'Scotty',
            'role': 'Backend Engineering Agent',
            'color': '#ff6b35',
            'profile_name': 'scotty',
            'last_seen': int(time.time()),
            'status': 'active',
            'rules_of_engagement': scotty_roe
        },
        {
            'id': 'k-2so',
            'name': 'K-2SO',
            'role': 'Frontend Engineering Agent',
            'color': '#e91e63',
            'profile_name': 'k-2so',
            'last_seen': int(time.time()),
            'status': 'active',
            'rules_of_engagement': k2so_roe
        },
        {
            'id': 'moneypenny',
            'name': 'Moneypenny',
            'role': 'Sales & Outreach Agent',
            'color': '#ffd700',
            'profile_name': 'moneypenny',
            'last_seen': int(time.time()),
            'status': 'active',
            'rules_of_engagement': moneypenny_roe
        },
        {
            'id': 'geppetto',
            'name': 'Geppetto',
            'role': 'Solution Architect',
            'color': '#9c27b0',
            'profile_name': 'geppetto',
            'last_seen': int(time.time()),
            'status': 'active',
            'rules_of_engagement': geppetto_roe
        }
    ]

    for agent in agents:
        cursor.execute('''
            INSERT OR REPLACE INTO agents (id, name, role, color, profile_name, last_seen, status, rules_of_engagement)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent['id'],
            agent['name'],
            agent['role'],
            agent['color'],
            agent['profile_name'],
            agent['last_seen'],
            agent['status'],
            agent['rules_of_engagement']
        ))
    conn.commit()
    conn.close()
    print("✓ Initial data seeded successfully")


def broadcast_sse(event_type, data, event_id=None):
    """Broadcast SSE event to all connected clients."""
    payload = f"event: {event_type}\n"
    if event_id:
        payload += f"id: {event_id}\n"
    payload += f"data: {json.dumps(data)}\n\n"
    payload_bytes = payload.encode()

    with sse_lock:
        dead = []
        for client_queue in sse_clients:
            try:
                client_queue.put(payload_bytes)
            except Exception:
                dead.append(client_queue)
        for d in dead:
            sse_clients.remove(d)


def run_agent_listener():
    """Background thread that processes agent messages and evaluates RoE."""
    print("✓ Agent listener started")

    while listener_running:
        try:
            conn = get_dashboard_conn()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get all active agents
            cursor.execute("SELECT * FROM agents WHERE status = 'active'")
            agents = [dict(row) for row in cursor.fetchall()]

            now = int(time.time())

            for agent in agents:
                # Get unprocessed messages for this agent (direct messages + channel messages with @mentions)
                last_processed = agent.get('last_processed_message_id', 0)
                
                # Direct messages to this agent
                cursor.execute(
                    "SELECT * FROM messages WHERE agent_id = ? AND id > ? ORDER BY created_at",
                    (agent['id'], last_processed)
                )
                direct_messages = [dict(row) for row in cursor.fetchall()]
                
                # Channel messages that mention this agent (@mention)
                cursor.execute(
                    "SELECT * FROM messages WHERE channel != 'general' AND content LIKE ? AND id > ? ORDER BY created_at",
                    (f"%@{agent['id']}%", last_processed)
                )
                mention_messages = [dict(row) for row in cursor.fetchall()]
                
                # Combine and deduplicate
                all_new_messages = {m['id']: m for m in direct_messages + mention_messages}
                new_messages = list(all_new_messages.values())
                new_messages.sort(key=lambda m: m['created_at'])

                if new_messages:
                    for message in new_messages:
                        # Evaluate message against RulesEngine (same path as REST API)
                        event_payload = {
                            'agent_id': agent['id'],
                            'content': message['content'],
                            'task_ref': message.get('task_ref'),
                            'message_id': message['id']
                        }
                        result = evaluate_decision('message_created', event_payload)
                        if result['allowed']:
                            task_id = create_task_with_broadcast(
                                title=f"Handoff from {agent['name']}",
                                description=message['content'],
                                assignee=agent['id'],
                                priority=1
                            )
                            if task_id:
                                broadcast_sse('task_created', {'task_id': task_id, **event_payload})
                                print(f"  ✓ Created handoff task for {agent['name']}: {message['content']}")
                        else:
                            print(f"  ✗ Handoff denied by RoE: {result['decision']}")

                        # Update agent last_seen with retry
                        @with_retry()
                        def _update_last_seen():
                            conn_upd = get_dashboard_conn()
                            cur_upd = conn_upd.cursor()
                            cur_upd.execute(
                                "UPDATE agents SET last_seen = ? WHERE id = ?",
                                (now, agent['id'])
                            )
                            conn_upd.commit()
                            conn_upd.close()
                        _update_last_seen()

                    # Update last_processed_message_id to the highest message ID processed
                    max_msg_id = max(m['id'] for m in new_messages)
                    @with_retry()
                    def _update_processed_id():
                        conn_upd = get_dashboard_conn()
                        cur_upd = conn_upd.cursor()
                        cur_upd.execute(
                            "UPDATE agents SET last_processed_message_id = ? WHERE id = ?",
                            (max_msg_id, agent['id'])
                        )
                        conn_upd.commit()
                        conn_upd.close()
                    _update_processed_id()

            conn.close()
            time.sleep(5)

        except Exception as e:
            print(f"Error in AgentListener: {e}")
            time.sleep(5)


def run_heartbeat():
    """Update agent heartbeats and set status based on thresholds."""
    print("✓ Heartbeat started")

    while heartbeat_running:
        try:
            conn = get_dashboard_conn()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            now = int(time.time())

            # Get all agents
            cursor.execute("SELECT id, status, last_seen FROM agents")
            agents = [dict(row) for row in cursor.fetchall()]

            for agent in agents:
                current_status = agent['status']
                last_seen = agent['last_seen']

                # Determine new status based on thresholds
                if now - last_seen <= ACTIVE_THRESHOLD:
                    new_status = 'active'
                elif now - last_seen <= IDLE_THRESHOLD:
                    new_status = 'idle'
                else:
                    new_status = 'dormant'

                # Update status if changed
                if new_status != current_status:
                    @with_retry()
                    def _update_status():
                        conn_upd = get_dashboard_conn()
                        cur_upd = conn_upd.cursor()
                        cur_upd.execute(
                            "UPDATE agents SET status = ? WHERE id = ?",
                            (new_status, agent['id'])
                        )
                        conn_upd.commit()
                        conn_upd.close()
                    _update_status()
                    print(f"  ✓ Agent {agent['id']} status: {current_status} -> {new_status}")

                    # Broadcast status change
                    broadcast_sse('agent_status', {
                        'agent_id': agent['id'],
                        'status': new_status
                    })

            conn.close()
            time.sleep(60)

        except Exception as e:
            print(f"Error in heartbeat: {e}")
            time.sleep(60)


# Create Flask app
app = Flask(__name__, static_folder=os.path.join(DASHBOARD_DIR, "static"))

# Import and register blueprints
from routes import tasks_bp, messages_bp, agents_bp
app.register_blueprint(tasks_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(agents_bp)

# Set broadcast_sse in task_manager after blueprints registered (avoids circular import)
import services.task_manager as task_manager
task_manager.broadcast_sse = broadcast_sse


@app.route("/events")
def events():
    """SSE endpoint for real-time updates."""
    import queue

    client_queue = queue.Queue()
    with sse_lock:
        sse_clients.append(client_queue)

    def generate():
        # Send initial state - frontend expects raw agents/tasks payload
        from models.database import get_all_agents, get_all_tasks
        agents = get_all_agents()
        tasks = get_all_tasks()
        yield f"event: init\ndata: {json.dumps({'agents': agents, 'tasks': tasks})}\n\n"

        try:
            while True:
                try:
                    # Wait for events with timeout
                    event_data = client_queue.get(timeout=30)
                    yield event_data.decode()
                except queue.Empty:
                    # Send heartbeat
                    yield f"event: heartbeat\ndata: {json.dumps({'timestamp': time.time()})}\n\n"
        except GeneratorExit:
            pass
        finally:
            with sse_lock:
                if client_queue in sse_clients:
                    sse_clients.remove(client_queue)

    return Response(generate(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*"
    })


@app.route("/")
def index():
    """Serve the main dashboard HTML."""
    return send_from_directory(DASHBOARD_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files."""
    return send_from_directory(DASHBOARD_DIR, path)


@app.errorhandler(404)
def not_found(e):
    return {"detail": {"message": "Not found"}}, 404


@app.errorhandler(400)
def bad_request(e):
    return {"detail": {"message": "Bad request"}}, 400


@app.errorhandler(500)
def internal_error(e):
    return {"detail": {"message": "Internal server error"}}, 500


def run_server():
    """Run the Flask development server with background threads."""
    global listener_thread, heartbeat_thread

    print("✓ Starting Mission Control Dashboard on port", PORT)
    print("✓ Dashboard at http://localhost:" + str(PORT))
    print("✓ API at http://localhost:" + str(PORT) + "/api/")

    # Initialize database
    init_database()
    seed_initial_data()

    # Start background threads
    listener_thread = threading.Thread(target=run_agent_listener, daemon=True)
    listener_thread.start()

    heartbeat_thread = threading.Thread(target=run_heartbeat, daemon=True)
    heartbeat_thread.start()

    # Run Flask app
    app.run(host="127.0.0.1", port=PORT, threaded=True)


if __name__ == "__main__":
    run_server()