"""
Agent and initialization management for SpaceTraders
"""
import os
import logging
from typing import Optional

from dotenv import load_dotenv
from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.api.agents import get_my_agent
from space_traders_api_client.models.agent import Agent

from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class AgentManager:
    """Handles agent authentication and status"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the AgentManager
        
        Args:
            token: Optional API token. If not provided, will read from env var.
            
        Raises:
            ValueError: If no token is provided or found in environment.
        """
        load_dotenv()
        self.token = token or os.getenv('SPACETRADERS_TOKEN')
        if not self.token:
            raise ValueError(
                'No token provided. Set SPACETRADERS_TOKEN env var '
                'or pass token.'
            )
        
        # Initialize the client
        self.client = AuthenticatedClient(
            base_url='https://api.spacetraders.io/v2',
            token=self.token,
            timeout=30.0,
            verify_ssl=True,
            raise_on_unexpected_status=True
        )
        
        # Initialize state
        self.agent: Optional[Agent] = None
        self.rate_limiter = RateLimiter()
        
    async def initialize(self) -> None:
        """Initialize agent state and verify connection
        
        Raises:
            Exception: If unable to connect or retrieve agent status
        """
        try:
            await self.get_agent_status()
        except Exception as e:
            raise Exception(f'Failed to initialize agent state: {e}')
            
    async def get_agent_status(self) -> Agent:
        """Get current agent status
        
        Returns:
            Agent: Current agent data
            
        Raises:
            Exception: If unable to retrieve agent status
        """
        try:
            response = await self.rate_limiter.execute_with_retry(
                get_my_agent.asyncio_detailed,
                task_name="get_agent_status",
                client=self.client
            )
            
            if response.status_code != 200 or not response.parsed:
                raise Exception('Failed to get agent status')
            if not hasattr(response.parsed, 'data'):
                raise Exception('Failed to get agent status: Invalid response format')
                
            self.agent = response.parsed.data
            return self.agent
            
        except Exception as e:
            # Wrap any error with our standard message
            if str(e).startswith('Failed to get agent status'):
                raise
            raise Exception(f'Failed to get agent status: {e}')