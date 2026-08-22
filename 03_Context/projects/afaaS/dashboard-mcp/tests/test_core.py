"""Tests for Dashboard MCP Server core logic."""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard_mcp.core import DashboardCore, WebSocketHub
from dashboard_mcp.models import (
    AgentRegistration,
    AgentInfo,
    AgentStatus,
    TaskCreate,
    TaskInfo,
    TaskStatus,
    TaskPriority,
    MessageCreate,
    MessageInfo,
    ChannelCreate,
    ChannelInfo,
    WSMessage,
    EventType,
    FleetStatusResponse,
)
@pytest.fixture
def mock_database_url():
    """Mock database URL."""
    return "postgresql://postgres:postgres@localhost:5432/dashboard_mcp"
@pytest.fixture
def mock_redis_url():
    """Mock Redis URL."""
    return "redis://localhost:6379"
@pytest.fixture
def core_instance(mock_database_url, mock_redis_url):
    """Create a DashboardCore instance with mocked dependencies."""
    core = DashboardCore(mock_database_url, mock_redis_url)
    
    # Mock the engine and websocket hub
    core.engine = MagicMock()
    core.websocket_hub = MagicMock()
    core._redis_pubsub = None
    
    return core
@pytest_asyncio.fixture
async def core_with_session(core_instance):
    """Create a core instance with database sessions mocked."""
    # Mock the get_db_session context manager
    mock_session = AsyncMock()
    core_instance.get_db_session = AsyncMock(return_value=mock_session)
    
    # Mock the query results
    mock_query_result = AsyncMock()
    mock_query_result.scalar_one_or_none = AsyncMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_query_result)
    
    # Mock session.get
    mock_session.get = AsyncMock(return_value=None)
    
    return core_instance
