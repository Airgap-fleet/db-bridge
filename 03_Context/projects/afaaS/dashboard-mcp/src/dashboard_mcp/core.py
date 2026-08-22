"""Dashboard MCP Server Core - PostgreSQL backend for fleet registry, AgentComms channels, and Kanban board bridge."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.websockets import WebSocketState
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.ext.declarative import declared_attr

from .models import (
    AgentInfo,
    AgentStatus,
    TaskInfo,
    TaskStatus,
    TaskPriority,
    MessageInfo,
    ChannelInfo,
    WSMessage,
    EventType,
    KanbanTask,
    KanbanRun,
    KanbanEvent,
    FleetConfig,
    FleetStatusResponse,
    TaskListResponse,
    Config,
)

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

# Database models
Base = declarative_base()

class AgentRegistryDB(Base):
    """Database model for agent registry."""
    __tablename__ = "agent_registry"
    
    agent_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    capabilities = Column(JSON, nullable=False)
    model = Column(String, nullable=False)
    config = Column(JSON, nullable=True)
    status = Column(String, default=AgentStatus.OFFLINE.value)
    current_task = Column(String, nullable=True)
    token_usage = Column(Integer, default=0)
    last_heartbeat = Column(DateTime, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
class TaskQueueDB(Base):
    """Database model for task queue."""
    __tablename__ = "task_queue"
    
    task_id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey("agent_registry.agent_id"), nullable=False)
    goal = Column(Text, nullable=False)
    context = Column(JSON, nullable=False)
    priority = Column(String, default=TaskPriority.NORMAL.value)
    status = Column(String, default=TaskStatus.PENDING.value)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    logs = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
class ChannelDB(Base):
    """Database model for channels."""
    __tablename__ = "channels"
    
    channel_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    members = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    message_count = Column(Integer, default=0)
class MessageDB(Base):
    """Database model for messages."""
    __tablename__ = "messages"
    
    message_id = Column(String, primary_key=True)
    channel_id = Column(String, ForeignKey("channels.channel_id"), nullable=False)
    from_agent = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    mentions = Column(JSON, default=list)
    reply_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
class KanbanTaskDB(Base):
    """Database model for Kanban tasks."""
    __tablename__ = "kanban_tasks"
    
    task_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    assignee = Column(String, nullable=True)
    priority = Column(String, nullable=False)
    tags = Column(JSON, default=list)
    scheduled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
class KanbanRunDB(Base):
    """Database model for Kanban task runs."""
    __tablename__ = "kanban_runs"
    
    run_id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("kanban_tasks.task_id"), nullable=False)
    outcome = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    meta_data = Column(JSON, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    elapsed = Column(Integer, nullable=True)
class KanbanEventDB(Base):
    """Database model for Kanban events."""
    __tablename__ = "kanban_events"
    
    event_id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    task_id = Column(String, ForeignKey("kanban_tasks.task_id"), nullable=False)
    data = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)
class WebSocketHub:
    """WebSocket hub for managing active connections and broadcasting."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url)
        self._subscriptions: Dict[str, Set[WebSocket]] = {}
        self._channels: Set[str] = set()
    
    async def subscribe(self, websocket: WebSocket, channel: str = "all"):
        """Subscribe a WebSocket connection to a channel."""
        await websocket.accept()
        if channel not in self._subscriptions:
            self._subscriptions[channel] = set()
        self._subscriptions[channel].add(websocket)
        self._channels.add(channel)
        logger.info("WebSocket subscribed", channel=channel, websocket=websocket.client_host)
    
    async def unsubscribe(self, websocket: WebSocket, channel: str = "all"):
        """Unsubscribe a WebSocket connection from a channel."""
        if channel in self._subscriptions:
            self._subscriptions[channel].discard(websocket)
            if not self._subscriptions[channel]:
                del self._subscriptions[channel]
        self._channels.discard(channel)
        logger.info("WebSocket unsubscribed", channel=channel, websocket=websocket.client_host)
    
    async def broadcast(self, message: WSMessage, channel: str = "all"):
        """Broadcast a message to all subscribers in a channel."""
        if channel not in self._subscriptions:
            return
        
        message_data = {
            "type": message.type.value,
            "payload": message.payload,
            "timestamp": message.timestamp.isoformat(),
            "correlation_id": message.correlation_id,
        }
        
        disconnected = set()
        for websocket in self._subscriptions[channel]:
            try:
                await websocket.send_json(message_data)
            except WebSocketDisconnect:
                disconnected.add(websocket)
            except Exception as e:
                logger.error("WebSocket broadcast error", error=str(e), websocket=websocket.client_host)
        
        # Remove disconnected connections
        for websocket in disconnected:
            await self.unsubscribe(websocket, channel)
