"""Pydantic models for Dashboard MCP Server with Kanban integration."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict, field_validator


class AgentStatus(str, Enum):
    """Agent health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
class EventType(str, Enum):
    """WebSocket event types."""

    AGENT_STATUS = "agent_status"
    TASK_UPDATE = "task_update"
    NEW_MESSAGE = "new_message"
    CHANNEL_MESSAGE = "channel_message"
    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    CHANNEL_CREATED = "channel_created"
    KANBAN_EVENT = "kanban_event"
class AgentConfig(BaseModel):
    """Agent configuration."""

    model: str
    temperature: float = 0.7
    max_tokens: int = 8192
    system_prompt: Optional[str] = None
    tools: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        return v

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v):
        if not 100 <= v <= 1000000:
            raise ValueError("max_tokens must be between 100 and 1000000")
        return v
class AgentRegistration(BaseModel):
    """Agent registration request."""

    agent_id: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=128)
    role: str = Field(..., min_length=1, max_length=64)
    capabilities: list[str] = Field(default_factory=list)
    model: str = Field(..., min_length=1)
    config: Optional[AgentConfig] = None
class AgentInfo(BaseModel):
    """Complete agent information."""

    agent_id: str
    name: str
    role: str
    capabilities: list[str]
    model: str
    config: Optional[AgentConfig] = None
    status: AgentStatus = AgentStatus.OFFLINE
    current_task: Optional[str] = None
    token_usage: int = 0
    last_heartbeat: Optional[datetime] = None
    registered_at: datetime
    updated_at: datetime
class TaskInfo(BaseModel):
    """Task information."""

    task_id: str
    agent_id: str
    goal: str
    context: dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    logs: list[Any] = Field(default_factory=list)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime
class MessageInfo(BaseModel):
    """Message information."""

    message_id: str
    channel_id: str
    from_agent: str
    content: str
    mentions: list[str] = Field(default_factory=list)
    reply_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
class ChannelInfo(BaseModel):
    """Channel information."""

    channel_id: str
    name: str
    description: str
    members: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
class WSMessage(BaseModel):
    """WebSocket message."""

    type: EventType
    payload: dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
class KanbanTask(BaseModel):
    """Kanban task model."""

    task_id: str
    title: str
    body: str
    status: str
    assignee: Optional[str] = None
    priority: str = "normal"
    tags: list[str] = Field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
class KanbanRun(BaseModel):
    """Kanban task run model."""

    run_id: str
    task_id: str
    outcome: str
    summary: Optional[str] = None
    meta_data: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime
    completed_at: Optional[datetime] = None
    elapsed: Optional[int] = None
class KanbanEvent(BaseModel):
    """Kanban event model."""

    event_id: str
    type: str
    task_id: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime
class FleetConfig(BaseModel):
    """Fleet configuration from fleet.yaml."""

    agents: list[AgentRegistration]
    default_channels: list[str] = Field(default_factory=lambda: ["general", "alerts", "handoffs"])
    # Role-based task routing
    task_routing: dict[str, Any] = Field(default_factory=dict)
    # Kanban board configuration
    kanban_board: dict[str, Any] = Field(default_factory=dict)
    # Dispatcher configuration
    dispatcher: dict[str, Any] = Field(default_factory=dict)
class Config(BaseModel):
    """Server configuration from environment."""

    port: int = Field(default=8000, ge=1, le=65535)
    ws_enabled: bool = True
    agentcomms_path: str = "AgentComms.md"
    fleet_config: str = "fleet.yaml"
    channels_dir: str = "channels"
    enable_group_chat: bool = True
    default_channels: list[str] = Field(default_factory=lambda: ["general", "alerts", "handoffs"])
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    auth_token: Optional[str] = None
    # Kanban configuration
    kanban_board: str = Field(default="afaaS-fleet", description="Kanban board name for this fleet")
    fleet_config_path: str = Field(default="config/fleet.yaml", description="Path to fleet.yaml")
    kanban_dispatcher_enabled: bool = Field(default=True, description="Enable gateway-embedded dispatcher")

    model_config = ConfigDict(env_prefix="DASHBOARD_MCP_", case_sensitive=False)
class FleetStatusResponse(BaseModel):
    """Fleet status response with Kanban metrics."""

    agents: list[AgentInfo]
    total_agents: int
    healthy_agents: int
    running_tasks: int
    total_token_usage: int
    # Kanban metrics
    column_counts: dict[str, int]
    throughput_today: int
    assignee_breakdown: dict[str, int]
class TaskListResponse(BaseModel):
    """Task list response."""

    tasks: list[KanbanTask]
    total: int
    page: int
    page_size: int
class TaskCreate(BaseModel):
    """Task creation request."""

    title: str
    body: str = ""
    tags: list[str] = Field(default_factory=list)
    priority: str = "normal"
    assignee_role: Optional[str] = None
    scheduled_at: Optional[str] = None
class MessageCreate(BaseModel):
    """Message creation request."""

    channel_id: str
    from_agent: str
    content: str
    mentions: list[str] = Field(default_factory=list)
    reply_to: Optional[str] = None
class ChannelCreate(BaseModel):
    """Channel creation request."""

    name: str
    description: str = ""
    members: list[str] = Field(default_factory=list)