class TestDashboardCore:
    """Test cases for DashboardCore class."""
    
    @pytest.mark.asyncio
    async def test_register_agent_success(self, core_with_session):
        """Test successful agent registration."""
        # Setup mock data
        agent_id = "agent-123"
        name = "Test Agent"
        role = "developer"
        capabilities = ["coding", "testing"]
        model = "gpt-4"
        config = {"temperature": 0.5}
        
        agent_data = AgentRegistration(
            agent_id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities,
            model=model,
            config=config,
        )
        
        # Mock existing agent check
        core_with_session.get_db_session.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = None
        
        # Mock session.add and flush
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        
        # Mock WebSocket broadcast
        core_with_session.websocket_hub.broadcast = AsyncMock()
        
        # Call the method
        result = await core_with_session.register_agent(agent_data)
        
        # Assertions
        assert result.agent_id == agent_id
        assert result.name == name
        assert result.role == role
        assert result.capabilities == capabilities
        assert result.model == model
        assert result.status == AgentStatus.OFFLINE
        
        # Verify method calls
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        core_with_session.websocket_hub.broadcast.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_agent_duplicate(self, core_with_session):
        """Test agent registration with duplicate agent ID."""
        # Setup mock data
        agent_id = "agent-123"
        name = "Test Agent"
        role = "developer"
        capabilities = ["coding", "testing"]
        model = "gpt-4"
        
        agent_data = AgentRegistration(
            agent_id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities,
            model=model,
        )
        
        # Mock existing agent (duplicate)
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_query_result = AsyncMock()
        mock_query_result.scalar_one_or_none = AsyncMock(return_value=MagicMock())  # Existing agent
        mock_session.execute = AsyncMock(return_value=mock_query_result)
        
        # Call the method - should raise HTTPException
        with pytest.raises(Exception) as exc_info:
            await core_with_session.register_agent(agent_data)
        
        # Verify the exception
        assert "already registered" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_fleet_status(self, core_with_session):
        """Test getting fleet status."""
        # Setup mock agents
        agent1 = MagicMock()
        agent1.agent_id = "agent-1"
        agent1.name = "Agent One"
        agent1.role = "developer"
        agent1.capabilities = ["coding"]
        agent1.model = "gpt-4"
        agent1.config = None
        agent1.status = AgentStatus.HEALTHY.value
        agent1.current_task = None
        agent1.token_usage = 100
        agent1.last_heartbeat = datetime.utcnow() - timedelta(minutes=5)
        agent1.registered_at = datetime.utcnow() - timedelta(days=10)
        agent1.updated_at = datetime.utcnow()
        
        agent2 = MagicMock()
        agent2.agent_id = "agent-2"
        agent2.name = "Agent Two"
        agent2.role = "tester"
        agent2.capabilities = ["testing"]
        agent2.model = "gpt-3.5"
        agent2.config = None
        agent2.status = AgentStatus.DEGRADED.value
        agent2.current_task = "task-123"
        agent2.token_usage = 200
        agent2.last_heartbeat = datetime.utcnow() - timedelta(minutes=30)
        agent2.registered_at = datetime.utcnow() - timedelta(days=5)
        agent2.updated_at = datetime.utcnow()
        
        # Mock query results
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_query_result = AsyncMock()
        mock_query_result.scalars.return_value.all.return_value = [agent1, agent2]
        mock_session.execute = AsyncMock(return_value=mock_query_result)
        
        # Call the method
        result = await core_with_session.get_fleet_status()
        
        # Assertions
        assert result.total_agents == 2
        assert result.healthy_agents == 1
        assert result.running_tasks == 1
        assert result.total_token_usage == 300
        assert len(result.agents) == 2
        
        # Check agent data
        assert result.agents[0].agent_id == "agent-1"
        assert result.agents[1].agent_id == "agent-2"
    
    @pytest.mark.asyncio
    async def test_create_task_success(self, core_with_session):
        """Test successful task creation."""
        # Setup mock data
        agent_id = "agent-123"
        goal = "Create a new dashboard"
        context = {"priority": "high"}
        priority = TaskPriority.HIGH
        
        task_data = TaskCreate(
            agent_id=agent_id,
            goal=goal,
            context=context,
            priority=priority,
        )
        
        # Mock agent existence check
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_query_result = AsyncMock()
        mock_query_result.scalar_one_or_none = AsyncMock(return_value=MagicMock())  # Agent exists
        mock_session.execute = AsyncMock(return_value=mock_query_result)
        
        # Mock agent and task creation
        mock_agent = MagicMock()
        mock_session.get = AsyncMock(return_value=mock_agent)
        mock_agent.current_task = None
        mock_agent.status = AgentStatus.OFFLINE.value
        
        mock_task = MagicMock()
        mock_task.task_id = "task-456"
        mock_task.agent_id = agent_id
        mock_task.goal = goal
        mock_task.context = context
        mock_task.priority = priority.value
        mock_task.status = TaskStatus.PENDING.value
        mock_task.logs = []
        mock_task.created_at = datetime.utcnow()
        mock_task.started_at = None
        mock_task.completed_at = None
        mock_task.updated_at = datetime.utcnow()
        
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        
        # Call the method
        result = await core_with_session.create_task(task_data)
        
        # Assertions
        assert result.task_id == "task-456"
        assert result.agent_id == agent_id
        assert result.goal == goal
        assert result.context == context
        assert result.priority == priority
        assert result.status == TaskStatus.PENDING
        
        # Verify method calls
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_agent.current_task = "task-456"
        assert mock_agent.current_task == "task-456"
    
    @pytest.mark.asyncio
    async def test_create_task_agent_not_found(self, core_with_session):
        """Test task creation when agent doesn't exist."""
        # Setup mock data
        agent_id = "nonexistent-agent"
        goal = "Create a new dashboard"
        
        task_data = TaskCreate(
            agent_id=agent_id,
            goal=goal,
        )
        
        # Mock agent not found
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_query_result = AsyncMock()
        mock_query_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_query_result)
        
        # Call the method - should raise HTTPException
        with pytest.raises(Exception) as exc_info:
            await core_with_session.create_task(task_data)
        
        # Verify the exception
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, core_with_session):
        """Test successful message sending."""
        # Setup mock data
        channel_id = "channel-123"
        from_agent = "agent-1"
        content = "Hello, world!"
        mentions = ["agent-2"]
        reply_to = "msg-456"
        
        message_data = MessageCreate(
            channel_id=channel_id,
            from_agent=from_agent,
            content=content,
            mentions=mentions,
            reply_to=reply_to,
        )
        
        # Mock channel existence check
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_query_result = AsyncMock()
        mock_query_result.scalar_one_or_none = AsyncMock(return_value=MagicMock())  # Channel exists
        mock_session.execute = AsyncMock(return_value=mock_query_result)
        
        # Mock channel and message creation
        mock_channel = MagicMock()
        mock_channel.message_count = 0
        mock_session.get = AsyncMock(return_value=mock_channel)
        
        mock_message = MagicMock()
        mock_message.message_id = "msg-789"
        mock_message.channel_id = channel_id
        mock_message.from_agent = from_agent
        mock_message.content = content
        mock_message.mentions = mentions
        mock_message.reply_to = reply_to
        mock_message.created_at = datetime.utcnow()
        mock_message.updated_at = datetime.utcnow()
        
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        
        # Mock WebSocket broadcast
        core_with_session.websocket_hub.broadcast = AsyncMock()
        
        # Call the method
        result = await core_with_session.send_message(message_data)
        
        # Assertions
        assert result.message_id == "msg-789"
        assert result.channel_id == channel_id
        assert result.from_agent == from_agent
        assert result.content == content
        assert result.mentions == mentions
        assert result.reply_to == reply_to
        
        # Verify method calls
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        core_with_session.websocket_hub.broadcast.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_channel_success(self, core_with_session):
        """Test successful channel creation."""
        # Setup mock data
        name = "general"
        description = "General discussion channel"
        members = ["agent-1", "agent-2"]
        
        channel_data = ChannelCreate(
            name=name,
            description=description,
            members=members,
        )
        
        # Mock existing channel check
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_query_result = AsyncMock()
        mock_query_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_query_result)
        
        # Mock channel creation
        mock_channel = MagicMock()
        mock_channel.channel_id = "channel-456"
        mock_channel.name = name
        mock_channel.description = description
        mock_channel.members = members
        mock_channel.created_at = datetime.utcnow()
        mock_channel.updated_at = datetime.utcnow()
        mock_channel.message_count = 0
        
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        
        # Mock WebSocket broadcast
        core_with_session.websocket_hub.broadcast = AsyncMock()
        
        # Call the method
        result = await core_with_session.create_channel(channel_data)
        
        # Assertions
        assert result.channel_id == "channel-456"
        assert result.name == name
        assert result.description == description
        assert result.members == members
        
        # Verify method calls
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        core_with_session.websocket_hub.broadcast.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_channel_duplicate(self, core_with_session):
        """Test channel creation with duplicate name."""
        # Setup mock data
        name = "general"
        description = "General discussion channel"
        
        channel_data = ChannelCreate(
            name=name,
            description=description,
        )
        
        # Mock existing channel (duplicate)
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_query_result = AsyncMock()
        mock_query_result.scalar_one_or_none = AsyncMock(return_value=MagicMock())  # Existing channel
        mock_session.execute = AsyncMock(return_value=mock_query_result)
        
        # Call the method - should raise HTTPException
        with pytest.raises(Exception) as exc_info:
            await core_with_session.create_channel(channel_data)
        
        # Verify the exception
        assert "already exists" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_channel_history_success(self, core_with_session):
        """Test successful channel history retrieval."""
        # Setup mock data
        channel_id = "channel-123"
        limit = 50
        offset = 0
        
        # Mock channel existence check
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_query_result = AsyncMock()
        mock_query_result.scalar_one_or_none = AsyncMock(return_value=MagicMock())  # Channel exists
        mock_session.execute = AsyncMock(return_value=mock_query_result)
        
        # Mock messages
        mock_message1 = MagicMock()
        mock_message1.message_id = "msg-1"
        mock_message1.channel_id = channel_id
        mock_message1.from_agent = "agent-1"
        mock_message1.content = "Message 1"
        mock_message1.mentions = []
        mock_message1.reply_to = None
        mock_message1.created_at = datetime.utcnow() - timedelta(minutes=5)
        mock_message1.updated_at = datetime.utcnow()
        
        mock_message2 = MagicMock()
        mock_message2.message_id = "msg-2"
        mock_message2.channel_id = channel_id
        mock_message2.from_agent = "agent-2"
        mock_message2.content = "Message 2"
        mock_message2.mentions = []
        mock_message2.reply_to = None
        mock_message2.created_at = datetime.utcnow() - timedelta(minutes=10)
        mock_message2.updated_at = datetime.utcnow()
        
        mock_query_result2 = AsyncMock()
        mock_query_result2.scalars.return_value.all.return_value = [mock_message2, mock_message1]
        mock_session.execute = AsyncMock(side_effect=[mock_query_result, mock_query_result2])
        
        # Mock count query
        mock_count_result = AsyncMock()
        mock_count_result.scalar.return_value = 2
        mock_session.execute = AsyncMock(side_effect=[mock_query_result, mock_query_result2, mock_count_result])
        
        # Call the method
        result = await core_with_session.get_channel_history(channel_id, limit, offset)
        
        # Assertions
        assert result.total == 2
        assert result.has_more == False
        assert len(result.messages) == 2
        
        # Check message order (should be chronological)
        assert result.messages[0].message_id == "msg-1"  # Created later
        assert result.messages[1].message_id == "msg-2"  # Created earlier
    
    @pytest.mark.asyncio
    async def test_get_channel_history_channel_not_found(self, core_with_session):
        """Test channel history when channel doesn't exist."""
        # Setup mock data
        channel_id = "nonexistent-channel"
        
        # Mock channel not found
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_query_result = AsyncMock()
        mock_query_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_query_result)
        
        # Call the method - should raise HTTPException
        with pytest.raises(Exception) as exc_info:
            await core_with_session.get_channel_history(channel_id)
        
        # Verify the exception
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_agent_status(self, core_with_session):
        """Test updating agent status."""
        # Setup mock data
        agent_id = "agent-123"
        status = AgentStatus.HEALTHY
        current_task = "task-456"
        
        mock_agent = MagicMock()
        mock_agent.status = AgentStatus.OFFLINE.value
        mock_agent.current_task = None
        mock_agent.updated_at = datetime.utcnow()
        
        # Mock session.get
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_session.get = AsyncMock(return_value=mock_agent)
        mock_session.commit = AsyncMock()
        
        # Call the method
        await core_with_session.update_agent_status(agent_id, status, current_task)
        
        # Assertions
        assert mock_agent.status == status.value
        assert mock_agent.current_task == current_task
        assert mock_session.get.called_once_with(agent_id)
    
    @pytest.mark.asyncio
    async def test_update_agent_status_agent_not_found(self, core_with_session):
        """Test updating agent status when agent doesn't exist."""
        # Setup mock data
        agent_id = "nonexistent-agent"
        status = AgentStatus.HEALTHY
        
        # Mock agent not found
        mock_session = core_with_session.get_db_session.return_value.__aenter__.return_value
        mock_session.get = AsyncMock(return_value=None)
        
        # Call the method - should log warning and return
        with patch('dashboard_mcp.core.logger') as mock_logger:
            await core_with_session.update_agent_status(agent_id, status)
            
            # Verify warning was logged
            mock_logger.warning.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_websocket_hub_subscribe(self):
        """Test WebSocketHub subscription."""
        # Setup mock data
        redis_url = "redis://localhost:6379"
        hub = WebSocketHub(redis_url)
        
        # Mock websocket
        mock_websocket = MagicMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.client_host = "127.0.0.1"
        
        # Mock redis
        hub.redis = MagicMock()
        
        # Call the method
        await hub.subscribe(mock_websocket, "general")
        
        # Assertions
        mock_websocket.accept.assert_called_once()
        assert "general" in hub._subscriptions
        assert mock_websocket in hub._subscriptions["general"]
        assert "general" in hub._channels
    
    @pytest.mark.asyncio
    async def test_websocket_hub_broadcast(self):
        """Test WebSocketHub broadcast."""
        # Setup mock data
        redis_url = "redis://localhost:6379"
        hub = WebSocketHub(redis_url)
        
        # Setup channel with websockets
        mock_websocket1 = MagicMock()
        mock_websocket1.client_host = "127.0.0.1"
        mock_websocket1.send_json = AsyncMock()
        
        mock_websocket2 = MagicMock()
        mock_websocket2.client_host = "192.168.1.1"
        mock_websocket2.send_json = AsyncMock()
        
        hub._subscriptions = {
            "general": {mock_websocket1, mock_websocket2}
        }
        hub._channels = {"general"}
        
        # Create message
        message = WSMessage(
            type=EventType.AGENT_STATUS,
            payload={"agent_id": "agent-1", "status": "healthy"},
            correlation_id="test-123",
        )
        
        # Call the method
        await hub.broadcast(message, "general")
        
        # Assertions
        mock_websocket1.send_json.assert_called_once()
        mock_websocket2.send_json.assert_called_once()
        
        # Verify message data
        call_args = mock_websocket1.send_json.call_args[0][0]
        assert call_args["type"] == EventType.AGENT_STATUS.value
        assert call_args["payload"]["agent_id"] == "agent-1"
        assert call_args["correlation_id"] == "test-123"
    
    @pytest.mark.asyncio
    async def test_websocket_hub_broadcast_no_subscribers(self):
        """Test WebSocketHub broadcast with no subscribers."""
        # Setup mock data
        redis_url = "redis://localhost:6379"
        hub = WebSocketHub(redis_url)
        
        # Empty subscriptions
        hub._subscriptions = {}
        hub._channels = set()
        
        # Create message
        message = WSMessage(
            type=EventType.AGENT_STATUS,
            payload={"agent_id": "agent-1"},
        )
        
        # Should not raise exception
        await hub.broadcast(message, "general")
    
    @pytest.mark.asyncio
    async def test_initialize(self, core_instance):
        """Test DashboardCore initialization."""
        # Mock dependencies
        core_instance.engine = MagicMock()
        core_instance.websocket_hub = MagicMock()
        core_instance._redis_pubsub = MagicMock()
        core_instance._redis_pubsub.subscribe = AsyncMock()
        
        # Mock asyncio.create_task
        with patch('asyncio.create_task') as mock_create_task:
            # Call the method
            await core_instance.initialize()
            
            # Assertions
            assert core_instance.engine is not None
            assert core_instance.websocket_hub is not None
            core_instance._redis_pubsub.subscribe.assert_called_once_with("dashboard_events")
            mock_create_task.assert_called_once()
