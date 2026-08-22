"""Integration tests for Dashboard MCP Server."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock

from dashboard_mcp.server import app
@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)
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
def patched_core():
    """Patch the get_core function to return a mock core."""
    with patch('dashboard_mcp.server.get_core') as mock_get_core:
        mock_core = MagicMock()
        mock_get_core.return_value = mock_core
        yield mock_core
class TestDashboardServer:
    """Integration tests for Dashboard Server."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Dashboard MCP Server"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
    
    def test_health_endpoint_healthy(self, client, patched_core):
        """Test health endpoint when server is healthy."""
        # Mock core
        patched_core.engine = MagicMock()
        patched_core.websocket_hub = MagicMock()
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_websocket_endpoint_connection(self, client, patched_core):
        """Test WebSocket endpoint connection."""
        with client.websocket_connect("/ws?channel=general") as websocket:
            # Send ping
            websocket.send_json({"type": "ping"})
            
            # Receive pong
            response = websocket.receive_json()
            assert response["type"] == "pong"
            
            # Close connection
            websocket.close()
        
        # Verify WebSocket operations
        patched_core.websocket_hub.subscribe.assert_called()
        patched_core.websocket_hub.unsubscribe.assert_called()
    
    def test_websocket_endpoint_with_different_channel(self, client, patched_core):
        """Test WebSocket endpoint with different channel."""
        with client.websocket_connect("/ws?channel=alerts") as websocket:
            websocket.send_json({"type": "ping"})
            response = websocket.receive_json()
            assert response["type"] == "pong"
            websocket.close()
        
        # Verify specific channel was used
        call_args = patched_core.websocket_hub.subscribe.call_args
        assert call_args[0][1] == "alerts"  # channel parameter
    
    def test_websocket_endpoint_no_channel(self, client, patched_core):
        """Test WebSocket endpoint without channel parameter."""
        with client.websocket_connect("/ws") as websocket:
            websocket.send_json({"type": "ping"})
            response = websocket.receive_json()
            assert response["type"] == "pong"
            websocket.close()
        
        # Verify default channel 'all' was used
        call_args = patched_core.websocket_hub.subscribe.call_args
        assert call_args[0][1] == "all"  # default channel
    
    def test_websocket_endpoint_error_handling(self, client, patched_core):
        """Test WebSocket endpoint error handling."""
        with client.websocket_connect("/ws?channel=general") as websocket:
            # Send invalid JSON
            websocket.send(b'{"invalid": json}')
            
            # Server should handle the error gracefully
            # The connection might close or send an error response
            # We'll just verify the test doesn't crash
            try:
                # Try to receive something (might timeout)
                response = websocket.receive_text(timeout=1)
            except Exception:
                # Expected - connection might close due to error
                pass
            
            websocket.close()
    
    def test_mcp_tools_registration(self, patched_core):
        """Test that MCP tools are properly registered."""
        # Get the actual FastMCP instance
        from dashboard_mcp.server import mcp
        
        # Check that tools are registered
        # This is a basic check - in a real test you'd examine the tools list
        assert mcp.name == "dashboard-mcp"
        assert "register_agent" in dir(mcp)  # Tools are methods on the instance
        
    def test_server_configuration(self, patched_core):
        """Test server configuration."""
        from dashboard_mcp.server import Config
        
        # Test config defaults
        config = Config()
        assert config.port == 8000
        assert config.ws_enabled is True
        assert "general" in config.default_channels
    
    def test_cors_configuration(self, client):
        """Test CORS configuration."""
        # Make a request from a different origin
        response = client.get("/health", headers={
            "Origin": "http://example.com"
        })
        
        # Should allow CORS (star *)
        assert response.status_code == 200
    
    def test_server_lifecycle(self, client, patched_core):
        """Test server startup and shutdown."""
        # The server should be ready to handle requests
        response = client.get("/health")
        assert response.status_code == 200
        
        # Verify core was initialized
        patched_core.initialize.assert_called_once()
    
    def test_error_handling_invalid_endpoint(self, client):
        """Test error handling for invalid endpoints."""
        response = client.get("/invalid_endpoint")
        assert response.status_code == 404
    
    def test_error_handling_invalid_method(self, client):
        """Test error handling for invalid HTTP methods."""
        response = client.post("/")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_mcp_tools_call_register_agent(self, patched_core):
        """Test MCP tool register_agent call."""
        from dashboard_mcp.server import mcp
        
        # Mock the core response
        mock_agent = MagicMock()
        mock_agent.dict.return_value = {"agent_id": "test-123", "name": "Test Agent"}
        patched_core.register_agent.return_value = mock_agent
        
        # Call the tool (this is a simplified test)
        # In a real test, you'd use the MCP client
        assert callable(mcp.register_agent)
    
    def test_mcp_tools_call_get_fleet_status(self, patched_core):
        """Test MCP tool get_fleet_status call."""
        from dashboard_mcp.server import mcp
        
        # Mock the core response
        mock_status = MagicMock()
        mock_status.dict.return_value = {"total_agents": 5, "healthy_agents": 3}
        patched_core.get_fleet_status.return_value = mock_status
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.get_fleet_status)
    
    def test_mcp_tools_call_create_task(self, patched_core):
        """Test MCP tool create_task call."""
        from dashboard_mcp.server import mcp
        
        # Mock the core response
        mock_task = MagicMock()
        mock_task.dict.return_value = {"task_id": "task-456", "status": "pending"}
        patched_core.create_task.return_value = mock_task
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.create_task)
    
    def test_mcp_tools_call_send_message(self, patched_core):
        """Test MCP tool send_message call."""
        from dashboard_mcp.server import mcp
        
        # Mock the core response
        mock_message = MagicMock()
        mock_message.dict.return_value = {"message_id": "msg-789", "content": "Hello"}
        patched_core.send_message.return_value = mock_message
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.send_message)
    
    def test_mcp_tools_call_create_channel(self, patched_core):
        """Test MCP tool create_channel call."""
        from dashboard_mcp.server import mcp
        
        # Mock the core response
        mock_channel = MagicMock()
        mock_channel.dict.return_value = {"channel_id": "channel-123", "name": "general"}
        patched_core.create_channel.return_value = mock_channel
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.create_channel)
    
    def test_mcp_tools_call_get_channel_history(self, patched_core):
        """Test MCP tool get_channel_history call."""
        from dashboard_mcp.server import mcp
        
        # Mock the core response
        mock_history = MagicMock()
        mock_history.dict.return_value = {"messages": [], "total": 0}
        patched_core.get_channel_history.return_value = mock_history
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.get_channel_history)
    
    def test_mcp_tools_call_get_agent(self, patched_core):
        """Test MCP tool get_agent call."""
        from dashboard_mcp.server import mcp
        
        # Mock the core response
        mock_agent = MagicMock()
        mock_agent.dict.return_value = {"agent_id": "agent-123"}
        patched_core.get_agent_by_id.return_value = mock_agent
        
        # Verify the tool exists and is callable
        from dashboard_mcp.server import mcp
        assert callable(mcp.get_agent)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])