class DashboardCore:
    """Core business logic for dashboard operations with Kanban integration."""
    
    def __init__(self, database_url: str, redis_url: str):
        self.database_url = database_url
        self.redis_url = redis_url
        self.engine: Optional[AsyncEngine] = None
        self.websocket_hub: Optional[WebSocketHub] = None
        self._redis_pubsub = None
    
    async def initialize(self):
        """Initialize database connections and Redis pub/sub."""
        self.engine = create_async_engine(self.database_url)
        self.websocket_hub = WebSocketHub(self.redis_url)
        
        # Initialize Redis pub/sub for external broadcasting
        self._redis_pubsub = self.websocket_hub.redis.pubsub()
        await self._redis_pubsub.subscribe("dashboard_events")
        
        # Start background task for Redis message handling
        asyncio.create_task(self._handle_redis_messages())
        
        logger.info("DashboardCore initialized")
    
    @asynccontextmanager
    async def get_db_session(self) -> AsyncSession:
        """Get a database session."""
        async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    # Fleet Registry MCP Tools
    async def mcp_dashboard_fleet_agents(self) -> list[dict]:
        """List all fleet agents + status."""
        async with self.get_db_session() as session:
            stmt = session.query(AgentRegistryDB)
            agents_db = await session.execute(stmt)
            agents = agents_db.scalars().all()
            
            result = []
            for agent_db in agents:
                agent_info = AgentInfo(
                    agent_id=agent_db.agent_id,
                    name=agent_db.name,
                    role=agent_db.role,
                    capabilities=agent_db.capabilities,
                    model=agent_db.model,
                    config=agent_db.config,
                    status=agent_db.status,
                    current_task=agent_db.current_task,
                    token_usage=agent_db.token_usage,
                    last_heartbeat=agent_db.last_heartbeat,
                    registered_at=agent_db.registered_at,
                    updated_at=agent_db.updated_at,
                )
                result.append(agent_info.dict())
            
            logger.info("Fleet agents listed", count=len(result))
            return result
    
    async def mcp_dashboard_fleet_register(self, agent_data: AgentRegistration) -> dict:
        """Register agent in the system."""
        async with self.get_db_session() as session:
            # Check if agent already exists
            stmt = session.query(AgentRegistryDB).filter_by(agent_id=agent_data.agent_id)
            existing = await session.execute(stmt)
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=409, detail=f"Agent {agent_data.agent_id} already registered")
            
            # Create new agent registry entry
            agent_db = AgentRegistryDB(
                agent_id=agent_data.agent_id,
                name=agent_data.name,
                role=agent_data.role,
                capabilities=agent_data.capabilities,
                model=agent_data.model,
                config=agent_data.config.dict() if agent_data.config else None,
                status=AgentStatus.OFFLINE.value,
                registered_at=datetime.utcnow(),
            )
            session.add(agent_db)
            await session.flush()
            
            logger.info("Agent registered", agent_id=agent_data.agent_id, name=agent_data.name)
            return agent_db.__dict__
    
    async def mcp_dashboard_fleet_heartbeat(self, agent_id: str, status: AgentStatus, 
                                             current_task: Optional[str] = None, token_usage: int = 0) -> dict:
        """Agent heartbeat."""
        async with self.get_db_session() as session:
            agent_db = await session.get(AgentRegistryDB, agent_id)
            if not agent_db:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
            agent_db.status = status.value
            agent_db.current_task = current_task
            agent_db.token_usage = token_usage
            agent_db.last_heartbeat = datetime.utcnow()
            
            logger.info("Agent heartbeat", agent_id=agent_id, status=status.value)
            return agent_db.__dict__
    
    async def mcp_dashboard_fleet_unregister(self, agent_id: str) -> bool:
        """Unregister agent."""
        async with self.get_db_session() as session:
            agent_db = await session.get(AgentRegistryDB, agent_id)
            if not agent_db:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
            await session.delete(agent_db)
            await session.flush()
            
            logger.info("Agent unregistered", agent_id=agent_id)
            return True
    
    # AgentComms MCP Tools
    async def mcp_dashboard_agentcomms_channels(self) -> list[dict]:
        """List channels."""
        async with self.get_db_session() as session:
            stmt = session.query(ChannelDB)
            channels_db = await session.execute(stmt)
            channels = channels_db.scalars().all()
            
            result = []
            for channel_db in channels:
                channel_info = ChannelInfo(
                    channel_id=channel_db.channel_id,
                    name=channel_db.name,
                    description=channel_db.description,
                    members=channel_db.members,
                    created_at=channel_db.created_at,
                    updated_at=channel_db.updated_at,
                    message_count=channel_db.message_count,
                )
                result.append(channel_info.dict())
            
            logger.info("Channels listed", count=len(result))
            return result
    
    async def mcp_dashboard_agentcomms_create_channel(self, name: str, description: str = "", 
                                                      members: list[str] | None = None) -> dict:
        """Create channel."""
        async with self.get_db_session() as session:
            # Check if channel already exists
            stmt = session.query(ChannelDB).filter_by(name=name)
            existing = await session.execute(stmt)
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=409, detail=f"Channel {name} already exists")
            
            channel_db = ChannelDB(
                channel_id=str(uuid.uuid4()),
                name=name,
                description=description,
                members=members or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(channel_db)
            await session.flush()
            
            logger.info("Channel created", channel_id=channel_db.channel_id, name=name)
            return channel_db.__dict__
    
    async def mcp_dashboard_agentcomms_post(self, channel_id: str, from_agent: str, 
                                             content: str, mentions: list[str] | None = None,
                                             reply_to: Optional[str] = None) -> dict:
        """Post message to channel."""
        async with self.get_db_session() as session:
            # Check if channel exists
            stmt = session.query(ChannelDB).filter_by(channel_id=channel_id)
            channel = await session.execute(stmt)
            if not channel.scalar_one_or_none():
                raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
            
            message_db = MessageDB(
                message_id=str(uuid.uuid4()),
                channel_id=channel_id,
                from_agent=from_agent,
                content=content,
                mentions=mentions or [],
                reply_to=reply_to,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(message_db)
            
            # Update channel message count
            channel_db = await session.get(ChannelDB, channel_id)
            channel_db.message_count = channel_db.message_count + 1
            
            await session.flush()
            
            logger.info("Message posted", message_id=message_db.message_id, channel=channel_id)
            return message_db.__dict__
    
    async def mcp_dashboard_agentcomms_history(self, channel_id: str, limit: int = 100, 
                                               before_message_id: Optional[str] = None) -> list[dict]:
        """Get channel history."""
        async with self.get_db_session() as session:
            # Check if channel exists
            stmt = session.query(ChannelDB).filter_by(channel_id=channel_id)
            channel = await session.execute(stmt)
            if not channel.scalar_one_or_none():
                raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
            
            # Build query
            query = session.query(MessageDB).filter_by(channel_id=channel_id)
            if before_message_id:
                query = query.filter(MessageDB.message_id < before_message_id)
            
            messages_db = query.order_by(MessageDB.created_at.desc()).limit(limit).all()
            
            result = []
            for message_db in reversed(messages_db):
                message_info = MessageInfo(
                    message_id=message_db.message_id,
                    channel_id=message_db.channel_id,
                    from_agent=message_db.from_agent,
                    content=message_db.content,
                    mentions=message_db.mentions,
                    reply_to=message_db.reply_to,
                    created_at=message_db.created_at,
                    updated_at=message_db.updated_at,
                )
                result.append(message_info.dict())
            
            logger.info("Channel history retrieved", channel=channel_id, count=len(result))
            return result
    
    async def mcp_dashboard_agentcomms_watch(self, channel_id: str | None = None) -> None:
        """SSE/WebSocket stream of new messages."""
        # This method is meant to be called as a WebSocket endpoint
        # WebSocket handling is done in the FastAPI server
        pass
    
    # Kanban MCP Tools
    async def mcp_dashboard_kanban_board(self) -> dict:
        """Get board stats."""
        async with self.get_db_session() as session:
            # Get column counts
            stmt = session.query(KanbanTaskDB.status).group_by(KanbanTaskDB.status)
            status_counts = {}
            for row in await session.execute(stmt):
                status_counts[row[0]] = status_counts.get(row[0], 0) + 1
            
            # Get throughput (tasks completed today)
            today = datetime.utcnow().date()
            stmt = session.query(KanbanTaskDB).filter(
                KanbanTaskDB.updated_at >= today
            )
            completed_tasks = await session.execute(stmt)
            throughput = len(completed_tasks.scalars().all())
            
            # Get assignee breakdown
            stmt = session.query(KanbanTaskDB.assignee).group_by(KanbanTaskDB.assignee)
            assignee_breakdown = {}
            for row in await session.execute(stmt):
                assignee_breakdown[row[0]] = assignee_breakdown.get(row[0], 0) + 1
            
            result = {
                "column_counts": status_counts,
                "throughput_today": throughput,
                "assignee_breakdown": assignee_breakdown,
            }
            
            logger.info("Kanban board stats retrieved")
            return result
    
    async def mcp_dashboard_kanban_tasks(self, status: Optional[str] = None, 
                                         assignee_role: Optional[str] = None, 
                                         tags: list[str] | None = None, 
                                         priority: Optional[str] = None,
                                         search: Optional[str] = None) -> list[dict]:
        """List tasks with filters."""
        async with self.get_db_session() as session:
            # Start with base query
            query = session.query(KanbanTaskDB)
            
            # Apply filters
            if status:
                query = query.filter(KanbanTaskDB.status == status)
            if assignee_role:
                query = query.filter(KanbanTaskDB.assignee == assignee_role)
            if tags:
                for tag in tags:
                    query = query.filter(KanbanTaskDB.tags.op("@>")(f'{{{tag}}}'))
            if priority:
                query = query.filter(KanbanTaskDB.priority == priority)
            if search:
                query = query.filter(KanbanTaskDB.title.contains(search))
            
            tasks_db = query.all()
            
            result = []
            for task_db in tasks_db:
                task_info = KanbanTask(
                    task_id=task_db.task_id,
                    title=task_db.title,
                    body=task_db.body,
                    status=task_db.status,
                    assignee=task_db.assignee,
                    priority=task_db.priority,
                    tags=task_db.tags,
                    scheduled_at=task_db.scheduled_at,
                    created_at=task_db.created_at,
                    updated_at=task_db.updated_at,
                )
                result.append(task_info.dict())
            
            logger.info("Kanban tasks retrieved", count=len(result), filters={
                "status": status,
                "assignee_role": assignee_role,
                "tags": tags,
                "priority": priority,
                "search": search,
            })
            return result
    
    async def mcp_dashboard_kanban_task(self, task_id: str) -> dict:
        """Get task detail."""
        async with self.get_db_session() as session:
            task_db = await session.get(KanbanTaskDB, task_id)
            if not task_db:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Get runs for this task
            stmt = session.query(KanbanRunDB).filter_by(task_id=task_id)
            runs_db = await session.execute(stmt)
            runs = []
            for run_db in runs_db.scalars().all():
                runs.append({
                    "run_id": run_db.run_id,
                    "outcome": run_db.outcome,
                    "summary": run_db.summary,
                    "metadata": run_db.metadata,
                    "started_at": run_db.started_at,
                    "completed_at": run_db.completed_at,
                    "elapsed": run_db.elapsed,
                })
            
            task_info = KanbanTask(
                task_id=task_db.task_id,
                title=task_db.title,
                body=task_db.body,
                status=task_db.status,
                assignee=task_db.assignee,
                priority=task_db.priority,
                tags=task_db.tags,
                scheduled_at=task_db.scheduled_at,
                created_at=task_db.created_at,
                updated_at=task_db.updated_at,
            )
            
            result = task_info.dict()
            result["runs"] = runs
            
            logger.info("Kanban task retrieved", task_id=task_id)
            return result
    
    async def mcp_dashboard_kanban_create(self, title: str, body: str = "", 
                                          tags: list[str] | None = None,
                                          priority: str = "normal",
                                          assignee_role: Optional[str] = None,
                                          scheduled_at: Optional[datetime] = None) -> dict:
        """Create task — idempotent by title+board."""
        async with self.get_db_session() as session:
            # Check if task already exists (idempotency)
            stmt = session.query(KanbanTaskDB).filter_by(title=title)
            existing = await session.execute(stmt)
            if existing.scalar_one_or_none():
                logger.info("Task already exists", title=title)
                return existing.scalar_one_or_none().__dict__
            
            # Create new task
            task_db = KanbanTaskDB(
                task_id=str(uuid.uuid4()),
                title=title,
                body=body,
                status="todo",
                assignee=assignee_role,
                priority=priority,
                tags=tags or [],
                scheduled_at=scheduled_at,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(task_db)
            await session.flush()
            
            logger.info("Kanban task created", task_id=task_db.task_id, title=title)
            return task_db.__dict__
    
    async def mcp_dashboard_kanban_assign(self, task_id: str, assignee_role: Optional[str] = None,
                                          assignee_profile: Optional[str] = None) -> dict:
        """Assign task."""
        async with self.get_db_session() as session:
            task_db = await session.get(KanbanTaskDB, task_id)
            if not task_db:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Determine assignee based on parameters
            assignee = None
            if assignee_role:
                assignee = assignee_role
            elif assignee_profile:
                assignee = assignee_profile
            
            task_db.assignee = assignee
            task_db.status = "in_progress" if assignee else "todo"
            task_db.updated_at = datetime.utcnow()
            
            await session.flush()
            
            logger.info("Kanban task assigned", task_id=task_id, assignee=assignee)
            return task_db.__dict__
    
    async def mcp_dashboard_kanban_complete(self, task_id: str, summary: str,
                                            metadata: dict[str, Any] | None = None,
                                            result: dict[str, Any] | None = None) -> dict:
        """Complete task — structured handoff."""
        async with self.get_db_session() as session:
            task_db = await session.get(KanbanTaskDB, task_id)
            if not task_db:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Create run record
            run_db = KanbanRunDB(
                run_id=str(uuid.uuid4()),
                task_id=task_id,
                outcome="completed",
                summary=summary,
                meta_data=metadata or {},
                started_at=task_db.created_at,
                completed_at=datetime.utcnow(),
                elapsed=(datetime.utcnow() - task_db.created_at).seconds,
            )
            session.add(run_db)
            
            # Update task status
            task_db.status = "completed"
            task_db.updated_at = datetime.utcnow()
            
            await session.flush()
            
            # Broadcast completion event
            kanban_event = KanbanEvent(
                event_id=str(uuid.uuid4()),
                type="completed",
                task_id=task_id,
                data={"summary": summary, "metadata": metadata or {}},
            )
            await self.websocket_hub.broadcast(
                WSMessage(
                    type=EventType.KANBAN_EVENT,
                    payload=kanban_event.dict(),
                    correlation_id=str(uuid.uuid4()),
                )
            )
            
            logger.info("Kanban task completed", task_id=task_id)
            return task_db.__dict__
    
    async def mcp_dashboard_kanban_block(self, task_id: str, reason: str, kind: str = "needs_input") -> dict:
        """Block task."""
        async with self.get_db_session() as session:
            task_db = await session.get(KanbanTaskDB, task_id)
            if not task_db:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            # Update task status based on block reason
            if kind == "needs_input":
                task_db.status = "blocked"
            elif kind == "capability":
                task_db.status = "blocked - insufficient capability"
            elif kind == "transient":
                task_db.status = "blocked - transient issue"
            elif kind == "dependency":
                task_db.status = "blocked - dependency"
            
            task_db.updated_at = datetime.utcnow()
            
            # Create event
            event_db = KanbanEventDB(
                event_id=str(uuid.uuid4()),
                type="blocked",
                task_id=task_id,
                data={"reason": reason, "kind": kind},
                timestamp=datetime.utcnow(),
            )
            session.add(event_db)
            
            await session.flush()
            
            logger.info("Kanban task blocked", task_id=task_id, reason=reason, kind=kind)
            return task_db.__dict__
    
    async def mcp_dashboard_kanban_promote(self, task_id: str, from_status: str = "todo",
                                           to_status: str = "in_progress") -> dict:
        """Promote task."""
        async with self.get_db_session() as session:
            task_db = await session.get(KanbanTaskDB, task_id)
            if not task_db:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
            if task_db.status != from_status:
                raise HTTPException(status_code=400, detail=f"Task status is {task_db.status}, not {from_status}")
            
            task_db.status = to_status
            task_db.updated_at = datetime.utcnow()
            
            # Create event
            event_db = KanbanEventDB(
                event_id=str(uuid.uuid4()),
                type="promoted",
                task_id=task_id,
                data={"from_status": from_status, "to_status": to_status},
                timestamp=datetime.utcnow(),
            )
            session.add(event_db)
            
            await session.flush()
            
            logger.info("Kanban task promoted", task_id=task_id, from_status=from_status, to_status=to_status)
            return task_db.__dict__
    
    async def mcp_dashboard_kanban_watch(self, filter_kind: Optional[str] = None, 
                                          filter_task_id: Optional[str] = None) -> None:
        """SSE/WebSocket stream of task events."""
        # This method is meant to be called as a WebSocket endpoint
        # WebSocket handling is done in the FastAPI server
        pass
    
    async def mcp_dashboard_kanban_runs(self, task_id: str) -> list[dict]:
        """Get task attempt history."""
        async with self.get_db_session() as session:
            # Get runs for this task
            stmt = session.query(KanbanRunDB).filter_by(task_id=task_id)
            runs_db = await session.execute(stmt)
            
            result = []
            for run_db in runs_db.scalars().all():
                result.append({
                    "run_id": run_db.run_id,
                    "task_id": run_db.task_id,
                    "outcome": run_db.outcome,
                    "summary": run_db.summary,
                    "metadata": run_db.metadata,
                    "started_at": run_db.started_at,
                    "completed_at": run_db.completed_at,
                    "elapsed": run_db.elapsed,
                })
            
            logger.info("Kanban task runs retrieved", task_id=task_id, count=len(result))
            return result
    
    # Helper method to get fleet config
    async def mcp_dashboard_fleet_config(self) -> dict:
        """Get fleet configuration from fleet.yaml."""
        # This would read and parse fleet.yaml file
        # For now, return a default config
        config = FleetConfig(
            agents=[],
            default_channels=["general", "alerts", "handoffs"],
            task_routing={},
            kanban_board={},
            dispatcher={},
        )
        return config.dict()
    
    # Helper methods for external use
    async def get_agent_by_id(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent by ID."""
        async with self.get_db_session() as session:
            stmt = session.query(AgentRegistryDB).filter_by(agent_id=agent_id)
            agent_db = await session.execute(stmt)
            agent = agent_db.scalar_one_or_none()
            
            if not agent:
                return None
            
            return AgentInfo(
                agent_id=agent.agent_id,
                name=agent.name,
                role=agent.role,
                capabilities=agent.capabilities,
                model=agent.model,
                config=agent.config,
                status=agent.status,
                current_task=agent.current_task,
                token_usage=agent.token_usage,
                last_heartbeat=agent.last_heartbeat,
                registered_at=agent.registered_at,
                updated_at=agent.updated_at,
            )
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus, current_task: Optional[str] = None):
        """Update agent status and optionally current task."""
        async with self.get_db_session() as session:
            agent_db = await session.get(AgentRegistryDB, agent_id)
            if not agent_db:
                logger.warning("Agent not found for status update", agent_id=agent_id)
                return
            
            agent_db.status = status.value
            if current_task is not None:
                agent_db.current_task = current_task
            agent_db.updated_at = datetime.utcnow()
            
            logger.info("Agent status updated", agent_id=agent_id, status=status.value)
    
    async def _handle_redis_messages(self):
        """Handle incoming Redis pub/sub messages."""
        if not self._redis_pubsub:
            return
        
        async for message in self._redis_pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    logger.debug("Redis message received", data=data)
                    # Process Redis message if needed
                except json.JSONDecodeError:
                    logger.error("Invalid JSON in Redis message", data=message['data'])

    # AgentListener integration methods
    async def get_active_agents(self) -> List[AgentInfo]:
        """Get all active agents from the database."""
        async with self.get_db_session() as session:
            stmt = session.query(AgentRegistryDB).filter(
                AgentRegistryDB.status.in_([AgentStatus.HEALTHY.value, AgentStatus.DEGRADED.value])
            )
            agents_db = await session.execute(stmt)
            agents = agents_db.scalars().all()

            result = []
            for agent_db in agents:
                agent_info = AgentInfo(
                    agent_id=agent_db.agent_id,
                    name=agent_db.name,
                    role=agent_db.role,
                    capabilities=agent_db.capabilities,
                    model=agent_db.model,
                    config=agent_db.config,
                    status=AgentStatus(agent_db.status),
                    current_task=agent_db.current_task,
                    token_usage=agent_db.token_usage,
                    last_heartbeat=agent_db.last_heartbeat,
                    registered_at=agent_db.registered_at,
                    updated_at=agent_db.updated_at,
                )
                result.append(agent_info)

            return result

    async def create_task_from_listener(self, agent_id: str, goal: str, context: dict[str, Any], 
                                        priority: str = "normal", triggered_by_message: Optional[str] = None) -> dict:
        """Create a task from AgentListener evaluation."""
        async with self.get_db_session() as session:
            # Check if agent exists
            agent_db = await session.get(AgentRegistryDB, agent_id)
            if not agent_db:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

            # Create task in task_queue
            task_db = TaskQueueDB(
                task_id=str(uuid.uuid4()),
                agent_id=agent_id,
                goal=goal,
                context=context,
                priority=priority,
                status=TaskStatus.PENDING.value,
                logs=[f"Created via AgentListener - message: {triggered_by_message}"],
                created_at=datetime.utcnow(),
                started_at=None,
                completed_at=None,
                updated_at=datetime.utcnow(),
            )
            session.add(task_db)
            await session.flush()

            # Update agent current task
            agent_db.current_task = task_db.task_id

            logger.info("Task created via AgentListener",
                       agent_id=agent_id,
                       task_id=task_db.task_id,
                       goal=goal,
                       triggered_by_message=triggered_by_message)

            return task_db.__dict__

    async def update_agent_last_seen(self, agent_id: str, status: AgentStatus, current_task: Optional[str] = None):
        """Update agent's last seen timestamp and status."""
        async with self.get_db_session() as session:
            agent_db = await session.get(AgentRegistryDB, agent_id)
            if not agent_db:
                logger.warning("Agent not found for last seen update", agent_id=agent_id)
                return

            agent_db.status = status.value
            if current_task is not None:
                agent_db.current_task = current_task
            agent_db.last_heartbeat = datetime.utcnow()
            agent_db.updated_at = datetime.utcnow()

            logger.info("Agent last seen updated", 
                       agent_id=agent_id, 
                       status=status.value, 
                       current_task=current_task)