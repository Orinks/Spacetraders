"""
Cooldown management for ship actions
"""
import json
import asyncio
from datetime import datetime
from typing import Optional

from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.api.fleet import get_ship_cooldown


class CooldownManager:
    """Manages cooldown timers for ship actions"""
    
    def __init__(self, client: AuthenticatedClient):
        """Initialize the cooldown manager
        
        Args:
            client: The authenticated client
        """
        self.client = client
        
    async def wait_for_cooldown(self, ship_symbol: str) -> bool:
        """Wait for any cooldown on a ship to expire
        
        Args:
            ship_symbol: The ship to check
            
        Returns:
            True if cooldown cleared, False if error
        """
        try:
            while True:
                response = await get_ship_cooldown.asyncio_detailed(
                    ship_symbol=ship_symbol,
                    client=self.client
                )
                
                if response.status_code == 204:
                    # No cooldown
                    return True
                    
                if response.status_code != 200:
                    print(f"Error checking cooldown: {response.status_code}")
                    return False
                    
                if not response.parsed:
                    print("No cooldown data in response")
                    return False
                    
                cooldown = response.parsed.data
                remaining = cooldown.remaining_seconds
                
                if remaining <= 0:
                    return True
                    
                print(f"Waiting {remaining} seconds for cooldown...")
                await asyncio.sleep(remaining)
                
        except Exception as e:
            print(f"Error checking cooldown: {e}")
            if hasattr(response, 'content'):
                print(f"Response content: {response.content}")
            return False