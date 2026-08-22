"""Task management service for Mission Control Dashboard."""

import json
import threading
import time
from models.database import STATUS_FLOW, get_all_agents, get_all_tasks
from models.database import create_task, update_task_status, update_task, delete_task
from models.database import create_message, create_agent, delete_agent
from services.rules_engine import evaluate_decision

# Global state for SSE connections
clients = []
clients_lock = threading.Lock()
gateway_ws = None

# broadcast_sse will be set by server.py after import
broadcast_sse = None

# Global state for SSE connections
clients = []
clients_lock = threading.Lock()
gateway_ws = None


def broadcast(event):
    """Send event to all SSE clients."""
    data = f"event: update\ndata: {json.dumps(event)}\n\n"
    with clients_lock:
        dead = []
        for client in clients:
            try:
                client.write(data.encode())
            except Exception:
                dead.append(client)
        for d in dead:
            clients.remove(d)


def register_client(wfile):
    """Register a new SSE client."""
    with clients_lock:
        clients.append(wfile)


def unregister_client(wfile):
    """Unregister an SSE client."""
    with clients_lock:
        if wfile in clients:
            clients.remove(wfile)


def get_initial_state():
    """Get initial state for SSE connection."""
    return {
        "type": "init",
        "agents": get_all_agents(),
        "tasks": get_all_tasks()
    }


def heartbeat_loop(wfile):
    """Send heartbeat every 30 seconds."""
    try:
        while True:
            time.sleep(30)
            wfile.write(b"event: heartbeat\ndata: {}\n\n")
    except Exception:
        pass


def _broadcast_if_allowed(event_type: str, event: dict):
    """Evaluate rules before broadcasting. Returns True if broadcasted."""
    payload = event.copy()
    # Extract agent_id if present for context
    agent_id = payload.get("agent_id") or payload.get("assignee")
    result = evaluate_decision(event_type, payload)
    if result["allowed"]:
        broadcast(event)
        return True
    else:
        # Log the denial but don't broadcast
        print(f"RoE deny: {event_type} - {result['decision']}")
        return False


def create_task_with_broadcast(title, description="", assignee="", priority=1, skills=None, model_override=None, source="api"):
    """Create task and broadcast to SSE clients (if allowed by RoE)."""
    event = {"type": "task_created", "assignee": assignee, "title": title, "description": description, "priority": priority, "source": source}
    if source != "manual":  # Skip RoE for manual user actions
        if not _broadcast_if_allowed("task_created", event):
            return None  # Denied by RoE
    task_id = create_task(title, description, assignee, priority, skills, model_override)
    event["task_id"] = task_id
    if source != "manual":
        _broadcast_if_allowed("task_created", event)
    return task_id


def update_task_status_with_broadcast(task_id, status):
    """Update task status and broadcast to SSE clients (if allowed by RoE)."""
    event = {"type": "task_updated", "task_id": task_id, "status": status}
    if not _broadcast_if_allowed("task_updated", event):
        return False
    update_task_status(task_id, status)
    _broadcast_if_allowed("task_updated", event)
    return True


def update_task_with_broadcast(task_id, **kwargs):
    """Update task and broadcast to SSE clients (if allowed by RoE)."""
    event = {"type": "task_updated", "task_id": task_id, **kwargs}
    if not _broadcast_if_allowed("task_updated", event):
        return False
    updated = update_task(task_id, **kwargs)
    if updated:
        _broadcast_if_allowed("task_updated", event)
    return updated


def delete_task_with_broadcast(task_id):
    """Delete task and broadcast to SSE clients (if allowed by RoE)."""
    event = {"type": "task_deleted", "task_id": task_id}
    if not _broadcast_if_allowed("task_deleted", event):
        return False
    deleted = delete_task(task_id)
    if deleted:
        _broadcast_if_allowed("task_deleted", event)
    return deleted


def create_message_with_broadcast(agent_id, content, task_ref=None, channel='general', agent_name=None, agent_color=None):
    """Create message and broadcast to SSE clients (if allowed by RoE)."""
    event = {"type": "message_created", "agent_id": agent_id, "content": content, "task_ref": task_ref, "channel": channel}
    if not _broadcast_if_allowed("message_created", event):
        return None
    message_id = create_message(agent_id, content, task_ref, channel, agent_name, agent_color)
    event["message_id"] = message_id
    # Broadcast the message_created event with full details
    broadcast_sse('message_created', {
        'message_id': message_id,
        'agent_id': agent_id,
        'content': content,
        'task_ref': task_ref,
        'channel': channel
    })
    return message_id


def create_agent_with_broadcast(agent_id, name, role, color, profile_name=None):
    """Create agent and broadcast to SSE clients (if allowed by RoE)."""
    event = {"type": "agent_created", "agent_id": agent_id, "name": name, "role": role, "color": color}
    if not _broadcast_if_allowed("agent_created", event):
        return None
    agent_id = create_agent(agent_id, name, role, color, profile_name)
    _broadcast_if_allowed("agent_created", event)
    return agent_id


def delete_agent_with_broadcast(agent_id):
    """Delete agent and broadcast to SSE clients (if allowed by RoE)."""
    event = {"type": "agent_deleted", "agent_id": agent_id}
    if not _broadcast_if_allowed("agent_deleted", event):
        return False
    deleted = delete_agent(agent_id)
    if deleted:
        _broadcast_if_allowed("agent_deleted", event)
    return deleted