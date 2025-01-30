"""
SpaceTraders automated game client
"""
import os
import asyncio
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from space_traders_api_client import AuthenticatedClient
from space_traders_api_client.api.agents import get_my_agent
from space_traders_api_client.api.fleet import (
    get_my_ships,
    orbit_ship,
    dock_ship,
    refuel_ship,
    navigate_ship,
    extract_resources,
    purchase_ship
)
from space_traders_api_client.api.systems import (
    get_system,
    get_systems,
    get_system_waypoints,
    get_shipyard
)
from space_traders_api_client.api.contracts import (
    get_contracts,
    get_contract,
    accept_contract,
    deliver_contract,
    fulfill_contract
)
from space_traders_api_client.models.agent import Agent
from space_traders_api_client.models.ship import Ship
from space_traders_api_client.models.ship_nav_status import ShipNavStatus
from space_traders_api_client.models.ship_registration import ShipRegistration
from space_traders_api_client.models.ship_role import ShipRole
from space_traders_api_client.models.ship_fuel import ShipFuel
from space_traders_api_client.models.ship_cargo import ShipCargo
from tests.factories import ShipFactory, ShipNavFactory
from space_traders_api_client.models.waypoint_type import WaypointType
from space_traders_api_client.models.waypoint_trait_symbol import WaypointTraitSymbol
from space_traders_api_client.models.ship_type import ShipType
from space_traders_api_client.models.system import System
from space_traders_api_client.models.contract import Contract
from space_traders_api_client.models.deliver_contract_body import DeliverContractBody

