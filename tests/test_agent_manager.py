"""Tests for agent manager functionality"""
import os
import pytest
from unittest.mock import patch, MagicMock
import asyncio

from game.agent_manager import AgentManager
from space_traders_api_client.models.agent import Agent
from space_traders_api_client.types import Response

# Mock response data
MOCK_AGENT_DATA = {
    "accountId": "test_id",
    "symbol": "TEST_AGENT",
    "headquarters": "TEST_HQ",
    "credits": 100000,
    "startingFaction": "TEST_FACTION",
    "shipCount": 0
}

@pytest.fixture(scope="module")
def event_loop():
    """Create an event loop for each test module."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def cleanup_queues():
    """Cleanup any pending tasks after each test."""
    yield
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

@pytest.fixture
def mock_env_token():
    """Fixture to set and clean up env token"""
    token = "test_token"
    os.environ['SPACETRADERS_TOKEN'] = token
    yield token
    del os.environ['SPACETRADERS_TOKEN']

@pytest.fixture
def mock_response():
    """Fixture for mock API response"""
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.parsed = MagicMock()
    response.parsed.data = Agent.from_dict(MOCK_AGENT_DATA)
    return response

class TestAgentManager:
    """Test suite for AgentManager class"""

    def test_init_with_token(self):
        """Test initialization with explicit token"""
        token = "test_token"
        manager = AgentManager(token=token)
        assert manager.token == token
        assert manager.agent is None

    def test_init_with_env_token(self, mock_env_token):
        """Test initialization with env token"""
        manager = AgentManager()
        assert manager.token == mock_env_token
        assert manager.agent is None

    def test_init_no_token(self):
        """Test initialization fails without token"""
        if 'SPACETRADERS_TOKEN' in os.environ:
            del os.environ['SPACETRADERS_TOKEN']
        with pytest.raises(ValueError, match="No token provided"):
            AgentManager()

    @pytest.mark.asyncio
    async def test_get_agent_status_success(self, mock_response, cleanup_queues):
        """Test successful agent status retrieval"""
        with patch('game.agent_manager.get_my_agent.asyncio_detailed') as mock_get:
            mock_get.return_value = mock_response

            manager = AgentManager("test_token")
            agent = await manager.get_agent_status()

            assert agent == mock_response.parsed.data
            assert manager.agent == mock_response.parsed.data
            assert agent.symbol == "TEST_AGENT"
            assert agent.headquarters == "TEST_HQ"
            assert agent.credits_ == 100000

    @pytest.mark.asyncio
    async def test_get_agent_status_error(self, cleanup_queues):
        """Test agent status retrieval error handling"""
        error_response = MagicMock(spec=Response)
        error_response.status_code = 404
        error_response.parsed = None

        with patch('game.agent_manager.get_my_agent.asyncio_detailed') as mock_get:
            mock_get.return_value = error_response

            manager = AgentManager("test_token")
            with pytest.raises(Exception, match="Failed to get agent status"):
                await manager.get_agent_status()

    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_response, cleanup_queues):
        """Test successful initialization"""
        with patch('game.agent_manager.get_my_agent.asyncio_detailed') as mock_get:
            mock_get.return_value = mock_response

            manager = AgentManager("test_token")
            await manager.initialize()

            assert manager.agent == mock_response.parsed.data

    @pytest.mark.asyncio
    async def test_initialize_failure(self, cleanup_queues):
        """Test initialization failure"""
        with patch('game.agent_manager.get_my_agent.asyncio_detailed') as mock_get:
            mock_get.side_effect = Exception("API Error")

            manager = AgentManager("test_token")
            with pytest.raises(Exception, match="Failed to initialize agent state"):
                await manager.initialize()
