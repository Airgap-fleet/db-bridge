"""Agent Listener - Background thread for processing agent messages and evaluating rules of engagement."""

from __future__ import annotations

import asyncio
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from .core import DashboardCore, WebSocketHub, WSMessage, EventType
from .models import (
    AgentInfo,
    AgentStatus,
    MessageInfo,
    TaskCreate,
    TaskPriority,
    KanbanTask,
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
class AgentListener:
    """Background thread system that processes incoming messages from agents and evaluates them against agent rules of engagement."""

    def __init__(self, dashboard_core: DashboardCore, poll_interval: int = 5):
        """Initialize AgentListener.

        Args:
            dashboard_core: DashboardCore instance for database and websocket operations
            poll_interval: Polling interval in seconds (default: 5)
        """
        self.dashboard_core = dashboard_core
        self.poll_interval = poll_interval
        self.running = True
        self.heartbeat_running = True
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        self.message_cursor: Dict[str, str] = {}  # agent_id -> last_message_id
        self.last_heartbeat = {}

        # Default rules of engagement
        self.rules_of_engagement = self._load_default_rules()

    def _load_default_rules(self) -> List[str]:
        """Load default rules of engagement from configuration."""
        return [
            # Protocol: Emergency Response
            "# Protocol: Emergency Response",
            "IF message contains \"emergency\" OR @system OR status changes to \"unhealthy\":",
            "  - Create task in critical with priority high",
            "  - Assign to self",
            "  - Escalate",
            "",
            # Protocol: Routine Operations
            "# Protocol: Routine Operations",
            "IF message contains \"status update\" OR @admin:",
            "  - Create task in status with priority normal",
            "  - Assign to self",
            "",
            # Protocol: Urgent Requests
            "# Protocol: Urgent Requests",
            "IF message contains \"urgent\" OR @urgent:",
            "  - Create task in urgent with priority critical",
            "  - Assign to self",
            "  - Reply \"Processing urgent request...\"",
        ]

    def start(self):
        """Start the AgentListener background threads."""
        logger.info("Starting AgentListener", poll_interval=self.poll_interval)

        # Start main polling thread
        self.thread_pool.submit(self._polling_loop)

        # Start heartbeat thread
        self.thread_pool.submit(self._heartbeat_loop)

    def stop(self):
        """Stop the AgentListener gracefully."""
        logger.info("Stopping AgentListener")
        self.running = False
        self.heartbeat_running = False

        # Wait for threads to finish
        self.thread_pool.shutdown(wait=True)
        logger.info("AgentListener stopped")

    def _polling_loop(self):
        """Main polling loop that checks for new messages."""
        while self.running:
            try:
                # Get all active agents
                active_agents = asyncio.run(self._get_active_agents())

                for agent in active_agents:
                    # Poll for new messages
                    asyncio.run(self._process_agent_messages(agent))

                # Sleep before next poll
                time.sleep(self.poll_interval)

            except Exception as e:
                logger.error("Error in polling loop", error=str(e))
                time.sleep(self.poll_interval)

    async def _get_active_agents(self) -> List[AgentInfo]:
        """Get all active agents from the database."""
        async with self.dashboard_core.get_db_session() as session:
            from .core import AgentRegistryDB

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

    async def _process_agent_messages(self, agent: AgentInfo):
        """Process messages for a specific agent."""
        try:
            # Get last message ID for this agent
            last_message_id = self.message_cursor.get(agent.agent_id)

            # Get all messages from agent's channels
            # In a real implementation, you'd query based on agent membership
            # For now, we'll use a simplified approach

            # Update agent's last_seen timestamp
            await self._update_agent_last_seen(agent.agent_id)

            # Get recent messages (simplified - in real implementation would query channels)
            recent_messages = await self._get_recent_messages(agent.agent_id)

            for message in recent_messages:
                # Check if we've already processed this message
                if last_message_id and message.message_id <= last_message_id:
                    continue

                # Process the message
                await self._evaluate_message(agent, message)

                # Update cursor
                self.message_cursor[agent.agent_id] = message.message_id

        except Exception as e:
            logger.error("Error processing agent messages", agent_id=agent.agent_id, error=str(e))

    async def _get_recent_messages(self, agent_id: str) -> List[MessageInfo]:
        """Get recent messages for an agent."""
        async with self.dashboard_core.get_db_session() as session:
            from .core import MessageDB

            # Get all messages from all channels
            stmt = session.query(MessageDB).order_by(MessageDB.created_at.desc()).limit(50)
            messages_db = await session.execute(stmt)
            messages = messages_db.scalars().all()

            result = []
            for message_db in messages:
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
                result.append(message_info)

            return result

    async def _evaluate_message(self, agent: AgentInfo, message: MessageInfo):
        """Evaluate a message against rules of engagement."""
        try:
            # Parse rules and evaluate conditions
            protocols = self._parse_rules(self.rules_of_engagement)

            for protocol in protocols:
                # Check if message matches protocol conditions
                if self._matches_conditions(message, protocol['conditions']):
                    # Execute actions
                    await self._execute_actions(agent, message, protocol['actions'])
                    break  # Stop after first matching protocol

        except Exception as e:
            logger.error("Error evaluating message", error=str(e))

    def _parse_rules(self, rules_text: str) -> List[Dict[str, Any]]:
        """Parse rules text into structured protocol objects."""
        protocols = []
        current_protocol = None

        for line in rules_text.split('\n'):
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            # Check for protocol header
            if line.startswith('# Protocol:'):
                if current_protocol:
                    protocols.append(current_protocol)

                protocol_name = line.replace('# Protocol:', '').strip()
                current_protocol = {
                    'name': protocol_name,
                    'conditions': [],
                    'actions': []
                }
            elif line.startswith('IF'):
                # Parse conditions
                conditions_text = line[2:].strip()
                conditions = self._parse_conditions(conditions_text)
                if current_protocol:
                    current_protocol['conditions'] = conditions
            elif line.startswith('- '):
                # Parse actions
                action_text = line[2:].strip()
                actions = self._parse_actions(action_text)
                if current_protocol:
                    current_protocol['actions'].extend(actions)

        # Add last protocol
        if current_protocol:
            protocols.append(current_protocol)

        return protocols

    def _parse_conditions(self, conditions_text: str) -> List[Dict[str, Any]]:
        """Parse conditions text into structured condition objects."""
        conditions = []

        # Split by OR, handling parentheses
        or_parts = re.split(r'\s+OR\s+', conditions_text)

        for part in or_parts:
            part = part.strip()

            if part.startswith('message contains "'):
                # Message content condition
                keyword = part[17:-1]  # Extract between quotes
                conditions.append({
                    'type': 'message_content',
                    'keyword': keyword.lower()
                })
            elif part.startswith('@'):
                # Mention condition
                mention = part[1:]  # Remove @
                conditions.append({
                    'type': 'mention',
                    'mention': mention
                })
            elif part.startswith('status changes to "'):
                # Status change condition
                status = part[20:-1]  # Extract between quotes
                conditions.append({
                    'type': 'status_change',
                    'status': status
                })
            elif part == 'status changes':
                # Generic status change condition
                conditions.append({
                    'type': 'status_change',
                    'status': None  # Match any status change
                })

        return conditions

    def _parse_actions(self, action_text: str) -> List[Dict[str, Any]]:
        """Parse action text into structured action objects."""
        actions = []

        if action_text.startswith('Create task in '):
            # Create task action
            task_type = action_text[15:].split(' with priority ')[0].strip()
            priority_part = action_text.split(' with priority ')[1].strip() if ' with priority ' in action_text else 'normal'

            priority_map = {
                'low': TaskPriority.LOW,
                'normal': TaskPriority.NORMAL,
                'high': TaskPriority.HIGH,
                'critical': TaskPriority.CRITICAL
            }

            actions.append({
                'type': 'create_task',
                'task_type': task_type,
                'priority': priority_map.get(priority_part.lower(), TaskPriority.NORMAL)
            })

        elif action_text.startswith('Assign to self'):
            # Assign to self action
            actions.append({
                'type': 'assign_to_self'
            })

        elif action_text.startswith('Reply "'):
            # Reply action
            reply_text = action_text[7:-1]  # Remove quotes
            actions.append({
                'type': 'reply',
                'text': reply_text
            })

        elif action_text.startswith('Escalate'):
            # Escalate action
            actions.append({
                'type': 'escalate'
            })

        return actions

    def _matches_conditions(self, message: MessageInfo, conditions: List[Dict[str, Any]]) -> bool:
        """Check if a message matches the given conditions."""
        if not conditions:
            return False

        # All conditions in a protocol must match (AND logic)
        for condition in conditions:
            if not self._matches_condition(message, condition):
                return False

        return True

    def _matches_condition(self, message: MessageInfo, condition: Dict[str, Any]) -> bool:
        """Check if a message matches a single condition."""
        condition_type = condition['type']

        if condition_type == 'message_content':
            # Check if message contains keyword
            keyword = condition['keyword']
            return keyword in message.content.lower()

        elif condition_type == 'mention':
            # Check if agent is mentioned
            mention = condition['mention']
            return mention in message.mentions

        elif condition_type == 'status_change':
            # For now, return False for status change conditions
            # In a real implementation, you'd check the agent's status
            return False

        return False

    async def _execute_actions(self, agent: AgentInfo, message: MessageInfo, actions: List[Dict[str, Any]]):
        """Execute a sequence of actions based on evaluated conditions."""
        try:
            for action in actions:
                await self._execute_action(agent, message, action)

        except Exception as e:
            logger.error("Error executing actions", error=str(e))

    async def _execute_action(self, agent: AgentInfo, message: MessageInfo, action: Dict[str, Any]):
        """Execute a single action."""
        action_type = action['type']

        if action_type == 'create_task':
            await self._create_task_action(agent, message, action)

        elif action_type == 'assign_to_self':
            await self._assign_to_self_action(agent, message)

        elif action_type == 'reply':
            await self._reply_action(agent, message, action)

        elif action_type == 'escalate':
            await self._escalate_action(agent, message)

    async def _create_task_action(self, agent: AgentInfo, message: MessageInfo, action: Dict[str, Any]):
        """Create a task based on the action parameters."""
        try:
            # In a real implementation, you'd use the DashboardCore methods
            # For now, we'll create a task in the database
            task_create = TaskCreate(
                title=f"{action['task_type']} triggered by message",
                body=f"From agent {agent.agent_id}: {message.content}",
                priority=action['priority'].value,
                assignee_role=agent.role,
                tags=["auto-generated", action['task_type']]
            )

            # Use the DashboardCore to create the task
            # This would require adding a method to DashboardCore
            logger.info("Task created via AgentListener",
                       agent_id=agent.agent_id,
                       message_id=message.message_id,
                       task_type=action['task_type'],
                       priority=action['priority'].value)

        except Exception as e:
            logger.error("Error creating task", error=str(e))

    async def _assign_to_self_action(self, agent: AgentInfo, message: MessageInfo):
        """Assign task to self (agent)."""
        try:
            # In a real implementation, you'd update the agent's current task
            logger.info("Task assigned to self via AgentListener",
                       agent_id=agent.agent_id,
                       message_id=message.message_id)

        except Exception as e:
            logger.error("Error assigning task to self", error=str(e))

    async def _reply_action(self, agent: AgentInfo, message: MessageInfo, action: Dict[str, Any]):
        """Reply to a message."""
        try:
            # In a real implementation, you'd post a reply message
            reply_text = action['text']
            logger.info("Reply sent via AgentListener",
                       agent_id=agent.agent_id,
                       message_id=message.message_id,
                       reply_text=reply_text)

        except Exception as e:
            logger.error("Error sending reply", error=str(e))

    async def _escalate_action(self, agent: AgentInfo, message: MessageInfo):
        """Escalate a task or issue."""
        try:
            # In a real implementation, you'd escalate the task
            logger.info("Task escalated via AgentListener",
                       agent_id=agent.agent_id,
                       message_id=message.message_id)

        except Exception as e:
            logger.error("Error escalating task", error=str(e))

    async def _update_agent_last_seen(self, agent_id: str):
        """Update agent's last seen timestamp."""
        try:
            await self.dashboard_core.update_agent_status(
                agent_id,
                AgentStatus.HEALTHY,
                None  # Don't update current task
            )

        except Exception as e:
            logger.error("Error updating agent last seen", error=str(e))

    def _heartbeat_loop(self):
        """Heartbeat loop that updates agent statuses based on activity thresholds."""
        while self.heartbeat_running:
            try:
                # Get all agents
                agents = asyncio.run(self._get_active_agents())

                for agent in agents:
                    # Calculate time since last heartbeat
                    if agent.last_heartbeat:
                        time_since_heartbeat = datetime.utcnow() - agent.last_heartbeat
                    else:
                        time_since_heartbeat = timedelta(hours=24)  # Very old

                    # Determine status based on thresholds
                    new_status = self._determine_agent_status(time_since_heartbeat)

                    # Update agent status if changed
                    if agent.status != new_status:
                        asyncio.run(self._update_agent_status(agent.agent_id, new_status))

                # Sleep before next heartbeat
                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error("Error in heartbeat loop", error=str(e))
                time.sleep(60)

    def _determine_agent_status(self, time_since: timedelta) -> AgentStatus:
        """Determine agent status based on time since last heartbeat."""
        minutes_since = int(time_since.total_seconds() / 60)

        if minutes_since <= 5:
            return AgentStatus.HEALTHY
        elif minutes_since <= 120:
            return AgentStatus.DEGRADED
        else:
            return AgentStatus.UNHEALTHY