class SpaceTrader:
    """Main game automation class"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the SpaceTrader with optional token"""
        load_dotenv()
        self.token = token or os.getenv('SPACETRADERS_TOKEN')
        if not self.token:
            raise ValueError("No token provided. Set SPACETRADERS_TOKEN env var or pass token to constructor")
        
        # Initialize the client
        self.client = AuthenticatedClient(
            base_url="https://api.spacetraders.io/v2",
            token=self.token,
            timeout=30.0,
            verify_ssl=True
        )
        self.agent: Optional[Agent] = None
        self.ships: Dict[str, Ship] = {}
        self.current_system: Optional[System] = None
        self.contracts: Dict[str, Contract] = {}  # Store active contracts
        
    async def initialize(self):
        """Initialize the game state and verify connection"""
        # Get agent status
        response = await get_my_agent.asyncio_detailed(client=self.client)
        if response.status_code != 200:
            raise Exception(f"Failed to get agent status: {response.status_code}")
        self.agent = response.parsed.data
        
        # Get ships
        ships_response = await get_my_ships.asyncio_detailed(client=self.client)
        if ships_response.status_code != 200:
            raise Exception(f"Failed to get ships: {ships_response.status_code}")
        
        self.ships = {
            ship.symbol: ship 
            for ship in ships_response.parsed.data
        }
        
        # Get current system if we have ships
        if self.ships:
            first_ship = next(iter(self.ships.values()))
            system_response = await get_system.asyncio_detailed(
                system_symbol=first_ship.nav.system_symbol,
                client=self.client
            )
            if system_response.status_code == 200:
                self.current_system = system_response.parsed.data

        # Get active contracts
        await self.update_contracts()
    
    async def update_contracts(self):
        """Update the list of available contracts"""
        try:
            response = await get_contracts.asyncio_detailed(client=self.client)
            if response.status_code == 200:
                self.contracts = {
                    contract.id: contract
                    for contract in response.parsed.data
                }
                print(f"Found {len(self.contracts)} active contracts")
            else:
                print(f"Failed to get contracts: {response.status_code}")
        except Exception as e:
            print(f"Error updating contracts: {e}")

    async def accept_contract(self, contract_id: str) -> bool:
        """Accept a contract by ID"""
        try:
            response = await accept_contract.asyncio_detailed(
                contract_id=contract_id,
                client=self.client
            )
            if response.status_code == 200:
                print(f"Successfully accepted contract {contract_id}")
                await self.update_contracts()  # Refresh contracts
                return True
            else:
                print(f"Failed to accept contract: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error accepting contract: {e}")
            return False

    async def deliver_contract_cargo(self, contract_id: str, ship_symbol: str, trade_symbol: str, units: int) -> bool:
        """Deliver cargo for a contract"""
        try:
            body = DeliverContractBody(
                ship_symbol=ship_symbol,
                trade_symbol=trade_symbol,
                units=units
            )
            response = await deliver_contract.asyncio_detailed(
                contract_id=contract_id,
                client=self.client,
                body=body
            )
            if response.status_code == 200:
                print(f"Successfully delivered {units} units of {trade_symbol} for contract {contract_id}")
                return True
            else:
                print(f"Failed to deliver cargo: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error delivering cargo: {e}")
            return False

    async def fulfill_contract(self, contract_id: str) -> bool:
        """Fulfill a completed contract"""
        try:
            response = await fulfill_contract.asyncio_detailed(
                contract_id=contract_id,
                client=self.client
            )
            if response.status_code == 200:
                print(f"Successfully fulfilled contract {contract_id}")
                await self.update_contracts()  # Refresh contracts
                return True
            else:
                print(f"Failed to fulfill contract: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error fulfilling contract: {e}")
            return False

    async def get_agent_status(self) -> Agent:
        """Get current agent status"""
        response = await get_my_agent.asyncio_detailed(client=self.client)
        if response.status_code != 200:
            raise Exception(f"Failed to get agent status: {response.status_code}")
        self.agent = response.parsed.data
        return self.agent
    
    async def scan_systems(self, limit: int = 20) -> list[System]:
        """Scan nearby systems for opportunities"""
        response = await get_systems.asyncio_detailed(
            client=self.client,
            limit=limit
        )
        if response.status_code != 200:
            raise Exception(f"Failed to list systems: {response.status_code}")
        return response.parsed.data
    
    async def manage_fleet(self):
        """Manage fleet operations"""
        # Update ship statuses
        ships_response = await get_my_ships.asyncio_detailed(client=self.client)
        if ships_response.status_code != 200:
            raise Exception(f"Failed to get ships: {ships_response.status_code}")
        
        self.ships = {
            ship.symbol: ship 
            for ship in ships_response.parsed.data
        }

        # Update contracts
        await self.update_contracts()
        
        # Process each ship
        for ship in self.ships.values():
            await self._process_ship(ship)
            
        # Check for deliverable contracts
        for contract_id, contract in self.contracts.items():
            if not contract.accepted:
                print(f"Found unaccepted contract {contract_id}")
                await self.accept_contract(contract_id)
            elif contract.fulfilled:
                print(f"Contract {contract_id} is already fulfilled")
            else:
                print(f"Processing contract {contract_id}")
                await self._process_contract(contract)

    async def _process_ship(self, ship: Ship):
        """Process individual ship actions based on its state"""
        try:
            if not hasattr(ship, 'nav'):
                print(f"Ship {ship.symbol} has no navigation data")
                return
                
            # If ship is in transit, wait for it to arrive
            if ship.nav.status == ShipNavStatus.IN_TRANSIT:
                print(f"Ship {ship.symbol} is in transit to {ship.nav.waypoint_symbol}")
                return
                
            # If ship is at a market waypoint, consider trading
            if ship.nav.status == ShipNavStatus.DOCKED:
                print(f"Ship {ship.symbol} is docked at {ship.nav.waypoint_symbol}")
                await self._handle_market_actions(ship)
            else:
                print(f"Ship {ship.symbol} is {ship.nav.status} at {ship.nav.waypoint_symbol}")
                
        except Exception as e:
            print(f"Error processing ship {ship.symbol}: {e}")
    
    async def _handle_market_actions(self, ship: Ship):
        """Handle market-related actions for a ship"""
        try:
            if not hasattr(ship, 'cargo'):
                print(f"Ship {ship.symbol} has no cargo data")
                return
                
            print(f"Analyzing market options for ship {ship.symbol}")
            print(f"Current cargo: {ship.cargo.units}/{ship.cargo.capacity} units")
            if hasattr(ship.cargo, 'inventory'):
                for item in ship.cargo.inventory:
                    print(f"- {item.units}x {item.symbol}")
            
        except Exception as e:
            print(f"Error handling market actions for ship {ship.symbol}: {e}")

    async def _process_contract(self, contract: Contract):
        """Process a specific contract's requirements"""
        try:
            if not contract or not hasattr(contract, 'terms'):
                print(f"Contract has invalid format")
                return
                
            if not hasattr(contract.terms, 'deliver') or not contract.terms.deliver:
                print(f"Contract {contract.id} has no delivery requirements")
                return

            for delivery in contract.terms.deliver:
                if not hasattr(delivery, 'trade_symbol') or not hasattr(delivery, 'units_required'):
                    print(f"Delivery in contract {contract.id} has invalid format")
                    continue
                    
                # Find a suitable ship for delivery
                for ship in self.ships.values():
                    if not hasattr(ship, 'nav') or not hasattr(ship, 'cargo'):
                        continue
                        
                    if ship.nav.status != ShipNavStatus.DOCKED:
                        continue
                        
                    # Check if ship has required cargo
                    if not hasattr(ship.cargo, 'inventory'):
                        continue
                        
                    for item in ship.cargo.inventory:
                        if (item.symbol == delivery.trade_symbol and 
                            item.units >= delivery.units_required):
                            
                            # Attempt delivery
                            try:
                                success = await self.deliver_contract_cargo(
                                    contract_id=contract.id,
                                    ship_symbol=ship.symbol,
                                    trade_symbol=delivery.trade_symbol,
                                    units=delivery.units_required
                                )
                                
                                if success:
                                    # Check if contract can be fulfilled
                                    contract_details = await get_contract.asyncio(
                                        contract_id=contract.id,
                                        client=self.client
                                    )
                                    if contract_details and contract_details.fulfilled:
                                        await self.fulfill_contract(contract.id)
                                return
                            except Exception as e:
                                print(f"Error delivering cargo for contract {contract.id}: {e}")
                                
        except Exception as e:
            print(f"Error processing contract {contract.id if hasattr(contract, 'id') else 'unknown'}: {e}")

    async def trade_loop(self):
        """Main trading loop"""
        while True:
            try:
                # Update agent status
                await self.get_agent_status()
                
                # Manage fleet operations
                await self.manage_fleet()
                
                # Add delay to avoid rate limiting
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"Error in trade loop: {e}")
                await asyncio.sleep(10)  # Longer delay on error

    async def find_engineered_asteroids(self, system_symbol: str) -> List[Dict[str, Any]]:
        """Find engineered asteroids in the given system"""
        response = await get_system_waypoints.sync_detailed(
            system_symbol=system_symbol,
            client=self.client,
            type_=WaypointType.ENGINEERED_ASTEROID
        )
        if response.status_code == 200 and response.parsed:
            return response.parsed.data
        return []

    async def navigate_to_waypoint(self, ship_symbol: str, waypoint_symbol: str) -> bool:
        """Navigate ship to a specific waypoint"""
        response = await navigate_ship.sync_detailed(
            ship_symbol=ship_symbol,
            client=self.client,
            json_body={"waypointSymbol": waypoint_symbol}
        )
        return response.status_code == 200

    async def dock_ship(self, ship_symbol: str) -> bool:
        """Dock the ship at current waypoint"""
        response = await dock_ship.sync_detailed(
            ship_symbol=ship_symbol,
            client=self.client
        )
        return response.status_code == 200

    async def refuel_ship(self, ship_symbol: str) -> bool:
        """Refuel the ship at current waypoint"""
        response = await refuel_ship.sync_detailed(
            ship_symbol=ship_symbol,
            client=self.client
        )
        return response.status_code == 200

    async def orbit_ship(self, ship_symbol: str) -> bool:
        """Put the ship in orbit at current waypoint"""
        response = await orbit_ship.sync_detailed(
            ship_symbol=ship_symbol,
            client=self.client
        )
        return response.status_code == 200

    async def extract_resources(self, ship_symbol: str) -> Optional[Dict[str, Any]]:
        """Extract resources at current location"""
        response = await extract_resources.sync_detailed(
            ship_symbol=ship_symbol,
            client=self.client
        )
        if response.status_code == 200 and response.parsed:
            return response.parsed["data"]
        return None

    async def mine_asteroid(self, ship_symbol: str, asteroid_waypoint: str) -> bool:
        """Complete mining operation at an asteroid
        
        Steps:
        1. Navigate to asteroid
        2. Dock and refuel
        3. Orbit asteroid
        4. Extract resources
        """
        # Navigate to asteroid
        if not await self.navigate_to_waypoint(ship_symbol, asteroid_waypoint):
            return False
            
        # Wait for navigation to complete
        ship = self.ships.get(ship_symbol)
        while ship and ship.nav.status == ShipNavStatus.IN_TRANSIT:
            await asyncio.sleep(1)
            ship = (await get_my_ships.sync_detailed(client=self.client, limit=20)).parsed.data[0]
            
        # Dock and refuel
        if not await self.dock_ship(ship_symbol):
            return False
        if not await self.refuel_ship(ship_symbol):
            return False
            
        # Orbit asteroid
        if not await self.orbit_ship(ship_symbol):
            return False
            
        # Extract resources
        result = await self.extract_resources(ship_symbol)
        return result is not None

    async def find_shipyard(self, system_symbol: str) -> Optional[Dict[str, Any]]:
        """Find a shipyard in the given system"""
        response = await get_system_waypoints.asyncio_detailed(
            system_symbol=system_symbol,
            client=self.client,
            traits=[WaypointTraitSymbol.SHIPYARD]
        )
        if response.status_code == 200 and response.parsed and response.parsed.data:
            return response.parsed.data[0]
        return None

    async def get_available_ships(self, system_symbol: str, waypoint_symbol: str) -> List[Dict[str, Any]]:
        """Get list of ships available for purchase at a shipyard"""
        response = await get_shipyard.asyncio_detailed(
            system_symbol=system_symbol,
            waypoint_symbol=waypoint_symbol,
            client=self.client
        )
        if response.status_code == 200 and response.parsed:
            return response.parsed["data"]["ships"]
        return []

    async def purchase_mining_ship(self, system_symbol: str) -> Optional[Ship]:
        """Purchase a mining ship from the nearest shipyard
        
        Returns:
            The newly purchased ship if successful, None otherwise
        """
        # Find a shipyard
        shipyard = await self.find_shipyard(system_symbol)
        if not shipyard:
            print(f"No shipyard found in system {system_symbol}")
            return None
            
        # Get available ships
        ships = await self.get_available_ships(system_symbol, shipyard.symbol)
        mining_ships = [s for s in ships if s["type"] == ShipType.SHIP_MINING_DRONE]
        
        if not mining_ships:
            print(f"No mining ships available at shipyard {shipyard.symbol}")
            return None
            
        # Purchase the ship
        response = await purchase_ship.asyncio_detailed(
            client=self.client,
            json_body={
                "shipType": ShipType.SHIP_MINING_DRONE,
                "waypointSymbol": shipyard.symbol
            }
        )
        
        if response.status_code == 201 and response.parsed:
            ship_data = response.parsed["data"]["ship"]
            # Handle both dictionary and Ship object responses
            if isinstance(ship_data, dict):
                # Convert registration dict to ShipRegistration object if needed
                if isinstance(ship_data.get('registration'), dict):
                    ship_data['registration'] = ShipRegistration(**ship_data['registration'])
                ship = ShipFactory(**ship_data)
            else:
                ship = ship_data  # Already a Ship object
                
            self.ships[ship.symbol] = ship
            print(f"Successfully purchased mining ship {ship.symbol}")
            return ship
            
        print(f"Failed to purchase mining ship: {response.parsed.error.message if response.parsed else 'Unknown error'}")
        return None
