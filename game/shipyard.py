"""
Shipyard management for purchasing and configuring ships
"""
from typing import Optional, List, Dict
import json

from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.models.ship_mount import ShipMount
from space_traders_api_client.models.ship_modification_transaction import ShipModificationTransaction
from space_traders_api_client.models.purchase_ship_response_201 import PurchaseShipResponse201
from space_traders_api_client.models.waypoint_trait_symbol import WaypointTraitSymbol
from space_traders_api_client.api.fleet import (
    get_mounts,
    install_mount,
    purchase_ship,
)
from space_traders_api_client.api.systems import (
    get_shipyard,
    get_system_waypoints,
)


class ShipyardManager:
    """Manages shipyard operations and ship modifications"""
    
    MINING_SHIP_TYPES = ["SHIP_MINING_DRONE"]
    
    def __init__(self, client: AuthenticatedClient):
        """Initialize ShipyardManager
        
        Args:
            client: Authenticated API client
        """
        self.client = client
        
    async def get_ship_mounts(self, ship_symbol: str) -> List[ShipMount]:
        """Get current mounts on a ship
        
        Args:
            ship_symbol: Symbol of the ship to check
            
        Returns:
            List of currently installed mounts
        """
        try:
            response = await get_mounts.asyncio_detailed(
                ship_symbol=ship_symbol,
                client=self.client
            )
            if response.status_code == 200 and response.parsed:
                return response.parsed.data
            else:
                print(f"Failed to get ship mounts: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error getting ship mounts: {e}")
            return []

    async def install_mount(
        self,
        ship_symbol: str,
        mount_symbol: str
    ) -> Optional[ShipModificationTransaction]:
        """Install a mount on a ship
        
        Args:
            ship_symbol: Symbol of the ship to modify
            mount_symbol: Symbol of the mount to install
            
        Returns:
            Transaction details if successful, None otherwise
        """
        try:
            response = await install_mount.asyncio_detailed(
                ship_symbol=ship_symbol,
                client=self.client,
                json_body={"symbol": mount_symbol}
            )
            if response.status_code == 201 and response.parsed:
                print(f"Successfully installed {mount_symbol} on {ship_symbol}")
                return response.parsed.data.transaction
            else:
                print(f"Failed to install mount: {response.status_code}")
                print(f"Response: {response}")
                return None
        except Exception as e:
            print(f"Error installing mount: {e}")
            return None
            
    async def get_shipyard_info(self, waypoint: str) -> Optional[Dict]:
        """Get shipyard information for a waypoint
        
        Args:
            waypoint: The waypoint symbol to check
            
        Returns:
            Shipyard information if available, None otherwise
        """
        try:
            response = await get_shipyard.asyncio_detailed(
                waypoint_symbol=waypoint,
                client=self.client
            )
            if response.status_code == 200 and response.parsed:
                return response.parsed.data.to_dict()
            else:
                print(f"Failed to get shipyard info: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting shipyard info: {e}")
            return None
            
    def has_mining_mount(self, mounts: List[ShipMount]) -> bool:
        """Check if ship has a mining mount installed
        
        Args:
            mounts: List of current ship mounts
            
        Returns:
            True if mining mount found, False otherwise
        """
        for mount in mounts:
            if mount.symbol in ["MOUNT_MINING_LASER", "MOUNT_MINING_LASER_II"]:
                return True
        return False

    async def find_shipyards_in_system(self, system_symbol: str) -> List[str]:
        """Find all shipyards in a system

        Args:
            system_symbol: The system to search in

        Returns:
            List of waypoint symbols that have shipyards
        """
        shipyards = []
        try:
            # Start with page 1
            page = 1
            while True:
                response = await get_system_waypoints.asyncio_detailed(
                    system_symbol=system_symbol,
                    client=self.client,
                    page=page
                )
                
                if response.status_code != 200 or not response.parsed:
                    print(f"Failed to get waypoints: {response.status_code}")
                    break

                # Look for shipyard waypoints
                for waypoint in response.parsed.data:
                    if any(trait.symbol == WaypointTraitSymbol.SHIPYARD for trait in waypoint.traits):
                        shipyards.append(waypoint.symbol)
                
                # Check if there are more pages
                total_pages = response.parsed.meta.total / 20  # 20 is default page size
                if page >= total_pages:
                    break
                    
                page += 1

            print(f"Found {len(shipyards)} shipyards in system {system_symbol}")
            return shipyards

        except Exception as e:
            print(f"Error finding shipyards: {e}")
            return []

    async def find_available_mining_ship(self, system_symbol: str) -> Optional[tuple[str, Dict]]:
        """Find an available mining ship to purchase in a system

        Args:
            system_symbol: The system to search in

        Returns:
            Tuple of (waypoint symbol, ship details) if found, None otherwise
        """
        print(f"Searching for available mining ships in system {system_symbol}")
        try:
            # First find all shipyards
            shipyards = await self.find_shipyards_in_system(system_symbol)
            if not shipyards:
                print("No shipyards found in system")
                return None

            # Check each shipyard for mining ships
            best_ship = None
            best_price = float('inf')
            best_waypoint = None

            for waypoint in shipyards:
                shipyard_info = await self.get_shipyard_info(waypoint)
                if not shipyard_info:
                    continue

                # Look for mining ships
                for ship in shipyard_info.get('ships', []):
                    if ship['type'] in self.MINING_SHIP_TYPES:
                        price = ship.get('purchasePrice', float('inf'))
                        if price < best_price:
                            best_price = price
                            best_ship = ship
                            best_waypoint = waypoint

            if best_ship and best_waypoint:
                print(f"Found {best_ship['type']} at {best_waypoint} for {best_price} credits")
                return (best_waypoint, best_ship)
            else:
                print("No mining ships available in any shipyard")
                return None

        except Exception as e:
            print(f"Error finding available mining ships: {e}")
            return None

    async def purchase_mining_ship(self, system_symbol: str) -> Optional[PurchaseShipResponse201]:
        """Purchase a mining ship from any available shipyard in the system
        
        Args:
            system_symbol: The system to search for shipyards
            
        Returns:
            Purchase response if successful, None otherwise
        """
        try:
            # Find the best available mining ship
            result = await self.find_available_mining_ship(system_symbol)
            if not result:
                print("Could not find any available mining ships")
                return None

            waypoint, ship = result
            print(f"Attempting to purchase {ship['type']} at {waypoint} for {ship['purchasePrice']} credits")

            # Purchase the ship
            response = await purchase_ship.asyncio_detailed(
                client=self.client,
                json_body={"shipType": ship['type']},
                waypoint_symbol=waypoint
            )

            if response.status_code == 201 and response.parsed:
                print(f"Successfully purchased ship: {response.parsed.data.ship.symbol}")
                return response
            else:
                print(f"Failed to purchase ship: {response.status_code}")
                if response.content:
                    print(f"Response: {response.content.decode()}")
                return None

        except Exception as e:
            print(f"Error purchasing mining ship: {e}")
            return None