"""
Contract management for SpaceTraders
"""
from typing import Dict, Optional, Any
import json
import asyncio

from space_traders_api_client import AuthenticatedClient, errors
from space_traders_api_client.models.contract import Contract
from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.ship_nav_status import ShipNavStatus
from space_traders_api_client.models.navigate_ship_body import NavigateShipBody
from space_traders_api_client.api.contracts import (
    accept_contract,
    deliver_contract,
    fulfill_contract,
    get_contract,
    get_contracts,
)
from space_traders_api_client.api.fleet import (
    orbit_ship,
    navigate_ship,
    get_ship_nav,
    dock_ship
)
from space_traders_api_client.api.systems import (
    get_system_waypoints,
    get_waypoint
)

from .mining import SurveyManager
from .shipyard import ShipyardManager


class ContractManager:
    """Manages contract operations and fulfillment"""

    RATE_LIMIT_DELAY = 0.5  # Base delay between API calls
    
    def __init__(self, client: AuthenticatedClient):
        """Initialize ContractManager
        
        Args:
            client: Authenticated API client
        """
        self.client = client
        self.contracts: Dict[str, Contract] = {}
        self.shipyard_manager = ShipyardManager(client)

    async def handle_rate_limit(
        self,
        func_name: str,
        response: Any,
        retry_count: int = 0,
        max_retries: int = 3
    ) -> Optional[float]:
        """Handle rate limit response, return retry delay if needed
        
        Args:
            func_name: Name of function for logging
            response: API response object
            retry_count: Current retry attempt
            max_retries: Maximum number of retries
            
        Returns:
            Delay in seconds to wait before retry, or None if no retry needed
        """
        if response.status_code == 429:  # Rate limited
            if retry_count >= max_retries:
                print(f"{func_name}: Too many retries ({retry_count})")
                return None

            retry_after = self.RATE_LIMIT_DELAY  # Default retry delay
            try:
                error_data = json.loads(response.content.decode())
                retry_after = error_data.get('error', {}).get('data', {}).get('retryAfter', self.RATE_LIMIT_DELAY)
            except:
                pass
            print(f"{func_name}: Rate limited, waiting {retry_after} seconds...")
            return retry_after

        return None
        
    async def update_contracts(self) -> None:
        """Update the list of available contracts"""
        for attempt in range(3):
            try:
                await asyncio.sleep(self.RATE_LIMIT_DELAY)
                response = await get_contracts.asyncio_detailed(
                    client=self.client
                )
                
                retry_after = await self.handle_rate_limit(
                    "update_contracts",
                    response,
                    attempt
                )
                if retry_after:
                    await asyncio.sleep(retry_after)
                    continue
                    
                if response.status_code == 200 and response.parsed:
                    self.contracts = {
                        contract.id: contract
                        for contract in response.parsed.data
                    }
                    print(f"Found {len(self.contracts)} active contracts")
                    break
                else:
                    print(f"Failed to get contracts: {response.status_code}")
            except Exception as e:
                print(f"Error updating contracts: {e}")
                await asyncio.sleep(1)  # Wait before retry
                
    async def accept_contract(self, contract_id: str) -> bool:
        """Accept a contract by ID"""
        for attempt in range(3):
            try:
                await asyncio.sleep(self.RATE_LIMIT_DELAY)
                response = await accept_contract.asyncio_detailed(
                    contract_id=contract_id,
                    client=self.client
                )
                
                retry_after = await self.handle_rate_limit(
                    "accept_contract",
                    response,
                    attempt
                )
                if retry_after:
                    await asyncio.sleep(retry_after)
                    continue
                    
                if response.status_code == 200:
                    print(f"Successfully accepted contract {contract_id}")
                    await self.update_contracts()  # Refresh contracts
                    return True
                else:
                    print(f"Failed to accept contract: {response.status_code}")
                    return False
            except Exception as e:
                print(f"Error accepting contract: {e}")
                await asyncio.sleep(1)  # Wait before retry
        return False

    async def deliver_contract_cargo(
        self,
        contract_id: str,
        ship_symbol: str,
        trade_symbol: str,
        units: int
    ) -> bool:
        """Deliver cargo for a contract
        
        Args:
            contract_id: ID of the contract
            ship_symbol: Symbol of the ship delivering cargo
            trade_symbol: Symbol of the trade good
            units: Number of units to deliver
        """
        for attempt in range(3):
            try:
                await asyncio.sleep(self.RATE_LIMIT_DELAY)
                
                # First dock the ship
                dock_response = await dock_ship.asyncio_detailed(
                    ship_symbol=ship_symbol,
                    client=self.client
                )
                
                retry_after = await self.handle_rate_limit(
                    "deliver_contract_cargo (dock)",
                    dock_response,
                    attempt
                )
                if retry_after:
                    await asyncio.sleep(retry_after)
                    continue
                    
                if dock_response.status_code != 200:
                    print(f"Failed to dock ship: {dock_response.status_code}")
                    continue
                
                # Then deliver the cargo
                response = await deliver_contract.asyncio_detailed(
                    contract_id=contract_id,
                    client=self.client,
                    json_body={
                        "shipSymbol": ship_symbol,
                        "tradeSymbol": trade_symbol,
                        "units": units
                    }
                )
                
                retry_after = await self.handle_rate_limit(
                    "deliver_contract_cargo (deliver)",
                    response,
                    attempt
                )
                if retry_after:
                    await asyncio.sleep(retry_after)
                    continue
                
                if response.status_code == 200:
                    print(
                        f"Successfully delivered {units} units of {trade_symbol} "
                        f"for contract {contract_id}"
                    )
                    return True
                else:
                    print(f"Failed to deliver cargo: {response.status_code}")
                    if response.content:
                        print(f"Response: {response.content.decode()}")
            except Exception as e:
                print(f"Error delivering cargo: {e}")
                await asyncio.sleep(1)  # Wait before retry
        return False

    async def fulfill_contract(self, contract_id: str) -> bool:
        """Fulfill a completed contract"""
        for attempt in range(3):
            try:
                await asyncio.sleep(self.RATE_LIMIT_DELAY)
                response = await fulfill_contract.asyncio_detailed(
                    contract_id=contract_id,
                    client=self.client
                )
                
                retry_after = await self.handle_rate_limit(
                    "fulfill_contract",
                    response,
                    attempt
                )
                if retry_after:
                    await asyncio.sleep(retry_after)
                    continue
                    
                if response.status_code == 200:
                    print(f"Successfully fulfilled contract {contract_id}")
                    await self.update_contracts()  # Refresh contracts
                    return True
                else:
                    print(f"Failed to fulfill contract: {response.status_code}")
                    return False
            except Exception as e:
                print(f"Error fulfilling contract: {e}")
                await asyncio.sleep(1)  # Wait before retry
        return False
            
    async def ensure_ship_can_mine(self, ship: Ship) -> bool:
        """Ensure a ship has mining capabilities
        
        Args:
            ship: Ship to check/modify
            
        Returns:
            True if ship can mine (or was upgraded), False otherwise
        """
        for attempt in range(3):
            try:
                # Check current mounts
                mounts = await self.shipyard_manager.get_ship_mounts(ship.symbol)
                if self.shipyard_manager.has_mining_mount(mounts):
                    print(f"Ship {ship.symbol} already has mining capabilities")
                    return True
                    
                # Need to install mining mount
                print(f"Ship {ship.symbol} needs mining capabilities")
                
                # Check if local waypoint has a shipyard
                if not hasattr(ship, 'nav') or not ship.nav.waypoint_symbol:
                    print("Ship has no navigation data")
                    return False
                    
                shipyard_info = await self.shipyard_manager.get_shipyard_info(
                    ship.nav.waypoint_symbol
                )
                
                if not shipyard_info:
                    print(f"No shipyard at {ship.nav.waypoint_symbol}")
                    return False
                    
                # Try to install mining laser
                from space_traders_api_client.models.ship_mount_symbol import ShipMountSymbol
                from space_traders_api_client.models.install_mount_install_mount_request import InstallMountInstallMountRequest

                mount_body = InstallMountInstallMountRequest(
                    symbol=ShipMountSymbol.MOUNT_MINING_LASER_I
                )
                transaction = await self.shipyard_manager.install_mount(
                    ship_symbol=ship.symbol,
                    body=mount_body
                )
                    
                if transaction:
                    print(
                        f"Installed mining laser on {ship.symbol} "
                        f"for {transaction.price_paid} credits"
                    )
                    return True
                else:
                    print("Failed to install mining laser")
                    return False
            except Exception as e:
                print(f"Error ensuring ship can mine: {e}")
                await asyncio.sleep(1)  # Wait before retry
        return False
            
    async def find_mining_site(
        self,
        current_system: str
    ) -> Optional[str]:
        """Find a suitable mining location
        
        Args:
            current_system: Current system symbol
            
        Returns:
            Waypoint symbol if found, None otherwise
        """
        for attempt in range(3):
            try:
                await asyncio.sleep(self.RATE_LIMIT_DELAY)
                response = await get_system_waypoints.asyncio_detailed(
                    system_symbol=current_system,
                    client=self.client
                )
                
                retry_after = await self.handle_rate_limit(
                    "find_mining_site",
                    response,
                    attempt
                )
                if retry_after:
                    await asyncio.sleep(retry_after)
                    continue
                
                if response.status_code != 200 or not response.parsed:
                    print(f"Failed to get waypoints: {response.status_code}")
                    continue
                    
                # Look for asteroid fields or asteroids
                mining_waypoints = []
                for waypoint in response.parsed.data:
                    if waypoint.type_ in [
                        "ASTEROID",
                        "ASTEROID_FIELD"
                    ]:
                        mining_waypoints.append(waypoint.symbol)
                        
                if not mining_waypoints:
                    print("No suitable mining locations found")
                    return None
                    
                # Return first available site
                return mining_waypoints[0]
                    
            except Exception as e:
                print(f"Error finding mining site: {e}")
                await asyncio.sleep(1)  # Wait before retry
        return None
            
    async def navigate_to_waypoint(
        self,
        ship: Ship,
        destination: str
    ) -> bool:
        """Navigate a ship to a waypoint
        
        Args:
            ship: Ship to move
            destination: Destination waypoint symbol
            
        Returns:
            True if navigation successful, False otherwise
        """
        for attempt in range(3):
            try:
                # Check if already at destination
                if ship.nav.waypoint_symbol == destination:
                    print(f"Ship {ship.symbol} is already at {destination}")
                    return True
                    
                # Make sure we're in orbit before navigation
                if ship.nav.status != ShipNavStatus.IN_ORBIT:
                    print(f"Moving ship {ship.symbol} into orbit")
                    orbit_response = await orbit_ship.asyncio_detailed(
                        ship_symbol=ship.symbol,
                        client=self.client
                    )
                    
                    retry_after = await self.handle_rate_limit(
                        "navigate_to_waypoint (orbit)",
                        orbit_response,
                        attempt
                    )
                    if retry_after:
                        await asyncio.sleep(retry_after)
                        continue
                        
                    if orbit_response.status_code != 200:
                        print(f"Failed to orbit: {orbit_response.status_code}")
                        if orbit_response.content:
                            print(f"Response: {orbit_response.content.decode()}")
                        continue
                    
                print(f"Navigating {ship.symbol} to {destination}")
                nav_body = NavigateShipBody(waypoint_symbol=destination)
                response = await navigate_ship.asyncio_detailed(
                    ship_symbol=ship.symbol,
                    client=self.client,
                    body=nav_body
                )
                
                retry_after = await self.handle_rate_limit(
                    "navigate_to_waypoint (navigate)",
                    response,
                    attempt
                )
                if retry_after:
                    await asyncio.sleep(retry_after)
                    continue
                
                if response.status_code == 200:
                    return True
                else:
                    print(f"Navigation failed: {response.status_code}")
                    if response.content:
                        print(f"Response: {response.content.decode()}")
                    continue
                    
            except Exception as e:
                print(f"Error during navigation: {e}")
                await asyncio.sleep(1)  # Wait before retry
        return False

    async def wait_for_arrival(self, ship_symbol: str) -> bool:
        """Wait for a ship to arrive at its destination
        
        Args:
            ship_symbol: Symbol of ship to wait for
            
        Returns:
            True when arrived, False if error
        """
        while True:
            try:
                await asyncio.sleep(self.RATE_LIMIT_DELAY)
                response = await get_ship_nav.asyncio_detailed(
                    ship_symbol=ship_symbol,
                    client=self.client
                )
                
                if response.status_code == 429:
                    retry_after = 1
                    try:
                        error_data = json.loads(response.content.decode())
                        retry_after = error_data.get('error', {}).get('data', {}).get('retryAfter', 1)
                    except:
                        pass
                    await asyncio.sleep(retry_after)
                    continue
                
                if response.status_code != 200 or not response.parsed:
                    print(f"Failed to get ship status: {response.status_code}")
                    return False
                    
                nav = response.parsed.data
                if nav.status != "IN_TRANSIT":
                    return True
                    
                # Wait before checking again
                print(f"Ship {ship_symbol} still in transit...")
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"Error waiting for arrival: {e}")
                return False

    async def process_contract(
        self,
        contract: Contract,
        ships: Dict[str, Ship],
        survey_manager: SurveyManager
    ) -> None:
        """Process a specific contract's requirements
        
        Args:
            contract: The contract to process
            ships: Dictionary of available ships
            survey_manager: Survey manager for mining operations
        """
        try:
            print(f"Processing contract with details: {json.dumps(contract.to_dict(), indent=2)}")
            
            if not contract or not hasattr(contract, 'terms'):
                print('Contract has invalid format')
                return
                
            if not hasattr(contract.terms, 'deliver'):
                print(f'Contract {contract.id} has no delivery terms')
                return
                
            if not contract.terms.deliver:
                print(f'Contract {contract.id} has no delivery requirements')
                return

            # Check if contract can be fulfilled with rate limiting
            for attempt in range(3):  # Try up to 3 times
                try:
                    await asyncio.sleep(self.RATE_LIMIT_DELAY)
                    response = await get_contract.asyncio_detailed(
                        contract_id=contract.id,
                        client=self.client
                    )
                    
                    retry_after = await self.handle_rate_limit(
                        "process_contract",
                        response,
                        attempt
                    )
                    if retry_after:
                        await asyncio.sleep(retry_after)
                        continue
                    
                    if response.status_code == 200 and response.parsed:
                        contract_details = response.parsed.data
                        break  # Success, exit retry loop
                    else:
                        print(f"Failed to get contract details: {response.status_code}")
                        return
                except Exception as e:
                    print(f"Error getting contract details (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(1)  # Wait before retry
                    continue
            else:
                print("Failed to get contract details after 3 attempts")
                return
                    
            if contract_details.fulfilled:
                print(f"Contract {contract.id} is already fulfilled")
                await self.fulfill_contract(contract.id)
                return
                
            # If not fulfilled, check delivery requirements
            for delivery in contract_details.terms.deliver:
                print(f"Contract requires {delivery.units_required} units of {delivery.trade_symbol}")
                print(f"Currently fulfilled: {delivery.units_fulfilled}")
                if delivery.units_fulfilled < delivery.units_required:
                    remaining = delivery.units_required - delivery.units_fulfilled
                    print(f"Need to deliver {remaining} units to {delivery.destination_symbol}")
                    
                    # Find a suitable ship for mining
                    mining_ship = None
                    for ship in ships.values():
                        if (
                            hasattr(ship, 'cargo') 
                            and ship.cargo.capacity > 0
                            and ship.cargo.units == 0  # Only use empty ships
                            and hasattr(ship, 'nav')
                            and ship.nav.status != ShipNavStatus.IN_TRANSIT
                        ):
                            # Check if the ship has mining capabilities
                            mounts = await self.shipyard_manager.get_ship_mounts(ship.symbol)
                            if self.shipyard_manager.has_mining_mount(mounts):
                                mining_ship = ship
                                break

                    if not mining_ship:
                        print("No suitable mining ship available. Attempting to purchase one...")
                        # Try to purchase a mining ship in the current system
                        current_system = ship.nav.system_symbol if hasattr(ship, 'nav') else None
                        if current_system:
                            purchase_response = await self.shipyard_manager.purchase_mining_ship(
                                system_symbol=current_system
                            )
                            if purchase_response:
                                # Update ships list
                                print("Successfully purchased new mining ship")
                                return  # Exit to let fleet manager update ships list
                            else:
                                print("Failed to purchase mining ship")
                                return
                        else:
                            print("Could not determine current system")
                            return

                    print(f"Using ship {mining_ship.symbol} for mining {delivery.trade_symbol}")
                    
                    # Ensure ship can mine
                    can_mine = await self.ensure_ship_can_mine(mining_ship)
                    if not can_mine:
                        print("Unable to prepare ship for mining")
                        return
                        
                    # Find a mining site
                    if not hasattr(mining_ship, 'nav'):
                        print("Ship has no navigation data")
                        return
                        
                    current_system = mining_ship.nav.system_symbol
                    mining_site = await self.find_mining_site(current_system)
                    
                    if not mining_site:
                        print("Could not find suitable mining location")
                        return
                        
                    print(f"Found mining site at {mining_site}")
                    
                    # Navigate to mining site
                    if not await self.navigate_to_waypoint(mining_ship, mining_site):
                        print("Failed to navigate to mining site")
                        return
                        
                    if not await self.wait_for_arrival(mining_ship.symbol):
                        print("Failed while waiting for arrival")
                        return

                    # The ship needs to be in orbit for surveys
                    response = await orbit_ship.asyncio_detailed(
                        ship_symbol=mining_ship.symbol,
                        client=self.client
                    )
                    if response.status_code != 200:
                        print(f"Failed to move ship to orbit: {response.status_code}")
                        return
                    print(f"Ship {mining_ship.symbol} moved to orbit")
                    
                    # Create surveys until we find the resource we need
                    max_attempts = 5
                    attempts = 0
                    best_survey = None
                    
                    while attempts < max_attempts:
                        attempts += 1
                        print(f"Survey attempt {attempts}/{max_attempts}")
                        
                        # Wait for any cooldowns before surveying
                        if not hasattr(mining_ship, 'cooldown') or (
                            mining_ship.cooldown 
                            and mining_ship.cooldown.remaining_seconds > 0
                        ):
                            print("Ship is on cooldown")
                            await asyncio.sleep(
                                mining_ship.cooldown.remaining_seconds 
                                if hasattr(mining_ship, 'cooldown') 
                                and mining_ship.cooldown 
                                else 5
                            )
                        
                        # Create a new survey
                        survey = await survey_manager.create_survey(mining_ship.symbol)
                        if not survey:
                            print("Failed to create survey")
                            return
                            
                        print(f"Survey created at waypoint {survey.symbol}")
                        
                        # Check if we found what we need
                        best_survey = survey_manager.get_best_survey(delivery.trade_symbol)
                        if best_survey:
                            print(f"Found survey with {delivery.trade_symbol}")
                            break
                        else:
                            print(f"No {delivery.trade_symbol} in this survey, trying again...")
                            
                    if not best_survey:
                        print(f"Could not find {delivery.trade_symbol} after {max_attempts} surveys")
                        return
                        
                    # Wait for any cooldowns before extracting
                    if not hasattr(mining_ship, 'cooldown') or (
                        mining_ship.cooldown 
                        and mining_ship.cooldown.remaining_seconds > 0
                    ):
                        print("Ship is on cooldown")
                        await asyncio.sleep(
                            mining_ship.cooldown.remaining_seconds 
                            if hasattr(mining_ship, 'cooldown') 
                            and mining_ship.cooldown 
                            else 5
                        )
                    
                    # Attempt extraction with the best survey
                    extraction = await survey_manager.extract_resources_with_survey(
                        mining_ship.symbol,
                        best_survey
                    )
                    
                    if extraction and hasattr(extraction, 'yield_'):
                        print(f"Extracted {extraction.yield_.units} units of {extraction.yield_.symbol}")
                        
                        # If we mined the right resource, try to deliver it
                        if extraction.yield_.symbol == delivery.trade_symbol:
                            # Navigate to delivery point
                            if not await self.navigate_to_waypoint(
                                mining_ship,
                                delivery.destination_symbol
                            ):
                                print("Failed to navigate to delivery point")
                                return
                                
                            if not await self.wait_for_arrival(mining_ship.symbol):
                                print("Failed while waiting for delivery arrival")
                                return
                            
                            delivered = await self.deliver_contract_cargo(
                                contract_id=contract.id,
                                ship_symbol=mining_ship.symbol,
                                trade_symbol=delivery.trade_symbol,
                                units=min(extraction.yield_.units, remaining)
                            )
                            
                            if delivered:
                                print(f"Successfully delivered cargo for contract {contract.id}")
                            else:
                                print("Failed to deliver cargo")
                        else:
                            print(f"Extracted {extraction.yield_.symbol} but needed {delivery.trade_symbol}")
                    else:
                        print("Extraction failed or yielded no resources")
                        
                    print("Continuing to next trade cycle...")
                    return
                    
        except Exception as e:
            contract_id = (
                contract.id if hasattr(contract, 'id') else 'unknown'
            )
            import traceback
            print(f'Error processing contract {contract_id}: {e}')
            print('Full traceback:')
            print(traceback.format_exc())