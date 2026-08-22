#!/usr/bin/env python3
"""Dashboard MCP Server - Run MCP directly with FastAPI lifespan."""

import asyncio
import uvicorn
from fastmcp import FastMCP

# Create FastMCP application
mcp = FastMCP(name="dashboard-mcp")

# Import tools after mcp is created
from dashboard_mcp.core import DashboardCore, WebSocketHub, WSMessage, EventType
from dashboard_mcp.models import (
    AgentRegistration, TaskCreate, MessageCreate, ChannelCreate,
    Config, KanbanTask, KanbanRun, KanbanEvent, FleetConfig,
    AgentStatus
)
from typing import Any
import os
import structlog
import logging

# Setup structured logging
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)
logger = structlog.get_logger()

# Global core instance
_core_instance: DashboardCore | None = None


def get_core() -> DashboardCore:
    """Get or create the core instance."""
    global _core_instance
    if _core_instance is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dashboard_mcp")
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        _core_instance = DashboardCore(database_url, redis_url)
        asyncio.create_task(_core_instance.initialize())
    return _core_instance


# MCP Tools
@mcp.tool()
async def register_agent(agent_id: str, name: str, role: str, capabilities: list[str], model: str, config: dict[str, Any] | None = None) -> dict:
    """Register agent in the system."""
    core = get_core()
    agent_data = AgentRegistration(
        agent_id=agent_id,
        name=name,
        role=role,
        capabilities=capabilities,
        model=model,
        config=config,
    )
    return await core.mcp_dashboard_fleet_register(agent_data)


@mcp.tool()
async def get_fleet_agents() -> list[dict]:
    """List all fleet agents + status."""
    core = get_core()
    return await core.mcp_dashboard_fleet_agents()


@mcp.tool()
async def agent_heartbeat(agent_id: str, status: str, current_task: str | None = None, token_usage: int = 0) -> dict:
    """Agent heartbeat."""
    core = get_core()
    status_enum = AgentStatus(status)
    return await core.mcp_dashboard_fleet_heartbeat(agent_id, status_enum, current_task, token_usage)


@mcp.tool()
async def unregister_agent(agent_id: str) -> dict:
    """Unregister agent."""
    core = get_core()
    return await core.mcp_dashboard_fleet_unregister(agent_id)


@mcp.tool()
async def create_channel(name: str, description: str = "", members: list[str] | None = None) -> dict:
    """Create channel."""
    core = get_core()
    return await core.mcp_dashboard_agentcomms_create_channel(name, description, members)


@mcp.tool()
async def list_channels() -> list[dict]:
    """List channels."""
    core = get_core()
    return await core.mcp_dashboard_agentcomms_channels()


@mcp.tool()
async def post_message(channel_id: str, from_agent: str, content: str, mentions: list[str] | None = None, reply_to: str | None = None) -> dict:
    """Post message to channel."""
    core = get_core()
    return await core.mcp_dashboard_agentcomms_post(channel_id, from_agent, content, mentions, reply_to)


@mcp.tool()
async def get_channel_history(channel_id: str, limit: int = 100) -> list[dict]:
    """Get channel history."""
    core = get_core()
    return await core.mcp_dashboard_agentcomms_history(channel_id, limit)


@mcp.tool()
async def watch_messages(channel_id: str | None = None) -> dict:
    """SSE/WebSocket stream of new messages."""
    return {
        "endpoint": "/ws",
        "description": "Connect to WebSocket for real-time message streaming",
        "parameters": {"channel_id": "Optional channel ID to filter messages"},
        "usage": "Use the WebSocket endpoint with channel_id parameter to subscribe to message updates"
    }


@mcp.tool()
async def get_board_stats() -> dict:
    """Get Kanban board stats."""
    core = get_core()
    return await core.mcp_dashboard_kanban_board()


@mcp.tool()
async def list_tasks(status: str | None = None, assignee_role: str | None = None, tags: list[str] | None = None, priority: str | None = None, search: str | None = None) -> list[dict]:
    """List tasks with filters."""
    core = get_core()
    return await core.mcp_dashboard_kanban_tasks(status, assignee_role, tags, priority, search)


@mcp.tool()
async def get_task(task_id: str) -> dict:
    """Get task detail."""
    core = get_core()
    return await core.mcp_dashboard_kanban_task(task_id)


@mcp.tool()
async def create_task(title: str, body: str = "", tags: list[str] | None = None, priority: str = "normal", assignee_role: str | None = None, scheduled_at: str | None = None) -> dict:
    """Create task — idempotent by title+board."""
    core = get_core()
    scheduled_datetime = None
    if scheduled_at:
        from datetime import datetime
        scheduled_datetime = datetime.fromisoformat(scheduled_at)
    return await core.mcp_dashboard_kanban_create(title, body, tags, priority, assignee_role, scheduled_datetime)


@mcp.tool()
async def assign_task(task_id: str, assignee_role: str | None = None, assignee_profile: str | None = None) -> dict:
    """Assign task."""
    core = get_core()
    return await core.mcp_dashboard_kanban_assign(task_id, assignee_role, assignee_profile)


@mcp.tool()
async def complete_task(task_id: str, summary: str, metadata: dict[str, Any] | None = None, result: dict[str, Any] | None = None) -> dict:
    """Complete task — structured handoff."""
    core = get_core()
    return await core.mcp_dashboard_kanban_complete(task_id, summary, metadata, result)


@mcp.tool()
async def block_task(task_id: str, reason: str, kind: str = "needs_input") -> dict:
    """Block task."""
    core = get_core()
    return await core.mcp_dashboard_kanban_block(task_id, reason, kind)


@mcp.tool()
async def promote_task(task_id: str, from_status: str = "todo", to_status: str = "in_progress") -> dict:
    """Promote task."""
    core = get_core()
    return await core.mcp_dashboard_kanban_promote(task_id, from_status, to_status)


@mcp.tool()
async def watch_tasks(filter_kind: str | None = None, filter_task_id: str | None = None) -> dict:
    """SSE/WebSocket stream of task events."""
    return {
        "endpoint": "/ws",
        "description": "Connect to WebSocket for real-time task event streaming",
        "parameters": {
            "filter_kind": "Optional filter for event type",
            "filter_task_id": "Optional filter for specific task"
        },
        "usage": "Use the WebSocket endpoint with appropriate filters to subscribe to task updates"
    }


@mcp.tool()
async def get_task_runs(task_id: str) -> list[dict]:
    """Get task attempt history."""
    core = get_core()
    return await core.mcp_dashboard_kanban_runs(task_id)


@mcp.tool()
async def get_fleet_config() -> dict:
    """Get fleet configuration from fleet.yaml."""
    core = get_core()
    return await core.mcp_dashboard_fleet_config()


if __name__ == "__main__":
    # Run MCP with HTTP transport on port 8001, stateless mode for 2026-07-28
    asyncio.run(mcp.run_http_async(host="0.0.0.0", port=8001, path="/mcp", stateless_http=True))