"""Pydantic models for Dashboard MCP Server."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from typing import Optional
from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import ConfigDict


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


class AgentConfig(BaseModel):
    """Agent configuration."""

    model: str
    temperature: float = 0.7
    max_tokens: int = 8192
    system_prompt: Optional[str] = None
    tools: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


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
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(extra="allow")


class AgentLogEntry(BaseModel):
    """Single agent log entry."""

    timestamp: datetime
    level: str
    message: str
    tool_name: Optional[str] = None
    tool_args: Optional[dict[str, Any]] = None
    tool_result: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskCreate(BaseModel):
    """Task creation request."""

    agent_id: str
    goal: str = Field(..., min_length=1, max_length=4096)
    context: dict[str, Any] = Field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL


class TaskInfo(BaseModel):
    """Complete task information."""

    task_id: str
    agent_id: str
    goal: str
    context: dict[str, Any]
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    logs: list[AgentLogEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChannelCreate(BaseModel):
    """Channel creation request."""

    name: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    description: str = Field(default="", max_length=512)
    members: list[str] = Field(default_factory=list)


class ChannelInfo(BaseModel):
    """Channel information."""

    channel_id: str
    name: str
    description: str
    members: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0


class MessageCreate(BaseModel):
    """Message creation request."""

    channel_id: str
    from_agent: str
    content: str = Field(..., min_length=1, max_length=8192)
    mentions: list[str] = Field(default_factory=list)
    reply_to: Optional[str] = None


class MessageInfo(BaseModel):
    """Message information."""

    message_id: str
    channel_id: str
    from_agent: str
    content: str
    mentions: list[str] = Field(default_factory=list)
    reply_to: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WSMessage(BaseModel):
    """WebSocket message envelope."""

    type: EventType
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


class FleetStatusResponse(BaseModel):
    """Fleet status response."""

    agents: list[AgentInfo]
    total_agents: int
    healthy_agents: int
    running_tasks: int
    total_token_usage: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskListResponse(BaseModel):
    """Task list response."""

    tasks: list[TaskInfo]
    total: int
    page: int
    page_size: int


class ChannelListResponse(BaseModel):
    """Channel list response."""

    channels: list[ChannelInfo]
    total: int


class ChannelHistoryResponse(BaseModel):
    """Channel history response."""

    messages: list[MessageInfo]
    total: int
    has_more: bool


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

    model_config = ConfigDict(env_prefix="DASHBOARD_MCP_", case_sensitive=False)


class FleetConfig(BaseModel):
    """Fleet configuration from fleet.yaml."""

    agents: list[AgentRegistration]
    default_channels: list[str] = Field(default_factory=lambda: ["general", "alerts", "handoffs"])