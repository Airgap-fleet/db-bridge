"""Dashboard MCP Server - AFaaS Fleet API + AgentComms + Group Chat layer."""

__version__ = "0.1.0"

from .core import DashboardCore, WebSocketHub, WSMessage, EventType
from .models import (
    AgentRegistration,
    TaskCreate,
    MessageCreate,
    ChannelCreate,
    Config,
    KanbanTask,
    KanbanRun,
    KanbanEvent,
    FleetConfig,
)

__all__ = [
    "__version__",
    "DashboardCore",
    "WebSocketHub", 
    "WSMessage",
    "EventType",
    "AgentRegistration",
    "TaskCreate",
    "MessageCreate",
    "ChannelCreate",
    "Config",
    "KanbanTask",
    "KanbanRun",
    "KanbanEvent",
    "FleetConfig",
]