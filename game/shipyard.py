"""
Shipyard management for purchasing and configuring ships
"""
from typing import Optional, List, Dict, Tuple
import json
import asyncio

from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.models.ship_mount import ShipMount
from space_traders_api_client.models.ship_modification_transaction import ShipModificationTransaction
from space_traders_api_client.models.purchase_ship_response_201 import PurchaseShipResponse201
from space_traders_api_client.models.waypoint_trait_symbol import WaypointTraitSymbol
from space_traders_api_client.models.install_mount_install_mount_request import InstallMountInstallMountRequest
from space_traders_api_client.models.refuel_ship_body import RefuelShipBody
from space_traders_api_client.api.fleet import (
    get_mounts,
    install_mount,
    purchase_ship,
    get_my_ships,
    navigate_ship,
    orbit_ship,
    dock_ship,
    refuel_ship,
)
from space_traders_api_client.api.systems import (
    get_shipyard,
    get_system_waypoints,
    get_systems,
)
from space_traders_api_client.models.ship_mount_symbol import ShipMountSymbol


class ShipyardManager:
    """Manages shipyard operations and ship modifications"""

    MINING_SHIP_TYPES = ["SHIP_MINING_DRONE", "SHIP_MINER"]
    TRANSPORT_SHIP_TYPES = ["SHIP_LIGHT_HAULER", "SHIP_HEAVY_FREIGHTER"]
    RATE_LIMIT_DELAY = 0.5  # Delay between API calls to avoid rate limiting

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
            print(f"Failed to get ship mounts: {response.status_code}")
            return []
        except Exception as e:
            print(f"Error getting ship mounts: {e}")
            return []

    async def install_mount(
        self,
        ship_symbol: str,
        body: InstallMountInstallMountRequest
    ) -> Optional[ShipModificationTransaction]:
        """Install a mount on a ship

        Args:
            ship_symbol: Symbol of the ship to modify
            body: Install mount request details

        Returns:
            Transaction details if successful, None otherwise
        """
        try:
            response = await install_mount.asyncio_detailed(
                ship_symbol=ship_symbol,
                client=self.client,
                json_body=body
            )
            if response.status_code == 201 and response.parsed:
                print(f"Successfully installed mount on {ship_symbol}")
                return response.parsed.data.transaction
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
            await asyncio.sleep(self.RATE_LIMIT_DELAY)  # Rate limiting
            # Extract system from waypoint
            system = waypoint.split('-')[0] + '-' + waypoint.split('-')[1]
            response = await get_shipyard.asyncio_detailed(
                system_symbol=system,
                waypoint_symbol=waypoint,
                client=self.client
            )
            if response.status_code == 200 and response.parsed:
                return response.parsed.data.to_dict()
            elif response.status_code == 429:  # Rate limited
                retry_after = 1  # Default retry delay
                try:
                    error_data = json.loads(response.content.decode())
                    retry_after = error_data.get('error', {}).get('data', {}).get(
                        'retryAfter',
                        1
                    )
                except json.JSONDecodeError as err:
                    print(f"Error parsing retry response: {err}")
                print(f"Rate limited, waiting {retry_after} seconds...")
                await asyncio.sleep(retry_after)
                return await self.get_shipyard_info(waypoint)  # Retry
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
        mining_mounts = [
            ShipMountSymbol.MOUNT_MINING_LASER_I,
            ShipMountSymbol.MOUNT_MINING_LASER_II,
            ShipMountSymbol.MOUNT_MINING_LASER_III,
        ]
        return any(mount.symbol in mining_mounts for mount in mounts)

    async def find_shipyards_in_system(self, system_symbol: str) -> List[str]:
        """Find all shipyards in a system

        Args:
            system_symbol: The system to search in

        Returns:
            List of waypoint symbols that have shipyards
        """
        shipyards = []
        try:
            # Get all waypoints in system with pagination
            page = 1
            while True:
                await asyncio.sleep(self.RATE_LIMIT_DELAY)  # Rate limiting
                response = await get_system_waypoints.asyncio_detailed(
                    system_symbol=system_symbol,
                    client=self.client,
                    page=page,
                    limit=20  # Max page size
                )

                if response.status_code == 429:  # Rate limited
                    retry_after = 1  # Default retry delay
                    try:
                        error_data = json.loads(response.content.decode())
                        retry_after = error_data.get('error', {}).get('data', {}).get(
                            'retryAfter',
                            1
                        )
                    except json.JSONDecodeError as err:
                        print(f"Error parsing retry response: {err}")
                    print(f"Rate limited, waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    continue  # Retry same page

                if response.status_code != 200 or not response.parsed:
                    print(f"Failed to get waypoints: {response.status_code}")
                    break

                # Look for shipyard waypoints and markets
                for waypoint in response.parsed.data:
                    # Check both SHIPYARD and MARKETPLACE traits
                    has_shipyard = any(
                        trait.symbol == WaypointTraitSymbol.SHIPYARD 
                        for trait in waypoint.traits
                    )
                    has_marketplace = any(
                        trait.symbol == WaypointTraitSymbol.MARKETPLACE
                        for trait in waypoint.traits
                    )

                    # Print details about the waypoint and its traits
                    print(f"Waypoint {waypoint.symbol} ({waypoint.type_}):")
                    print(f"  Traits: {[trait.symbol for trait in waypoint.traits]}")

                    if has_shipyard:
                        print("  Found shipyard!")
                        shipyards.append(waypoint.symbol)
                    elif has_marketplace:
                        print("  Has marketplace, checking for shipyard...")
                        # Query waypoint specifically
                        await asyncio.sleep(self.RATE_LIMIT_DELAY)
                        shipyard_info = await self.get_shipyard_info(waypoint.symbol)
                        if shipyard_info:
                            print("  Confirmed shipyard at marketplace!")
                            shipyards.append(waypoint.symbol)

                # Check total pages from meta data
                total_count = response.parsed.meta.total if response.parsed.meta else 0
                if total_count > page * 20:  # More pages available
                    page += 1
                else:
                    break  # No more pages

            print(f"Found {len(shipyards)} shipyards in system {system_symbol}")
            return shipyards

        except Exception as e:
            print(f"Error finding shipyards: {e}")
            return []

    async def find_nearby_systems(self, limit: int = 20) -> List[str]:
        """Get list of nearby systems

        Args:
            limit: Maximum number of systems to return

        Returns:
            List of system symbols
        """
        try:
            systems = []
            page = 1
            while len(systems) < limit:
                await asyncio.sleep(self.RATE_LIMIT_DELAY)  # Rate limiting
                response = await get_systems.asyncio_detailed(
                    client=self.client,
                    page=page,
                    limit=20  # Max page size
                )

                if response.status_code == 429:  # Rate limited
                    retry_after = 1  # Default retry delay
                    try:
                        error_data = json.loads(response.content.decode())
                        retry_after = error_data.get('error', {}).get('data', {}).get(
                            'retryAfter',
                            1
                        )
                    except json.JSONDecodeError as err:
                        print(f"Error parsing retry response: {err}")
                    print(f"Rate limited, waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    continue  # Retry the same page

                if response.status_code == 200 and response.parsed:
                    new_systems = [system.symbol for system in response.parsed.data]
                    systems.extend(new_systems)

                    # If page is not full, we've reached the end
                    if len(new_systems) < 20:
                        break

                    page += 1
                else:
                    print(f"Failed to get nearby systems: {response.status_code}")
                    break

            return systems[:limit]

        except Exception as e:
            print(f"Error getting nearby systems: {e}")
            return []

    async def find_available_mining_ship(
        self,
        system_symbol: str
    ) -> Optional[Tuple[str, Dict]]:
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
                            # Get fuel capacity from frame
                            frame = ship.get('frame', {})
                            fuel_capacity = frame.get('fuelCapacity', 0)
                            print(
                                f"Found {ship['type']} with {fuel_capacity} fuel "
                                f"capacity at {waypoint} for {price} credits"
                            )
                            best_price = price
                            best_ship = ship
                            best_waypoint = waypoint

            if best_ship and best_waypoint:
                fuel_cap = best_ship.get('frame', {}).get('fuelCapacity', 0)
                print(
                    f"Selected {best_ship['type']} at {best_waypoint} "
                    f"for {best_price} credits (fuel capacity: {fuel_cap})"
                )
                return (best_waypoint, best_ship)
            print("No mining ships available in any shipyard")
            return None

        except Exception as e:
            print(f"Error finding available mining ships: {e}")
            return None

    async def find_mining_ship_in_nearby_systems(
        self,
        current_system: str,
        min_fuel_capacity: Optional[int] = None
    ) -> Optional[Tuple[str, Dict]]:
        """Search for mining ships in nearby systems

        Args:
            current_system: Current system symbol
            min_fuel_capacity: Minimum fuel capacity required

        Returns:
            Tuple of (waypoint symbol, ship details) if found, None otherwise
        """
        try:
            # First check current system
            result = await self.find_available_mining_ship(current_system)
            if result:
                waypoint, ship = result
                # Check fuel capacity if specified
                fuel_cap = ship.get('frame', {}).get('fuelCapacity', 0)
                if min_fuel_capacity is None or fuel_cap >= min_fuel_capacity:
                    return result
                print(
                    f"Found ship with insufficient fuel capacity: "
                    f"{fuel_cap} (need {min_fuel_capacity})"
                )

            # If not found, check nearby systems
            nearby_systems = await self.find_nearby_systems()
            print(f"Checking {len(nearby_systems)} nearby systems for mining ships")

            for system in nearby_systems:
                if system == current_system:
                    continue

                print(f"Checking system {system}")
                result = await self.find_available_mining_ship(system)
                if result:
                    waypoint, ship = result
                    # Check fuel capacity if specified
                    fuel_cap = ship.get('frame', {}).get('fuelCapacity', 0)
                    if min_fuel_capacity is None or fuel_cap >= min_fuel_capacity:
                        return result
                    print(
                        f"Found ship with insufficient fuel capacity: "
                        f"{fuel_cap} (need {min_fuel_capacity})"
                    )

            return None

        except Exception as e:
            print(f"Error searching nearby systems: {e}")
            return None

    async def purchase_command_ship(
        self,
        system_symbol: str,
        min_cargo_capacity: Optional[int] = None,
        min_fuel_capacity: Optional[int] = None
    ) -> Optional[PurchaseShipResponse201]:
        """Purchase a transport/command ship for hauling cargo

        Args:
            system_symbol: System to search in
            min_cargo_capacity: Minimum cargo capacity required
            min_fuel_capacity: Minimum fuel capacity required

        Returns:
            Purchase response if successful, None otherwise
        """
        try:
            # Find all shipyards in system
            shipyards = await self.find_shipyards_in_system(system_symbol)

            best_ship = None
            best_price = float('inf')
            best_waypoint = None

            for waypoint in shipyards:
                shipyard_info = await self.get_shipyard_info(waypoint)
                if not shipyard_info:
                    continue

                # Look for transport ships
                for ship in shipyard_info.get('ships', []):
                    if ship['type'] in self.TRANSPORT_SHIP_TYPES:
                        price = ship.get('purchasePrice', float('inf'))

                        # Check capacities
                        cargo_cap = ship.get('frame', {}).get('cargoCapacity', 0)
                        fuel_cap = ship.get('frame', {}).get('fuelCapacity', 0)

                        if min_cargo_capacity and cargo_cap < min_cargo_capacity:
                            continue
                        if min_fuel_capacity and fuel_cap < min_fuel_capacity:
                            continue

                        if price < best_price:
                            print(
                                f"Found {ship['type']} at {waypoint}\n"
                                f"  Cargo: {cargo_cap}, Fuel: {fuel_cap}\n"
                                f"  Price: {price} credits"
                            )
                            best_price = price
                            best_ship = ship
                            best_waypoint = waypoint

            if best_ship and best_waypoint:
                # Purchase the ship
                print(f"Attempting to purchase {best_ship['type']} at {best_waypoint}")

                from space_traders_api_client.models.purchase_ship_body import (
                    PurchaseShipBody
                )
                from space_traders_api_client.models.ship_type import ShipType

                body = PurchaseShipBody(
                    ship_type=ShipType(best_ship['type']),
                    waypoint_symbol=best_waypoint
                )

                response = await purchase_ship.asyncio_detailed(
                    client=self.client,
                    body=body
                )

                if response.status_code == 201 and response.parsed:
                    print(
                        f"Successfully purchased command ship: "
                        f"{response.parsed.data.ship.symbol}"
                    )
                    return response.parsed
                print(f"Failed to purchase ship: {response.status_code}")
                if response.content:
                    print(f"Response: {response.content.decode()}")
                return None
            print("No suitable command ships found")
            return None

        except Exception as e:
            print(f"Error purchasing command ship: {e}")
            return None

    async def purchase_mining_ship(
        self,
        system_symbol: str,
        min_fuel_capacity: Optional[int] = None
    ) -> Optional[PurchaseShipResponse201]:
        """Purchase a mining ship from any available shipyard

        Args:
            system_symbol: The system to search for shipyards
            min_fuel_capacity: Minimum fuel capacity required

        Returns:
            Purchase response if successful, None otherwise
        """
        try:
            # Find the best available mining ship
            result = await self.find_mining_ship_in_nearby_systems(
                system_symbol,
                min_fuel_capacity=min_fuel_capacity
            )
            if not result:
                if min_fuel_capacity:
                    print(
                        f"Could not find any available mining ships "
                        f"with {min_fuel_capacity} fuel capacity"
                    )
                else:
                    print("Could not find any available mining ships")
                return None

            waypoint, ship = result
            print(
                f"Attempting to purchase {ship['type']} at {waypoint} "
                f"for {ship['purchasePrice']} credits"
            )

            # Purchase the ship
            await asyncio.sleep(self.RATE_LIMIT_DELAY)  # Rate limiting
            from space_traders_api_client.models.purchase_ship_body import (
                PurchaseShipBody
            )
            from space_traders_api_client.models.ship_type import ShipType
            from space_traders_api_client.models.navigate_ship_body import (
                NavigateShipBody
            )
            from space_traders_api_client.models.install_mount_install_mount_request import (  # noqa: E501
                InstallMountInstallMountRequest
            )

            # Create the request body
            body = PurchaseShipBody(
                ship_type=ShipType(ship['type']),
                waypoint_symbol=waypoint
            )

            response = await purchase_ship.asyncio_detailed(
                client=self.client,
                body=body
            )

            if response.status_code == 429:  # Rate limited
                retry_after = 1  # Default retry delay
                try:
                    error_data = json.loads(response.content.decode())
                    retry_after = error_data.get('error', {}).get('data', {}).get(
                        'retryAfter',
                        1
                    )
                except json.JSONDecodeError as err:
                    print(f"Error parsing retry response: {err}")
                print(f"Rate limited, waiting {retry_after} seconds...")
                await asyncio.sleep(retry_after)
                return await self.purchase_mining_ship(system_symbol)  # Retry

            if response.status_code == 201 and response.parsed:
                ship_symbol = response.parsed.data.ship.symbol
                print(f"Successfully purchased ship: {ship_symbol}")

                if response.parsed.data.ship.nav:
                    current_waypoint = response.parsed.data.ship.nav.waypoint_symbol
                    print(f"Ship is at waypoint {current_waypoint}")

                    # Try to find a shipyard to install the mount
                    print("Searching for shipyard to install mining mount...")
                    shipyards = await self.find_shipyards_in_system(system_symbol)
                    if shipyards:
                        for shipyard in shipyards:
                            # First make sure ship is refueled
                            dock_response = await dock_ship.asyncio_detailed(
                                ship_symbol=ship_symbol,
                                client=self.client
                            )
                            if dock_response.status_code != 200:
                                print(f"Failed to dock: {dock_response.status_code}")
                                continue

                            refuel_response = await refuel_ship.asyncio_detailed(
                                ship_symbol=ship_symbol,
                                client=self.client,
                                body=RefuelShipBody()
                            )
                            if refuel_response.status_code != 200:
                                print(f"Failed to refuel: {refuel_response.status_code}")
                                continue
                            print("Ship refueled successfully")

                            # Then navigate to the shipyard if needed
                            if current_waypoint != shipyard:
                                print(f"Navigating to shipyard at {shipyard}")

                                # First move ship to orbit if needed
                                orbit_response = await orbit_ship.asyncio_detailed(
                                    ship_symbol=ship_symbol,
                                    client=self.client
                                )
                                if orbit_response.status_code != 200:
                                    print(f"Failed to orbit: {orbit_response.status_code}")
                                    continue

                                nav_body = NavigateShipBody(
                                    waypoint_symbol=shipyard
                                )
                                nav_response = await navigate_ship.asyncio_detailed(
                                    ship_symbol=ship_symbol,
                                    client=self.client,
                                    body=nav_body
                                )

                                if nav_response.status_code != 200:
                                    print(f"Failed to navigate: {nav_response.status_code}")
                                    if nav_response.content:
                                        print(
                                            f"Response: {nav_response.content.decode()}"
                                        )
                                    continue

                                # Wait for arrival
                                try:
                                    while True:
                                        await asyncio.sleep(5)  # Check every 5 seconds
                                        ship_response = await get_my_ships.asyncio_detailed(  # noqa: E501
                                            client=self.client
                                        )
                                        if (ship_response.status_code == 200 and
                                                ship_response.parsed):
                                            ship = next(
                                                (s for s in ship_response.parsed.data
                                                 if s.symbol == ship_symbol),
                                                None
                                            )
                                            if ship and ship.nav.status != "IN_TRANSIT":
                                                break
                                except Exception as e:
                                    print(f"Error waiting for arrival: {e}")
                                    continue

                            print(f"Attempting to install mining mount...")
                            mount_body = InstallMountInstallMountRequest(
                                symbol=ShipMountSymbol.MOUNT_MINING_LASER_I
                            )
                            transaction = await self.install_mount(
                                ship_symbol=ship_symbol,
                                body=mount_body
                            )

                            if transaction:
                                print(
                                    f"Successfully installed mining mount for "
                                    f"{transaction.price_paid} credits"
                                )
                                break
                            print(
                                "Failed to install mount at this shipyard, "
                                "trying another..."
                            )

                    else:
                        print("No shipyards found to install mining mount")
                else:
                    print("No navigation data available for ship")

                return response

            error_msg = "Failed to purchase ship"
            if response.status_code:
                error_msg += f": {response.status_code}"
            if response.content:
                error_msg += f"\nResponse: {response.content.decode()}"
            print(error_msg)
            return None

        except Exception as e:
            print(f"Error purchasing mining ship: {e}")
            return None