class TestDashboardServer:
    """Test cases for DashboardServer FastAPI application."""
    
    @pytest.fixture
    def mock_core():
        """Create a mock core instance."""
        core = MagicMock()
        core.websocket_hub = MagicMock()
        core.websocket_hub.subscribe = AsyncMock()
        core.websocket_hub.unsubscribe = AsyncMock()
        core.websocket_hub.broadcast = AsyncMock()
        return core
    
    @pytest.fixture
    def server_app(mock_core):
        """Create the server app with mocked core."""
        # Mock the get_core function to return our mock core
        with patch('dashboard_mcp.server.get_core') as mock_get_core:
            mock_get_core.return_value = mock_core
            from dashboard_mcp.server import app
            
            yield app
    
    def test_root_endpoint(self, server_app):
        """Test the root endpoint."""
        response = server_app.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Dashboard MCP Server"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
    
    def test_health_endpoint_healthy(self, server_app):
        """Test health endpoint when server is healthy."""
        # Mock core
        server_app.dependency_overrides['get_core']().engine = MagicMock()
        server_app.dependency_overrides['get_core']().websocket_hub = MagicMock()
        
        response = server_app.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_mcp_tools_call_register_agent(self, server_app):
        """Test MCP tool register_agent call."""
        # Mock the core response
        mock_agent = MagicMock()
        mock_agent.dict.return_value = {"agent_id": "test-123", "name": "Test Agent"}
        server_app.dependency_overrides['get_core']().register_agent.return_value = mock_agent
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.register_agent)
    
    def test_mcp_tools_call_get_fleet_status(self, server_app):
        """Test MCP tool get_fleet_status call."""
        # Mock the core response
        mock_status = MagicMock()
        mock_status.dict.return_value = {"total_agents": 5, "healthy_agents": 3}
        server_app.dependency_overrides['get_core']().get_fleet_status.return_value = mock_status
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.get_fleet_status)
    
    def test_mcp_tools_call_create_task(self, server_app):
        """Test MCP tool create_task call."""
        # Mock the core response
        mock_task = MagicMock()
        mock_task.dict.return_value = {"task_id": "task-456", "status": "pending"}
        server_app.dependency_overrides['get_core']().create_task.return_value = mock_task
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.create_task)
    
    def test_mcp_tools_call_send_message(self, server_app):
        """Test MCP tool send_message call."""
        # Mock the core response
        mock_message = MagicMock()
        mock_message.dict.return_value = {"message_id": "msg-789", "content": "Hello"}
        server_app.dependency_overrides['get_core']().send_message.return_value = mock_message
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.send_message)
    
    def test_mcp_tools_call_create_channel(self, server_app):
        """Test MCP tool create_channel call."""
        # Mock the core response
        mock_channel = MagicMock()
        mock_channel.dict.return_value = {"channel_id": "channel-123", "name": "general"}
        server_app.dependency_overrides['get_core']().create_channel.return_value = mock_channel
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.create_channel)
    
    def test_mcp_tools_call_get_channel_history(self, server_app):
        """Test MCP tool get_channel_history call."""
        # Mock the core response
        mock_history = MagicMock()
        mock_history.dict.return_value = {"messages": [], "total": 0}
        server_app.dependency_overrides['get_core']().get_channel_history.return_value = mock_history
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.get_channel_history)
    
    def test_mcp_tools_call_get_agent(self, server_app):
        """Test MCP tool get_agent call."""
        # Mock the core response
        mock_agent = MagicMock()
        mock_agent.dict.return_value = {"agent_id": "agent-123"}
        server_app.dependency_overrides['get_core']().get_agent_by_id.return_value = mock_agent
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.get_agent)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])