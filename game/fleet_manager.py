"""
Fleet and navigation management for SpaceTraders
"""
import asyncio
from typing import Dict, Optional

from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.api.fleet import (
    dock_ship,
    get_my_ships,
    navigate_ship,
    orbit_ship,
    refuel_ship,
)
from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.ship_nav_status import ShipNavStatus
from space_traders_api_client.models.navigate_ship_body import NavigateShipBody


class FleetManager:
    """Manages ship operations and navigation"""
    
    def __init__(self, client: AuthenticatedClient):
        """Initialize FleetManager
        
        Args:
            client: Authenticated API client
        """
        self.client = client
        self.ships: Dict[str, Ship] = {}
        
    async def update_fleet(self) -> None:
        """Update status of all ships
        
        Raises:
            Exception: If unable to retrieve ship data
        """
        response = await get_my_ships.asyncio_detailed(
            client=self.client
        )
        if response.status_code != 200 or not response.parsed:
            raise Exception(
                'Failed to get ships '
                f'(code: {response.status_code})'
            )
        
        self.ships = {
            ship.symbol: ship
            for ship in response.parsed.data
        }
        
    async def navigate_to_waypoint(
        self,
        ship_symbol: str,
        waypoint_symbol: str
    ) -> bool:
        """Navigate ship to a specific waypoint
        
        Args:
            ship_symbol: Symbol of the ship to navigate
            waypoint_symbol: Symbol of the destination waypoint
            
        Returns:
            bool: True if navigation was successful
        """
        nav_body = NavigateShipBody(waypoint_symbol=waypoint_symbol)
        response = await navigate_ship.asyncio_detailed(
            ship_symbol=ship_symbol,
            client=self.client,
            body=nav_body
        )
        return response.status_code == 200
        
    async def dock_ship(self, ship_symbol: str) -> bool:
        """Dock the ship at current waypoint"""
        response = await dock_ship.asyncio_detailed(
            ship_symbol=ship_symbol,
            client=self.client
        )
        return response.status_code == 200
        
    async def refuel_ship(self, ship_symbol: str) -> bool:
        """Refuel the ship at current waypoint"""
        response = await refuel_ship.asyncio_detailed(
            ship_symbol=ship_symbol,
            client=self.client
        )
        return response.status_code == 200
        
    async def orbit_ship(self, ship_symbol: str) -> bool:
        """Put the ship in orbit at current waypoint"""
        response = await orbit_ship.asyncio_detailed(
            ship_symbol=ship_symbol,
            client=self.client
        )
        return response.status_code == 200
        
    async def wait_for_arrival(self, ship_symbol: str) -> Optional[Ship]:
        """Wait for ship to arrive at destination"""
        max_attempts = 30  # 5 minutes with 10s sleep
        attempts = 0
        
        while attempts < max_attempts:
            ship_response = await get_my_ships.asyncio_detailed(
                client=self.client
            )
            if ship_response.status_code != 200 or not ship_response.parsed:
                return None
                
            ship = next(
                (s for s in ship_response.parsed.data
                 if s.symbol == ship_symbol),
                None
            )
            
            if not ship:
                return None
                
            if ship.nav.status != ShipNavStatus.IN_TRANSIT:
                return ship
                
            print('Ship {} in transit... waiting'.format(ship_symbol))
            await asyncio.sleep(10)
            attempts += 1
            
        print('Timeout waiting for ship {} to arrive'.format(ship_symbol))
        return None